# AI Slide Deck Validator

This application validates slide decks using AI and deterministic checks. It supports PDF, PowerPoint (.pptx), LibreOffice Presentation (.odp), Canva, Figma, Google Slides, and Keynote formats.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key

3. Set up Google Slides API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Slides API for your project
   - Create a service account and download the JSON key file
   - Rename the downloaded file to `google_service_account.json` and place it in the root directory of the project

4. Run the application:
   ```
   python app.py
   ```

## Usage

1. Open the application in your web browser.
2. Upload a slide deck file (PDF, PPTX, ODP, or KEY) or provide a Canva, Figma, or Google Slides URL.
3. Click "Validate" to process the slide deck.
4. View the validation results, including both deterministic and AI-powered checks.

## Security Notes

- Always use environment variables for sensitive information like API keys.
- Ensure that the `google_service_account.json` file is stored securely and not exposed to unauthorized users.
- Regularly rotate your API keys and update the corresponding environment variables.

