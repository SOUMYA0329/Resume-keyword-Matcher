"""
Extracts plain text from a resume file (PDF or DOCX) so the rest of the
pipeline only ever has to deal with plain strings.
"""

from pathlib import Path
import pdfplumber
import docx


def extract_text_from_pdf(file_path: str) -> str:
    """Pull all text out of a PDF, page by page."""
    text_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)


def extract_text_from_docx(file_path: str) -> str:
    """Pull all text out of a Word document, paragraph by paragraph."""
    document = docx.Document(file_path)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def parse_resume(file_path: str) -> str:
    """
    Dispatch to the right parser based on file extension.
    Returns cleaned plain text, ready for NLP processing.
    """
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif suffix == ".docx":
        raw_text = extract_text_from_docx(file_path)
    elif suffix == ".txt":
        raw_text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .pdf, .docx, or .txt")

    return _clean_text(raw_text)


def _clean_text(text: str) -> str:
    """Light cleanup: collapse whitespace, drop empty lines."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python resume_parser.py <path_to_resume>")
        sys.exit(1)

    extracted = parse_resume(sys.argv[1])
    print(extracted)