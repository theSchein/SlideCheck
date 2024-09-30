import os
import time
import random
import json
import logging
import base64
import io
from PIL import Image
import fitz  # PyMuPDF
from openai import OpenAI, OpenAIError, APIError, RateLimitError, AuthenticationError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logger.debug(
    f"Initializing OpenAI client with API key: {'[REDACTED]' if OPENAI_API_KEY else 'Not set'}"
)

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

    time.sleep(2)

    media_check = check_media_content(slide_data)
    results.append(media_check)

    time.sleep(2)

    audio_in_video_check = check_audio_in_video(slide_data)
    results.append(audio_in_video_check)

    return results

def send_openai_request_with_function(prompt: str,
                                      images=None,
                                      max_retries=10,
                                      base_delay=1,
                                      max_delay=120) -> str:
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key is not set. Skipping AI check.")
        return "AI check skipped"

    for attempt in range(max_retries):
        try:
            logger.debug(
                f"Sending request to OpenAI API {'for media detection' if images else 'with function calling'} (attempt {attempt + 1}/{max_retries})"
            )

            messages = [{"role": "user", "content": prompt}]
            if images:
                messages[0]["content"] = [{
                    "type": "text",
                    "text": prompt
                }, *[{
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img}"
                    }
                } for img in images]]

            response = client.chat.completions.create(
                model="gpt-4o" if images else "gpt-4",
                messages=messages,
                max_tokens=300,
            )
            message = response.choices[0].message
            return message.content
        except Exception as e:
            logger.error(
                f"Error in send_openai_request_with_function: {str(e)}",
                exc_info=True)
            if attempt == max_retries - 1:
                return f"AI check failed: Unexpected error - {str(e)}"

        delay = min(max_delay, (base_delay * 2**attempt) +
                    random.uniform(0, 0.1 * (2**attempt)))
        logger.info(f"Retrying in {delay:.2f} seconds...")
        time.sleep(delay)

def check_title_slide(slide_data):
    first_slide_content = slide_data['content'][0] if slide_data['content'] else ""
    prompt = (
        "You are an assistant that determines if a slide is a clear title slide.\n"
        "Analyze the following slide content and answer with 'Yes' or 'No' only.\n\n"
        f"Slide Content:\n{first_slide_content[:1500]}")
    response = send_openai_request_with_function(prompt)

    if response.startswith("AI check failed"):
        return {'check': 'Title Slide', 'passed': False, 'message': response}

    has_title_slide = response.lower().strip() == 'yes'
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
        f"Slide Content:\n{all_text[:1500]}")
    response = send_openai_request_with_function(prompt)

    if response.startswith("AI check failed"):
        return {
            'check': 'Bullet Point Density',
            'passed': False,
            'message': response
        }

    is_text_heavy = response.lower().strip() == 'yes'
    return {
        'check': 'Bullet Point Density',
        'passed': not is_text_heavy,
        'message': 'The slides have a good balance of text and visuals.'
        if not is_text_heavy else
        'The slides may be too text-heavy or have too many bullet points.'
    }

def check_content_relevance(slide_data, conference):
    all_text = ' '.join(slide_data['content'])
    prompt = (
        f"You are an assistant that evaluates slide content for relevance to a conference.\n"
        f"The conference name is '{conference.name}'.\n"
        f"Determine if the slide content is relevant to this conference.\n"
        f"Answer with 'Yes' or 'No' only.\n\n"
        f"Slide Content:\n{all_text[:1500]}")
    response = send_openai_request_with_function(prompt)

    if response.startswith("AI check failed"):
        return {
            'check': 'Content Relevance',
            'passed': False,
            'message': response
        }

    is_relevant = response.lower().strip() == 'yes'
    return {
        'check': 'Content Relevance',
        'passed': is_relevant,
        'message': f'The content is relevant to {conference.name}.' if is_relevant else
        f'The content may not be relevant to {conference.name}.'
    }

def check_media_content(slide_data):
    pdf_path = slide_data.get('temp_file_path')
    if not pdf_path:
        return {
            'check': 'Media Content',
            'passed': False,
            'message': 'Unable to perform media content check: PDF path not found.'
        }

    images = extract_images_from_pdf(pdf_path)
    if not images:
        return {
            'check': 'Media Content',
            'passed': False,
            'message': 'No images found in the PDF for analysis.'
        }

    prompt = prepare_media_detection_prompt()
    response = send_openai_request_with_function(prompt, images=images[:3])

    if response.startswith("AI check failed"):
        return {'check': 'Media Content', 'passed': False, 'message': response}

    has_images = 'image' in response.lower() or 'chart' in response.lower() or 'graph' in response.lower()
    has_videos = 'video' in response.lower() or 'motion' in response.lower() or 'play button' in response.lower()

    message = []
    if has_images:
        message.append("Images detected")
    if has_videos:
        message.append("Video content detected")
    if not has_images and not has_videos:
        message.append("No images or videos detected")

    return {
        'check': 'Media Content',
        'passed': has_images or has_videos,
        'message': '. '.join(message) + '.'
    }

def extract_images_from_pdf(pdf_path):
    images = []
    doc = fitz.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        with io.BytesIO() as output:
            img.save(output, format="PNG")
            images.append(base64.b64encode(output.getvalue()).decode('utf-8'))
    doc.close()
    return images

def prepare_media_detection_prompt():
    return (
        "You are an AI assistant specialized in analyzing images from presentations. "
        "Your task is to determine if the provided images contain static content (like regular images or charts) "
        "or if they appear to be frames from a video.\n\n"
        "Here are some key points to consider:\n"
        "1. Look for play buttons, video controls, or timeline indicators that suggest video content.\n"
        "2. Check for sequential images that might represent video frames.\n"
        "3. Identify any motion blur or action shots that are typical in video stills.\n"
        "4. Recognize standard presentation elements like charts, graphs, or static images.\n\n"
        "After analyzing the images, describe what you see, mentioning specifically if you detect static images, "
        "charts, graphs, or any indicators of video content.\n\n"
        "Here are the images for your analysis:\n")


def check_audio_in_video(slide_data):
    if slide_data.get('video_tracks') and slide_data.get('audio_tracks'):
        prompt = (
            "Based on the following information about a presentation, determine if there is audio associated with the videos:\n"
            f"Video tracks: {slide_data['video_tracks']}\n"
            f"Audio tracks: {slide_data['audio_tracks']}\n"
            "Answer with 'Yes' if there is likely audio associated with the videos, or 'No' if it's unclear or unlikely."
        )
        response = send_openai_request_with_function(prompt)

        if response.startswith("AI check failed"):
            return {'check': 'Audio in Video', 'passed': False, 'message': response}

        has_audio = response.lower().strip() == 'yes'
        return {
            'check': 'Audio in Video',
            'passed': has_audio,
            'message': 'The video likely has associated audio.' if has_audio else 'It\'s unclear or unlikely that the video has associated audio.'
        }
    else:
        return {
            'check': 'Audio in Video',
            'passed': False,
            'message': 'No video or audio tracks detected in the presentation.'
        }