import os
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        raise ValueError(f"Failed to read PDF document: {str(e)}")
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from a DOCX document using standard zip/XML parsing."""
    try:
        with zipfile.ZipFile(file_path, "r") as docx_zip:
            xml_content = docx_zip.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            
            # XML namespace for WordprocessingML
            namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            
            paragraphs = []
            for p in tree.iterfind(".//w:p", namespaces):
                texts = [node.text for node in p.iterfind(".//w:t", namespaces) if node.text]
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs).strip()
    except Exception as e:
        raise ValueError(f"Failed to read DOCX document: {str(e)}")


def extract_text_from_txt(file_path: str) -> str:
    """Extract text content from a plain text file supporting multiple encodings."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read().strip()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError("Failed to decode text file with supported encodings (UTF-8, Latin-1).")


def extract_text(file_path: str) -> str:
    """
    Extract readable text from a resume file (PDF, DOCX, or TXT).
    Raises ValueError if file format is unsupported or if extracted text is empty.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found at: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(file_path)
    elif ext == ".txt":
        raw_text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Only PDF, DOCX, and TXT are supported.")

    if not raw_text or len(raw_text.strip()) < 15:
        raise ValueError("The uploaded document contains no readable text or is empty.")

    return raw_text.strip()