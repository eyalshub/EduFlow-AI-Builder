# core/services/file_ingest.py

import json
import mimetypes
from typing import Literal, TypedDict, Union
from pathlib import Path

from docx import Document
import fitz  # PyMuPDF

# 🧱 Structured return type
class FileIngestResult(TypedDict):
    kind: Literal["json", "text"]
    content: Union[str, dict]

# 🔍 Detect file format based on extension
def detect_format(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".json":
        return "json"
    if ext in [".txt", ".md"]:
        return "text"
    if ext == ".docx":
        return "docx"
    if ext == ".pdf":
        return "pdf"
    return "unknown"

# 📂 Extract content from file (PDF, DOCX, TXT, JSON)
async def ingest_upload(file_bytes: bytes, filename: str) -> FileIngestResult:
    file_type = detect_format(filename)

    if file_type == "json":
        try:
            content = json.loads(file_bytes.decode("utf-8"))
            return {"kind": "json", "content": content}
        except Exception as e:
            raise ValueError(f"Failed to parse JSON: {str(e)}")

    elif file_type == "txt":
        try:
            return {"kind": "text", "content": file_bytes.decode("utf-8")}
        except Exception as e:
            raise ValueError(f"Failed to decode TXT: {str(e)}")

    elif file_type == "docx":
        try:
            doc = Document()
            doc._part._blob = file_bytes  # dirty patch
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return {"kind": "text", "content": "\n".join(paragraphs)}
        except Exception as e:
            raise ValueError(f"Failed to read DOCX: {str(e)}")

    elif file_type == "pdf":
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            return {"kind": "text", "content": text}
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")

    else:
        raise ValueError(f"Unsupported file format: {file_type}")


# def test_detect_format():
#     assert detect_format("lesson.json") == "json"
#     assert detect_format("file.TXT") == "text"
#     assert detect_format("intro.docx") == "docx"
#     assert detect_format("scan.pdf") == "pdf"
#     assert detect_format("image.png") == "unknown"
#     print("✅ test_detect_format passed")

# test_detect_format()