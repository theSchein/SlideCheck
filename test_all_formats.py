import os
import tempfile
from utils.file_processor import process_file, process_url
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_pdf():
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(b'%PDF-1.5\nSample PDF content')
        temp_pdf_path = temp_pdf.name

    try:
        result = process_file(temp_pdf_path)
        assert result['type'] == 'pdf', "Result type should be 'pdf'"
        assert result['num_slides'] > 0, "Should have at least one page"
        assert len(result['content']) > 0, "Should have some content"
        print("PDF processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during PDF processing test: {str(e)}", exc_info=True)
    finally:
        os.unlink(temp_pdf_path)

def test_pptx():
    # You need to provide a sample PPTX file for testing
    pptx_path = "path/to/sample.pptx"
    if os.path.exists(pptx_path):
        try:
            result = process_file(pptx_path)
            assert result['type'] == 'pdf', "Result type should be 'pdf' (converted from pptx)"
            assert result['num_slides'] > 0, "Should have at least one slide"
            assert len(result['content']) > 0, "Should have some content"
            print("PPTX processing test passed successfully!")
        except Exception as e:
            logger.error(f"Error during PPTX processing test: {str(e)}", exc_info=True)
    else:
        print("PPTX test skipped: No sample file available")

def test_otp():
    # You need to provide a sample OTP file for testing
    otp_path = "path/to/sample.otp"
    if os.path.exists(otp_path):
        try:
            result = process_file(otp_path)
            assert result['type'] == 'pdf', "Result type should be 'pdf' (converted from otp)"
            assert result['num_slides'] > 0, "Should have at least one slide"
            assert len(result['content']) > 0, "Should have some content"
            print("OTP processing test passed successfully!")
        except Exception as e:
            logger.error(f"Error during OTP processing test: {str(e)}", exc_info=True)
    else:
        print("OTP test skipped: No sample file available")

def test_canva():
    # Replace with a valid Canva presentation URL
    canva_url = "https://www.canva.com/design/DAFxxx/view"
    try:
        result = process_url(canva_url)
        assert result['type'] == 'canva', "Result type should be 'canva'"
        assert result['num_slides'] > 0, "Should have at least one slide"
        assert len(result['content']) > 0, "Should have some content"
        print("Canva processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during Canva processing test: {str(e)}", exc_info=True)

def test_figma():
    # Replace with a valid Figma presentation URL
    figma_url = "https://www.figma.com/file/xxx/Sample-Presentation"
    try:
        result = process_url(figma_url)
        assert result['type'] == 'figma', "Result type should be 'figma'"
        assert result['num_slides'] > 0, "Should have at least one slide"
        assert len(result['content']) > 0, "Should have some content"
        print("Figma processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during Figma processing test: {str(e)}", exc_info=True)

def test_keynote():
    # You need to provide a sample Keynote file for testing
    keynote_path = "path/to/sample.key"
    if os.path.exists(keynote_path):
        try:
            result = process_file(keynote_path)
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
