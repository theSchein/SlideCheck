import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_processor import (
    process_file,
    process_pdf,
    convert_to_pdf,
    convert_rtf_to_pdf,
    convert_docx_to_pdf,
    convert_keynote_to_pdf,
    process_markdown,
    process_url,
    process_generic_url,
    process_google_slides
)

class TestSlideshowChecker(unittest.TestCase):
    
    def setUp(self):
        # Set up the path to the sample_data folder within the tests directory
        self.sample_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")

    def test_process_file_pdf(self):
        pdf_path = os.path.join(self.sample_data_dir, "sample.pdf")
        result = process_file(pdf_path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'application/pdf')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)
        self.assertIn('fonts', result)

    def test_process_file_pptx(self):
        pptx_path = os.path.join(self.sample_data_dir, "sample.pptx")
        result = process_file(pptx_path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)
        self.assertIn('video_tracks', result)
        self.assertIn('audio_tracks', result)

    def test_process_file_markdown(self):
        md_path = os.path.join(self.sample_data_dir, "sample.md")
        result = process_file(md_path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'markdown')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)

    def test_process_file_rtf(self):
        rtf_path = os.path.join(self.sample_data_dir, "sample.rtf")
        result = process_file(rtf_path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'application/rtf')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)

    def test_process_file_docx(self):
        docx_path = os.path.join(self.sample_data_dir, "sample.docx")
        result = process_file(docx_path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)

    def test_process_file_keynote(self):
        keynote_path = os.path.join(self.sample_data_dir, "sample.key")
        result = process_file(keynote_path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'application/x-iwork-keynote-sffkey')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)

    def test_process_file_url(self):
        url = "https://docs.google.com/presentation/d/your_presentation_id/edit"
        result = process_file(url)
        self.assertIsInstance(result, dict)
        self.assertIn('type', result)
        self.assertIn('num_slides', result)
        self.assertIn('content', result)

    def test_process_pdf(self):
        pdf_path = os.path.join(self.sample_data_dir, "sample.pdf")
        result = process_pdf(pdf_path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'pdf')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)
        self.assertIn('fonts', result)

    def test_convert_to_pdf(self):
        pptx_path = os.path.join(self.sample_data_dir, "sample.pptx")
        pdf_path, video_tracks, audio_tracks = convert_to_pdf(pptx_path)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertIsInstance(video_tracks, list)
        self.assertIsInstance(audio_tracks, list)

    def test_convert_rtf_to_pdf(self):
        rtf_path = os.path.join(self.sample_data_dir, "sample.rtf")
        pdf_path = convert_rtf_to_pdf(rtf_path)
        self.assertTrue(os.path.exists(pdf_path))

    def test_convert_docx_to_pdf(self):
        docx_path = os.path.join(self.sample_data_dir, "sample.docx")
        pdf_path = convert_docx_to_pdf(docx_path)
        self.assertTrue(os.path.exists(pdf_path))

    def test_convert_keynote_to_pdf(self):
        keynote_path = os.path.join(self.sample_data_dir, "sample.key")
        pdf_path = convert_keynote_to_pdf(keynote_path)
        self.assertTrue(os.path.exists(pdf_path))

    def test_process_markdown(self):
        md_path = os.path.join(self.sample_data_dir, "sample.md")
        result = process_markdown(md_path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'markdown')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)

    def test_process_url(self):
        url = "https://docs.google.com/presentation/d/your_presentation_id/edit"
        result = process_url(url)
        self.assertIsInstance(result, dict)
        self.assertIn('type', result)
        self.assertIn('num_slides', result)
        self.assertIn('content', result)

    def test_process_generic_url(self):
        url = "https://example.com"
        result = process_generic_url(url)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'url')
        self.assertIn('url', result)
        self.assertIn('temp_file_path', result)

    def test_process_google_slides(self):
        url = "https://docs.google.com/presentation/d/your_presentation_id/edit"
        result = process_google_slides(url)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['type'], 'google_slides')
        self.assertIn('num_slides', result)
        self.assertIn('content', result)

if __name__ == "__main__":
    unittest.main()