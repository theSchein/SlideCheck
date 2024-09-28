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
from keynote_parser import keynote_parser
import zipfile
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_file(input_data):
    logger.debug(f"Starting to process input: {input_data}")
    try:
        if isinstance(input_data, str) and (input_data.startswith('http://') or input_data.startswith('https://')):
            return process_url(input_data)
        else:
            file_type = magic.from_file(input_data, mime=True)
            if file_type == 'application/zip' and input_data.lower().endswith('.otp'):
                file_type = 'application/vnd.oasis.opendocument.presentation'
            elif file_type == 'application/zip' and input_data.lower().endswith('.key'):
                file_type = 'application/x-iwork-keynote-sffkey'

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name

            if file_type == 'application/pdf':
                result = process_pdf(input_data)
            elif file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                convert_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type in ['application/vnd.oasis.opendocument.presentation', 'application/x-openoffice-presentation']:
                convert_odf_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'text/markdown':
                convert_markdown_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'application/rtf':
                convert_rtf_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                convert_docx_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'application/x-iwork-keynote-sffkey':
                convert_keynote_to_pdf(input_data, temp_pdf_path)
                result = process_pdf(temp_pdf_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            result['temp_file_path'] = temp_pdf_path
            return result
    except Exception as e:
        logger.error(f"Error in process_file: {str(e)}", exc_info=True)
        return {'error': str(e)}

def process_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        content = []
        for page in doc:
            content.append(page.get_text())
        doc.close()
        return {'type': 'pdf', 'num_slides': num_pages, 'content': content}
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        return {'error': f"Failed to process PDF: {str(e)}"}

def convert_to_pdf(input_file, output_file):
    prs = Presentation(input_file)
    pdf = canvas.Canvas(output_file, pagesize=letter)
    for slide in prs.slides:
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 700, f"Slide {prs.slides.index(slide) + 1}")
        for shape in slide.shapes:
            if hasattr(shape, 'text'):
                pdf.drawString(100, 680 - 20 * slide.shapes.index(shape), shape.text)
        pdf.showPage()
    pdf.save()

def convert_odf_to_pdf(input_file, output_file):
    doc = load(input_file)
    allparas = doc.getElementsByType(text.P)
    pdf = canvas.Canvas(output_file, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    y = 750
    for para in allparas:
        content = teletype.extractText(para)
        pdf.drawString(50, y, content)
        y -= 14
        if y < 50:
            pdf.showPage()
            y = 750
    pdf.save()

def convert_markdown_to_pdf(input_file, output_file):
    with open(input_file, 'r') as f:
        markdown_text = f.read()
    html = markdown.markdown(markdown_text)
    font_config = FontConfiguration()
    HTML(string=html).write_pdf(output_file, font_config=font_config)

def process_url(url):
    try:
        parsed_url = urlparse(url)
        if 'canva.com' in parsed_url.netloc:
            return process_canva_link(url)
        elif 'figma.com' in parsed_url.netloc:
            return process_figma_link(url)
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        text_content = soup.get_text()

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name

        font_config = FontConfiguration()
        HTML(string=content).write_pdf(temp_pdf_path, font_config=font_config)

        result = process_pdf(temp_pdf_path)
        result['type'] = 'url'
        result['url'] = url
        result['temp_file_path'] = temp_pdf_path
        return result
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}", exc_info=True)
        return {'error': str(e)}

def process_canva_link(url):
    try:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                
                page.wait_for_selector('.view-wrapper', timeout=30000)
                
                slides = page.query_selector_all('.view-wrapper')
                content = []
                
                for slide in slides:
                    slide_text = slide.inner_text()
                    content.append(slide_text)
                
                browser.close()
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name
            
            pdf = canvas.Canvas(temp_pdf_path, pagesize=letter)
            pdf.setFont("Helvetica", 12)
            
            for i, slide_content in enumerate(content):
                pdf.drawString(100, 750, f"Slide {i + 1}")
                y = 720
                for line in slide_content.split('\n'):
                    pdf.drawString(100, y, line)
                    y -= 20
                    if y < 50:
                        pdf.showPage()
                        y = 750
                pdf.showPage()
            
            pdf.save()
            
            result = process_pdf(temp_pdf_path)
            result['type'] = 'canva'
            result['url'] = url
            result['temp_file_path'] = temp_pdf_path
            return result
        except Exception as e:
            logger.error(f"Error initializing Playwright: {str(e)}")
            return process_url_fallback(url, 'canva')
    except Exception as e:
        logger.error(f"Error processing Canva link: {str(e)}", exc_info=True)
        return process_url_fallback(url, 'canva')

def process_figma_link(url):
    try:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                
                page.wait_for_selector('.view-wrapper', timeout=30000)
                
                slides = page.query_selector_all('.view-wrapper')
                content = []
                
                for slide in slides:
                    slide_text = slide.inner_text()
                    content.append(slide_text)
                
                browser.close()
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name
            
            pdf = canvas.Canvas(temp_pdf_path, pagesize=letter)
            pdf.setFont("Helvetica", 12)
            
            for i, slide_content in enumerate(content):
                pdf.drawString(100, 750, f"Slide {i + 1}")
                y = 720
                for line in slide_content.split('\n'):
                    pdf.drawString(100, y, line)
                    y -= 20
                    if y < 50:
                        pdf.showPage()
                        y = 750
                pdf.showPage()
            
            pdf.save()
            
            result = process_pdf(temp_pdf_path)
            result['type'] = 'figma'
            result['url'] = url
            result['temp_file_path'] = temp_pdf_path
            return result
        except Exception as e:
            logger.error(f"Error initializing Playwright: {str(e)}")
            return process_url_fallback(url, 'figma')
    except Exception as e:
        logger.error(f"Error processing Figma link: {str(e)}", exc_info=True)
        return process_url_fallback(url, 'figma')

def process_url_fallback(url, link_type):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name

        pdf = canvas.Canvas(temp_pdf_path, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        
        lines = content.split('\n')
        y = 750
        for line in lines:
            pdf.drawString(50, y, line[:80])
            y -= 14
            if y < 50:
                pdf.showPage()
                y = 750
        pdf.save()

        result = process_pdf(temp_pdf_path)
        result['type'] = link_type
        result['url'] = url
        result['temp_file_path'] = temp_pdf_path
        return result
    except Exception as e:
        logger.error(f"Error in fallback processing for {link_type} link: {str(e)}")
        return {'error': str(e)}

def convert_rtf_to_pdf(input_file, output_file):
    with open(input_file, 'r') as file:
        rtf_content = file.read()

    plain_text = rtf_to_text(rtf_content)

    pdf = canvas.Canvas(output_file, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    lines = plain_text.split('\n')
    y = 750
    for line in lines:
        pdf.drawString(50, y, line)
        y -= 14
        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()

def convert_docx_to_pdf(input_file, output_file):
    doc = Document(input_file)
    pdf = canvas.Canvas(output_file, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    y = 750
    for paragraph in doc.paragraphs:
        lines = paragraph.text.split('\n')
        for line in lines:
            pdf.drawString(50, y, line)
            y -= 14
            if y < 50:
                pdf.showPage()
                y = 750

    pdf.save()

def convert_keynote_to_pdf(input_file, output_file):
    try:
        try:
            import keynote_parser
            kn = keynote_parser.Keynote(input_file)
            slides = kn.slides
        except (ImportError, AttributeError):
            slides = extract_text_from_keynote(input_file)

        pdf = canvas.Canvas(output_file, pagesize=letter)
        pdf.setFont("Helvetica", 12)

        for i, slide_content in enumerate(slides):
            pdf.drawString(100, 750, f"Slide {i + 1}")
            y = 720
            for line in slide_content.split('\n'):
                pdf.drawString(100, y, line)
                y -= 20
                if y < 50:
                    pdf.showPage()
                    y = 750
            pdf.showPage()

        pdf.save()
    except Exception as e:
        logger.error(f"Error converting Keynote to PDF: {str(e)}", exc_info=True)
        raise

def extract_text_from_keynote(keynote_file):
    slides = []
    with zipfile.ZipFile(keynote_file, 'r') as zip_ref:
        for filename in zip_ref.namelist():
            if filename.startswith('Data/Slide') and filename.endswith('.apxl'):
                with zip_ref.open(filename) as file:
                    tree = ET.parse(file)
                    root = tree.getroot()
                    slide_content = ""
                    for text_elem in root.iter('{http://developer.apple.com/namespaces/keynote2}text'):
                        slide_content += text_elem.text + "\n" if text_elem.text else ""
                    slides.append(slide_content)
    return slides