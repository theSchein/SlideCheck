import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Optional
from werkzeug.utils import secure_filename
from utils.file_processor import process_file
from utils.deterministic_checker import run_deterministic_checks
from utils.ai_checker import run_ai_checks
from openai import OpenAI
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from PyPDF2 import PdfMerger
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class Conference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    max_slides = db.Column(db.Integer, nullable=False)
    required_sections = db.Column(db.String(500), nullable=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(200), nullable=True)
    results = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    passed = db.Column(db.Boolean, default=False)
    conference_id = db.Column(db.Integer, db.ForeignKey('conference.id'), nullable=False)
    conference = db.relationship('Conference', backref=db.backref('submissions', lazy=True))

class SlideForm(FlaskForm):
    file = FileField('Upload Slide Deck (PDF, PPTX, ODP)', validators=[Optional()])
    url = StringField('Or enter Canva or Google Slides URL', validators=[Optional(), URL()])
    conference = SelectField('Select Conference', coerce=int, validators=[DataRequired()])
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
        logger.debug(f"Checking admin session: {session.get('admin')}")
        if 'admin' not in session:
            logger.warning("Admin session not found, redirecting to login")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SlideForm()
    form.conference.choices = [(c.id, c.name) for c in Conference.query.all()]
    if request.method == 'POST' and form.validate():
        try:
            logger.debug("Form submitted successfully")
            temp_file_path = None
            filename = None
            url = None
            if form.file.data:
                logger.debug(f"Processing uploaded file: {form.file.data.filename}")
                filename = secure_filename(form.file.data.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.file.data.save(filepath)
                logger.debug(f"File saved: {filepath}")
                
                slide_data = process_file(filepath)
                if 'error' in slide_data:
                    return jsonify({'error': slide_data['error']}), 400
                temp_file_path = slide_data.get('temp_file_path')
            elif form.url.data:
                logger.debug(f"Processing URL: {form.url.data}")
                url = form.url.data
                slide_data = process_file(url)
                if 'error' in slide_data:
                    return jsonify({'error': slide_data['error']}), 400
                temp_file_path = slide_data.get('temp_file_path')
            
            logger.debug("File processing completed")

            conference = Conference.query.get(form.conference.data)
            deterministic_results = run_deterministic_checks(slide_data, conference)
            logger.debug("Deterministic checks completed")
            logger.debug(f"Deterministic check results: {deterministic_results}")
            ai_results = run_ai_checks(slide_data, conference)
            logger.debug("AI checks completed")

            all_results = deterministic_results + ai_results
            passed = all(result['passed'] for result in all_results)

            submission = Submission(filename=filename, url=url, results=all_results, passed=passed, conference_id=conference.id)
            db.session.add(submission)
            db.session.commit()

            response = jsonify({'status': 'Completed', 'results': all_results})
            response.headers['Content-Type'] = 'application/json'
            logger.debug(f"Sending response: {response.get_data(as_text=True)}")

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
    logger.info("Admin logged in successfully")
    return redirect(url_for('dashboard'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/admin/update_config', methods=['POST'])
@admin_required
def update_admin_config():
    checks = request.form.getlist('checks')
    file_types = request.form.getlist('file_types')
    
    logger.info(f"Updated checks: {checks}")
    logger.info(f"Updated file types: {file_types}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/dashboard')
@admin_required
def dashboard():
    try:
        logger.debug("Accessing dashboard route")
        page = request.args.get('page', 1, type=int)
        per_page = 10
        submissions = Submission.query.order_by(Submission.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        total_submissions = Submission.query.count()
        passed_submissions = Submission.query.filter_by(passed=True).count()
        pending_submissions = total_submissions - passed_submissions

        logger.debug(f"Dashboard accessed. Total submissions: {total_submissions}, Passed: {passed_submissions}, Pending: {pending_submissions}")

        return render_template('dashboard.html', 
                               submissions=submissions,
                               total_submissions=total_submissions,
                               passed_submissions=passed_submissions,
                               pending_submissions=pending_submissions)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}", exc_info=True)
        return render_template('error.html', error_message="An error occurred while loading the dashboard. Please try again later."), 500

@app.route('/api/submissions')
@admin_required
def api_submissions():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    filter_type = request.args.get('filter', 'all')

    query = Submission.query

    if filter_type == 'passed':
        query = query.filter_by(passed=True)
    elif filter_type == 'failed':
        query = query.filter_by(passed=False)

    submissions = query.order_by(Submission.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    submissions_data = [{
        'id': s.id,
        'filename': s.filename,
        'url': s.url,
        'timestamp': s.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'passed': s.passed
    } for s in submissions.items]

    return jsonify({
        'submissions': submissions_data,
        'total_pages': submissions.pages,
        'current_page': page
    })

@app.route('/api/submission/<int:submission_id>')
@admin_required
def api_submission_details(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    return jsonify({
        'id': submission.id,
        'filename': submission.filename,
        'url': submission.url,
        'timestamp': submission.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'passed': submission.passed,
        'results': submission.results
    })

@app.route('/download_master_deck')
@admin_required
def download_master_deck():
    passed_submissions = Submission.query.filter_by(passed=True).all()
    merger = PdfMerger()

    for submission in passed_submissions:
        if submission.filename and submission.filename.lower().endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], submission.filename)
            if os.path.exists(file_path):
                merger.append(file_path)

    output = io.BytesIO()
    merger.write(output)
    output.seek(0)
    merger.close()

    return send_file(
        output,
        as_attachment=True,
        download_name='master_deck.pdf',
        mimetype='application/pdf'
    )

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'error': str(e)}), 500

def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if conference_id column exists in submission table
        inspector = db.inspect(db.engine)
        if 'conference_id' not in [c['name'] for c in inspector.get_columns('submission')]:
            # Add conference_id column
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE submission ADD COLUMN conference_id INTEGER'))
                conn.commit()
        
        # Add sample conferences if they don't exist
        if Conference.query.count() == 0:
            sample_conferences = [
                Conference(name="TechCon 2024", max_slides=15, required_sections="Introduction,Methodology,Results,Conclusion"),
                Conference(name="DataSummit 2024", max_slides=20, required_sections="Abstract,Data Analysis,Findings,Future Work"),
            ]
            db.session.add_all(sample_conferences)
            db.session.commit()

# Call init_db() function
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)