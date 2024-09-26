import os
import time
import random
from openai import OpenAI
from openai import APIError, RateLimitError

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

    # Add a small delay between checks
    time.sleep(1)

    # Check for bullet point density
    bullet_point_check = check_bullet_point_density(slide_data)
    results.append(bullet_point_check)

    return results

def send_openai_request(prompt: str, max_retries=5, base_delay=1, max_delay=60) -> str:
    if not openai_client:
        return "AI check skipped"
    
    for attempt in range(max_retries):
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=100
            )
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("OpenAI returned an empty response.")
            return content
        except RateLimitError:
            if attempt == max_retries - 1:
                return "AI check failed: Rate limit exceeded. Please try again later."
            delay = min(max_delay, (base_delay * 2 ** attempt) + random.uniform(0, 0.1 * (2 ** attempt)))
            time.sleep(delay)
        except APIError as e:
            return f"AI check failed: OpenAI API error - {str(e)}"
        except Exception as e:
            return f"AI check failed: Unexpected error - {str(e)}"

def check_title_slide(slide_data):
    first_slide_content = slide_data['content'][0] if slide_data['content'] else ""
    prompt = f"Analyze this slide content and determine if it's a clear title slide: {first_slide_content[:500]}"
    response = send_openai_request(prompt)
    
    if response.startswith("AI check failed"):
        return {
            'check': 'Title Slide',
            'passed': False,
            'message': response
        }
    
    has_title_slide = 'yes' in response.lower()
    return {
        'check': 'Title Slide',
        'passed': has_title_slide,
        'message': 'The deck has a clear title slide.' if has_title_slide else 'No clear title slide detected.'
    }

def check_bullet_point_density(slide_data):
    all_text = ' '.join(slide_data['content'])
    prompt = f"Analyze this slide content and determine if it has too many bullet points or is too text-heavy: {all_text[:1000]}"
    response = send_openai_request(prompt)
    
    if response.startswith("AI check failed"):
        return {
            'check': 'Bullet Point Density',
            'passed': False,
            'message': response
        }
    
    is_text_heavy = 'yes' in response.lower()
    return {
        'check': 'Bullet Point Density',
        'passed': not is_text_heavy,
        'message': 'The slides have a good balance of text and visuals.' if not is_text_heavy else 'The slides may be too text-heavy or have too many bullet points.'
    }
