"""
Standalone Zuci Case Studies Scraper Worker
Runs as a separate process to avoid uvicorn event loop issues
"""
import asyncio
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from document_management import crawl_zuci_with_playwright, PLAYWRIGHT_AVAILABLE
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def generate_case_study_summary(study: dict, groq_client) -> str:
    """Generate a 5-6 line summary for a case study using LLM"""
    try:
        from groq import Groq

        description = study.get('description', '')
        title = study.get('title', '')
        category = study.get('category', '')
        tags = ', '.join(study.get('tags', [])[:3])

        summary_prompt = f"""Summarize this case study in 5-6 concise lines:

Title: {title}
Category: {category}
Description: {description}
Tags: {tags}

Provide a clear, informative summary that explains:
1. What the case study is about
2. The industry/domain
3. Key challenges or problems addressed
4. Main solutions or outcomes
5. Business impact or results

Keep it professional and focused on business value. Maximum 6 lines."""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a business analyst creating concise case study summaries."},
                {"role": "user", "content": summary_prompt}
            ],
            model="llama-3.1-8b-instant",  # Faster model for quicker generation
            temperature=0.3,  # Lower temperature for more consistent outputs
        )

        summary = chat_completion.choices[0].message.content
        lines = [line.strip() for line in summary.split('\n') if line.strip()]
        summary = '\n'.join(lines[:6])
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return f"{study.get('title', 'Case Study')}\n{study.get('category', 'General')} - {study.get('type', 'Case Study')}\n{study.get('description', '')[:200]}"


async def run_scraper(user_id: str):
    """Main scraper function that runs independently"""

    # Load environment
    load_dotenv(Path(__file__).parent / '.env')

    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]

    # Initialize Groq
    from groq import Groq
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    groq_client = Groq(api_key=GROQ_API_KEY)

    # Initialize CaseStudyManager for vector database storage
    from config.case_study_manager import CaseStudyManager
    case_study_manager = CaseStudyManager(db, llm_function=None)
    logger.info("✓ CaseStudyManager initialized for vector database storage")

    result = {
        "success": False,
        "message": "",
        "total_found": 0,
        "total_saved": 0,
        "total_updated": 0,
        "case_studies": []
    }

    try:
        logger.info("Starting Zuci case studies scraping in worker process...")

        if not PLAYWRIGHT_AVAILABLE:
            result["message"] = "Playwright not installed. Run: pip install playwright && playwright install"
            return result

        # Scrape case studies
        logger.info("Using Playwright for scraping (bypasses Cloudflare/bot detection)")
        case_studies = await crawl_zuci_with_playwright()

        if not case_studies:
            result["message"] = "No case studies found"
            return result

        result["total_found"] = len(case_studies)
        saved_studies = []
        updated_studies = []

        # Process each case study
        logger.info(f"🤖 Generating AI summaries for {len(case_studies)} case studies...")

        for idx, study in enumerate(case_studies, 1):
            try:
                filename = study.get('filename', f"{study['title'][:50].replace(' ', '_')}.pdf")

                logger.info(f"[{idx}/{len(case_studies)}] 🤖 Generating summary for: {study['title'][:60]}...")
                summary = await generate_case_study_summary(study, groq_client)
                logger.info(f"[{idx}/{len(case_studies)}] ✓ Summary generated")

                doc_file = {
                    "id": str(uuid.uuid4()),
                    "filename": filename,
                    "category": study.get('category', 'General'),
                    "doc_type": study.get('type', 'Case Study'),
                    "file_content": study.get('file_content', ''),
                    "file_size": study.get('file_size', 0),
                    "mime_type": "application/pdf",
                    "summary": summary,
                    "uploaded_by": user_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "metadata": {
                        "source": "zuci_systems",
                        "source_url": study.get('source_url'),
                        "pdf_url": study.get('pdf_url'),
                        "description": study.get('description'),
                        "tags": study.get('tags', [])
                    }
                }

                if doc_file['file_content']:
                    existing_doc = await db.document_files.find_one(
                        {"filename": filename},
                        {"_id": 0, "id": 1}
                    )

                    if existing_doc:
                        doc_file['id'] = existing_doc['id']
                        doc_file['updated_at'] = datetime.now(timezone.utc).isoformat()

                        await db.document_files.replace_one(
                            {"id": existing_doc['id']},
                            doc_file
                        )
                        logger.info(f"[{idx}/{len(case_studies)}] 💾 Updated in DB: {filename[:40]}")

                        # Store/update in vector database for semantic search
                        try:
                            case_study_manager.store_in_vector_db(
                                file_id=doc_file['id'],
                                file_url=study.get('source_url', ''),
                                title=study['title'],
                                summary=summary,
                                category=doc_file['category']
                            )
                            logger.info(f"✓ Embeddings stored/updated for: {filename}")
                        except Exception as e:
                            logger.error(f"Failed to store embeddings for {filename}: {e}")

                        updated_studies.append({
                            "id": doc_file['id'],
                            "title": study['title'],
                            "category": doc_file['category'],
                            "type": doc_file['doc_type'],
                            "source_url": study.get('source_url'),
                            "pdf_url": study.get('pdf_url'),
                            "filename": doc_file['filename'],
                            "tags": study.get('tags', []),
                            "summary": summary,
                            "action": "updated"
                        })
                    else:
                        await db.document_files.insert_one(doc_file)
                        logger.info(f"[{idx}/{len(case_studies)}] 💾 Created new in DB: {filename[:40]}")

                        # Store in vector database for semantic search
                        try:
                            case_study_manager.store_in_vector_db(
                                file_id=doc_file['id'],
                                file_url=study.get('source_url', ''),
                                title=study['title'],
                                summary=summary,
                                category=doc_file['category']
                            )
                            logger.info(f"✓ Embeddings stored for: {filename}")
                        except Exception as e:
                            logger.error(f"Failed to store embeddings for {filename}: {e}")

                        saved_studies.append({
                            "id": doc_file['id'],
                            "title": study['title'],
                            "category": doc_file['category'],
                            "type": doc_file['doc_type'],
                            "source_url": study.get('source_url'),
                            "pdf_url": study.get('pdf_url'),
                            "filename": doc_file['filename'],
                            "tags": study.get('tags', []),
                            "summary": summary,
                            "action": "created"
                        })

            except Exception as e:
                logger.error(f"Error saving case study {study.get('title')}: {str(e)}")
                continue

        all_studies = saved_studies + updated_studies

        # Log vector database statistics
        vector_db_count = 0
        if case_study_manager.vector_db:
            try:
                all_vector_studies = case_study_manager.vector_db.get_all_case_studies()
                vector_db_count = len(all_vector_studies)
                logger.info(f"✓ Vector database now contains {vector_db_count} case studies for semantic search")
            except Exception as e:
                logger.error(f"Error getting vector DB stats: {e}")

        result.update({
            "success": True,
            "message": f"Successfully processed {len(all_studies)} case studies ({len(saved_studies)} new, {len(updated_studies)} updated). Vector DB: {vector_db_count} embeddings stored.",
            "total_saved": len(saved_studies),
            "total_updated": len(updated_studies),
            "vector_db_count": vector_db_count,
            "case_studies": all_studies
        })

    except Exception as e:
        logger.error(f"Error in scraper worker: {str(e)}")
        import traceback
        traceback.print_exc()
        result["message"] = f"Failed to scrape case studies: {str(e)}"
    finally:
        client.close()

    return result


if __name__ == "__main__":
    # Get user_id from command line argument
    user_id = sys.argv[1] if len(sys.argv) > 1 else "system"

    # Run the scraper
    result = asyncio.run(run_scraper(user_id))

    # Output result as JSON
    print(json.dumps(result))
