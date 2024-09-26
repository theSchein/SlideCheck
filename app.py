import os
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField
from wtforms.validators import DataRequired, URL
from werkzeug.utils import secure_filename
from utils.file_processor import process_file, process_url
from utils.deterministic_checker import run_deterministic_checks
from utils.ai_checker import run_ai_checks

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = '/tmp'

class SlideForm(FlaskForm):
    file = FileField('Upload Slide Deck')
    url = StringField('Or enter URL', validators=[URL()])
    submit = SubmitField('Validate')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SlideForm()
    if form.validate_on_submit():
        try:
            if form.file.data:
                filename = secure_filename(form.file.data.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.file.data.save(filepath)
                slide_data = process_file(filepath)
            elif form.url.data:
                slide_data = process_url(form.url.data)
            else:
                return jsonify({'error': 'No file or URL provided'}), 400

            deterministic_results = run_deterministic_checks(slide_data)
            ai_results = run_ai_checks(slide_data)

            results = deterministic_results + ai_results
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    return render_template('index.html', form=form)

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
