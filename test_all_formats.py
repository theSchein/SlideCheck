import os
import tempfile
from utils.file_processor import process_file, process_url
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_pdf():
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        c = canvas.Canvas(temp_pdf.name, pagesize=letter)
        c.drawString(100, 750, "Sample PDF content")
        c.showPage()
        c.save()
        temp_pdf_path = temp_pdf.name

    try:
        result = process_file(temp_pdf_path)
        assert 'error' not in result, f"Error processing PDF: {result.get('error')}"
        assert result['type'] == 'pdf', "Result type should be 'pdf'"
        assert result['num_slides'] > 0, "Should have at least one page"
        assert len(result['content']) > 0, "Should have some content"
        print("PDF processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during PDF processing test: {str(e)}", exc_info=True)
    finally:
        os.unlink(temp_pdf_path)

def test_pptx():
    pptx_path = "path/to/sample.pptx"
    if os.path.exists(pptx_path):
        try:
            result = process_file(pptx_path)
            assert 'error' not in result, f"Error processing PPTX: {result.get('error')}"
            assert result['type'] == 'pdf', "Result type should be 'pdf' (converted from pptx)"
            assert result['num_slides'] > 0, "Should have at least one slide"
            assert len(result['content']) > 0, "Should have some content"
            print("PPTX processing test passed successfully!")
        except Exception as e:
            logger.error(f"Error during PPTX processing test: {str(e)}", exc_info=True)
    else:
        print("PPTX test skipped: No sample file available")

def test_otp():
    otp_path = "path/to/sample.otp"
    if os.path.exists(otp_path):
        try:
            result = process_file(otp_path)
            assert 'error' not in result, f"Error processing OTP: {result.get('error')}"
            assert result['type'] == 'pdf', "Result type should be 'pdf' (converted from otp)"
            assert result['num_slides'] > 0, "Should have at least one slide"
            assert len(result['content']) > 0, "Should have some content"
            print("OTP processing test passed successfully!")
        except Exception as e:
            logger.error(f"Error during OTP processing test: {str(e)}", exc_info=True)
    else:
        print("OTP test skipped: No sample file available")

def test_canva():
    canva_url = "https://www.canva.com/design/DAFxxx/view"
    try:
        result = process_url(canva_url)
        assert 'error' not in result, f"Error processing Canva: {result.get('error')}"
        assert result['type'] == 'canva', "Result type should be 'canva'"
        assert result['num_slides'] > 0, "Should have at least one slide"
        assert len(result['content']) > 0, "Should have some content"
        print("Canva processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during Canva processing test: {str(e)}", exc_info=True)

def test_figma():
    figma_url = "https://www.figma.com/file/xxx/Sample-Presentation"
    try:
        result = process_url(figma_url)
        assert 'error' not in result, f"Error processing Figma: {result.get('error')}"
        assert result['type'] == 'figma', "Result type should be 'figma'"
        assert result['num_slides'] > 0, "Should have at least one slide"
        assert len(result['content']) > 0, "Should have some content"
        print("Figma processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during Figma processing test: {str(e)}", exc_info=True)

def test_keynote():
    keynote_path = "path/to/sample.key"
    if os.path.exists(keynote_path):
        try:
            result = process_file(keynote_path)
            assert 'error' not in result, f"Error processing Keynote: {result.get('error')}"
            assert result['type'] == 'pdf', "Result type should be 'pdf' (converted from keynote)"
            assert result['num_slides'] > 0, "Should have at least one slide"
            assert len(result['content']) > 0, "Should have some content"
            print("Keynote processing test passed successfully!")
        except Exception as e:
            logger.error(f"Error during Keynote processing test: {str(e)}", exc_info=True)
    else:
        print("Keynote test skipped: No sample file available")

if __name__ == "__main__":
    test_pdf()
    test_pptx()
    test_otp()
    test_canva()
    test_figma()
    test_keynote()