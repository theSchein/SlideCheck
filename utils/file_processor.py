import magic
import fitz  # PyMuPDF
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_file(filepath):
    logger.debug(f"Starting to process file: {filepath}")
    try:
        file_type = magic.from_file(filepath, mime=True)
        logger.debug(f"Detected file type: {file_type}")
        if file_type == 'application/pdf':
            return process_pdf(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Only PDF files are accepted.")
    except Exception as e:
        logger.error(f"Error in process_file: {str(e)}", exc_info=True)
        raise

def process_pdf(filepath):
    logger.debug(f"Starting to process PDF file: {filepath}")
    try:
        with fitz.open(filepath) as doc:
            num_pages = len(doc)
            logger.debug(f"Number of pages in PDF: {num_pages}")
            text_content = []
            for page in doc:
                text = page.get_text()
                logger.debug(f"Extracted text from page {page.number + 1}: {text[:100]}...")  # Log first 100 characters
                text_content.append(text)

        logger.debug("PDF processing completed successfully")
        return {
            'type': 'pdf',
            'num_slides': num_pages,
            'content': text_content
        }
    except Exception as e:
        logger.error(f"Error processing PDF file: {str(e)}", exc_info=True)
        raise
