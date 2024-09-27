import PyPDF2
import re
import json

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
    custom_checks = json.loads(conference.custom_checks) if conference.custom_checks else {}
    
    if custom_checks.get('code_snippets', {}).get('enabled', False):
        results.append(check_code_snippets(all_text, custom_checks['code_snippets']['threshold']))
    
    if custom_checks.get('technical_terminology', {}).get('enabled', False):
        results.append(check_technical_terminology(all_text, custom_checks['technical_terminology']['threshold']))
    
    if custom_checks.get('data_visualization', {}).get('enabled', False):
        results.append(check_data_visualization(all_text, custom_checks['data_visualization']['threshold']))
    
    if custom_checks.get('statistical_terms', {}).get('enabled', False):
        results.append(check_statistical_terms(all_text, custom_checks['statistical_terms']['threshold']))

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

def check_code_snippets(text, threshold):
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
    
    code_snippet_count = sum(1 for pattern in code_patterns if re.search(pattern, text, re.IGNORECASE))
    has_code = code_snippet_count >= threshold
    return {
        'check': 'Code Snippets',
        'passed': has_code,
        'message': f'The presentation contains {code_snippet_count} code snippet(s). Threshold: {threshold}.'
    }

def check_data_visualization(text, threshold):
    viz_keywords = ['chart', 'graph', 'plot', 'diagram', 'visualization', 'dashboard']
    viz_count = sum(1 for keyword in viz_keywords if keyword in text.lower())
    has_viz = viz_count >= threshold
    return {
        'check': 'Data Visualization',
        'passed': has_viz,
        'message': f'The presentation includes {viz_count} data visualization keyword(s). Threshold: {threshold}.'
    }

def check_technical_terminology(text, threshold):
    tech_terms = ['algorithm', 'api', 'database', 'framework', 'machine learning', 'cloud computing', 'blockchain', 'cybersecurity', 'artificial intelligence', 'iot']
    found_terms = [term for term in tech_terms if term in text.lower()]
    has_tech_terms = len(found_terms) >= threshold
    return {
        'check': 'Technical Terminology',
        'passed': has_tech_terms,
        'message': f'The presentation includes {len(found_terms)} technical term(s): {", ".join(found_terms)}. Threshold: {threshold}.'
    }

def check_statistical_terms(text, threshold):
    stat_terms = ['mean', 'median', 'mode', 'standard deviation', 'variance', 'regression', 'correlation', 'p-value', 'confidence interval', 'hypothesis test']
    found_terms = [term for term in stat_terms if term in text.lower()]
    has_stat_terms = len(found_terms) >= threshold
    return {
        'check': 'Statistical Terms',
        'passed': has_stat_terms,
        'message': f'The presentation includes {len(found_terms)} statistical term(s): {", ".join(found_terms)}. Threshold: {threshold}.'
    }