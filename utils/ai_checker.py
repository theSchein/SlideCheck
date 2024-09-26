import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY is not set. AI checks will be skipped.")
    openai_client = None
else:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

def run_ai_checks(slide_data):
    if not openai_client:
        return [{
            'check': 'AI Checks',
            'passed': False,
            'message': 'AI checks were skipped due to missing OpenAI API key.'
        }]

    results = []

    # Check for title slide
    title_check = check_title_slide(slide_data)
    results.append(title_check)

    return results

def send_openai_request(prompt: str) -> str:
    if not openai_client:
        return "AI check skipped"
    
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=100
    )
    content = completion.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response.")
    return content

def check_title_slide(slide_data):
    first_slide_content = slide_data['content'][0] if slide_data['content'] else ""
    prompt = f"Analyze this slide content and determine if it's a clear title slide: {first_slide_content[:500]}"
    response = send_openai_request(prompt)
    has_title_slide = 'yes' in response.lower()
    return {
        'check': 'Title Slide',
        'passed': has_title_slide,
        'message': 'The deck has a clear title slide.' if has_title_slide else 'No clear title slide detected.'
    }
