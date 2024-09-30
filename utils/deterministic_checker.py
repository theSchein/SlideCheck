import PyPDF2
import re
import json


def run_deterministic_checks(slide_data, conference):
    results = []

    # Check file type
    file_type = slide_data['type']
    results.append({
        'check': 'File type',
        'passed': file_type == 'pdf',
        'message': f'File type is {file_type}.'
    })

    # Check number of slides
    num_slides = slide_data['num_slides']
    results.append({
        'check':
        'Number of slides',
        'passed':
        num_slides <= conference.max_slides,
        'message':
        f'The deck has {num_slides} slides. Maximum allowed for this conference is {conference.max_slides} slides.'
    })

    # Check for required sections
    required_sections = conference.required_sections.split(
        ',') if conference.required_sections else []
    found_sections = set()
    all_text = ' '.join(slide_data['content']).lower()

    for section in required_sections:
        if section.lower() in all_text:
            found_sections.add(section)

    missing_sections = set(required_sections) - found_sections
    results.append({
        'check':
        'Required sections',
        'passed':
        len(missing_sections) == 0,
        'message':
        'All required sections found.' if len(missing_sections) == 0 else
        f'Missing sections: {", ".join(missing_sections)}'
    })

    # Conference-specific checks
    # custom_checks = json.loads(
    #     conference.custom_checks) if conference.custom_checks else {}

    # if custom_checks.get('code_snippets', {}).get('enabled', False):
    #     results.append(
    #         check_code_snippets(all_text,
    #                             custom_checks['code_snippets']['threshold']))

    # if custom_checks.get('technical_terminology', {}).get('enabled', False):
    #     results.append(
    #         check_technical_terminology(
    #             all_text, custom_checks['technical_terminology']['threshold']))

    # if custom_checks.get('data_visualization', {}).get('enabled', False):
    #     results.append(
    #         check_data_visualization(
    #             all_text, custom_checks['data_visualization']['threshold']))

    # if custom_checks.get('statistical_terms', {}).get('enabled', False):
    #     results.append(
    #         check_statistical_terms(
    #             all_text, custom_checks['statistical_terms']['threshold']))

    # Check font usage
    results.append(check_font_usage(slide_data, conference))

    return results



# def check_code_snippets(text, threshold):
#     code_patterns = [
#         r'\bdef\s+\w+\s*\(.*\):',  # Python function definition
#         r'\bclass\s+\w+:',  # Python class definition
#         r'\bif\s+.*:',  # Python if statement
#         r'\bfor\s+.*:',  # Python for loop
#         r'\bwhile\s+.*:',  # Python while loop
#         r'\bfunction\s+\w+\s*\(.*\)\s*{',  # JavaScript function
#         r'\bconst\s+\w+\s*=',  # JavaScript const declaration
#         r'\blet\s+\w+\s*=',  # JavaScript let declaration
#         r'\bvar\s+\w+\s*=',  # JavaScript var declaration
#     ]

#     code_snippet_count = sum(1 for pattern in code_patterns
#                              if re.search(pattern, text, re.IGNORECASE))
#     has_code = code_snippet_count >= threshold
#     return {
#         'check':
#         'Code Snippets',
#         'passed':
#         has_code,
#         'message':
#         f'The presentation contains {code_snippet_count} code snippet(s). Threshold: {threshold}.'
#     }


# def check_technical_terminology(text, threshold):
#     tech_terms = [
#         'algorithm', 'api', 'database', 'framework', 'machine learning',
#         'cloud computing', 'blockchain', 'cybersecurity',
#         'artificial intelligence', 'iot'
#     ]
#     found_terms = [term for term in tech_terms if term in text.lower()]
#     has_tech_terms = len(found_terms) >= threshold
#     return {
#         'check':
#         'Technical Terminology',
#         'passed':
#         has_tech_terms,
#         'message':
#         f'The presentation includes {len(found_terms)} technical term(s): {", ".join(found_terms)}. Threshold: {threshold}.'
#     }


# def check_statistical_terms(text, threshold):
#     stat_terms = [
#         'mean', 'median', 'mode', 'standard deviation', 'variance',
#         'regression', 'correlation', 'p-value', 'confidence interval',
#         'hypothesis test'
#     ]
#     found_terms = [term for term in stat_terms if term in text.lower()]
#     has_stat_terms = len(found_terms) >= threshold
#     return {
#         'check':
#         'Statistical Terms',
#         'passed':
#         has_stat_terms,
#         'message':
#         f'The presentation includes {len(found_terms)} statistical term(s): {", ".join(found_terms)}. Threshold: {threshold}.'
#     }


def check_font_usage(slide_data, conference):
    file_type = slide_data['type']

    if file_type == 'pdf' and 'fonts' in slide_data:
        fonts_used = slide_data['fonts']
        allowed_fonts = conference.allowed_fonts.split(',') if conference.allowed_fonts and conference.allowed_fonts != '*' else []

        if not allowed_fonts or conference.allowed_fonts == '*':
            return {
                'check':
                'Font usage',
                'passed':
                True,
                'message':
                f'Fonts used: {", ".join(fonts_used)}. All fonts are allowed for this conference.'
            }

        disallowed_fonts = [
            font for font in fonts_used if font not in allowed_fonts
        ]

        if disallowed_fonts:
            return {
                'check':
                'Font usage',
                'passed':
                False,
                'message':
                f'Disallowed fonts used: {", ".join(disallowed_fonts)}. Allowed fonts: {", ".join(allowed_fonts)}'
            }
        else:
            return {
                'check': 'Font usage',
                'passed': True,
                'message':
                f'All fonts used are allowed: {", ".join(fonts_used)}'
            }
    else:
        return {
            'check': 'Font usage',
            'passed': True,
            'message': 'Font check not applicable for this file type.'
        }

