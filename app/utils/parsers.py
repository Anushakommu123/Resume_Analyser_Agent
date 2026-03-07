"""Parse resume and job description files (PDF, DOCX, TXT, MD)."""
import os
from pathlib import Path
from fastapi import UploadFile


async def save_uploaded_file(upload: UploadFile, dest_dir: str) -> str:
    """
    Save an uploaded file to dest_dir and return the file path.
    """
    os.makedirs(dest_dir, exist_ok=True)
    name = upload.filename or "upload"
    safe_name = os.path.basename(name).replace("..", "_")
    path = os.path.join(dest_dir, safe_name)
    content = await upload.read()
    with open(path, "wb") as f:
        f.write(content)
    return path


async def parse_file(file_path: str) -> str:
    """
    Extract text from a file. Supports .txt, .md, .pdf, .docx.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except ImportError:
            return "[PDF support requires: pip install pypdf]"
        except Exception as e:
            return f"[Error reading PDF: {e}]"

    if suffix in (".docx", ".doc"):
        try:
            from docx import Document
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            return "[DOCX support requires: pip install python-docx]"
        except Exception as e:
            return f"[Error reading DOCX: {e}]"

    # Fallback: try as text
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"[Could not read file: {e}]"
