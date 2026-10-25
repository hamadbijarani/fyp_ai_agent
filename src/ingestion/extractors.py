from __future__ import annotations

from pathlib import Path


def extract_text(path: str | Path) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in {".txt", ".md", ".log", ".csv"}:
        return p.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader
        reader = PdfReader(str(p))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if suffix == ".docx":
        import docx

        doc = docx.Document(str(p))
        return "\n".join(par.text for par in doc.paragraphs)
    raise ValueError(f"Unsupported file type: {suffix}")


def supported_extensions() -> set[str]:
    return {".txt", ".md", ".log", ".csv", ".pdf", ".docx"}
