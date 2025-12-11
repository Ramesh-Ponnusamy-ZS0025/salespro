"""
Document Management Module
Contains: File upload, case studies, cloud storage, Zuci case study scraper
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Set
import uuid
from datetime import datetime, timezone
import logging
import base64
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import asyncio
import random
import sys
from typing import Tuple

logger = logging.getLogger(__name__)
from login import User, get_current_user

# Try to import playwright - optional dependency
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available. Install with: pip install playwright && playwright install")

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["document_management"])

# Database reference - will be set from server.py
db = None

# LLM helper reference - will be set from server.py
generate_llm_response = None

# Case study manager reference - will be set from server.py
case_study_manager = None

def set_db(database):
    global db
    db = database

def set_llm_helper(llm_func):
    global generate_llm_response
    generate_llm_response = llm_func

def set_case_study_manager(manager):
    global case_study_manager
    case_study_manager = manager

# ============== MODELS ==============

class CaseStudyExtractRequest(BaseModel):
    company_name: str
    url: str

class CaseStudySummary(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    case_title: str
    summary: List[str]
    category: str
    source_url: str
    pdf_url: Optional[str] = None
    impact_summary: str
    full_text: str
    key_metrics: List[str] = []
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CaseStudyListResponse(BaseModel):
    case_studies: List[Dict[str, Any]]
    grouped_by_category: Dict[str, List[Dict[str, Any]]]

class DocumentFile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    category: str  # Healthcare, Finance, etc.
    doc_type: str  # Case Study, Architecture, Use Case, Design, Figma, Workflow
    file_content: str  # base64 encoded
    file_size: int
    mime_type: str
    summary: Optional[str] = None
    uploaded_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentFileUpload(BaseModel):
    filename: str
    category: str
    doc_type: str
    file_content: str  # base64
    mime_type: str
    file_size: int

class CloudStorageConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    storage_type: str  # 'onedrive' or 'sharepoint'
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    drive_id: Optional[str] = None
    drive_name: Optional[str] = None
    folder_path: str = "/"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CloudStorageConfigCreate(BaseModel):
    storage_type: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[str] = None
    drive_id: Optional[str] = None
    drive_name: Optional[str] = None
    folder_path: str = "/"

class CloudStorageConfigUpdate(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[str] = None
    drive_id: Optional[str] = None
    folder_path: Optional[str] = None
    is_active: Optional[bool] = None

class ZuciCaseStudy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    type: str  # Case Study / Success Story / Use Case
    source_url: str
    pdf_url: Optional[str] = None
    filename: Optional[str] = None
    file_content: Optional[str] = None  # base64 encoded PDF
    file_size: Optional[int] = None
    mime_type: str = "application/pdf"
    tags: List[str] = []
    uploaded_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============== DOCUMENT MANAGEMENT ROUTES ==============

@router.post("/document-files/upload")
async def upload_document_file(doc_data: DocumentFileUpload, current_user: User = Depends(get_current_user)):
    """Upload a document file to the Document Management system"""
    doc_file = DocumentFile(
        **doc_data.model_dump(),
        uploaded_by=current_user.id
    )

    doc = doc_file.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()

    # Store in MongoDB
    await db.document_files.insert_one(doc)

    # Store in Vector Database for fast similarity search
    if case_study_manager and doc_file.summary:
        try:
            case_study_manager.store_in_vector_db(
                file_id=doc_file.id,
                file_url=doc_file.metadata.get('source_url', '') if doc_file.metadata else '',
                title=doc_file.filename,
                summary=doc_file.summary,
                category=doc_file.category
            )
            logger.info(f"✓ Document stored in vector DB: {doc_file.filename}")
        except Exception as e:
            logger.error(f"Failed to store in vector DB: {e}")
            # Don't fail the upload if vector DB fails

    return {
        "id": doc_file.id,
        "message": "Document uploaded successfully",
        "filename": doc_file.filename
    }

@router.get("/document-files/for-campaign")
async def get_documents_for_campaign():
    """Get document files formatted for campaign case study picker"""
    documents = await db.document_files.find(
        {},
        {"_id": 0, "id": 1, "filename": 1, "category": 1, "doc_type": 1, "metadata": 1, "summary": 1}
    ).to_list(1000)

    result = []
    for doc in documents:
        metadata = doc.get('metadata', {})
        result.append({
            'id': doc['id'],
            'title': doc['filename'],
            'category': doc['category'],
            'doc_type': doc['doc_type'],
            'source_url': metadata.get('source_url', ''),
            'summary': doc.get('summary', '')
        })

    return {"documents": result}

@router.get("/document-files")
async def get_document_files(current_user: User = Depends(get_current_user)):
    """Get all document files for the current user, grouped by category and type"""
    documents = await db.document_files.find(
        {"uploaded_by": current_user.id},
        {"_id": 0, "file_content": 0}  # Exclude file_content for list view
    ).to_list(1000)

    for doc in documents:
        if isinstance(doc.get('created_at'), str):
            doc['created_at'] = datetime.fromisoformat(doc['created_at'])
        if isinstance(doc.get('updated_at'), str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])

    # Group by category and type
    grouped = {}
    for doc in documents:
        category = doc['category']
        doc_type = doc['doc_type']

        if category not in grouped:
            grouped[category] = {}
        if doc_type not in grouped[category]:
            grouped[category][doc_type] = []

        grouped[category][doc_type].append(doc)

    return {
        "documents": documents,
        "grouped": grouped,
        "total": len(documents)
    }

@router.get("/document-files/{doc_id}")
async def get_document_file(doc_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific document file with full content"""
    doc = await db.document_files.find_one(
        {"id": doc_id, "uploaded_by": current_user.id},
        {"_id": 0}
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if isinstance(doc.get('created_at'), str):
        doc['created_at'] = datetime.fromisoformat(doc['created_at'])
    if isinstance(doc.get('updated_at'), str):
        doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])

    # Ensure file_content exists and is valid base64
    if 'file_content' in doc and doc['file_content']:
        try:
            base64.b64decode(doc['file_content'])
        except Exception as e:
            logger.error(f"Invalid base64 content for doc {doc_id}: {str(e)}")
            doc['file_content'] = None

    return doc

@router.put("/document-files/{doc_id}")
async def update_document_file(doc_id: str, update_data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """Update document metadata (category, type, filename)"""
    existing = await db.document_files.find_one(
        {"id": doc_id, "uploaded_by": current_user.id},
        {"_id": 0}
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    # Only allow updating certain fields
    allowed_fields = ['filename', 'category', 'doc_type']
    update_payload = {k: v for k, v in update_data.items() if k in allowed_fields}
    update_payload['updated_at'] = datetime.now(timezone.utc).isoformat()

    await db.document_files.update_one(
        {"id": doc_id},
        {"$set": update_payload}
    )

    return {"message": "Document updated successfully"}

@router.delete("/document-files/{doc_id}")
async def delete_document_file(doc_id: str, current_user: User = Depends(get_current_user)):
    """Delete a document file"""
    result = await db.document_files.delete_one(
        {"id": doc_id, "uploaded_by": current_user.id}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}

@router.get("/document-files/categories/list")
async def get_document_categories(current_user: User = Depends(get_current_user)):
    """Get list of all unique categories and types"""
    documents = await db.document_files.find(
        {"uploaded_by": current_user.id},
        {"_id": 0, "category": 1, "doc_type": 1}
    ).to_list(1000)

    categories = list(set(doc['category'] for doc in documents))
    doc_types = list(set(doc['doc_type'] for doc in documents))

    return {
        "categories": sorted(categories),
        "doc_types": sorted(doc_types)
    }

# ============== ZUCI CASE STUDIES SCRAPER ==============

async def crawl_zuci_with_playwright() -> List[Dict[str, Any]]:
    """Crawl Zuci using Playwright (bypasses Cloudflare/bot detection) - Gets ALL case studies"""
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("Playwright not installed. Run: pip install playwright && playwright install")

    base_url = "https://www.zucisystems.com/category/casestudy/"
    case_studies = []
    visited_urls = set()

    async with async_playwright() as p:
        # Launch browser with stealth settings
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/131.0.0.0 Safari/537.36'
            ),
            locale='en-US',
            timezone_id='America/New_York',
        )

        # Add extra headers to context
        await context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })

        page = await context.new_page()

        try:
            logger.info("🔄 Crawling ALL case studies from Zuci Systems...")

            case_study_links = set()
            page_num = 1
            max_pages = 15  # Safety limit to prevent infinite loops

            # Crawl all pagination pages to get ALL case study links
            while page_num <= max_pages:
                current_url = f"{base_url}page/{page_num}/" if page_num > 1 else base_url
                logger.info(f"📄 Scanning page {page_num}: {current_url}")

                try:
                    response = await page.goto(current_url, wait_until='domcontentloaded', timeout=30000)

                    if response and response.status == 404:
                        logger.info(f"✓ Reached end of pagination at page {page_num}")
                        break

                    if response and response.status == 403:
                        logger.error("❌ Got 403 - Cloudflare protection triggered")
                        break

                    # Wait for content to load
                    await asyncio.sleep(0.5)

                    # Extract all case study links from this page
                    links = await page.query_selector_all('a[href]')
                    page_links_found = 0

                    for link_element in links:
                        href = await link_element.get_attribute('href')
                        if not href:
                            continue

                        # Normalize URL
                        if href.startswith('/'):
                            href = f"https://www.zucisystems.com{href}"
                        elif not href.startswith('http'):
                            continue

                        # Check if it's a case study link
                        if 'zucisystems.com' in href and any(keyword in href.lower() for keyword in ['case', 'study', 'success', 'story']):
                            # Exclude pagination and category URLs
                            if '/page/' not in href and '/category/' not in href:
                                if href not in case_study_links:
                                    case_study_links.add(href)
                                    page_links_found += 1

                    logger.info(f"   ✓ Found {page_links_found} new case study links on page {page_num}")

                    # Check if there's a next page link
                    next_button = await page.query_selector('a.next, a[rel="next"], .pagination .next')
                    if not next_button and page_links_found == 0:
                        logger.info(f"✓ No more pages found after page {page_num}")
                        break

                    page_num += 1

                except Exception as e:
                    logger.warning(f"Error on page {page_num}: {str(e)}")
                    break

            logger.info(f"✅ Total case study links discovered: {len(case_study_links)}")

            # Now process ALL discovered case studies
            total_studies = len(case_study_links)
            logger.info(f"📊 Processing all {total_studies} case studies...")

            # Process case studies in batches for better performance
            for idx, link in enumerate(case_study_links, 1):
                if link in visited_urls:
                    continue

                visited_urls.add(link)

                try:
                    logger.info(f"📄 [{idx}/{total_studies}] Processing: {link[:70]}...")

                    # Minimal wait to avoid overwhelming the server
                    await asyncio.sleep(random.uniform(0.2, 0.4))

                    # Navigate to case study page
                    cs_response = await page.goto(link, wait_until='domcontentloaded', timeout=20000)

                    if cs_response and cs_response.status != 200:
                        logger.warning(f"⚠️  Failed to load {link}: {cs_response.status}")
                        continue

                    # Extract information
                    title = await page.title()
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    logger.info(f"   ✓ Loaded: {title[:60]}")

                    # Extract description
                    description = None
                    desc_meta = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
                    if desc_meta:
                        description = desc_meta.get('content', '').strip()
                    elif soup.find('p'):
                        first_p = soup.find('p')
                        description = first_p.get_text().strip()[:300] if first_p else None

                    # Extract category/type
                    page_text = soup.get_text().lower()
                    case_type = "Case Study"
                    if 'success story' in page_text:
                        case_type = "Success Story"
                    elif 'use case' in page_text:
                        case_type = "Use Case"

                    # More comprehensive category detection
                    category = "General"
                    category_keywords = {
                        'AI': ['artificial intelligence', 'machine learning', 'deep learning', 'ai'],
                        'Healthcare': ['healthcare', 'health', 'medical', 'hospital', 'patient'],
                        'Finance': ['finance', 'banking', 'fintech', 'payment', 'financial'],
                        'Retail': ['retail', 'e-commerce', 'ecommerce', 'shopping'],
                        'Manufacturing': ['manufacturing', 'factory', 'production', 'industrial'],
                        'Technology': ['technology', 'tech', 'software', 'digital'],
                        'Insurance': ['insurance', 'insurer', 'policy'],
                        'Education': ['education', 'learning', 'training', 'university'],
                        'Automotive': ['automotive', 'vehicle', 'car'],
                        'Logistics': ['logistics', 'supply chain', 'warehouse', 'shipping']
                    }

                    for cat, keywords in category_keywords.items():
                        if any(kw in page_text for kw in keywords):
                            category = cat
                            break

                    # Find PDF link
                    pdf_url = None
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag.get('href', '')
                        if href.endswith('.pdf') or 'download' in href.lower():
                            pdf_url = href if href.startswith('http') else urljoin(link, href)
                            break

                    # Download PDF if found (with retry logic)
                    file_content = None
                    file_size = 0
                    filename = None

                    if pdf_url:
                        filename = pdf_url.split('/')[-1].split('?')[0]
                        if not filename.endswith('.pdf'):
                            filename = f"{title[:30].replace(' ', '_')}.pdf"

                        logger.info(f"   📥 Downloading PDF: {filename[:40]}...")

                        try:
                            pdf_response = await context.request.get(pdf_url, timeout=20000)
                            if pdf_response.status == 200:
                                pdf_data = await pdf_response.body()
                                file_content = base64.b64encode(pdf_data).decode('utf-8')
                                file_size = len(pdf_data)
                                logger.info(f"   ✅ Downloaded: {filename} ({file_size // 1024}KB)")
                            else:
                                logger.warning(f"   ⚠️  PDF download failed: {pdf_response.status}")
                        except asyncio.TimeoutError:
                            logger.warning(f"   ⚠️  PDF download timeout")
                        except Exception as e:
                            logger.warning(f"   ⚠️  PDF download error: {str(e)[:50]}")

                    case_studies.append({
                        'title': title,
                        'description': description,
                        'category': category,
                        'type': case_type,
                        'source_url': link,
                        'pdf_url': pdf_url,
                        'filename': filename,
                        'file_content': file_content,
                        'file_size': file_size,
                        'tags': []
                    })

                    # Progress update every 10 items
                    if idx % 10 == 0:
                        logger.info(f"📊 Progress: {idx}/{total_studies} case studies processed ({len([cs for cs in case_studies if cs.get('file_content')])} with PDFs)")

                except Exception as e:
                    logger.error(f"Error processing {link}: {str(e)}")
                    continue

            logger.info(f"✅ Extraction complete! Processed {len(case_studies)} case studies")
            logger.info(f"   📄 With PDFs: {len([cs for cs in case_studies if cs.get('file_content')])}")
            logger.info(f"   📝 Text only: {len([cs for cs in case_studies if not cs.get('file_content')])}")

        except Exception as e:
            logger.error(f"Error with Playwright scraping: {str(e)}")
            raise e
        finally:
            await browser.close()

    return case_studies

async def download_pdf(session: aiohttp.ClientSession, url: str) -> tuple:
    """Download PDF file and return content + size"""
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 403:
                    logger.warning(f"Got 403 for PDF {url} on attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        logger.error(f"Failed to download PDF after {max_retries} attempts: 403 Forbidden")
                        return None, 0

                if response.status == 200:
                    content = await response.read()
                    return content, len(content)
                else:
                    logger.warning(f"Failed to download PDF {url}: {response.status}")
                    return None, 0

        except aiohttp.ClientError as e:
            logger.error(f"Error downloading PDF from {url} on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
                continue
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF from {url}: {str(e)}")
            return None, 0

    return None, 0

async def extract_case_study_info(session: aiohttp.ClientSession, url: str, visited: Set[str]) -> Optional[Dict[str, Any]]:
    """Extract case study information from a page"""
    if url in visited:
        return None

    visited.add(url)

    # Retry logic for individual case study pages
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 403:
                    logger.warning(f"Got 403 for {url} on attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        logger.error(f"Failed to fetch {url} after {max_retries} attempts: 403 Forbidden")
                        return None

                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status}")
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                break  # Success, exit retry loop

        except aiohttp.ClientError as e:
            logger.error(f"Request error for {url} on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
                continue
            else:
                return None

    # Extract case study information
    try:
        # Extract title
        title = None
        title_selectors = [
            soup.find('h1'),
            soup.find('h2'),
            soup.find('title')
        ]
        for selector in title_selectors:
            if selector:
                title = selector.get_text().strip()
                break

        if not title:
            title = "Untitled Case Study"

        # Extract description
        description = None
        desc_selectors = [
            soup.find('meta', {'name': 'description'}),
            soup.find('meta', {'property': 'og:description'}),
            soup.find('p')
        ]
        for selector in desc_selectors:
            if selector:
                if selector.name == 'meta':
                    description = selector.get('content', '').strip()
                else:
                    description = selector.get_text().strip()[:200]
                if description:
                    break

        # Determine type based on content
        page_text = soup.get_text().lower()
        case_type = "Case Study"
        if 'success story' in page_text or 'customer story' in page_text:
            case_type = "Success Story"
        elif 'use case' in page_text:
            case_type = "Use Case"
        elif 'transformation' in page_text:
            case_type = "Transformation Story"
        elif 'solution' in page_text:
            case_type = "Industry Solution"

        # Extract category/industry
        category = None
        category_keywords = ['AI', 'Healthcare', 'Finance', 'Retail', 'Manufacturing', 'Technology', 'Education', 'E-commerce']
        for keyword in category_keywords:
            if keyword.lower() in page_text:
                category = keyword
                break

        if not category:
            category = "General"

        # Extract tags
        tags = []
        tag_elements = soup.find_all('a', {'class': ['tag', 'category', 'label']})
        for tag in tag_elements:
            tag_text = tag.get_text().strip()
            if tag_text and len(tag_text) < 30:
                tags.append(tag_text)

        # Find PDF download link
        pdf_url = None
        pdf_links = soup.find_all('a', href=True)
        for link in pdf_links:
            href = link.get('href', '')
            if href.endswith('.pdf') or 'download' in href.lower() or 'pdf' in href.lower():
                pdf_url = href
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin(url, pdf_url)
                break

        # Extract filename from PDF URL
        filename = None
        if pdf_url:
            filename = pdf_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]

        return {
            'title': title,
            'description': description,
            'category': category,
            'type': case_type,
            'source_url': url,
            'pdf_url': pdf_url,
            'filename': filename,
            'tags': tags[:5]
        }

    except Exception as e:
        logger.error(f"Error extracting case study from {url}: {str(e)}")
        return None

async def crawl_zuci_case_studies() -> List[Dict[str, Any]]:
    """Crawl Zuci Systems case study page and extract all case studies"""
    base_url = "https://www.zucisystems.com/category/casestudy/"
    case_studies = []
    visited = set()

    # Enhanced headers to bypass bot detection - mimicking real Chrome browser
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Cache-Control": "max-age=0",
        "Pragma": "no-cache",
    }

    # Create connector without SSL verification (some corporate sites have cert issues)
    connector = aiohttp.TCPConnector(ssl=False)

    # Create cookie jar to maintain session
    cookie_jar = aiohttp.CookieJar()

    async with aiohttp.ClientSession(headers=headers, connector=connector, cookie_jar=cookie_jar) as session:
        try:
            # First, visit the homepage to establish session and cookies
            logger.info("Visiting homepage to establish session...")
            try:
                async with session.get("https://www.zucisystems.com", timeout=aiohttp.ClientTimeout(total=20)) as home_response:
                    if home_response.status == 200:
                        logger.info("Homepage visited successfully, session established")
                    await asyncio.sleep(random.uniform(2, 4))  # Wait before going to case studies page
            except Exception as e:
                logger.warning(f"Could not visit homepage: {str(e)}")

            # Add retry logic for the main page
            max_retries = 3
            retry_delay = 2

            for attempt in range(max_retries):
                try:
                    await asyncio.sleep(random.uniform(1, 3))  # Random delay before request

                    async with session.get(base_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 403:
                            logger.warning(f"Got 403 on attempt {attempt + 1}/{max_retries}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay * (attempt + 1))
                                continue
                            else:
                                logger.error(f"Failed to fetch main page after {max_retries} attempts: 403 Forbidden")
                                return []

                        if response.status != 200:
                            logger.error(f"Failed to fetch main page: {response.status}")
                            return []

                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        break  # Success, exit retry loop

                except aiohttp.ClientError as e:
                    logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        raise

            # Find all case study links
            case_study_links = []

            for link in soup.find_all('a', href=True):
                href = link.get('href')

                if any(keyword in href.lower() for keyword in ['case', 'study', 'success', 'story', 'customer']):
                    if href.startswith('/'):
                        href = f"https://www.zucisystems.com{href}"
                    elif not href.startswith('http'):
                        continue

                    if 'zucisystems.com' in href and href not in visited:
                        case_study_links.append(href)

            # Also look for "Read More" links
            read_more_links = soup.find_all('a', text=['Read More', 'Learn More', 'View Details', 'Read Full Story'])
            for link in read_more_links:
                href = link.get('href')
                if href:
                    if href.startswith('/'):
                        href = f"https://www.zucisystems.com{href}"
                    if 'zucisystems.com' in href and href not in visited:
                        case_study_links.append(href)

            case_study_links = list(set(case_study_links))
            logger.info(f"Found {len(case_study_links)} potential case study links")

            # Extract info from each case study with delays between requests
            for idx, link in enumerate(case_study_links[:20]):
                # Add random delay between requests to avoid rate limiting
                if idx > 0:
                    delay = random.uniform(2, 5)
                    logger.info(f"Waiting {delay:.1f}s before next request...")
                    await asyncio.sleep(delay)

                case_study_info = await extract_case_study_info(session, link, visited)
                if case_study_info:
                    if case_study_info.get('pdf_url') or case_study_info.get('description'):
                        if case_study_info.get('pdf_url'):
                            # Add delay before PDF download
                            await asyncio.sleep(random.uniform(1, 3))
                            pdf_content, pdf_size = await download_pdf(session, case_study_info['pdf_url'])
                            if pdf_content:
                                case_study_info['file_content'] = base64.b64encode(pdf_content).decode('utf-8')
                                case_study_info['file_size'] = pdf_size

                        case_studies.append(case_study_info)
                        logger.info(f"Extracted: {case_study_info['title']}")

        except Exception as e:
            logger.error(f"Error crawling case studies: {str(e)}")
            raise e

    return case_studies

async def generate_case_study_summary(study: Dict[str, Any]) -> str:
    """Generate a 5-6 line summary for a case study using LLM"""
    try:
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

        summary = await generate_llm_response(summary_prompt)
        lines = [line.strip() for line in summary.split('\n') if line.strip()]
        summary = '\n'.join(lines[:6])
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return f"{study.get('title', 'Case Study')}\n{study.get('category', 'General')} - {study.get('type', 'Case Study')}\n{study.get('description', '')[:200]}"

@router.post("/document-files/scrape-zuci-case-studies")
async def scrape_zuci_case_studies(current_user: User = Depends(get_current_user)):
    """Scrape Zuci Systems website for case studies and save them to document files."""
    import subprocess
    import json
    from pathlib import Path

    try:
        logger.info("Starting Zuci case studies scraping in worker process...")

        # Run scraper as separate subprocess to avoid uvicorn event loop issues
        worker_script = Path(__file__).parent / "scraper_worker.py"

        if not worker_script.exists():
            raise HTTPException(
                status_code=500,
                detail="Scraper worker script not found. Please contact administrator."
            )

        # Run the worker script as a subprocess
        logger.info(f"Launching scraper worker for user: {current_user.id}")

        process = subprocess.Popen(
            [sys.executable, str(worker_script), current_user.id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(worker_script.parent)
        )

        # Wait for process to complete (with timeout)
        try:
            stdout, stderr = process.communicate(timeout=600)  # 10 minutes timeout
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            raise HTTPException(
                status_code=500,
                detail="Scraping timed out after 10 minutes. Please try again or contact administrator."
            )

        # Log stderr if any
        if stderr:
            logger.warning(f"Scraper stderr: {stderr}")

        # Parse the JSON result from stdout
        try:
            # Find the JSON output (last line should be the result)
            lines = stdout.strip().split('\n')
            result_json = None
            for line in reversed(lines):
                try:
                    result_json = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue

            if not result_json:
                raise ValueError("No valid JSON output from scraper")

            logger.info(f"Scraper completed: {result_json.get('message', 'No message')}")

            return result_json

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse scraper output: {str(e)}")
            logger.error(f"Stdout: {stdout}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse scraper results: {str(e)}"
            )

    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape case studies: {str(e)}")

@router.post("/document-files/sync-vector-db")
async def sync_vector_database(current_user: User = Depends(get_current_user)):
    """Sync documents from MongoDB to Vector Database for semantic search"""
    try:
        if not case_study_manager:
            raise HTTPException(
                status_code=500,
                detail="Case Study Manager not initialized"
            )

        if not case_study_manager.vector_db:
            raise HTTPException(
                status_code=500,
                detail="Vector Database not available. Please install sentence-transformers: pip install sentence-transformers"
            )

        if not case_study_manager.vector_db.embedding_model:
            raise HTTPException(
                status_code=500,
                detail="Embedding model not available. Please install sentence-transformers: pip install sentence-transformers"
            )

        logger.info(f"User {current_user.id} initiated vector DB sync")

        # Sync missing documents
        synced_count = await case_study_manager.sync_missing_documents()

        # Get total count in vector DB
        total_count = len(case_study_manager.vector_db.get_all_file_ids())

        return {
            "success": True,
            "message": f"Successfully synced {synced_count} documents to vector database",
            "synced_count": synced_count,
            "total_vector_db_count": total_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing vector DB: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to sync vector database: {str(e)}")
