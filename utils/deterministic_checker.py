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

    return results
