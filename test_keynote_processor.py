import os
from utils.file_processor import process_file
import tempfile
from keynote_parser import keynote_file

def create_sample_keynote():
    # Create a simple Keynote file programmatically
    kn = keynote_file.Keynote()
    slide = kn.add_slide()
    text_box = slide.add_text_box()
    paragraph = text_box.add_paragraph()
    paragraph.add_text("Sample Keynote Presentation")
    
    with tempfile.NamedTemporaryFile(suffix='.key', delete=False) as temp_key:
        kn.write(temp_key.name)
    return temp_key.name

def test_keynote_processing():
    keynote_file = create_sample_keynote()
    result = None
    try:
        result = process_file(keynote_file)
        print("Keynote Processing Result:")
        print(f"Number of slides: {result['num_slides']}")
        print(f"Content: {result['content']}")
        assert result['type'] == 'pdf', "Resulting file should be a PDF"
        assert int(result['num_slides']) >= 1, "Should have at least one slide"
        assert "Sample Keynote Presentation" in ' '.join(result['content']), "Content should include the sample text"
        print("Keynote processing test passed successfully!")
    except Exception as e:
        print(f"Error during Keynote processing test: {str(e)}")
    finally:
        os.unlink(keynote_file)
        if result and 'temp_file_path' in result:
            os.unlink(result['temp_file_path'])

if __name__ == "__main__":
    test_keynote_processing()
