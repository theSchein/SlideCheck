import fitz
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        content = []
        fonts = set()

        for page in doc:
            content.append(page.get_text())
            for font in page.get_fonts():
                fonts.add(font[3])

        doc.close()

        return {
            'type': 'pdf',
            'num_slides': num_pages,
            'content': content,
            'fonts': list(fonts)
        }
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        return {'error': f"Failed to process PDF: {str(e)}"}

def save_pdf(pdf_content):
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
            temp_pdf.write(pdf_content)
        return temp_pdf_path
    except Exception as e:
        logger.error(f"Error saving PDF: {str(e)}", exc_info=True)
        raise
