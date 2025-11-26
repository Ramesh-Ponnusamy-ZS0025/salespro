"""
Test script for Zuci case studies scraper
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def test_scrape():
    base_url = "https://www.zucisystems.com/category/casestudy/"
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"Fetching: {base_url}")
            async with session.get(base_url, timeout=aiohttp.ClientTimeout(total=20)) as response:
                print(f"Status: {response.status}")
                
                if response.status != 200:
                    print("Failed to fetch page")
                    return
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                print(f"\nPage title: {soup.find('title').get_text() if soup.find('title') else 'No title'}")
                
                # Find all links
                all_links = soup.find_all('a', href=True)
                print(f"\nTotal links found: {len(all_links)}")
                
                # Filter case study links
                case_study_links = []
                for link in all_links:
                    href = link.get('href')
                    if any(keyword in href.lower() for keyword in ['case', 'study', 'success', 'story']):
                        if href.startswith('/'):
                            href = f"https://www.zucisystems.com{href}"
                        if 'zucisystems.com' in href:
                            case_study_links.append(href)
                
                case_study_links = list(set(case_study_links))
                print(f"\nCase study links found: {len(case_study_links)}")
                
                for i, link in enumerate(case_study_links[:5], 1):
                    print(f"{i}. {link}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_scrape())
