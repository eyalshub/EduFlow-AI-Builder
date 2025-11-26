from fastapi import UploadFile
from typing import List

ALLOWED_EXTENSIONS = ["pdf", "docx", "txt"]

def validate_file_type(file: UploadFile) -> bool:
    ext = file.filename.split(".")[-1].lower()
    return ext in ALLOWED_EXTENSIONS

def filter_valid_files(files: List[UploadFile]) -> List[UploadFile]:
    return [file for file in files if validate_file_type(file)]
