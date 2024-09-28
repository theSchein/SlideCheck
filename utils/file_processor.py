import magic
import fitz 
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
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import subprocess
import platform
import requests
from playwright.sync_api import sync_playwright
from docx import Document
from striprtf.striprtf import rtf_to_text

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_file(input_data):
    logger.debug(f"Starting to process input: {input_data}")
    try:
        if isinstance(input_data, str) and (input_data.startswith('http://') or input_data.startswith('https://')):
            return process_url(input_data)
        else:
            file_type = magic.from_file(input_data, mime=True)
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name

            if file_type == 'application/pdf':
                result = process_pdf(input_data)
            elif file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                convert_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'application/vnd.oasis.opendocument.presentation':
                convert_odf_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'text/markdown':
                convert_markdown_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                convert_docx_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'text/rtf':
                convert_rtf_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            result['temp_file_path'] = temp_pdf_path
            return result
    except Exception as e:
        logger.error(f"Error in process_file: {str(e)}", exc_info=True)
        return {'error': str(e)}

def process_url(url):
    logger.debug(f"Processing URL: {url}")
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if 'canva.com' in domain:
        return process_canva(url)
    elif 'docs.google.com' in domain and 'presentation' in parsed_url.path:
        return process_google_slides(url)
    elif 'figma.com' in domain:
        return process_figma(url)
    else:
        raise ValueError(f"Unsupported URL: {url}. Supported URLs are from Canva, Google Slides, and Figma.")

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

def convert_odf_to_pdf(input_file, output_pdf):
    logger.debug(f"Converting ODF file to PDF: {input_file}")
    try:
        doc = load(input_file)
        all_text = []
        for paragraph in doc.getElementsByType(text.P):
            all_text.append(teletype.extractText(paragraph))
        
        pdf = canvas.Canvas(output_pdf, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        y = 750
        for line in all_text:
            pdf.drawString(50, y, line)
            y -= 20
            if y < 50:
                pdf.showPage()
                y = 750
        pdf.save()
        logger.debug(f"Successfully converted ODF to PDF: {output_pdf}")
    except Exception as e:
        logger.error(f"Error converting ODF to PDF: {str(e)}", exc_info=True)
        raise

def convert_markdown_to_pdf(input_file, output_pdf):
    logger.debug(f"Converting Markdown file to PDF: {input_file}")
    try:
        with open(input_file, 'r') as f:
            markdown_text = f.read()

        html = markdown.markdown(markdown_text)

        font_config = FontConfiguration()
        css = CSS(string='''
            @page { size: letter; margin: 1cm }
            body { font-family: Arial, sans-serif; }
        ''',
                  font_config=font_config)

        HTML(string=html).write_pdf(output_pdf,
                                    stylesheets=[css],
                                    font_config=font_config)
        logger.debug(f"Successfully converted Markdown to PDF: {output_pdf}")
    except Exception as e:
        logger.error(f"Error converting Markdown to PDF: {str(e)}",
                     exc_info=True)
        raise

def convert_docx_to_pdf(input_file, output_pdf):
    logger.debug(f"Converting DOCX file to PDF: {input_file}")
    try:
        doc = Document(input_file)
        pdf = canvas.Canvas(output_pdf, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        y = 750
        for paragraph in doc.paragraphs:
            text = paragraph.text
            pdf.drawString(50, y, text)
            y -= 20
            if y < 50:
                pdf.showPage()
                y = 750
        pdf.save()
        logger.debug(f"Successfully converted DOCX to PDF: {output_pdf}")
    except Exception as e:
        logger.error(f"Error converting DOCX to PDF: {str(e)}", exc_info=True)
        raise

def convert_rtf_to_pdf(input_file, output_pdf):
    logger.debug(f"Converting RTF file to PDF: {input_file}")
    try:
        with open(input_file, 'r') as file:
            rtf_text = file.read()
        plain_text = rtf_to_text(rtf_text)
        
        pdf = canvas.Canvas(output_pdf, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        y = 750
        for line in plain_text.split('\n'):
            pdf.drawString(50, y, line)
            y -= 20
            if y < 50:
                pdf.showPage()
                y = 750
        pdf.save()
        logger.debug(f"Successfully converted RTF to PDF: {output_pdf}")
    except Exception as e:
        logger.error(f"Error converting RTF to PDF: {str(e)}", exc_info=True)
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
                logger.debug(f"Extracted text from page {page.number + 1}: {text[:100]}...")
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

def process_figma(url):
    logger.debug(f"Processing Figma URL: {url}")
    try:
        # Extract file key from URL
        file_key = url.split('/')[-1]

        # Get Figma file information (you'll need to set up FIGMA_ACCESS_TOKEN)
        headers = {"X-FIGMA-TOKEN": os.environ.get("FIGMA_ACCESS_TOKEN")}
        response = requests.get(f"https://api.figma.com/v1/files/{file_key}", headers=headers)
        response.raise_for_status()
        file_data = response.json()

        # Use Playwright to capture the design as PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            output_pdf = temp_pdf.name

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            page.pdf(path=output_pdf, format="Letter")
            browser.close()

        logger.debug(f"Successfully processed Figma URL to PDF: {output_pdf}")
        return {
            'type': 'figma',
            'num_slides': len(file_data['document']['children']),
            'content': [child['name'] for child in file_data['document']['children']],
            'url': url,
            'temp_file_path': output_pdf
        }
    except Exception as e:
        logger.error(f"Error processing Figma URL: {str(e)}", exc_info=True)
        raise