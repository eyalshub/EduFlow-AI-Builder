# app/stage_1/fetchers/file_processor.py

import os
from typing import Optional

from app.services.fetchers.pdf_handler import PDFHandler
from app.services.fetchers.docx_handler import DocxExtractor


def process_uploaded_file(file_path: str) -> Optional[dict]:
    """
    Processes an uploaded document (PDF or DOCX) and returns a structured dictionary
    containing the extracted content, metadata, and paths to images/tables.

    Args:
        file_path (str): Full path to the uploaded file

    Returns:
        dict: {
            "sourceType": "Uploaded_PDF" or "Uploaded_DOCX",
            "sourceName": <filename>,
            "sourceURI": <file_path>,
            "retrievedAt": <ISO timestamp>,
            "processedContent": {
                "summary": <extracted text>,
                "sections": []  # to be added in Stage 4
            }
        }
    """
    ext = os.path.splitext(file_path)[-1].lower()
    filename = os.path.basename(file_path)

    if ext == ".pdf":
        handler = PDFHandler(file_path)
        text = handler.extract()
        handler.save(text)
        source_type = "Uploaded_PDF"

    elif ext == ".docx":
        extractor = DocxExtractor(file_path)
        text = extractor.extract_text()
        extractor.save()
        source_type = "Uploaded_DOCX"

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return {
        "sourceType": source_type,
        "sourceName": filename,
        "sourceURI": file_path,
        "retrievedAt": extractor.metadata["timestamp"] if ext == ".docx" else handler.save.__self__.metadata["timestamp"],
        "processedContent": {
            "summary": text.strip(),
            "sections": []  # Optional: populated in Stage 4
        }
    }


__all__ = ["process_uploaded_file"]
