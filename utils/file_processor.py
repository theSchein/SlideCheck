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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_file(input_data):
    logger.debug(f"Starting to process input: {input_data}")
    try:
        if isinstance(input_data, str) and (input_data.startswith('http://') or input_data.startswith('https://')):
            return process_url(input_data)
        else:
            file_type = magic.from_file(input_data, mime=True)
            if file_type == 'application/zip' and input_data.lower().endswith('.odp'):
                file_type = 'application/vnd.oasis.opendocument.presentation'
            
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
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            result['temp_file_path'] = temp_pdf_path
            return result
    except Exception as e:
        logger.error(f"Error in process_file: {str(e)}", exc_info=True)
        return {'error': str(e)}

def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    content = []
    for page in doc:
        content.append(page.get_text())
    doc.close()
    return {
        'type': 'pdf',
        'num_slides': num_pages,
        'content': content
    }

# Rest of the file remains unchanged
