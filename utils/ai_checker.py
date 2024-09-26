import os
import time
import random
import logging
from openai import OpenAI
from openai import APIError, RateLimitError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID")
OPENAI_PROJECT_ID = os.environ.get("OPENAI_PROJECT_ID")

print(f"OPENAI_API_KEY is {'set' if OPENAI_API_KEY else 'not set'}")
print(f"OPENAI_ORG_ID is {'set' if OPENAI_ORG_ID else 'not set'}")
print(f"OPENAI_PROJECT_ID is {'set' if OPENAI_PROJECT_ID else 'not set'}")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is not set. AI checks will be skipped.")
    openai_client = None
else:
    if OPENAI_ORG_ID and OPENAI_PROJECT_ID:
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            organization=OPENAI_ORG_ID,
            project=OPENAI_PROJECT_ID
        )
    elif OPENAI_ORG_ID:
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            organization=OPENAI_ORG_ID
        )
    else:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)

def check_openai_connection():
    prompt = "This is a test connection. Please respond with 'Connected'."
    try:
        response = send_openai_request(prompt, max_retries=3, base_delay=1, max_delay=5)
        print(f"OpenAI API response: {response}")
        print(f"Using organization: {OPENAI_ORG_ID if OPENAI_ORG_ID else 'Default'}")
        print(f"Using project: {OPENAI_PROJECT_ID if OPENAI_PROJECT_ID else 'Default'}")
        return response == "Connected"
    except Exception as e:
        print(f"Error connecting to OpenAI API: {str(e)}")
        return False

def run_ai_checks(slide_data):
    if not openai_client:
        return [{
            'check': 'AI Checks',
            'passed': False,
            'message': 'AI checks were skipped due to missing OpenAI API key.'
        }]

    results = []

    # Check OpenAI connection
    connection_check = {
        'check': 'OpenAI Connection',
        'passed': check_openai_connection(),
        'message': 'Successfully connected to OpenAI API.' if check_openai_connection() else 'Failed to connect to OpenAI API.'
    }
    results.append(connection_check)

    if not connection_check['passed']:
        return results

    # Check for title slide
    title_check = check_title_slide(slide_data)
    results.append(title_check)

    # Add a delay between checks
    time.sleep(2)

    # Check for bullet point density
    bullet_point_check = check_bullet_point_density(slide_data)
    results.append(bullet_point_check)

    return results

def send_openai_request(prompt: str, max_retries=10, base_delay=1, max_delay=120) -> str:
    if not openai_client:
        return "AI check skipped"
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Sending request to OpenAI API (attempt {attempt + 1}/{max_retries})")
            print(f"Using model: gpt-4o-mini")
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=100
            )
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("OpenAI returned an empty response.")
            logger.debug("Successfully received response from OpenAI API")
            return content
        except Exception as e:
            print(f"Error in send_openai_request: {str(e)}")
            if attempt == max_retries - 1:
                raise
            delay = min(max_delay, (base_delay * 2 ** attempt) + random.uniform(0, 0.1 * (2 ** attempt)))
            time.sleep(delay)

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
