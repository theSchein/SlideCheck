def run_deterministic_checks(slide_data):
    results = []

    # Check file type
    file_type = slide_data['type']
    results.append({
        'check': 'File type',
        'passed': file_type in ['pdf', 'powerpoint', 'google_slides', 'figma', 'canva'],
        'message': f'File type is {file_type}.'
    })

    # Check number of slides
    num_slides = slide_data['num_slides']
    results.append({
        'check': 'Number of slides',
        'passed': 5 <= num_slides <= 15,
        'message': f'The deck has {num_slides} slides. Ideal range is 5-15 slides.'
    })

    # Check for fonts (placeholder - actual implementation would depend on file type)
    results.append({
        'check': 'Font usage',
        'passed': True,
        'message': 'Font check not implemented for this file type.'
    })

    # Check for audio/video (placeholder - actual implementation would depend on file type)
    results.append({
        'check': 'Audio/Video presence',
        'passed': True,
        'message': 'Audio/Video check not implemented for this file type.'
    })

    # Add the new image presence check
    results.append(check_image_presence(slide_data))

    return results

def check_image_presence(slide_data):
    # This is a simple check that looks for common image-related keywords in the slide content
    image_keywords = ['image', 'picture', 'photo', 'figure', 'diagram', 'graph', 'chart']
    all_text = ' '.join(slide_data['content']).lower()
    has_images = any(keyword in all_text for keyword in image_keywords)
    
    return {
        'check': 'Image Presence',
        'passed': has_images,
        'message': 'The deck likely contains images.' if has_images else 'No images detected in the deck.'
    }
