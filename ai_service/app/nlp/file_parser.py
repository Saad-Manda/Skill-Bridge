from pdfminer.high_level import extract_text
import docx2txt

def parse_pdf(file_path: str) -> str:
    return extract_text(file_path)

def parse_docx(file_path: str) -> str:
    return docx2txt.process(file_path)

def parse_file(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        return parse_pdf(file_path)
    elif file_path.endswith(".docx"):
        return parse_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")