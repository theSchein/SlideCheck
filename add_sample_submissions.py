from app import app, db, Submission
from datetime import datetime
import json

def add_sample_submissions():
    with app.app_context():
        # Sample submission 1
        submission1 = Submission(
            filename="sample1.pdf",
            url=None,
            results=json.dumps([
                {"check": "File type", "passed": True, "message": "File type is pdf."},
                {"check": "Number of slides", "passed": True, "message": "The deck has 10 slides. Ideal range is 5-15 slides."},
                {"check": "Title Slide", "passed": True, "message": "The deck has a clear title slide."}
            ]),
            timestamp=datetime.utcnow(),
            passed=True
        )

        # Sample submission 2
        submission2 = Submission(
            filename=None,
            url="https://docs.google.com/presentation/d/sample2",
            results=json.dumps([
                {"check": "File type", "passed": True, "message": "File type is Google Slides."},
                {"check": "Number of slides", "passed": False, "message": "The deck has 20 slides. Ideal range is 5-15 slides."},
                {"check": "Title Slide", "passed": True, "message": "The deck has a clear title slide."}
            ]),
            timestamp=datetime.utcnow(),
            passed=False
        )

        # Add submissions to the database
        db.session.add(submission1)
        db.session.add(submission2)
        db.session.commit()

    print("Sample submissions added to the database.")

if __name__ == "__main__":
    add_sample_submissions()
