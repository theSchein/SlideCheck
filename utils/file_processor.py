import magic
import fitz  # PyMuPDF
import logging
from pptx import Presentation
from odf import text, teletype
from odf.opendocument import load

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_file(filepath):
    logger.debug(f"Starting to process file: {filepath}")
    try:
        file_type = magic.from_file(filepath, mime=True)
        logger.debug(f"Detected file type: {file_type}")
        if file_type == 'application/pdf':
            return process_pdf(filepath)
        elif file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            return process_pptx(filepath)
        elif file_type == 'application/vnd.oasis.opendocument.presentation':
            return process_odp(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Supported types are PDF, PowerPoint, and LibreOffice Presentation.")
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
            'content': text_content,
            'file_path': filepath  # Add this line
        }
    except Exception as e:
        logger.error(f"Error processing PDF file: {str(e)}", exc_info=True)
        raise

def process_pptx(filepath):
    logger.debug(f"Starting to process PowerPoint file: {filepath}")
    try:
        presentation = Presentation(filepath)
        num_slides = len(presentation.slides)
        logger.debug(f"Number of slides in PowerPoint: {num_slides}")
        text_content = []
        for slide in presentation.slides:
            slide_text = ""
            for shape in slide.shapes:
                if hasattr(shape, 'text'):
                    slide_text += shape.text + "\n"
            logger.debug(f"Extracted text from slide: {slide_text[:100]}...")  # Log first 100 characters
            text_content.append(slide_text)

        logger.debug("PowerPoint processing completed successfully")
        return {
            'type': 'powerpoint',
            'num_slides': num_slides,
            'content': text_content,
            'file_path': filepath  # Add this line
        }
    except Exception as e:
        logger.error(f"Error processing PowerPoint file: {str(e)}", exc_info=True)
        raise

def process_odp(filepath):
    logger.debug(f"Starting to process LibreOffice Presentation file: {filepath}")
    try:
        doc = load(filepath)
        slides = doc.getElementsByType(text.Page)
        num_slides = len(slides)
        logger.debug(f"Number of slides in LibreOffice Presentation: {num_slides}")
        text_content = []
        for slide in slides:
            slide_text = teletype.extractText(slide)
            logger.debug(f"Extracted text from slide: {slide_text[:100]}...")  # Log first 100 characters
            text_content.append(slide_text)

        logger.debug("LibreOffice Presentation processing completed successfully")
        return {
            'type': 'libreoffice',
            'num_slides': num_slides,
            'content': text_content,
            'file_path': filepath  # Add this line
        }
    except Exception as e:
        logger.error(f"Error processing LibreOffice Presentation file: {str(e)}", exc_info=True)
        raise
