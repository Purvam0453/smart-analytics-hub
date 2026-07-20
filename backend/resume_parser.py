from pypdf import PdfReader


def extract_text(file_path):

    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        text += page.extract_text() or ""

    return text