"""
Test script for Zuci case studies scraper
"""
import asyncio
import sys
sys.path.append('.')

from document_management import crawl_zuci_with_playwright, crawl_zuci_case_studies, PLAYWRIGHT_AVAILABLE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scraper():
    logger.info("Starting Zuci case studies scraper test...")

    try:
        # Try Playwright first if available
        if PLAYWRIGHT_AVAILABLE:
            logger.info("Testing with Playwright scraper...")
            try:
                case_studies = await crawl_zuci_with_playwright()
            except Exception as e:
                logger.error(f"Playwright failed: {str(e)}")
                logger.info("Falling back to aiohttp scraper...")
                case_studies = await crawl_zuci_case_studies()
        else:
            logger.warning("Playwright not available. Testing with aiohttp scraper...")
            logger.warning("For better results, install Playwright: pip install playwright && playwright install chromium")
            case_studies = await crawl_zuci_case_studies()

        logger.info(f"\n{'='*60}")
        logger.info(f"SCRAPER TEST RESULTS")
        logger.info(f"{'='*60}")
        logger.info(f"Total case studies found: {len(case_studies)}")

        for idx, study in enumerate(case_studies, 1):
            logger.info(f"\n[{idx}] {study['title']}")
            logger.info(f"    Category: {study.get('category', 'N/A')}")
            logger.info(f"    Type: {study.get('type', 'N/A')}")
            logger.info(f"    URL: {study.get('source_url', 'N/A')}")
            logger.info(f"    PDF: {'Yes' if study.get('pdf_url') else 'No'}")
            logger.info(f"    Has Content: {'Yes' if study.get('file_content') else 'No'}")

        logger.info(f"\n{'='*60}")
        logger.info(f"Test completed successfully!")

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())
