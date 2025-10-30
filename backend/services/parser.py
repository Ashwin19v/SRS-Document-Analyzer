from io import BytesIO
from typing import Optional
from pypdf import PdfReader
from docx import Document


def extract_text(data: bytes, ext: str) -> str:
    ext = ext.lower()
    if ext == ".txt":
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    if ext == ".pdf":
        try:
            reader = PdfReader(BytesIO(data))
            texts = []
            for page in reader.pages:
                txt = page.extract_text() or ""
                texts.append(txt)
            return "\n".join(texts)
        except Exception:
            return ""
    if ext == ".docx":
        try:
            doc = Document(BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""
    return ""
