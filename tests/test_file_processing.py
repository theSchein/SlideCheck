import unittest
import os
import sys
from io import StringIO
from unittest.runner import TextTestResult

# Add the parent directory to sys.path to allow imports from the utils folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_processor import (process_file, process_pdf, convert_to_pdf,
                                  convert_keynote_to_pdf,
                                  convert_markdown_to_pdf, process_url,
                                  process_figma, process_canva,
                                  process_google_slides)


class CustomTestResult(TextTestResult):

    def __init__(self, stream, descriptions, verbosity):
        super(CustomTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.successes = []

    def addSuccess(self, test):
        super(CustomTestResult, self).addSuccess(test)
        self.successes.append(test)

    def printErrors(self):
        self.stream.writeln("\nTest Results:")
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)
        self.stream.writeln(f"\nSuccesses ({len(self.successes)}):")
        for test in self.successes:
            self.stream.writeln(f"  {test.id()}")


class CustomTextTestRunner(unittest.TextTestRunner):

    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1):
        super(CustomTextTestRunner, self).__init__(stream, descriptions,
                                                   verbosity)

    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)


class TestSlideshowChecker(unittest.TestCase):

    def setUp(self):
        self.sample_data_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sample_data")
        self.urls_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sample_data/slideshowURLs.txt")
        with open(self.urls_file, 'r') as f:
            self.urls = [line.strip() for line in f.readlines()]

    def save_processed_data(self, file_name, data):
        output_file = os.path.join(self.processed_data_dir,
                                   f"{file_name}.json")
        with open(output_file, 'w') as f:
            json.dump(data, f)

    def test_process_file_pdf(self):
        pdf_path = os.path.join(self.sample_data_dir, "sample.pdf")
        result = process_file(pdf_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'application/pdf',
                         "Type should be 'application/pdf'")
        self.assertEqual(result['original_type'], 'application/pdf',
                         "Original type should be 'application/pdf'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")
        self.assertIn('fonts', result, "Result should contain 'fonts'")

    def test_process_file_pptx(self):
        pptx_path = os.path.join(self.sample_data_dir, "sample.pptx")
        result = process_file(pptx_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'application/pdf',
                         "Type should be 'application/pdf'")
        self.assertEqual(
            result['original_type'],
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            "Original type should be 'application/vnd.openxmlformats-officedocument.presentationml.presentation'"
        )
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")
        self.assertIn('video_tracks', result,
                      "Result should contain 'video_tracks'")
        self.assertIn('audio_tracks', result,
                      "Result should contain 'audio_tracks'")

    def test_process_markdown(self):
        md_path = os.path.join(self.sample_data_dir, "sample.md")
        result = process_file(md_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'application/pdf',
                         "Type should be 'application/pdf'")
        self.assertEqual(result['original_type'], 'markdown',
                         "Original type should be 'markdown'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")
        self.assertIn('temp_file_path', result,
                      "Result should contain 'temp_file_path'")

    def test_process_file_keynote(self):
        keynote_path = os.path.join(self.sample_data_dir, "sample.key")
        result = process_file(keynote_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'application/pdf',
                         "Type should be 'application/pdf'")
        self.assertEqual(
            result['original_type'], 'application/x-iwork-keynote-sffkey',
            "Original type should be 'application/x-iwork-keynote-sffkey'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")

    def test_process_pdf(self):
        pdf_path = os.path.join(self.sample_data_dir, "sample.pdf")
        result = process_pdf(pdf_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'pdf', "Type should be 'pdf'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")
        self.assertIn('fonts', result, "Result should contain 'fonts'")

    def test_convert_to_pdf(self):
        pptx_path = os.path.join(self.sample_data_dir, "sample.pptx")
        pdf_path, video_tracks, audio_tracks = convert_to_pdf(pptx_path)
        self.assertTrue(os.path.exists(pdf_path), "PDF file should be created")
        self.assertIsInstance(video_tracks, list,
                              "video_tracks should be a list")
        self.assertIsInstance(audio_tracks, list,
                              "audio_tracks should be a list")

    def test_convert_keynote_to_pdf(self):
        keynote_path = os.path.join(self.sample_data_dir, "sample.key")
        pdf_path = convert_keynote_to_pdf(keynote_path)
        self.assertTrue(os.path.exists(pdf_path), "PDF file should be created")

    def test_process_markdown(self):
        md_path = os.path.join(self.sample_data_dir, "sample.md")
        result = convert_markdown_to_pdf(md_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'markdown',
                         "Type should be 'markdown'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")
        self.assertIn('temp_file_path', result,
                      "Result should contain 'temp_file_path'")

    def test_process_url(self):
        for url in self.urls:
            result = process_url(url)
            self.assertIsInstance(result, dict,
                                  "Result should be a dictionary")
            self.assertEqual(result['type'], 'application/pdf',
                             "Type should be 'application/pdf'")
            self.assertIn('original_type', result,
                          "Result should contain 'original_type'")
            self.assertIn('url', result, "Result should contain 'url'")
            self.assertIn('temp_file_path', result,
                          "Result should contain 'temp_file_path'")
            self.assertIn('num_slides', result,
                          "Result should contain 'num_slides'")
            self.assertIn('content', result, "Result should contain 'content'")

    def test_process_figma(self):
        figma_url = next(url for url in self.urls if 'figma.com' in url)
        result = process_figma(figma_url)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'application/pdf',
                         "Type should be 'application/pdf'")
        self.assertEqual(result['original_type'], 'figma',
                         "Original type should be 'figma'")
        self.assertIn('url', result, "Result should contain 'url'")
        self.assertIn('temp_file_path', result,
                      "Result should contain 'temp_file_path'")

    def test_process_canva(self):
        canva_url = next(url for url in self.urls if 'canva.com' in url)
        result = process_canva(canva_url)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'application/pdf',
                         "Type should be 'application/pdf'")
        self.assertEqual(result['original_type'], 'canva',
                         "Original type should be 'canva'")
        self.assertIn('url', result, "Result should contain 'url'")
        self.assertIn('temp_file_path', result,
                      "Result should contain 'temp_file_path'")

    def test_process_google_slides(self):
        google_slides_url = next(url for url in self.urls
                                 if 'docs.google.com' in url)
        result = process_google_slides(google_slides_url)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'application/pdf',
                         "Type should be 'application/pdf'")
        self.assertEqual(result['original_type'], 'google_slides',
                         "Original type should be 'google_slides'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")
        self.assertIn('url', result, "Result should contain 'url'")
        self.assertIn('temp_file_path', result,
                      "Result should contain 'temp_file_path'")


if __name__ == "__main__":
    runner = CustomTextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
