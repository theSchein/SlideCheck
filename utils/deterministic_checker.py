import PyPDF2
import re

def run_deterministic_checks(slide_data, conference):
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
        'passed': num_slides <= conference.max_slides,
        'message': f'The deck has {num_slides} slides. Maximum allowed for this conference is {conference.max_slides} slides.'
    })

    # Check for required sections
    required_sections = conference.required_sections.split(',') if conference.required_sections else []
    found_sections = set()
    all_text = ' '.join(slide_data['content']).lower()
    
    for section in required_sections:
        if section.lower() in all_text:
            found_sections.add(section)
    
    missing_sections = set(required_sections) - found_sections
    results.append({
        'check': 'Required sections',
        'passed': len(missing_sections) == 0,
        'message': f'All required sections found.' if len(missing_sections) == 0 else f'Missing sections: {", ".join(missing_sections)}'
    })

    # Conference-specific checks
    if conference.name == "TechCon 2024":
        results.append(check_code_snippets(all_text))
    elif conference.name == "DataSummit 2024":
        results.append(check_data_visualization(all_text))

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
        return {
            'check': 'Image Presence',
            'passed': True,
            'message': f'The {file_type} presentation likely contains images.'
        }
    else:
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

def check_code_snippets(text):
    code_patterns = [
        r'\bdef\s+\w+\s*\(.*\):',  # Python function definition
        r'\bclass\s+\w+:',  # Python class definition
        r'\bif\s+.*:',  # Python if statement
        r'\bfor\s+.*:',  # Python for loop
        r'\bwhile\s+.*:',  # Python while loop
        r'\bfunction\s+\w+\s*\(.*\)\s*{',  # JavaScript function
        r'\bconst\s+\w+\s*=',  # JavaScript const declaration
        r'\blet\s+\w+\s*=',  # JavaScript let declaration
        r'\bvar\s+\w+\s*=',  # JavaScript var declaration
    ]
    
    has_code = any(re.search(pattern, text, re.IGNORECASE) for pattern in code_patterns)
    return {
        'check': 'Code Snippets',
        'passed': has_code,
        'message': 'The presentation contains code snippets.' if has_code else 'No code snippets detected in the presentation.'
    }

def check_data_visualization(text):
    viz_keywords = ['chart', 'graph', 'plot', 'diagram', 'visualization', 'dashboard']
    has_viz = any(keyword in text.lower() for keyword in viz_keywords)
    return {
        'check': 'Data Visualization',
        'passed': has_viz,
        'message': 'The presentation includes data visualizations.' if has_viz else 'No data visualizations detected in the presentation.'
    }
