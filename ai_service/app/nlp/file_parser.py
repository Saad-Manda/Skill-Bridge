from pdfminer.high_level import extract_text
import docx2txt


def parse_pdf(file_path: str) -> str:
    return extract_text(file_path)


def parse_docx(file_path: str) -> str:
    return docx2txt.process(file_path)


def parse_file(file_path: str) -> str:
    lower = file_path.lower()
    if lower.endswith(".pdf"):
        return parse_pdf(file_path)
    elif lower.endswith(".docx"):
        return parse_docx(file_path)
    elif lower.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
