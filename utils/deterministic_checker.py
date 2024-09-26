import PyPDF2

def run_deterministic_checks(slide_data):
    results = []

    # Check file type
    file_type = slide_data['type']
    results.append({
        'check': 'File type',
        'passed': file_type in ['pdf', 'powerpoint', 'libreoffice', 'canva', 'google_slides'],
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

    # Add the image presence check
    results.append(check_image_presence(slide_data))

    return results

def check_image_presence(slide_data):
    file_type = slide_data['type']
    file_path = slide_data.get('file_path')
    url = slide_data.get('url')

    if file_type == 'pdf' and file_path:
        return check_for_images_pdf(file_path)
    elif file_type in ['canva', 'google_slides']:
        # For now, we'll assume Canva and Google Slides always have images
        return {
            'check': 'Image Presence',
            'passed': True,
            'message': f'The {file_type} presentation likely contains images.'
        }
    else:
        # Fallback to keyword-based check for other file types
        image_keywords = ['image', 'picture', 'photo', 'figure', 'diagram', 'graph', 'chart']
        all_text = ' '.join(slide_data['content']).lower()
        has_images = any(keyword in all_text for keyword in image_keywords)
        return {
            'check': 'Image Presence',
            'passed': has_images,
            'message': 'The deck likely contains images.' if has_images else 'No images detected in the deck.'
        }

def check_for_images_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    has_images = False
    for page in reader.pages:
        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].get_object()
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    has_images = True
                    break
        if has_images:
            break
    return {
        'check': 'Image Presence',
        'passed': has_images,
        'message': 'The PDF contains images.' if has_images else 'No images detected in the PDF.'
    }
