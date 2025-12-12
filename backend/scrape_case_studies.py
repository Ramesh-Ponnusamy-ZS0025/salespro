"""
Script to scrape case studies from Zuci Systems website
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
import time

def scrape_case_studies(max_pages: int = 11) -> List[Dict]:
    """
    Scrape case studies from Zuci Systems website
    The site has pagination, so we'll scrape multiple pages
    """
    case_studies = []
    base_url = "https://www.zucisystems.com/category/casestudy/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for page in range(1, max_pages + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page/{page}/"

        print(f"Scraping page {page}: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all case study articles
            articles = soup.find_all('article', class_='post')

            if not articles:
                print(f"No articles found on page {page}")
                break

            for article in articles:
                case_study = {}

                # Get title
                title_elem = article.find('h2', class_='entry-title')
                if title_elem:
                    link_elem = title_elem.find('a')
                    if link_elem:
                        case_study['title'] = link_elem.get_text(strip=True)
                        case_study['url'] = link_elem.get('href', '')

                # Get excerpt/description
                excerpt_elem = article.find('div', class_='entry-summary')
                if not excerpt_elem:
                    excerpt_elem = article.find('div', class_='entry-content')

                if excerpt_elem:
                    case_study['excerpt'] = excerpt_elem.get_text(strip=True)[:300]

                # Get categories/tags
                categories = []
                cat_links = article.find_all('a', rel='category tag')
                for cat_link in cat_links:
                    cat_text = cat_link.get_text(strip=True)
                    if cat_text and cat_text.lower() != 'casestudy':
                        categories.append(cat_text)

                case_study['categories'] = categories

                # Get meta info (date, author, etc.)
                meta_elem = article.find('div', class_='entry-meta')
                if meta_elem:
                    date_elem = meta_elem.find('time', class_='entry-date')
                    if date_elem:
                        case_study['date'] = date_elem.get('datetime', '')

                # Only add if we have at least a title
                if case_study.get('title'):
                    case_studies.append(case_study)
                    print(f"  - Found: {case_study['title']}")

            # Be nice to the server
            time.sleep(1)

        except Exception as e:
            print(f"Error scraping page {page}: {str(e)}")
            continue

    return case_studies


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text for relevance matching"""
    # Simple keyword extraction (you can enhance this)
    text = text.lower()

    # Common industry keywords
    keywords = []

    # Technology keywords
    tech_keywords = ['ai', 'ml', 'data', 'analytics', 'cloud', 'api', 'mobile',
                     'automation', 'digital', 'transformation', 'engineering',
                     'software', 'development', 'testing', 'qa', 'devops']

    # Industry keywords
    industry_keywords = ['healthcare', 'finance', 'banking', 'retail', 'insurance',
                         'technology', 'manufacturing', 'education']

    for keyword in tech_keywords + industry_keywords:
        if keyword in text:
            keywords.append(keyword)

    return list(set(keywords))


def enhance_case_studies(case_studies: List[Dict]) -> List[Dict]:
    """Add keywords and other metadata to case studies"""
    for cs in case_studies:
        # Extract keywords from title and excerpt
        text = f"{cs.get('title', '')} {cs.get('excerpt', '')}"
        cs['keywords'] = extract_keywords(text)

        # Add a simple relevance score placeholder
        cs['relevance_score'] = 0

    return case_studies


def save_case_studies(case_studies: List[Dict], filename: str = 'case_studies.json'):
    """Save case studies to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(case_studies, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(case_studies)} case studies to {filename}")


if __name__ == "__main__":
    print("Starting case study scraper...\n")

    # Scrape case studies (104 case studies across ~11 pages)
    case_studies = scrape_case_studies(max_pages=11)

    # Enhance with keywords
    case_studies = enhance_case_studies(case_studies)

    # Save to JSON
    save_case_studies(case_studies, 'case_studies.json')

    print(f"\nTotal case studies scraped: {len(case_studies)}")
    print("\nSample case study:")
    if case_studies:
        print(json.dumps(case_studies[0], indent=2))
