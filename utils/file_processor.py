import os
import fitz
import logging
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re
from io import BytesIO
from PyPDF2 import PdfReader
import markdown
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from docx import Document
from striprtf.striprtf import rtf_to_text
import zipfile
import xml.etree.ElementTree as ET
import magic

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def process_file(input_data):
    logger.debug(f"Starting to process input: {input_data}")
    try:
        if isinstance(input_data, str) and (input_data.startswith('http://') or
                                            input_data.startswith('https://')):
            return process_url(input_data)
        else:
            file_type = magic.from_file(input_data, mime=True)
            file_extension = os.path.splitext(input_data)[1].lower()

            logger.debug(
                f"Detected file type: {file_type}, File extension: {file_extension}"
            )

            # Handle cases where magic returns application/octet-stream
            if file_type == 'application/octet-stream':
                if file_extension == '.pptx':
                    file_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                elif file_extension == '.key':
                    file_type = 'application/x-iwork-keynote-sffkey'
                elif file_extension == '.md':
                    file_type = 'text/markdown'

            result = None
            temp_pdf_path = None
            video_tracks = []
            audio_tracks = []

            if file_type == 'application/pdf':
                result = process_pdf(input_data)
            elif file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                temp_pdf_path, video_tracks, audio_tracks = convert_to_pdf(
                    input_data)
                result = process_pdf(temp_pdf_path)
            elif file_type == 'text/markdown' or file_extension == '.md':
                result = process_markdown(input_data)
            elif file_type == 'application/x-iwork-keynote-sffkey' or file_extension == '.key':
                temp_pdf_path = convert_keynote_to_pdf(input_data)
                result = process_pdf(temp_pdf_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            if result:
                result.update({
                    'type': file_type,
                    'temp_file_path': temp_pdf_path or input_data,
                    'video_tracks': video_tracks,
                    'audio_tracks': audio_tracks
                })
                return result
            else:
                raise ValueError("Processing failed to produce a result")

    except Exception as e:
        logger.error(f"Error in process_file: {str(e)}", exc_info=True)
        return {'error': str(e), 'type': 'unknown'}


def process_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        content = []
        fonts = set()

        for page in doc:
            content.append(page.get_text())

            # Extract fonts from each page
            for font in page.get_fonts():
                # font[3] is the font name
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


def convert_to_pdf(input_file):
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        output_file = temp_pdf.name

    try:
        prs = Presentation(input_file)
        pdf = canvas.Canvas(output_file, pagesize=letter)

        video_tracks = []
        audio_tracks = []

        for slide_index, slide in enumerate(prs.slides):
            pdf.setFont("Helvetica", 12)
            pdf.drawString(100, 700, f"Slide {slide_index + 1}")
            y_position = 680
            for shape in slide.shapes:
                if hasattr(shape, 'text'):
                    text_frame = shape.text_frame
                    for paragraph in text_frame.paragraphs:
                        text = paragraph.text
                        pdf.drawString(100, y_position,
                                       text[:80])  # Limit text to 80 chars
                        y_position -= 20
                elif shape.shape_type == MSO_SHAPE_TYPE.MEDIA:
                    if hasattr(shape, 'media_format') and hasattr(
                            shape.media_format, 'mime_type'):
                        mime_type = shape.media_format.mime_type
                        if mime_type.startswith('video'):
                            video_tracks.append(
                                f"Video on slide {slide_index + 1}")
                            pdf.drawString(100, y_position, "[Video]")
                        elif mime_type.startswith('audio'):
                            audio_tracks.append(
                                f"Audio on slide {slide_index + 1}")
                            pdf.drawString(100, y_position, "[Audio]")
                    y_position -= 20

                if y_position < 50:
                    pdf.showPage()
                    y_position = 700
            pdf.showPage()
        pdf.save()
        logger.debug(f"Successfully converted {input_file} to PDF")
        return output_file, video_tracks, audio_tracks
    except Exception as e:
        logger.error(f"Error converting {input_file} to PDF: {str(e)}",
                     exc_info=True)
        raise


def convert_rtf_to_pdf(input_file):
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        output_file = temp_pdf.name

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
    return output_file


def convert_keynote_to_pdf(input_file):
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        output_file = temp_pdf.name

    try:
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
        return output_file
    except Exception as e:
        logger.error(f"Error converting Keynote to PDF: {str(e)}",
                     exc_info=True)
        raise


def extract_text_from_keynote(keynote_file):
    slides = []
    with zipfile.ZipFile(keynote_file, 'r') as zip_ref:
        for filename in zip_ref.namelist():
            if filename.startswith('Data/Slide') and filename.endswith(
                    '.apxl'):
                with zip_ref.open(filename) as file:
                    tree = ET.parse(file)
                    root = tree.getroot()
                    slide_content = ""
                    for text_elem in root.iter(
                            '{http://developer.apple.com/namespaces/keynote2}text'
                    ):
                        slide_content += text_elem.text + "\n" if text_elem.text else ""
                    slides.append(slide_content)
    return slides


def process_markdown(markdown_path):
    try:
        with open(markdown_path, 'r', encoding='utf-8') as md_file:
            md_content = md_file.read()

        html = markdown.markdown(md_content)

        with tempfile.NamedTemporaryFile(suffix='.pdf',
                                         delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name

        font_config = FontConfiguration()
        HTML(string=html).write_pdf(temp_pdf_path, font_config=font_config)

        result = process_pdf(temp_pdf_path)
        result['type'] = 'text/markdown'
        result['temp_file_path'] = temp_pdf_path
        return result
    except Exception as e:
        logger.error(f"Error processing Markdown: {str(e)}", exc_info=True)
        return {
            'error': f"Failed to process Markdown: {str(e)}",
            'type': 'text/markdown'
        }


def process_url(url):
    try:
        parsed_url = urlparse(url)
        if 'docs.google.com' in parsed_url.netloc and 'presentation' in parsed_url.path:
            return process_google_slides(url)

        return process_generic_url(url)
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}", exc_info=True)
        return {'error': str(e), 'type': 'url'}


def process_figma(url):
    try:
        # Here you would implement the logic to process Figma URLs
        # For now, we'll just return a placeholder result
        return {
            'type': 'figma',
            'url': url,
            'message': 'Figma processing not yet implemented'
        }
    except Exception as e:
        logger.error(f"Error processing Figma URL: {str(e)}", exc_info=True)
        return {'error': str(e), 'type': 'figma'}


def process_canva(url):
    try:
        # Here you would implement the logic to process Canva URLs
        # For now, we'll just return a placeholder result
        return {
            'type': 'canva',
            'url': url,
            'message': 'Canva processing not yet implemented'
        }
    except Exception as e:
        logger.error(f"Error processing Canva URL: {str(e)}", exc_info=True)
        return {'error': str(e), 'type': 'canva'}


def process_google_slides(url):
    try:
        # Extract presentation ID from URL
        match = re.search('/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            raise ValueError("Invalid Google Slides URL")
        presentation_id = match.group(1)

        # Construct the export URL
        export_url = f"https://docs.google.com/presentation/d/{presentation_id}/export/pdf"

        # Download the PDF
        response = requests.get(export_url)
        if response.status_code != 200:
            raise Exception(
                "Failed to download the presentation. Make sure it's public and the URL is correct."
            )

        # Read the PDF content
        pdf_content = BytesIO(response.content)
        pdf_reader = PdfReader(pdf_content)

        # Extract text from each page (slide)
        content = []
        for page in pdf_reader.pages:
            content.append(page.extract_text().strip())

        return {
            'type': 'google_slides',
            'num_slides': len(pdf_reader.pages),
            'content': content
        }
    except Exception as e:
        logger.error(f"Error processing Google Slides: {str(e)}",
                     exc_info=True)
        return {'error': str(e), 'type': 'google_slides'}


def process_generic_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()

        with tempfile.NamedTemporaryFile(suffix='.pdf',
                                         delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name

        font_config = FontConfiguration()
        HTML(string=content).write_pdf(temp_pdf_path, font_config=font_config)

        result = process_pdf(temp_pdf_path)
        result['type'] = 'url'
        result['url'] = url
        result['temp_file_path'] = temp_pdf_path
        return result
    except Exception as e:
        logger.error(f"Error in generic URL processing: {str(e)}")
        return {'error': str(e), 'type': 'url'}


# Main execution
if __name__ == "__main__":
    # You can add test code here to run the script directly
    pass
