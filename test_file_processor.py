import os
from utils.file_processor import process_file
from docx import Document
import tempfile

def create_sample_docx():
    doc = Document()
    doc.add_heading('Sample DOCX Presentation', 0)
    doc.add_paragraph('This is a sample DOCX file for testing purposes.')
    doc.add_heading('Slide 2', level=1)
    doc.add_paragraph('This is the content of slide 2.')
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
        doc.save(temp_docx.name)
    return temp_docx.name

def create_sample_rtf():
    rtf_content = r'''{\rtf1\ansi\deff0
{\fonttbl {\f0 Times New Roman;}}
{\colortbl;\red0\green0\blue0;}
\f0\fs24\cf1
Sample RTF Presentation\par
\par
This is a sample RTF file for testing purposes.\par
\par
Slide 2\par
\par
This is the content of slide 2.\par
}'''
    with tempfile.NamedTemporaryFile(suffix='.rtf', mode='w', delete=False) as temp_rtf:
        temp_rtf.write(rtf_content)
    return temp_rtf.name

def test_docx_processing():
    docx_file = create_sample_docx()
    result = process_file(docx_file)
    print("DOCX Processing Result:")
    print(f"Number of slides: {result['num_slides']}")
    print(f"Content: {result['content']}")
    os.unlink(docx_file)
    os.unlink(result['temp_file_path'])

def test_rtf_processing():
    rtf_file = create_sample_rtf()
    result = process_file(rtf_file)
    print("RTF Processing Result:")
    print(f"Number of slides: {result['num_slides']}")
    print(f"Content: {result['content']}")
    os.unlink(rtf_file)
    os.unlink(result['temp_file_path'])

if __name__ == "__main__":
    test_docx_processing()
    test_rtf_processing()
