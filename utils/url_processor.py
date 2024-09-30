from playwright.sync_api import sync_playwright
import tempfile
import os
import logging
from .file_processor import process_pdf, save_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    return playwright, browser

def process_url(url):
    try:
        playwright, browser = setup_browser()
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()
        page.goto(url, wait_until='networkidle', timeout=60000)

        # Wait for the content to load
        page.wait_for_selector('body', state='visible', timeout=60000)

        # Generate PDF
        pdf_content = page.pdf(format='A4')

        context.close()
        browser.close()
        playwright.stop()

        # Save PDF and process it
        temp_pdf_path = save_pdf(pdf_content)
        result = process_pdf(temp_pdf_path)

        if 'error' not in result:
            result.update({
                'original_type': 'url',
                'type': 'application/pdf',
                'url': url,
                'temp_file_path': temp_pdf_path
            })
        return result
    except Exception as e:
        logger.error(f'Error processing URL: {str(e)}', exc_info=True)
        return {'error': str(e), 'type': 'unknown', 'url': url}
