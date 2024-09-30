import unittest
import os
import sys
import json

# Add the parent directory to sys.path to allow imports from the utils folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_processor import process_file, process_url
from utils.deterministic_checker import run_deterministic_checks

class Conference:
    def __init__(self, max_slides, required_sections, allowed_fonts):
        self.max_slides = max_slides
        self.required_sections = required_sections
        self.allowed_fonts = allowed_fonts

class TestDeterministicChecks(unittest.TestCase):
    def setUp(self):
        self.sample_data_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sample_data")
        self.processed_data_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "processed_data")
        if not os.path.exists(self.processed_data_dir):
            os.makedirs(self.processed_data_dir)

        self.conference = Conference(
            max_slides=30,
            required_sections="Introduction,Methods,Results,Conclusion",
            allowed_fonts="Arial,Helvetica,Times New Roman"
        )

        self.convert_samples_to_pdf()

    def convert_samples_to_pdf(self):
        for filename in os.listdir(self.sample_data_dir):
            if filename.endswith(('.pdf', '.pptx', '.key', '.md')):
                file_path = os.path.join(self.sample_data_dir, filename)
                result = process_file(file_path)
                output_name = f"processed_{os.path.splitext(filename)[0]}.json"
                self.save_processed_data(output_name, result)

        urls_file = os.path.join(self.sample_data_dir, "slideshowURLs.txt")
        if os.path.exists(urls_file):
            with open(urls_file, 'r') as f:
                urls = [line.strip() for line in f.readlines()]
            for i, url in enumerate(urls):
                result = process_url(url)
                output_name = f"processed_url_{i+1}.json"
                self.save_processed_data(output_name, result)

    def save_processed_data(self, file_name, data):
        output_file = os.path.join(self.processed_data_dir, file_name)
        with open(output_file, 'w') as f:
            json.dump(data, f)

    def load_processed_data(self, file_name):
        file_path = os.path.join(self.processed_data_dir, file_name)
        with open(file_path, 'r') as f:
            return json.load(f)

    def test_deterministic_checks(self):
        for filename in os.listdir(self.processed_data_dir):
            if filename.endswith('.json'):
                slide_data = self.load_processed_data(filename)

                print(f"Processing {filename}:")
                print(json.dumps(slide_data, indent=2))

                results = run_deterministic_checks(slide_data, self.conference)

                self.assertIsInstance(results, list)
                self.assertEqual(len(results), 4)  # Expecting 4 checks

                # Check if all required checks are present
                check_names = [result['check'] for result in results]
                required_checks = ['File type', 'Number of slides', 'Required sections', 'Font usage']
                self.assertEqual(set(check_names), set(required_checks))

                # Add more specific assertions here based on the expected results
                for result in results:
                    self.assertIn('check', result)
                    self.assertIn('passed', result)
                    self.assertIn('message', result)

                print(f"Results for {filename}:")
                print(json.dumps(results, indent=2))
                print("\n")

if __name__ == "__main__":
    unittest.main()