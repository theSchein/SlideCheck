import unittest
import os
import sys
from io import StringIO
from unittest.runner import TextTestResult

# Add the parent directory to sys.path to allow imports from the utils folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_processor import (process_file, process_pdf, convert_to_pdf,
                                  convert_keynote_to_pdf, process_markdown,
                                  process_url, process_generic_url,
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

    def test_process_file_pdf(self):
        pdf_path = os.path.join(self.sample_data_dir, "sample.pdf")
        result = process_file(pdf_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'application/pdf',
                         "Type should be 'application/pdf'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")
        self.assertIn('fonts', result, "Result should contain 'fonts'")

    def test_process_file_pptx(self):
        pptx_path = os.path.join(self.sample_data_dir, "sample.pptx")
        result = process_file(pptx_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(
            result['type'],
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            "Type should be 'application/vnd.openxmlformats-officedocument.presentationml.presentation'"
        )
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")
        self.assertIn('video_tracks', result,
                      "Result should contain 'video_tracks'")
        self.assertIn('audio_tracks', result,
                      "Result should contain 'audio_tracks'")

    def test_process_file_markdown(self):
        md_path = os.path.join(self.sample_data_dir, "sample.md")
        result = process_file(md_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'markdown',
                         "Type should be 'markdown'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")

    def test_process_file_keynote(self):
        keynote_path = os.path.join(self.sample_data_dir, "sample.key")
        result = process_file(keynote_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(
            result['type'], 'application/x-iwork-keynote-sffkey',
            "Type should be 'application/x-iwork-keynote-sffkey'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")

    def test_process_file_url(self):
        url = "https://docs.google.com/presentation/d/your_presentation_id/edit"
        result = process_file(url)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn('type', result, "Result should contain 'type'")
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
        result = process_markdown(md_path)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'markdown',
                         "Type should be 'markdown'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")

    def test_process_url(self):
        url = "https://www.figma.com/slides/MmzfmAWwR06geAJ7geK9MJ/project-status-template?node-id=1-284&t=PeJnht7wqhLLHMI4-1"
        result = process_url(url)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn('type', result, "Result should contain 'type'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")

    def test_process_generic_url(self):
        url = "https://www.canva.com/templates/EAF4OFZRD4Y-colourful-playful-class-agenda-education-presentation/"
        result = process_generic_url(url)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'url', "Type should be 'url'")
        self.assertIn('url', result, "Result should contain 'url'")
        self.assertIn('temp_file_path', result,
                      "Result should contain 'temp_file_path'")

    def test_process_google_slides(self):
        url = "https://docs.google.com/presentation/d/1tmpHzm716sAOKtunRpPOhRc0TgCX_Y2-_AnjMmKrY8A/edit?usp=sharing"
        result = process_google_slides(url)
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result['type'], 'google_slides',
                         "Type should be 'google_slides'")
        self.assertIn('num_slides', result,
                      "Result should contain 'num_slides'")
        self.assertIn('content', result, "Result should contain 'content'")


if __name__ == "__main__":
    runner = CustomTextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
