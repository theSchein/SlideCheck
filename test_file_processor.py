import os
from utils.file_processor import process_file
import tempfile
from odf.opendocument import OpenDocumentPresentation
from odf.style import Style, TextProperties, ParagraphProperties
from odf.draw import Page, Frame, TextBox
from odf.text import P

def create_sample_odp():
    doc = OpenDocumentPresentation()
    
    # Create a style for the text
    textstyle = Style(name="Standard", family="paragraph")
    textstyle.addElement(TextProperties(fontsize="24pt", fontweight="bold"))
    doc.styles.addElement(textstyle)

    # Create a page
    page = Page()
    
    # Add a text box to the page
    frame = Frame(width="500pt", height="100pt", x="50pt", y="50pt")
    textbox = TextBox()
    
    # Add text to the text box
    p = P(stylename=textstyle)
    p.addText("Sample ODP Presentation")
    textbox.addElement(p)
    
    p = P(stylename=textstyle)
    p.addText("This is a sample ODP file for testing purposes.")
    textbox.addElement(p)
    
    frame.addElement(textbox)
    page.addElement(frame)
    doc.body.addElement(page)

    with tempfile.NamedTemporaryFile(suffix='.odp', delete=False) as temp_odp:
        doc.save(temp_odp.name)
    return temp_odp.name

def create_sample_pdf():
    pdf_content = b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 300 144]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF"
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(pdf_content)
    return temp_pdf.name

def test_odp_processing():
    odp_file = create_sample_odp()
    result = process_file(odp_file)
    print("ODP Processing Result:")
    print(f"Number of slides: {result['num_slides']}")
    print(f"Content: {result['content']}")
    os.unlink(odp_file)
    os.unlink(result['temp_file_path'])

def test_pdf_processing():
    pdf_file = create_sample_pdf()
    result = process_file(pdf_file)
    print("PDF Processing Result:")
    print(f"Number of slides: {result['num_slides']}")
    print(f"Content: {result['content']}")
    os.unlink(pdf_file)

if __name__ == "__main__":
    test_odp_processing()
    test_pdf_processing()
