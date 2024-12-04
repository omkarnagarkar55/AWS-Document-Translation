from pdf2docx import Converter

def convert_pdf_to_docx(pdf_file, docx_file):
    """
    Converts a PDF file to a DOCX file.
    """
    converter = Converter(pdf_file)
    converter.convert(docx_file, start=0, end=None)  # Convert the entire PDF
    converter.close()
    print(f"PDF converted to DOCX: {docx_file}")


# Input PDF and output DOCX
pdf_file = 'test-pdf.pdf'    # Replace with your PDF file path
docx_file = 'output.docx'   # Replace with your desired DOCX file path

# Convert PDF to DOCX
convert_pdf_to_docx(pdf_file, docx_file)

