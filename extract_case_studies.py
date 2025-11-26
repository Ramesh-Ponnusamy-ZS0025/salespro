
# ============== ZUCI CASE STUDIES SCRAPER ==============

async def download_pdf(session: aiohttp.ClientSession, url: str) -> tuple[bytes, int]:
    """Download PDF file and return content + size"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 200:
                content = await response.read()
                return content, len(content)
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {str(e)}")
    return None, 0

async def extract_case_study_info(session: aiohttp.ClientSession, url: str, visited: Set[str]) -> Optional
    [Dict[str, Any]]:
    """Extract case study information from a page"""
    if url in visited:
        return None

    visited.add(url)

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
            if response.status != 200:
                return None

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

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
                        # Make absolute URL
                        from urllib.parse import urljoin
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
                'tags': tags[:5]  # Limit tags
            }

    except Exception as e:
        logger.error(f"Error extracting case study from {url}: {str(e)}")
        return None

async def crawl_zuci_case_studies() -> List[Dict[str, Any]]:
    """Crawl Zuci Systems case study page and extract all case studies"""
    base_url = "https://www.zucisystems.com/category/casestudy/"
    case_studies = []
    visited = set()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(base_url, timeout=aiohttp.ClientTimeout(total=20)) as response:
                html = await  response.text()

                if response.status != 200:
                    logger.error(f"Failed to fetch main page: {response.status}")
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Find all case study links
                case_study_links = []

                # Look for article links, blog post links, etc.
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    link_text = link.get_text().strip().lower()

                    # Filter for case study related links
                    if any(keyword in href.lower() for keyword in ['case', 'study', 'success', 'story', 'customer']):
                        if href.startswith('/'):
                            href = f"https://www.zucisystems.com{href}"
                        elif not href.startswith('http'):
                            continue

                        if 'zucisystems.com' in href and href not in visited:
                            case_study_links.append(href)

                # Also look for "Read More" links within case study cards
                read_more_links = soup.find_all('a', text=['Read More', 'Learn More', 'View Details', 'Read Full Story'])
                for link in read_more_links:
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            href = f"https://www.zucisystems.com{href}"
                        if 'zucisystems.com' in href and href not in visited:
                            case_study_links.append(href)

                # Remove duplicates
                case_study_links = list(set(case_study_links))
                logger.info(f"Found {len(case_study_links)} potential case study links")

                # Extract info from each case study
                for link in case_study_links[:20]:  # Limit to 20 to avoid timeout
                    case_study_info = await extract_case_study_info(session, link, visited)
                    if case_study_info:
                        # Only include if has PDF or meaningful content
                        if case_study_info.get('pdf_url') or case_study_info.get('description'):
                            # Download PDF if available
                            if case_study_info.get('pdf_url'):
                                pdf_content, pdf_size = await download_pdf(session, case_study_info['pdf_url'])
                                if pdf_content:
                                    case_study_info['file_content'] = base64.b64encode(pdf_content).decode('utf-8')
                                    case_study_info['file_size'] = pdf_size

                            case_studies.append(case_study_info)

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
        # Clean up the summary - remove extra whitespace and limit lines
        lines = [line.strip() for line in summary.split('\n') if line.strip()]
        summary = '\n'.join(lines[:6])  # Limit to 6 lines
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        # Fallback to basic summary
        return f"{study.get('title', 'Case Study')}\n{study.get('category', 'General')} - {study.get('type', 'Case Study')}\n{study.get('description', '')[:200]}"

@api_router.post("/document-files/scrape-zuci-case-studies")
async def scrape_zuci_case_studies(current_user: User = Depends(get_current_user)):
    """
    Scrape Zuci Systems website for case studies and save them to document files.
    Generates summaries and overwrites existing documents with the same filename.
    """
    try:
        logger.info("Starting Zuci case studies scraping...")
        case_studies = await crawl_zuci_case_studies()

        if not case_studies:
            return {
                "success": False,
                "message": "No case studies found",
                "case_studies": []
            }

        saved_studies = []
        updated_studies = []

        # Save each case study to database
        for study in case_studies:
            try:
                filename = study.get('filename', f"{study['title'][:50].replace(' ', '_')}.pdf")

                # Generate summary for the case study
                logger.info(f"Generating summary for: {study['title']}")
                summary = await generate_case_study_summary(study)

                # Create document file entry
                doc_file = {
                    "id": str(uuid.uuid4()),
                    "filename": filename,
                    "category": study.get('category', 'General'),
                    "doc_type": study.get('type', 'Case Study'),
                    "file_content": study.get('file_content', ''),
                    "file_size": study.get('file_size', 0),
                    "mime_type": "application/pdf",
                    "summary": summary,
                    "uploaded_by": current_user.id,
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

                # Only save if has file content
                if doc_file['file_content']:
                    # Check if document with same filename exists
                    existing_doc = await db.document_files.find_one(
                        {"filename": filename},
                        {"_id": 0, "id": 1}
                    )

                    if existing_doc:
                        # Overwrite existing document - keep the same ID
                        doc_file['id'] = existing_doc['id']
                        doc_file['updated_at'] = datetime.now(timezone.utc).isoformat()

                        await db.document_files.replace_one(
                            {"id": existing_doc['id']},
                            doc_file
                        )
                        logger.info(f"Overwritten existing document: {filename}")

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
                        # Insert new document
                        await db.document_files.insert_one(doc_file)
                        logger.info(f"Created new document: {filename}")

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

        return {
            "success": True,
            "message": f"Successfully processed {len(all_studies)} case studies ({len(saved_studies)} new, {len(updated_studies)} updated)",
            "total_found": len(case_studies),
            "total_saved": len(saved_studies),
            "total_updated": len(updated_studies),
            "case_studies": all_studies
        }

    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape case studies: {str(e)}")
