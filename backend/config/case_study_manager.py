"""
Centralized Case Study Manager
Provides auto-pick logic and consistent case study selection across all modules
Uses vector embeddings for fast semantic search
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import sqlite3
import numpy as np
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import sentence-transformers, fallback gracefully
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Vector search will be disabled.")
    logger.warning("Install with: pip install sentence-transformers")


class VectorDatabase:
    """
    SQLite-based vector database for fast case study similarity search
    Uses sentence-transformers for embeddings
    """

    def __init__(self, db_path: str = None):
        """
        Initialize vector database

        Args:
            db_path: Path to SQLite database file (defaults to backend/case_studies_vector.db)
        """
        # Use default path if none provided
        if db_path is None:
            # Use absolute path based on this file's location
            current_dir = Path(__file__).parent.parent
            db_path = str(current_dir / "case_studies_vector.db")

        self.db_path = db_path

        # Ensure directory exists
        db_path_obj = Path(self.db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Vector DB path: {self.db_path}")
        self.embedding_model = None
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension

        # Initialize embedding model
        import os
        os.environ["HF_HUB_DISABLE_SSL_VERIFY"] = "1"
        path_= r"C:\Users\ramesh.p\Downloads\zucisystems-ZSCHN01VM0001-CA.crt"
        os.environ["REQUESTS_CA_BUNDLE"] = path_
        os.environ["SSL_CERT_FILE"] = path_
        if EMBEDDINGS_AVAILABLE:
            try:
                logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', trust_remote_code=True,
    use_auth_token=False)
                logger.info("✓ Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.embedding_model = None

        # Create database and table
        self._init_database()

    def _init_database(self):
        """Create SQLite database and table with vector support"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create case studies table with vector stored as BLOB (numpy array bytes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS case_studies (
                    file_id TEXT PRIMARY KEY,
                    file_url TEXT,
                    title TEXT,
                    summary TEXT,
                    category TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index on file_id for fast lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_id ON case_studies(file_id)
            """)

            conn.commit()
            conn.close()

            logger.info(f"✓ Vector database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")

    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding vector for text

        Args:
            text: Text to embed

        Returns:
            Numpy array of embeddings or None if model not available
        """
        if not self.embedding_model:
            return None

        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def store_case_study(
        self,
        file_id: str,
        file_url: str,
        title: str,
        summary: str,
        category: str = ""
    ) -> bool:
        """
        Store case study with embedding

        Args:
            file_id: Unique file identifier
            file_url: URL to the file
            title: Case study title
            summary: Case study summary (3-5 lines)
            category: Category/tag

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding from title + summary
            combined_text = f"{title}. {summary}"
            embedding = self.generate_embedding(combined_text)

            if embedding is None:
                logger.warning(f"Skipping case study {file_id} - embeddings not available")
                return False

            # Convert numpy array to bytes for storage
            embedding_bytes = embedding.tobytes()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert or replace case study
            cursor.execute("""
                INSERT OR REPLACE INTO case_studies
                (file_id, file_url, title, summary, category, embedding, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (file_id, file_url, title, summary, category, embedding_bytes))

            conn.commit()
            conn.close()

            logger.info(f"✓ Stored case study: {title} (ID: {file_id})")
            return True

        except Exception as e:
            logger.error(f"Error storing case study {file_id}: {e}")
            return False

    def search_similar(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Search for similar case studies using vector similarity

        Args:
            query: Search query text
            top_k: Number of top results to return
            min_similarity: Minimum cosine similarity threshold (0-1)

        Returns:
            List of case study dictionaries with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)

            if query_embedding is None:
                logger.warning("Cannot search - embeddings not available")
                return []

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch all case studies
            cursor.execute("""
                SELECT file_id, file_url, title, summary, category, embedding
                FROM case_studies
            """)

            results = []
            for row in cursor.fetchall():
                file_id, file_url, title, summary, category, embedding_bytes = row

                # Convert bytes back to numpy array
                stored_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)

                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, stored_embedding)

                if similarity >= min_similarity:
                    results.append({
                        'file_id': file_id,
                        'file_url': file_url,
                        'title': title,
                        'summary': summary,
                        'category': category,
                        'similarity': float(similarity)
                    })

            conn.close()

            # Sort by similarity (highest first) and return top_k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            top_results = results[:top_k]

            logger.info(f"Vector search for '{query[:50]}...' found {len(top_results)} matches")
            for r in top_results:
                logger.info(f"  - {r['title']}: {r['similarity']:.2f} similarity")

            return top_results

        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors

        Returns:
            Similarity score between 0 and 1
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_all_case_studies(self) -> List[Dict[str, Any]]:
        """Get all stored case studies"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT file_id, file_url, title, summary, category
                FROM case_studies
                ORDER BY updated_at DESC
            """)

            results = []
            for row in cursor.fetchall():
                file_id, file_url, title, summary, category = row
                results.append({
                    'file_id': file_id,
                    'file_url': file_url,
                    'title': title,
                    'summary': summary,
                    'category': category
                })

            conn.close()
            return results

        except Exception as e:
            logger.error(f"Error fetching all case studies: {e}")
            return []

    def get_all_file_ids(self) -> List[str]:
        """Get all file_ids stored in vector database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT file_id FROM case_studies")
            file_ids = [row[0] for row in cursor.fetchall()]

            conn.close()
            return file_ids

        except Exception as e:
            logger.error(f"Error fetching file_ids from vector DB: {e}")
            return []

    def delete_case_study(self, file_id: str) -> bool:
        """Delete a case study from vector database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM case_studies WHERE file_id = ?", (file_id,))

            conn.commit()
            conn.close()

            logger.info(f"✓ Deleted case study: {file_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting case study {file_id}: {e}")
            return False


class CaseStudyManager:
    """
    Manages case study selection and integration across Campaign Builder,
    GTM Generator, Thread Intelligence, and Personalization Assistant

    Uses LLM-based intelligent matching to analyze document summaries
    and find the most relevant case studies for any context
    """

    def __init__(self, db, llm_function=None):
        """
        Initialize Case Study Manager with Vector Database

        Args:
            db: MongoDB database connection
            llm_function: LLM function for intelligent matching (optional, fallback)
        """
        self.db = db
        self.llm_function = llm_function

        # Initialize vector database for fast semantic search
        try:
            self.vector_db = VectorDatabase()
            logger.info("✓ CaseStudyManager initialized with Vector Database")
        except Exception as e:
            logger.error(f"Failed to initialize Vector Database: {e}")
            self.vector_db = None

        logger.info(f"CaseStudyManager ready - Vector DB: {self.vector_db is not None}, LLM fallback: {llm_function is not None}")

    def store_in_vector_db(
        self,
        file_id: str,
        file_url: str,
        title: str,
        summary: str,
        category: str = ""
    ) -> bool:
        """
        Store a case study in the vector database for fast similarity search

        Args:
            file_id: Unique document ID
            file_url: URL to the PDF/document
            title: Case study title
            summary: Case study summary (3-5 lines recommended)
            category: Category/tag

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.vector_db:
            logger.debug("Vector DB not available, skipping storage")
            return False

        if not self.vector_db.embedding_model:
            logger.debug("Embedding model not available, skipping storage")
            return False

        try:
            success = self.vector_db.store_case_study(
                file_id=file_id,
                file_url=file_url,
                title=title,
                summary=summary,
                category=category
            )

            if success:
                logger.info(f"✓ Stored in vector DB: {title}")

            return success

        except Exception as e:
            logger.debug(f"Error storing in vector DB: {e}")
            return False

    async def sync_missing_documents(self) -> int:
        """
        Sync documents that exist in MongoDB but not in vector database
        This is useful for backfilling existing documents that were created before vector DB

        Reads document content and generates summaries if needed

        Returns:
            Number of documents successfully synced
        """
        if not self.vector_db:
            logger.warning("Vector DB not available, cannot sync")
            return 0

        if not self.vector_db.embedding_model:
            logger.warning("Embedding model not available, skipping sync")
            logger.info("Install sentence-transformers with: pip install sentence-transformers")
            return 0

        try:
            logger.info("🔍 Checking for documents missing from vector DB...")

            # Get all file_ids from vector database
            vector_db_ids = set(self.vector_db.get_all_file_ids())
            logger.info(f"Vector DB contains {len(vector_db_ids)} documents")

            # Get ALL documents from MongoDB (not just those with title/summary)
            all_docs = await self.db.document_files.find({}).to_list(None)

            logger.info(f"MongoDB contains {len(all_docs)} total documents")

            # Find documents that are in MongoDB but not in vector DB
            synced_count = 0
            skipped_count = 0
            missing_count = 0

            for doc in all_docs:
                try:
                    file_id = doc.get('id')
                    print('file_id',file_id)

                    # Skip if no file_id
                    if not file_id:
                        skipped_count += 1
                        continue

                    # Check if this document is already in vector DB
                    if file_id in vector_db_ids:
                        continue  # Already synced

                    # This document is missing from vector DB
                    missing_count += 1

                    # Use filename instead of title (document_files use filename, not title)
                    filename = doc.get('filename', 'Untitled')
                    title = doc.get('title', filename)  # Fallback to filename if no title

                    file_url = doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else ''
                    category = doc.get('category', '')
                    doc_type = doc.get('doc_type', '')

                    # Get or generate summary
                    summary = doc.get('summary', '')

                    # If no summary exists, generate one from filename and metadata
                    if not summary or len(summary.strip()) < 10:
                        # Create a basic summary from available data
                        summary_parts = []
                        if category:
                            summary_parts.append(f"{category} industry")
                        if doc_type:
                            summary_parts.append(doc_type.lower())
                        summary_parts.append(f"document: {filename}")

                        # Try to extract text from document content if it's a text-based format
                        file_content = doc.get('file_content', '')
                        mime_type = doc.get('mime_type', '')

                        if file_content and 'text' in mime_type.lower():
                            try:
                                import base64
                                decoded = base64.b64decode(file_content).decode('utf-8', errors='ignore')
                                # Take first 200 characters as summary
                                if len(decoded.strip()) > 20:
                                    summary_parts.append(decoded[:200].strip())
                            except:
                                pass

                        summary = '. '.join(summary_parts) if summary_parts else f"{category} {doc_type} - {filename}"

                        logger.info(f"Generated summary for '{filename}': {summary[:100]}...")

                    # Validate we have minimum data
                    if not summary:
                        logger.debug(f"Skipping '{filename}' (ID: {file_id}) - cannot generate summary")
                        skipped_count += 1
                        continue

                    # Store in vector DB
                    logger.info(f"📝 Creating embedding for: {filename}")
                    if self.store_in_vector_db(file_id, file_url, filename, summary, category):
                        synced_count += 1
                        logger.info(f"✓ Synced to vector DB: {filename}")

                        # Update MongoDB with generated summary if it was created
                        if not doc.get('summary'):
                            try:
                                await self.db.document_files.update_one(
                                    {'id': file_id},
                                    {'$set': {'summary': summary}}
                                )
                                logger.info(f"  ✓ Updated MongoDB with generated summary")
                            except Exception as update_error:
                                logger.debug(f"Could not update summary in MongoDB: {update_error}")

                except Exception as doc_error:
                    logger.warning(f"Error processing document: {doc_error}")
                    continue

            logger.info(f"✅ Sync complete: {synced_count} new documents added to vector DB")
            logger.info(f"   Total in MongoDB: {len(all_docs)}")
            logger.info(f"   Missing from vector DB: {missing_count}")
            logger.info(f"   Successfully synced: {synced_count}")
            logger.info(f"   Skipped (invalid data): {skipped_count}")

            return synced_count

        except Exception as e:
            logger.error(f"Error syncing missing documents: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return 0

    async def sync_from_mongodb(self, max_docs: int = 1000) -> int:
        """
        Sync all case studies from MongoDB to vector database
        Reads document content and generates summaries if needed

        Args:
            max_docs: Maximum number of documents to sync

        Returns:
            Number of documents successfully synced
        """
        if not self.vector_db:
            logger.warning("Vector DB not available, cannot sync")
            return 0

        if not self.vector_db.embedding_model:
            logger.warning("Embedding model not available, skipping sync")
            logger.info("Install sentence-transformers with: pip install sentence-transformers")
            return 0

        try:
            logger.info("Syncing case studies from MongoDB to Vector DB...")

            # Fetch all documents from MongoDB
            all_docs = await self.db.document_files.find(
                {},
                {"_id": 0}
            ).limit(max_docs).to_list(max_docs)
            print(all_docs)
            synced_count = 0
            skipped_count = 0
            error_count = 0

            for doc in all_docs:
                try:
                    file_id = doc.get('id')

                    # Skip if no file_id
                    if not file_id:
                        logger.debug(f"Skipping document without ID")
                        skipped_count += 1
                        continue

                    # Use filename instead of title (document_files use filename, not title)
                    filename = doc.get('filename', 'Untitled')
                    title = doc.get('title', filename)  # Fallback to filename if no title

                    file_url = doc.get('metadata', {}).get('source_url', '') if doc.get('metadata') else ''
                    category = doc.get('category', '')
                    doc_type = doc.get('doc_type', '')

                    # Get or generate summary
                    summary = doc.get('summary', '')

                    # If no summary exists, generate one from filename and metadata
                    if not summary or len(summary.strip()) < 10:
                        # Create a basic summary from available data
                        summary_parts = []
                        if category:
                            summary_parts.append(f"{category} industry")
                        if doc_type:
                            summary_parts.append(doc_type.lower())
                        summary_parts.append(f"document: {filename}")

                        # Try to extract text from document content if it's a text-based format
                        file_content = doc.get('file_content', '')
                        mime_type = doc.get('mime_type', '')

                        if file_content and 'text' in mime_type.lower():
                            try:
                                import base64
                                decoded = base64.b64decode(file_content).decode('utf-8', errors='ignore')
                                # Take first 200 characters as summary
                                if len(decoded.strip()) > 20:
                                    summary_parts.append(decoded[:200].strip())
                            except:
                                pass

                        summary = '. '.join(summary_parts) if summary_parts else f"{category} {doc_type} - {filename}"
                        logger.info(f"Generated summary for '{filename}': {summary[:100]}...")

                    # Validate we have minimum data
                    if not summary or len(summary.strip()) < 5:
                        logger.debug(f"Skipping '{filename}' (ID: {file_id}) - cannot generate summary")
                        skipped_count += 1
                        continue

                    # Store in vector DB
                    if self.store_in_vector_db(file_id, file_url, filename, summary, category):
                        synced_count += 1

                        # Update MongoDB with generated summary if it was created
                        if not doc.get('summary'):
                            try:
                                await self.db.document_files.update_one(
                                    {'id': file_id},
                                    {'$set': {'summary': summary}}
                                )
                                logger.info(f"  ✓ Updated MongoDB with generated summary for {filename}")
                            except Exception as update_error:
                                logger.debug(f"Could not update summary in MongoDB: {update_error}")

                except Exception as doc_error:
                    logger.warning(f"Error processing document: {doc_error}")
                    error_count += 1
                    continue

            logger.info(f"✓ Sync complete: {synced_count} synced, {skipped_count} skipped, {error_count} errors out of {len(all_docs)} total documents")
            return synced_count

        except Exception as e:
            logger.error(f"Error syncing to vector DB: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return 0

    async def _llm_score_case_study_relevance(
        self,
        case_study_summary: str,
        case_study_title: str,
        context: str
    ) -> float:
        """
        Use LLM to intelligently score how relevant a case study is to the given context

        Args:
            case_study_summary: The case study summary to evaluate
            case_study_title: Title of the case study
            context: The context to match against (campaign details, thread, etc.)

        Returns:
            Relevance score from 0-100
        """
        if not self.llm_function:
            logger.warning("LLM function not available, returning default score")
            return 50.0

        try:
            prompt = f"""You are an expert at matching case studies to customer contexts.

Evaluate how relevant this case study is to the given context.

=== CASE STUDY ===
Title: {case_study_title}
Summary: {case_study_summary}

=== CONTEXT ===
{context}

=== INSTRUCTIONS ===
Analyze the case study summary and determine how relevant it is to the context based on:
1. Industry/domain similarity
2. Problem/challenge alignment
3. Solution/technology overlap
4. Business value/outcomes match
5. Use case similarity

Output ONLY a relevance score from 0-100:
- 0-20: Not relevant at all
- 21-40: Slightly relevant
- 41-60: Moderately relevant
- 61-80: Highly relevant
- 81-100: Extremely relevant, perfect match

Output format: Just the number (e.g., "75")
Do not include any explanation, just the score.
"""

            response = await self.llm_function(prompt)
            # Extract the score
            score_str = response.strip()
            # Remove any non-numeric characters except decimal point
            import re
            score_match = re.search(r'\d+', score_str)
            if score_match:
                score = float(score_match.group())
                score = max(0, min(100, score))  # Clamp between 0-100
                return score
            else:
                logger.warning(f"Could not parse score from LLM response: {response}")
                return 50.0

        except Exception as e:
            logger.error(f"Error in LLM scoring: {e}")
            return 50.0

    async def auto_pick_case_studies(
        self,
        service: str,
        stage: str = 'MOFU',
        icp: List[str] = None,
        custom_inputs: List[Dict[str, str]] = None,
        max_results: int = 3
    ) -> List[str]:
        """
        Automatically pick relevant case studies using FAST vector similarity search

        Args:
            service: Primary service offering
            stage: Funnel stage (TOFU/MOFU/BOFU)
            icp: Target ideal customer profile list
            custom_inputs: Additional context inputs
            max_results: Maximum number of case studies to return

        Returns:
            List of case study document IDs
        """
        try:
            # Build search query from context
            query_parts = [service, stage]
            if icp:
                query_parts.extend(icp)
            if custom_inputs:
                for ci in custom_inputs:
                    if ci.get('value'):
                        query_parts.append(ci.get('value'))

            search_query = ' '.join(query_parts)

            logger.info(f"Vector search query: '{search_query}'")

            # Use FAST vector similarity search if available
            if self.vector_db and self.vector_db.embedding_model:
                similar_cases = self.vector_db.search_similar(
                    query=search_query,
                    top_k=max_results,
                    min_similarity=0.3
                )

                if similar_cases:
                    # Map vector DB file_ids to MongoDB document IDs
                    file_ids = [cs['file_id'] for cs in similar_cases]
                    logger.info(f"✓ Vector search found {len(file_ids)} case studies (instant!)")
                    return file_ids
                else:
                    logger.warning("Vector search found no matches, trying fallback...")

            # Fallback: Try MongoDB lookup if vector DB failed
            logger.info("Using MongoDB fallback for case study selection...")
            all_docs = await self.db.document_files.find(
                {},
                {"_id": 0}
            ).limit(max_results).to_list(max_results)

            if all_docs:
                selected_ids = [doc['id'] for doc in all_docs]
                logger.info(f"Fallback selected {len(selected_ids)} case studies")
                return selected_ids

            logger.warning("No case studies found")
            return []

        except Exception as e:
            logger.error(f"Error auto-picking case studies: {str(e)}")
            return []
    
    def _calculate_relevance_score(
        self,
        doc: Dict[str, Any],
        service: str,
        stage: str,
        icp: List[str] = None,
        custom_inputs: List[Dict[str, str]] = None
    ) -> float:
        """
        Calculate relevance score for a case study based on multiple factors
        """
        score = 0.0
        
        # 1. Category/Service match (highest weight = 40 points)
        doc_category = doc.get('category', '').lower()
        service_lower = service.lower()
        
        # Direct match
        if service_lower in doc_category or doc_category in service_lower:
            score += 40
        else:
            # Check mapping
            for category, services in self.CATEGORY_SERVICE_MAP.items():
                if any(s.lower() in service_lower for s in services):
                    if category.lower() in doc_category:
                        score += 30
                        break
        
        # 2. Document type based on stage (20 points)
        stage_config = self.STAGE_WEIGHTS.get(stage, self.STAGE_WEIGHTS['MOFU'])
        doc_type = doc.get('doc_type', '')
        if doc_type in stage_config['preferred_types']:
            score += 20
        
        # 3. Keywords in summary/description match (20 points)
        summary = doc.get('summary', '').lower()
        description = doc.get('metadata', {}).get('description', '').lower()
        combined_text = f"{summary} {description}"
        
        stage_keywords = stage_config.get('awareness_keywords', []) + \
                        stage_config.get('evaluation_keywords', []) + \
                        stage_config.get('decision_keywords', [])
        
        keyword_matches = sum(1 for keyword in stage_keywords if keyword in combined_text)
        score += min(keyword_matches * 4, 20)  # Max 20 points
        
        # 4. ICP/Industry match (15 points)
        if icp:
            for icp_item in icp:
                if icp_item.lower() in combined_text:
                    score += 5
        
        # 5. Custom input relevance (5 points)
        if custom_inputs:
            for ci in custom_inputs:
                custom_value = ci.get('value', '').lower()
                if custom_value and any(word in combined_text for word in custom_value.split()[:5]):
                    score += 5
                    break
        
        # 6. Recency bonus - prefer newer case studies (up to 5 points)
        try:
            created_at = doc.get('created_at')
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            elif isinstance(created_at, datetime):
                pass
            else:
                created_at = None
            
            if created_at:
                days_old = (datetime.now() - created_at.replace(tzinfo=None)).days
                if days_old < 90:  # Within 3 months
                    score += 5
                elif days_old < 180:  # Within 6 months
                    score += 3
                elif days_old < 365:  # Within 1 year
                    score += 1
        except Exception:
            pass
        
        return score
    
    async def get_case_study_details(self, case_study_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch full details for selected case studies
        """
        try:
            studies = await self.db.document_files.find(
                {"id": {"$in": case_study_ids}},
                {"_id": 0}
            ).to_list(len(case_study_ids))
            
            return studies
        except Exception as e:
            logger.error(f"Error fetching case study details: {str(e)}")
            return []
    
    def format_case_study_reference(
        self,
        case_study: Dict[str, Any],
        context: str = 'inline'
    ) -> str:
        """
        Format case study reference for inclusion in content

        Args:
            case_study: Case study document
            context: 'inline', 'ps', or 'standalone'

        Returns:
            Formatted reference string
        """
        # Use filename as fallback for title (document_files use filename, not title)
        filename = case_study.get('filename', 'Untitled Case Study')
        title = case_study.get('title', filename)
        summary = case_study.get('summary', '')
        source_url = case_study.get('metadata', {}).get('source_url', '')
        
        # Extract key metric if available
        key_metric = self._extract_key_metric(summary)
        
        if context == 'inline':
            if key_metric and source_url:
                return f"We recently helped a similar organization achieve {key_metric}. [Full story here]({source_url})"
            elif source_url:
                return f"You might find this case study relevant: [{title}]({source_url})"
            else:
                return f"Similar success story: {title}"
        
        elif context == 'ps':
            if source_url:
                return f"P.S. You might find this relevant: [{title}]({source_url}) - showing how we solved a similar challenge."
            else:
                return f"P.S. Related case study: {title}"
        
        elif context == 'standalone':
            formatted = f"**{title}**\n"
            if summary:
                # Take first 2 sentences of summary
                summary_lines = summary.split('\n')
                formatted += f"{summary_lines[0][:200]}...\n"
            if source_url:
                formatted += f"[Read full case study]({source_url})"
            return formatted
        
        return title
    
    def _extract_key_metric(self, text: str) -> Optional[str]:
        """
        Extract a key metric from case study text (e.g., "40% faster", "3x ROI")
        """
        import re
        
        # Common metric patterns
        patterns = [
            r'\d+%\s+(?:faster|quicker|improvement|increase|reduction|decrease|growth)',
            r'\d+x\s+(?:faster|ROI|improvement|increase|growth)',
            r'reduced?\s+(?:by\s+)?\d+%',
            r'increased?\s+(?:by\s+)?\d+%',
            r'improved?\s+(?:by\s+)?\d+%',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    async def get_recommended_case_studies_for_thread(
        self,
        thread_context: str,
        objection_type: Optional[str] = None,
        service: str = None,
        max_results: int = 2
    ) -> List[str]:
        """
        Get case studies relevant to a specific thread using FAST vector similarity

        Args:
            thread_context: The email thread or conversation context
            objection_type: Type of objection if any (price, timing, capability, etc.)
            service: Service/product being discussed
            max_results: Maximum number of case studies to return

        Returns:
            List of case study document IDs ranked by relevance
        """
        try:
            # Build search query from thread context
            query_parts = [thread_context[:300]]  # First 300 chars of thread
            if service:
                query_parts.append(service)
            if objection_type:
                query_parts.append(objection_type)

            search_query = ' '.join(query_parts)

            logger.info(f"Vector search for thread: '{search_query[:100]}...'")

            # Use FAST vector similarity search if available
            if self.vector_db and self.vector_db.embedding_model:
                similar_cases = self.vector_db.search_similar(
                    query=search_query,
                    top_k=max_results,
                    min_similarity=0.3
                )

                if similar_cases:
                    file_ids = [cs['file_id'] for cs in similar_cases]
                    logger.info(f"✓ Vector search for thread found {len(file_ids)} case studies (instant!)")
                    return file_ids
                else:
                    logger.warning("Vector search found no matches for thread, using fallback...")

            # Fallback: Get any available case studies
            logger.info("Using MongoDB fallback for thread case study selection...")
            all_docs = await self.db.document_files.find(
                {},
                {"_id": 0}
            ).limit(max_results).to_list(max_results)

            if all_docs:
                selected_ids = [doc['id'] for doc in all_docs]
                logger.info(f"Fallback selected {len(selected_ids)} case studies")
                return selected_ids

            logger.warning("No case studies found for thread")
            return []

        except Exception as e:
            logger.error(f"Error in thread-based case study matching: {e}")
            return []

    async def get_latest_zuci_news(self, max_results: int = 2) -> List[Dict[str, Any]]:
        """
        Get the latest Zuci news items sorted by published_date

        Args:
            max_results: Maximum number of news items to return (default: 2)

        Returns:
            List of zuci_news dictionaries with id, title, description, published_date
        """
        try:
            logger.info(f"Fetching latest {max_results} Zuci news items...")

            # Fetch latest news from zuci_news collection, sorted by published_date descending
            news_items = await self.db.zuci_news.find(
                {},
                {"_id": 0}
            ).sort("published_date", -1).limit(max_results).to_list(max_results)

            if news_items:
                logger.info(f"✓ Found {len(news_items)} Zuci news items")
                return news_items
            else:
                logger.warning("No Zuci news items found in database")
                return []

        except Exception as e:
            logger.error(f"Error fetching Zuci news: {e}")
            return []
