from utils.file_processor import process_canva_link, process_figma_link
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_canva_processing():
    # Replace this with a valid Canva presentation URL
    canva_url = "https://www.canva.com/design/DAFxxx/view"
    
    try:
        result = process_canva_link(canva_url)
        
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

def test_figma_processing():
    # Replace this with a valid Figma presentation URL
    figma_url = "https://www.figma.com/file/xxx/Sample-Presentation"
    
    try:
        result = process_figma_link(figma_url)
        
        print("Figma Processing Result:")
        print(f"Type: {result['type']}")
        print(f"Number of slides: {result['num_slides']}")
        print(f"Content preview: {result['content'][:2]}")  # Show first two slides
        
        assert result['type'] == 'figma', "Result type should be 'figma'"
        assert result['num_slides'] > 0, "Should have at least one slide"
        assert len(result['content']) > 0, "Should have some content"
        
        print("Figma processing test passed successfully!")
    except Exception as e:
        logger.error(f"Error during Figma processing test: {str(e)}", exc_info=True)
    finally:
        if 'temp_file_path' in result:
            import os
            os.unlink(result['temp_file_path'])

if __name__ == "__main__":
    test_canva_processing()
    test_figma_processing()
