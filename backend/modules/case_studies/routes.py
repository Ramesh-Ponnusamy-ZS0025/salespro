"""
Case Studies Module for Chrome Extension
Uses existing VectorDatabase and CaseStudyManager from main backend
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from login import User, get_current_user
import logging

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["case-studies"])

# Database and case study manager references
db = None
case_study_manager = None

def set_db(database):
    global db
    db = database

def set_case_study_manager(manager):
    global case_study_manager
    case_study_manager = manager

# ============== MODELS ==============

class LinkedInProfileData(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    about: Optional[str] = None
    company_description: Optional[str] = None
    industry: Optional[str] = None

class RelevantCaseStudiesRequest(BaseModel):
    linkedin_data: LinkedInProfileData
    limit: int = 20

# ============== ENDPOINTS ==============

@router.get("/case-studies")
async def get_case_studies(
    query: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Get all case studies or search with query using vector similarity
    """
    try:
        if not case_study_manager:
            raise HTTPException(status_code=500, detail="Case study manager not initialized")

        if not case_study_manager.vector_db:
            raise HTTPException(status_code=500, detail="Vector database not available")

        # If query provided, use vector similarity search
        if query:
            logger.info(f"Vector search for: '{query}'")

            # Use vector DB search with similarity scores
            similar_cases = case_study_manager.vector_db.search_similar(
                query=query,
                top_k=min(limit, 100),
                min_similarity=0.2
            )

            # Fetch full details from MongoDB
            if similar_cases:
                file_ids = [cs['file_id'] for cs in similar_cases]
                documents = await db.document_files.find(
                    {"id": {"$in": file_ids}},
                    {"_id": 0}
                ).to_list(len(file_ids))

                # Create a mapping for quick lookup
                doc_map = {doc['id']: doc for doc in documents}

                # Combine vector DB results with MongoDB data
                case_studies = []
                for cs in similar_cases:
                    doc = doc_map.get(cs['file_id'])
                    if doc:
                        # Get similarity value
                        similarity = cs['similarity']

                        # Convert to percentage (0-100)
                        relevance_score = round(similarity * 100, 2)


                        # Clamp to 0-100 range
                        relevance_score = max(0.0, min(100.0, relevance_score))
                        relevance_score=round(relevance_score)

                        case_studies.append({
                            'id': doc['id'],
                            'title': doc.get('filename', cs.get('title', 'Untitled')),
                            'excerpt': doc.get('summary', cs.get('summary', '')),
                            'summary': doc.get('summary', cs.get('summary', '')),
                            'url': doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else '',
                            'file_url': doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else '',
                            'categories': [doc.get('category', '')] if doc.get('category') else [],
                            'category': doc.get('category', cs.get('category', '')),
                            'doc_type': doc.get('doc_type', ''),
                            'keywords': [],
                            'industry': doc.get('category', ''),
                            'technologies': [],
                            'results': doc.get('summary', ''),
                            'relevance_score': relevance_score,
                            'similarity': cs['similarity']
                        })

                logger.info(f"✓ Found {len(case_studies)} case studies with relevance scores")
                return {
                    "case_studies": case_studies,
                    "total": len(case_studies)
                }

        # No query - return all case studies
        logger.info("Fetching all case studies from vector DB")
        all_cases = case_study_manager.vector_db.get_all_case_studies()

        # Fetch full details from MongoDB
        if all_cases:
            file_ids = [cs['file_id'] for cs in all_cases]
            documents = await db.document_files.find(
                {"id": {"$in": file_ids}},
                {"_id": 0}
            ).limit(limit).to_list(limit)

            case_studies = []
            for doc in documents:
                case_studies.append({
                    'id': doc['id'],
                    'title': doc.get('filename', 'Untitled'),
                    'excerpt': doc.get('summary', ''),
                    'summary': doc.get('summary', ''),
                    'url': doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else '',
                    'file_url': doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else '',
                    'categories': [doc.get('category', '')] if doc.get('category') else [],
                    'category': doc.get('category', ''),
                    'doc_type': doc.get('doc_type', ''),
                    'keywords': [],
                    'industry': doc.get('category', ''),
                    'technologies': [],
                    'results': doc.get('summary', ''),
                    'relevance_score': 0.0
                })

            logger.info(f"✓ Returning {len(case_studies)} case studies")
            return {
                "case_studies": case_studies,
                "total": len(case_studies)
            }

        # Fallback: No vector DB data, try MongoDB directly
        logger.warning("No data in vector DB, falling back to MongoDB")
        documents = await db.document_files.find(
            {},
            {"_id": 0}
        ).limit(limit).to_list(limit)

        case_studies = []
        for doc in documents:
            case_studies.append({
                'id': doc['id'],
                'title': doc.get('filename', 'Untitled'),
                'excerpt': doc.get('summary', ''),
                'summary': doc.get('summary', ''),
                'url': doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else '',
                'file_url': doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else '',
                'categories': [doc.get('category', '')] if doc.get('category') else [],
                'category': doc.get('category', ''),
                'doc_type': doc.get('doc_type', ''),
                'keywords': [],
                'industry': doc.get('category', ''),
                'technologies': [],
                'results': doc.get('summary', ''),
                'relevance_score': 0.0
            })

        return {
            "case_studies": case_studies,
            "total": len(case_studies)
        }

    except Exception as e:
        logger.error(f"Error fetching case studies: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch case studies: {str(e)}"
        )


@router.post("/case-studies/relevant")
async def get_relevant_case_studies(
    request: dict,  # Accept any dict to handle both formats
    current_user: User = Depends(get_current_user)
):
    """
    Get relevant case studies based on LinkedIn profile using vector similarity

    Accepts two formats:
    1. {"linkedin_data": {...}, "limit": 20}  (new format)
    2. {...profile data...}  (Chrome extension format)
    """
    try:
        if not case_study_manager:
            raise HTTPException(status_code=500, detail="Case study manager not initialized")

        if not case_study_manager.vector_db:
            raise HTTPException(status_code=500, detail="Vector database not available")

        # Handle both request formats
        if 'linkedin_data' in request:
            # New format: {"linkedin_data": {...}, "limit": 20}
            linkedin_data = request['linkedin_data']
            limit = min(request.get('limit', 20), 100)
        else:
            # Chrome extension format: profile data directly
            linkedin_data = request
            limit = min(request.get('limit', 20), 100)

        # Build search query from LinkedIn profile
        query_parts = []

        if linkedin_data.get('title'):
            query_parts.append(linkedin_data['title'])

        if linkedin_data.get('company'):
            query_parts.append(linkedin_data['company'])

        if linkedin_data.get('about'):
            query_parts.append(linkedin_data['about'][:200])

        if linkedin_data.get('company_description'):
            query_parts.append(linkedin_data['company_description'][:200])

        if linkedin_data.get('industry'):
            query_parts.append(linkedin_data['industry'])

        # Build final search query
        search_query = ' '.join(query_parts)

        logger.info(f"Vector search for LinkedIn profile: {linkedin_data.get('name', 'Unknown')}")
        logger.info(f"Search query: '{search_query[:100]}...'")

        # If no search query built, return empty results
        if not search_query.strip():
            logger.warning("No search query could be built from profile data")
            return {
                "case_studies": [],
                "total": 0
            }

        # Use vector DB search with similarity scores
        similar_cases = case_study_manager.vector_db.search_similar(
            query=search_query,
            top_k=limit,
            min_similarity=0.2
        )

        # DEBUG: Log actual similarity values
        if similar_cases:
            logger.info(f"DEBUG: First case similarity value: {similar_cases[0].get('similarity')}")
            logger.info(f"DEBUG: First case similarity type: {type(similar_cases[0].get('similarity'))}")

        if not similar_cases:
            logger.warning("No similar case studies found, returning empty list")
            return {
                "case_studies": [],
                "total": 0
            }

        # Fetch full details from MongoDB
        file_ids = [cs['file_id'] for cs in similar_cases]
        documents = await db.document_files.find(
            {"id": {"$in": file_ids}},
            {"_id": 0}
        ).to_list(len(file_ids))

        # Create a mapping for quick lookup
        doc_map = {doc['id']: doc for doc in documents}

        # Combine vector DB results with MongoDB data
        case_studies = []
        for cs in similar_cases:
            doc = doc_map.get(cs['file_id'])
            if doc:
                # Get similarity value
                similarity = cs['similarity']

                # DEBUG: Log the actual value
                logger.info(f"DEBUG: Raw similarity for {doc.get('filename', 'unknown')}: {similarity}")

                # Convert to percentage (0-100)
                # The similarity should be 0-1 from cosine similarity
                relevance_score = round(similarity * 100, 2)

                # Clamp to 0-100 range to handle any edge cases
                relevance_score = max(0.0, min(100.0, relevance_score))
                relevance_score = round(relevance_score)

                logger.info(f"DEBUG: Calculated relevance_score: {relevance_score}")

                case_studies.append({
                    'id': doc['id'],
                    'title': doc.get('filename', cs.get('title', 'Untitled')),
                    'excerpt': doc.get('summary', cs.get('summary', ''))[:200],
                    'summary': doc.get('summary', cs.get('summary', '')),
                    'url': doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else '',
                    'file_url': doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else '',
                    'categories': [doc.get('category', '')] if doc.get('category') else [],
                    'category': doc.get('category', cs.get('category', '')),
                    'doc_type': doc.get('doc_type', ''),
                    'keywords': [],
                    'industry': doc.get('category', ''),
                    'technologies': [],
                    'results': doc.get('summary', ''),
                    'relevance_score': relevance_score,
                    'similarity': cs['similarity']
                })

        # Sort by relevance score
        case_studies.sort(key=lambda x: x['relevance_score'], reverse=True)

        logger.info(f"✓ Found {len(case_studies)} relevant case studies")

        return {
            "case_studies": case_studies,
            "total": len(case_studies)
        }

    except Exception as e:
        logger.error(f"Error finding relevant case studies: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find relevant case studies: {str(e)}"
        )
