import magic
import fitz  # PyMuPDF
import logging
from pptx import Presentation
from odf import text, teletype
from odf.opendocument import load
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pdf2image import convert_from_path
import io

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convert_to_pdf(input_file, output_pdf):
    logger.debug(f"Converting {input_file} to PDF: {output_pdf}")
    file_type = magic.from_file(input_file, mime=True)

    try:
        if file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            # Convert PowerPoint to PDF
            prs = Presentation(input_file)
            pdf = canvas.Canvas(output_pdf, pagesize=letter)

            for slide in prs.slides:
                pdf.setFont("Helvetica", 12)
                y = 700
                for shape in slide.shapes:
                    if hasattr(shape, 'text'):
                        text = shape.text
                        pdf.drawString(50, y, text)
                        y -= 20
                pdf.showPage()

            pdf.save()

        elif file_type == 'application/vnd.oasis.opendocument.presentation':
            # Convert LibreOffice to PDF (requires unoconv to be installed on the system)
            os.system(f"unoconv -f pdf -o {output_pdf} {input_file}")

        elif file_type == 'application/pdf':
            # If it's already a PDF, just copy the file
            with open(input_file, 'rb') as src, open(output_pdf, 'wb') as dst:
                dst.write(src.read())

        else:
            raise ValueError(f"Unsupported file type for conversion: {file_type}")

        logger.debug(f"Successfully converted {input_file} to PDF: {output_pdf}")
    except Exception as e:
        logger.error(f"Error converting file to PDF: {str(e)}", exc_info=True)
        raise

def process_file(input_data):
    logger.debug(f"Starting to process input: {input_data}")
    try:
        if isinstance(input_data, str) and (input_data.startswith('http://') or input_data.startswith('https://')):
            return process_url(input_data)
        else:
            # Create a temporary PDF file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name

            # Convert the input file to PDF
            convert_to_pdf(input_data, temp_pdf_path)

            # Process the resulting PDF file
            result = process_pdf(temp_pdf_path)

            # Add the temporary file path to the result
            result['temp_file_path'] = temp_pdf_path

            return result
    except Exception as e:
        logger.error(f"Error in process_file: {str(e)}", exc_info=True)
        raise

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
    
    # Extract the file ID from the URL
    parsed_url = urlparse(url)
    file_id = parse_qs(parsed_url.query).get('id', [None])[0]
    if not file_id:
        file_id = parsed_url.path.split('/')[-2]
    
    if not file_id:
        raise ValueError("Could not extract file ID from the Google Slides URL")

    # Construct the export URL
    export_url = f"https://docs.google.com/presentation/d/{file_id}/export/pdf"
    
    try:
        # Download the PDF
        response = requests.get(export_url)
        response.raise_for_status()  # Raise an exception for bad responses
        
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf_path = temp_pdf.name
        
        # Process the PDF
        result = process_pdf(temp_pdf_path)
        
        # Add the original URL and temporary file path to the result
        result['url'] = url
        result['temp_file_path'] = temp_pdf_path
        
        return result
    except requests.RequestException as e:
        logger.error(f"Error downloading Google Slides PDF: {str(e)}", exc_info=True)
        return {
            'type': 'google_slides',
            'num_slides': 0,
            'content': [f"Error processing Google Slides: {str(e)}"],
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
