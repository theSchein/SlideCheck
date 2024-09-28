from utils.file_processor import process_google_slides
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_google_slides_processing():
    # Replace this with a valid Google Slides presentation URL
    google_slides_url = "https://docs.google.com/presentation/d/your-presentation-id/edit"
    
    try:
        result = process_google_slides(google_slides_url)
        
        print("Google Slides Processing Result:")
        print(f"Type: {result['type']}")
        print(f"Number of slides: {result['num_slides']}")
        print(f"Content preview: {result['content'][:2]}")  # Show first two slides
        
        assert result['type'] == 'google_slides', "Result type should be 'google_slides'"
        assert result['num_slides'] > 0, "Should have at least one slide"
        assert len(result['content']) > 0, "Should have some content"
        
        print("Google Slides processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during Google Slides processing test: {str(e)}", exc_info=True)
    finally:
        if 'temp_file_path' in result:
            import os
            os.unlink(result['temp_file_path'])

if __name__ == "__main__":
    test_google_slides_processing()
