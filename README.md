# AI Slide Deck Validator

This application validates slide decks using AI and deterministic checks. It supports PDF, PowerPoint (.pptx), LibreOffice Presentation (.odp), Canva, and Google Slides formats.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GOOGLE_CREDENTIALS_PATH`: Path to your Google Slides API credentials file

3. Run the application:
   ```
   python app.py
   ```

## Google Slides API Setup

To use the Google Slides API integration, follow these steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the Google Slides API for your project.
4. Create credentials (OAuth 2.0 Client ID) for a Desktop application.
5. Download the credentials JSON file.
6. Rename the downloaded file to `google_credentials.json` and place it in a secure location.
7. Set the `GOOGLE_CREDENTIALS_PATH` environment variable to the full path of the `google_credentials.json` file.

Example:
```
export GOOGLE_CREDENTIALS_PATH="/path/to/google_credentials.json"
```

Make sure to keep your credentials file secure and never commit it to version control.

## Usage

1. Open the application in your web browser.
2. Upload a slide deck file (PDF, PPTX, or ODP) or provide a Canva or Google Slides URL.
3. Click "Validate" to process the slide deck.
4. View the validation results, including both deterministic and AI-powered checks.

## Security Notes

- Always use environment variables for sensitive information like API keys and credential file paths.
- Ensure that the `google_credentials.json` file is stored securely and not exposed to unauthorized users.
- Regularly rotate your API keys and update the corresponding environment variables.

