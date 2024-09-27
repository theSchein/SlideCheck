import os
import time
import random
import json
import logging
from openai import OpenAI, OpenAIError, APIError, RateLimitError, AuthenticationError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logger.debug(f"Initializing OpenAI client with API key: {'[REDACTED]' if OPENAI_API_KEY else 'Not set'}")

client = OpenAI(api_key=OPENAI_API_KEY)

def run_ai_checks(slide_data, conference):
    if not OPENAI_API_KEY:
        return [{
            'check': 'AI Checks',
            'passed': False,
            'message': 'AI checks were skipped due to missing OpenAI API key.'
        }]

    results = []

    title_check = check_title_slide(slide_data)
    results.append(title_check)

    time.sleep(2)

    bullet_point_check = check_bullet_point_density(slide_data)
    results.append(bullet_point_check)

    time.sleep(2)

    content_relevance_check = check_content_relevance(slide_data, conference)
    results.append(content_relevance_check)

    return results

def send_openai_request_with_function(prompt: str, max_retries=10, base_delay=1, max_delay=120) -> str:
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key is not set. Skipping AI check.")
        return "AI check skipped"

    function_definition = [
        {
            "name": "provide_binary_answer",
            "description": "Provides a binary answer to a question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "enum": ["Yes", "No"],
                        "description": "The binary answer to the question."
                    }
                },
                "required": ["answer"]
            }
        }
    ]

    for attempt in range(max_retries):
        try:
            logger.debug(f"Sending request to OpenAI API with function calling (attempt {attempt + 1}/{max_retries})")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                functions=function_definition,
                function_call={"name": "provide_binary_answer"},
                max_tokens=50,
            )
            message = response.choices[0].message
            if message.function_call:
                function_args = json.loads(message.function_call.arguments)
                return function_args.get("answer")
            else:
                raise ValueError("Function call not returned by the API.")
        except Exception as e:
            logger.error(f"Error in send_openai_request_with_function: {str(e)}", exc_info=True)
            if attempt == max_retries - 1:
                return f"AI check failed: Unexpected error - {str(e)}"

        delay = min(max_delay, (base_delay * 2 ** attempt) + random.uniform(0, 0.1 * (2 ** attempt)))
        logger.info(f"Retrying in {delay:.2f} seconds...")
        time.sleep(delay)

def check_title_slide(slide_data):
    first_slide_content = slide_data['content'][0] if slide_data['content'] else ""
    prompt = (
        "You are an assistant that determines if a slide is a clear title slide.\n"
        "Analyze the following slide content and answer with 'Yes' or 'No' only.\n\n"
        f"Slide Content:\n{first_slide_content[:1500]}"
    )
    response = send_openai_request_with_function(prompt)

    if response.startswith("AI check failed"):
        return {
            'check': 'Title Slide',
            'passed': False,
            'message': response
        }

    has_title_slide = response.lower() == 'yes'
    return {
        'check': 'Title Slide',
        'passed': has_title_slide,
        'message': 'The deck has a clear title slide.' if has_title_slide else 'No clear title slide detected.'
    }

def check_bullet_point_density(slide_data):
    all_text = ' '.join(slide_data['content'])
    prompt = (
        "You are an assistant that evaluates slide content for bullet point density.\n"
        "Determine if the slides have too many bullet points or are too text-heavy.\n"
        "Each slide should have less than 6 bullet points and less than 500 words.\n"
        "Answer with 'Yes' or 'No' only.\n\n"
        f"Slide Content:\n{all_text[:1500]}"
    )
    response = send_openai_request_with_function(prompt)

    if response.startswith("AI check failed"):
        return {
            'check': 'Bullet Point Density',
            'passed': False,
            'message': response
        }

    is_text_heavy = response.lower() == 'yes'
    return {
        'check': 'Bullet Point Density',
        'passed': not is_text_heavy,
        'message': 'The slides have a good balance of text and visuals.' if not is_text_heavy else 'The slides may be too text-heavy or have too many bullet points.'
    }

def check_content_relevance(slide_data, conference):
    all_text = ' '.join(slide_data['content'])
    prompt = (
        f"You are an assistant that evaluates slide content for relevance to a conference.\n"
        f"The conference name is '{conference.name}'.\n"
        f"Determine if the slide content is relevant to this conference.\n"
        f"Answer with 'Yes' or 'No' only.\n\n"
        f"Slide Content:\n{all_text[:1500]}"
    )
    response = send_openai_request_with_function(prompt)

    if response.startswith("AI check failed"):
        return {
            'check': 'Content Relevance',
            'passed': False,
            'message': response
        }

    is_relevant = response.lower() == 'yes'
    return {
        'check': 'Content Relevance',
        'passed': is_relevant,
        'message': f'The content is relevant to {conference.name}.' if is_relevant else f'The content may not be relevant to {conference.name}.'
    }
