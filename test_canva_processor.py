from utils.file_processor import process_url
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_canva_processing():
    # Replace this with a valid Canva presentation URL
    canva_url = "https://www.canva.com/design/DAFxxx/view"
    
    try:
        result = process_url(canva_url)
        
        print("Canva Processing Result:")
        print(f"Type: {result['type']}")
        print(f"Number of slides: {result['num_slides']}")
        print(f"Content preview: {result['content'][:2]}")  # Show first two slides
        
        assert result['type'] == 'canva', "Result type should be 'canva'"
        assert result['num_slides'] > 0, "Should have at least one slide"
        assert len(result['content']) > 0, "Should have some content"
        
        print("Canva processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during Canva processing test: {str(e)}", exc_info=True)
    finally:
        if 'temp_file_path' in result:
            import os
            os.unlink(result['temp_file_path'])

if __name__ == "__main__":
    test_canva_processing()
