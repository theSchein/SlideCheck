import os
import logging
from flask import Flask, render_template, request, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from utils.file_processor import process_file
from utils.deterministic_checker import run_deterministic_checks
from utils.ai_checker import run_ai_checks

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SlideForm(FlaskForm):
    file = FileField('Upload PDF Slide Deck', validators=[DataRequired()])
    submit = SubmitField('Validate')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SlideForm()
    if request.method == 'POST':
        try:
            logger.debug("Form submitted successfully")
            if form.file.data:
                logger.debug(f"Processing uploaded file: {form.file.data.filename}")
                filename = secure_filename(form.file.data.filename)
                if not filename.lower().endswith('.pdf'):
                    raise ValueError("Only PDF files are accepted.")
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.file.data.save(filepath)
                logger.debug(f"File saved: {filepath}")
                
                # Check if file exists and is readable
                if not os.path.exists(filepath):
                    raise FileNotFoundError(f"File not found: {filepath}")
                if not os.access(filepath, os.R_OK):
                    raise PermissionError(f"File not readable: {filepath}")
                
                file_size = os.path.getsize(filepath)
                logger.debug(f"File size: {file_size} bytes")
                
                slide_data = process_file(filepath)
                logger.debug("File processing completed")
            else:
                logger.warning("No file provided")
                error_response = jsonify({'error': 'No file provided'})
                error_response.headers['Content-Type'] = 'application/json'
                logger.debug(f"Sending error response: {error_response.get_data(as_text=True)}")
                return error_response, 400

            logger.debug("Running deterministic checks")
            deterministic_results = run_deterministic_checks(slide_data)
            logger.debug("Deterministic checks completed")

            logger.debug("Running AI checks")
            ai_results = run_ai_checks(slide_data)
            logger.debug("AI checks completed")

            results = deterministic_results + ai_results
            logger.debug(f"Validation complete. Results: {results}")
            
            response = jsonify(results)
            response.headers['Content-Type'] = 'application/json'
            logger.debug(f"Sending response: {response.get_data(as_text=True)}")
            return response
        except Exception as e:
            logger.error(f"Error during processing: {str(e)}", exc_info=True)
            error_response = jsonify({'error': str(e)})
            error_response.headers['Content-Type'] = 'application/json'
            logger.debug(f"Sending error response: {error_response.get_data(as_text=True)}")
            return error_response, 500

    return render_template('index.html', form=form)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    error_response = jsonify({'error': str(e)})
    error_response.headers['Content-Type'] = 'application/json'
    logger.debug(f"Sending error response: {error_response.get_data(as_text=True)}")
    return error_response, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
