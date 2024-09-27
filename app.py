import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField
from wtforms.validators import DataRequired, URL, Optional
from werkzeug.utils import secure_filename
from utils.file_processor import process_file
from utils.deterministic_checker import run_deterministic_checks
from utils.ai_checker import run_ai_checks
from openai import OpenAI
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class SlideForm(FlaskForm):
    file = FileField('Upload Slide Deck (PDF, PPTX, ODP)', validators=[Optional()])
    url = StringField('Or enter Canva or Google Slides URL', validators=[Optional(), URL()])
    submit = SubmitField('Validate')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if not self.file.data and not self.url.data:
            self.file.errors.append('Please either upload a file or provide a URL.')
            self.url.errors.append('Please either upload a file or provide a URL.')
            return False
        return True

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SlideForm()
    if request.method == 'POST' and form.validate():
        try:
            logger.debug("Form submitted successfully")
            temp_file_path = None
            if form.file.data:
                logger.debug(f"Processing uploaded file: {form.file.data.filename}")
                filename = secure_filename(form.file.data.filename)
                allowed_extensions = {'pdf', 'pptx', 'odp'}
                file_extension = filename.rsplit('.', 1)[1].lower()
                if file_extension not in allowed_extensions:
                    raise ValueError(f"Unsupported file type: .{file_extension}. Supported types are PDF, PowerPoint (.pptx), and LibreOffice Presentation (.odp).")
                
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
                temp_file_path = slide_data.get('temp_file_path')
            elif form.url.data:
                logger.debug(f"Processing URL: {form.url.data}")
                slide_data = process_file(form.url.data)
                temp_file_path = slide_data.get('temp_file_path')
            
            logger.debug("File processing completed")

            deterministic_results = run_deterministic_checks(slide_data)
            logger.debug("Deterministic checks completed")
            ai_results = run_ai_checks(slide_data)
            logger.debug("AI checks completed")

            all_results = deterministic_results + ai_results
            response = jsonify({'status': 'Completed', 'results': all_results})
            response.headers['Content-Type'] = 'application/json'
            logger.debug(f"Sending response: {response.get_data(as_text=True)}")

            # Clean up temporary file if it exists
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug(f"Temporary file removed: {temp_file_path}")

            return response

        except Exception as e:
            logger.error(f"Error during processing: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    return render_template('index.html', form=form)

@app.route('/admin/login')
def admin_login():
    # Placeholder for now, we'll implement proper login later
    session['admin'] = True
    return redirect(url_for('admin_dashboard'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
