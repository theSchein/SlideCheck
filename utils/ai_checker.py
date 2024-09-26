import os
import time
import random
import logging
from openai import OpenAI, OpenAIError, APIError, RateLimitError, AuthenticationError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logger.debug(f"Initializing OpenAI client with API key: {'[REDACTED]' if OPENAI_API_KEY else 'Not set'}")

client = OpenAI(api_key=OPENAI_API_KEY)

def check_openai_connection():
    prompt = "This is a test connection. Please respond with 'Connected'."
    try:
        logger.debug("Attempting to connect to OpenAI API...")
        response = send_openai_request(prompt, max_retries=3, base_delay=1, max_delay=5)
        logger.debug(f"OpenAI API response: {response}")
        return response.strip() == "Connected"
    except Exception as e:
        logger.error(f"Error connecting to OpenAI API: {str(e)}", exc_info=True)
        return False

def run_ai_checks(slide_data):
    if not OPENAI_API_KEY:
        return [{
            'check': 'AI Checks',
            'passed': False,
            'message': 'AI checks were skipped due to missing OpenAI API key.'
        }]

    results = []

    connection_passed = check_openai_connection()
    connection_check = {
        'check': 'OpenAI Connection',
        'passed': connection_passed,
        'message': 'Successfully connected to OpenAI API.' if connection_passed else 'Failed to connect to OpenAI API.'
    }
    results.append(connection_check)

    if not connection_passed:
        return results

    title_check = check_title_slide(slide_data)
    results.append(title_check)

    time.sleep(2)

    bullet_point_check = check_bullet_point_density(slide_data)
    results.append(bullet_point_check)

    return results

def send_openai_request(prompt: str, max_retries=10, base_delay=1, max_delay=120) -> str:
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key is not set. Skipping AI check.")
        return "AI check skipped"

    for attempt in range(max_retries):
        try:
            logger.debug(f"Sending request to OpenAI API (attempt {attempt + 1}/{max_retries})")
            logger.debug(f"Using model: gpt-4o-mini")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("OpenAI returned an empty response.")
            logger.debug("Successfully received response from OpenAI API")
            return content
        except AuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            return "AI check failed: Invalid API key or token."
        except RateLimitError as e:
            logger.error(f"Rate limit error: {str(e)}")
            if attempt == max_retries - 1:
                return "AI check failed: Rate limit exceeded. Please try again later."
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            if attempt == max_retries - 1:
                return f"AI check failed: OpenAI API error - {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in send_openai_request: {str(e)}", exc_info=True)
            if attempt == max_retries - 1:
                return f"AI check failed: Unexpected error - {str(e)}"

        delay = min(max_delay, (base_delay * 2 ** attempt) + random.uniform(0, 0.1 * (2 ** attempt)))
        logger.info(f"Retrying in {delay:.2f} seconds...")
        time.sleep(delay)

def check_title_slide(slide_data):
    first_slide_content = slide_data['content'][0] if slide_data['content'] else ""
    prompt = f"Is the following slide content a clear title slide? Answer 'Yes' or 'No'.\n\n{first_slide_content[:500]}"
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
    prompt = f"Does the following slide content have too many bullet points or is it too text-heavy? Answer 'Yes' or 'No'.\n\n{all_text[:1000]}"
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
