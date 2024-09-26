import magic
import fitz  # PyMuPDF
import logging
from pptx import Presentation
from odf import text, teletype
from odf.opendocument import load
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_file(input_data):
    logger.debug(f"Starting to process input: {input_data}")
    try:
        if isinstance(input_data, str) and (input_data.startswith('http://') or input_data.startswith('https://')):
            return process_url(input_data)
        else:
            return process_local_file(input_data)
    except Exception as e:
        logger.error(f"Error in process_file: {str(e)}", exc_info=True)
        raise

def process_local_file(filepath):
    logger.debug(f"Processing local file: {filepath}")
    file_type = magic.from_file(filepath, mime=True)
    logger.debug(f"Detected file type: {file_type}")
    if file_type == 'application/pdf':
        return process_pdf(filepath)
    elif file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        return process_pptx(filepath)
    elif file_type == 'application/vnd.oasis.opendocument.presentation':
        return process_odp(filepath)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Supported types are PDF, PowerPoint (.pptx), and LibreOffice Presentation (.odp).")

def process_url(url):
    logger.debug(f"Processing URL: {url}")
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if 'canva.com' in domain:
        return process_canva(url)
    elif 'docs.google.com' in domain and 'presentation' in parsed_url.path:
        return process_google_slides(url)
    else:
        raise ValueError(f"Unsupported URL: {url}. Supported URLs are from Canva and Google Slides.")

def process_canva(url):
    logger.debug(f"Processing Canva URL: {url}")
    # Note: This is a placeholder implementation. Actual implementation would require Canva API access or web scraping.
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title = soup.title.string if soup.title else "Untitled Canva Presentation"
    
    # Extract text content (this is a simplified approach and may not work for all Canva presentations)
    text_content = [p.get_text() for p in soup.find_all('p')]
    
    return {
        'type': 'canva',
        'num_slides': len(text_content),  # This is an approximation
        'content': text_content,
        'url': url
    }

def process_google_slides(url):
    logger.debug(f"Processing Google Slides URL: {url}")
    
    # Extract the presentation ID from the URL
    presentation_id = url.split('/')[-2]

    try:
        # Check if the GOOGLE_CREDENTIALS_PATH environment variable is set
        credentials_path = os.environ.get('GOOGLE_CREDENTIALS_PATH')
        if not credentials_path:
            raise ValueError("GOOGLE_CREDENTIALS_PATH environment variable is not set.")
        
        # Check if the credentials file exists
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Google credentials file not found at {credentials_path}")
        
        # Set up credentials
        creds = Credentials.from_authorized_user_file(credentials_path)

        # Build the Google Slides API service
        service = build('slides', 'v1', credentials=creds)

        # Call the Slides API
        presentation = service.presentations().get(presentationId=presentation_id).execute()
        slides = presentation.get('slides', [])

        num_slides = len(slides)
        content = []

        for slide in slides:
            slide_content = ""
            for element in slide.get('pageElements', []):
                if 'shape' in element and 'text' in element['shape']:
                    for textElement in element['shape']['text'].get('textElements', []):
                        if 'textRun' in textElement:
                            slide_content += textElement['textRun']['content']
            content.append(slide_content)

        logger.debug(f"Successfully processed Google Slides presentation with {num_slides} slides")
        return {
            'type': 'google_slides',
            'num_slides': num_slides,
            'content': content,
            'url': url
        }
    except ValueError as ve:
        logger.error(f"Google Slides authentication error: {str(ve)}")
        return {
            'type': 'google_slides',
            'num_slides': 0,
            'content': ["Error: Google Slides authentication not properly configured. Please set up the GOOGLE_CREDENTIALS_PATH environment variable."],
            'url': url
        }
    except FileNotFoundError as fnf:
        logger.error(f"Google Slides credentials file error: {str(fnf)}")
        return {
            'type': 'google_slides',
            'num_slides': 0,
            'content': ["Error: Google Slides credentials file not found. Please check the GOOGLE_CREDENTIALS_PATH environment variable."],
            'url': url
        }
    except Exception as e:
        logger.error(f"Error processing Google Slides: {str(e)}", exc_info=True)
        return {
            'type': 'google_slides',
            'num_slides': 0,
            'content': [f"Error processing Google Slides: {str(e)}"],
            'url': url
        }

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
            'file_path': filepath
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
            'file_path': filepath
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
            'file_path': filepath
        }
    except Exception as e:
        logger.error(f"Error processing LibreOffice Presentation file: {str(e)}", exc_info=True)
        raise
