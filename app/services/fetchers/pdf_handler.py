# File: pdf_handler.py
import os
import json
from datetime import datetime
from typing import Optional
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text as pdfminer_extract
from pdf2image import convert_from_path
from pytesseract import image_to_string
from langdetect import detect
import pdfplumber
import fitz  # PyMuPDF
import ftfy
import re
import csv
import logging
from pytesseract import image_to_string, pytesseract
from langdetect.lang_detect_exception import LangDetectException
from pdfminer.pdfparser import PDFSyntaxError

pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

logging.getLogger("pdfminer").setLevel(logging.ERROR)
POPPLER_BIN_PATH = os.path.join("../tools", "poppler", "poppler-23.11.0", "Library", "bin")

def is_hebrew(text: str, threshold: float = 0.2) -> bool:
    hebrew_chars = re.findall(r'[֐-׿]', text)
    return (len(hebrew_chars) / len(text)) >= threshold if text else False


def reverse_hebrew_lines(text: str) -> str:
    def reverse_if_hebrew(line):
        hebrew_ratio = len(re.findall(r'[֐-׿]', line)) / (len(line) + 1e-5)
        return line[::-1] if hebrew_ratio > 0.5 else line
    return "\n".join(reverse_if_hebrew(line) for line in text.splitlines())

def detect_language_safe(text: str) -> str:
    try:
        clean_text = re.sub(r"[^א-תa-zA-Z ]+", "", text)
        return detect(clean_text)
    except LangDetectException:
        return "unknown"

def fix_encoding_if_needed(text: str) -> str:
    if not text:
        return ""
    if any(c in text for c in ["\u202e", "�"]):
        return ftfy.fix_text(text)
    return text


def extract_text_with_ocr(path: str, lang: str = "heb+eng") -> str:
    pages = convert_from_path(path, dpi=300, poppler_path=POPPLER_BIN_PATH)
    return "\n\n".join(image_to_string(p, lang=lang) for p in pages)

# Extract text via OCR from image-based PDFs
def extract_text_ocr(path: str, lang: str = "eng") -> str:
    pages = convert_from_path(path, dpi=300, poppler_path=POPPLER_BIN_PATH)
    return "\n\n".join(image_to_string(p, lang=lang) for p in pages)


# Extract tables using pdfplumber
def extract_tables_from_pdf(path: str) -> list:
    """
    Extracts tables from a PDF file using pdfplumber, applying multiple strategies
    and post-processing for better accuracy and language handling.

    Returns:
        list: A list of extracted tables (list of rows per table).
    """
    all_extracted_tables = []

    extraction_strategies = [
        {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 3,
         "join_tolerance": 3, "text_tolerance": 3, "text_strategy": "lines"},
        {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 5,
         "join_tolerance": 5, "text_tolerance": 5, "text_strategy": "lines"},
        {"vertical_strategy": "text", "horizontal_strategy": "text", "snap_tolerance": 3,
         "join_tolerance": 3, "text_tolerance": 3, "text_strategy": "lines",
         "explicit_vertical_lines": [], "explicit_horizontal_lines": []},
        {"vertical_strategy": "lines", "horizontal_strategy": "text", "snap_tolerance": 3,
         "join_tolerance": 3, "text_tolerance": 3, "text_strategy": "lines"},
    ]

    try:
        with pdfplumber.open(path) as pdf:
            if not pdf.pages:
                logging.warning(f"[extract_tables_from_pdf] No pages found in '{os.path.basename(path)}'")
                return []

            for page_num, page in enumerate(pdf.pages):
                logging.info(f"[Tables] Processing page {page_num + 1} of '{os.path.basename(path)}'")
                page_tables = []

                for i, settings in enumerate(extraction_strategies):
                    try:
                        logging.debug(f"Trying strategy {i + 1} on page {page_num + 1}")
                        extracted = page.extract_tables(table_settings=settings)
                        if extracted:
                            logging.info(f"✔ Found {len(extracted)} tables with strategy {i + 1}")
                            page_tables.extend(extracted)
                        else:
                            logging.debug(f"No tables with strategy {i + 1}")
                    except Exception as e:
                        if "unexpected keyword argument 'strategy'" not in str(e):
                            logging.warning(f"[Tables] Strategy {i + 1} failed on page {page_num + 1}: {e}")
                        else:
                            logging.debug(
                                f"[Tables] Strategy {i + 1} skipped on page {page_num + 1} due to known invalid param.")

                if page_tables:
                    for table in page_tables:
                        cleaned_table = []
                        for row in table:
                            cleaned_row = []
                            for cell in row:
                                processed_cell = cell or ""
                                processed_cell = ftfy.fix_text(processed_cell)
                                if is_hebrew(processed_cell):
                                    processed_cell = reverse_hebrew_lines(processed_cell)
                                cleaned_row.append(processed_cell)
                            cleaned_table.append(cleaned_row)

                        if any(any(cell.strip() for cell in row) for row in cleaned_table):
                            all_extracted_tables.append(cleaned_table)
                else:
                    logging.info(f"[Tables] No tables found on page {page_num + 1} after all strategies")

        logging.info(f"[Tables] ✅ Total tables extracted: {len(all_extracted_tables)}")
        return all_extracted_tables

    except PDFSyntaxError as e:
        logging.error(f"[Tables] PDF Syntax Error: '{os.path.basename(path)}' might be corrupted: {e}")
    except Exception as e:
        logging.error(f"[Tables] Unexpected error while processing '{os.path.basename(path)}': {e}")

    return []



def extract_images_from_pdf(path: str, output_dir: str) -> list:
    """
    Extracts all images from a PDF file and saves them as PNGs.

    Args:
        path (str): Path to the input PDF file.
        output_dir (str): Directory to save extracted images.

    Returns:
        list: List of saved image filenames.
    """
    saved_images = []

    try:
        doc = fitz.open(path)
        os.makedirs(output_dir, exist_ok=True)

        for page_index, page in enumerate(doc):
            images = page.get_images(full=True)
            logging.info(f"[Images] Found {len(images)} images on page {page_index + 1}")

            for img_index, img in enumerate(images):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)

                    # Handle CMYK or alpha (RGBA) images by converting to RGB
                    if pix.n > 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    img_filename = f"page{page_index + 1}_img{img_index + 1}.png"
                    img_path = os.path.join(output_dir, img_filename)
                    pix.save(img_path)
                    saved_images.append(img_filename)
                    logging.debug(f"[Images] Saved image: {img_filename}")
                except Exception as img_error:
                    logging.warning(f"[Images] Failed to extract image {img_index + 1} on page {page_index + 1}: {img_error}")

        logging.info(f"[Images] ✅ Total images saved: {len(saved_images)}")
        return saved_images

    except Exception as e:
        logging.error(f"[extract_images_from_pdf] ❌ Failed to extract images from '{os.path.basename(path)}': {e}")
        return []


def full_ocr_with_debug(path: str, lang: str = "heb+eng") -> str:
    pages = convert_from_path(path, dpi=300, poppler_path=POPPLER_BIN_PATH)
    all_text = []

    for i, image in enumerate(pages):
        debug_image_path = f"debug_page_{i+1}.png"
        image.save(debug_image_path)
        print(f"[INFO] Saved page image to: {debug_image_path}")

        text = image_to_string(image, lang=lang)
        detected_lang = detect_language_safe(text)

        print(f"[PAGE {i+1}] LANG DETECTED: {detected_lang.upper()} ({len(text.split())} words)")
        print(f"[PAGE {i+1}] OCR OUTPUT:\n{text[:200]}...\n")

        if is_hebrew(text):
            text = reverse_hebrew_lines(text)
        all_text.append(text)

    combined_text = "\n\n".join(all_text)
    return fix_encoding_if_needed(combined_text)


def smart_extract_pdf(path: str) -> str:
    """
    Smartly extracts text from a PDF file using a tiered fallback strategy:
    1. Attempts extraction using pdfminer (best for structured text).
    2. Falls back to PyPDF2 if needed.
    3. Falls back to OCR if both fail or extract too little text.
    Post-processes the result with encoding fixes and Hebrew direction handling.

    Args:
        path (str): Path to the input PDF file.

    Returns:
        str: Cleaned, extracted text from the PDF.
    """
    extracted_text = ""  # Resulting full text

    try:
        logging.info(f"[SmartExtract] Trying pdfminer on '{os.path.basename(path)}'")
        text = pdfminer_extract(path)
        if len(text.strip()) > 50:
            extracted_text = text
            logging.info("[SmartExtract] ✅ Extracted using pdfminer.")
        else:
            logging.warning("[SmartExtract] pdfminer extracted too little, trying PyPDF2.")
    except Exception as e:
        logging.warning(f"[SmartExtract] ❌ pdfminer failed: {e}. Trying PyPDF2.")

    if not extracted_text or len(extracted_text.strip()) < 50:
        try:
            logging.info("[SmartExtract] Trying PyPDF2...")
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if len(text.strip()) > 50:
                extracted_text = text
                logging.info("[SmartExtract] ✅ Extracted using PyPDF2.")
            else:
                logging.warning("[SmartExtract] PyPDF2 extracted too little, falling back to OCR.")
        except Exception as e:
            logging.warning(f"[SmartExtract] ❌ PyPDF2 failed: {e}. Falling back to OCR.")

    if not extracted_text or len(extracted_text.strip()) < 50:
        try:
            logging.info("[SmartExtract] Performing full OCR with debug...")
            extracted_text = full_ocr_with_debug(path)
            logging.info("[SmartExtract] ✅ Extracted using OCR.")
        except Exception as e:
            logging.error(f"[SmartExtract] ❌ OCR failed: {e}")
            return ""

    # Post-process the extracted text
    try:
        final_text = fix_encoding_if_needed(extracted_text)
        final_text = reverse_hebrew_lines(final_text)
    except Exception as post_e:
        logging.warning(f"[SmartExtract] ⚠️ Post-processing failed: {post_e}")
        final_text = extracted_text

    return final_text


def debug_ocr_page(path: str, page_num: int = 0, lang: str = "heb+eng"):
    print(f"[DEBUG] Extracting OCR from page {page_num+1}...")
    pages = convert_from_path(path, dpi=500, poppler_path=POPPLER_BIN_PATH)

    if page_num >= len(pages):
        print("[ERROR] Page number out of range.")
        return

    image = pages[page_num]
    debug_image_path = f"debug_page_{page_num+1}.png"
    image.save(debug_image_path)
    print(f"[INFO] Saved page image to: {debug_image_path}")

    text = image_to_string(image, lang=lang)

    try:
        detected_lang = detect(text)
    except Exception:
        detected_lang = "unknown"

    print(f"\n[LANG DETECTED] {detected_lang}")
    print("\n----- OCR Output -----\n")
    print(text)
    print("\n-----------------------\n")

    # if is_hebrew(text):
    #     corrected = reverse_hebrew_lines(text)
    #     print("[INFO] After direction fix:\n")
    #     print(corrected)



class PDFHandler:
    def __init__(self, path: str):
        self.path = path

    def extract(self) -> Optional[str]:
        return smart_extract_pdf(self.path)

    def save(self, content: str, output_dir: str = "extracted_data"):
        os.makedirs(output_dir, exist_ok=True)
        folder = os.path.splitext(os.path.basename(self.path))[0]
        folder_path = os.path.join(output_dir, folder)
        os.makedirs(folder_path, exist_ok=True)

        # sava img
        images_dir = os.path.join(folder_path, "images")
        image_filenames = extract_images_from_pdf(self.path, images_dir)
        image_lines = [f"[IMAGE] images/{folder}/{name}" for name in image_filenames]

        # sava table
        tables = extract_tables_from_pdf(self.path)
        tables_dir = os.path.join(folder_path, "tables")
        os.makedirs(tables_dir, exist_ok=True)
        table_lines = []
        for idx, table in enumerate(tables):
            table_path = os.path.join(tables_dir, f"table_{idx+1}.csv")
            with open(table_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                for row in table:
                    writer.writerow(row)
            table_lines.append(f"[TABLE] tables/{folder}/table_{idx+1}.csv")

        # Full text essay with references
        full_content = content.strip() + "\n\n" + "\n".join(image_lines + table_lines)

        txt_path = os.path.join(folder_path, "content.txt")
        meta_path = os.path.join(folder_path, "meta.json")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        metadata = {
            "file": self.path,
            "word_count": len(content.split()),
            "timestamp": datetime.now().isoformat(),
            "file_type": "pdf",
            "images": image_lines,
            "tables": table_lines
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)


# if __name__ == "__main__":
#     test_path = "tichnunbereshit_tashpa.pdf"
#     handler = PDFHandler(test_path)
#
#     print(f"[INFO] Starting extraction for: {test_path}")
#     try:
#         content = handler.extract()
#
#         print("[INFO] Extraction completed. Saving data regardless of content length.")
#         handler.save(content)
#
#         if content and len(content.strip()) > 20:
#             print("[✓] Text extracted successfully. Preview:")
#             print(content[:500])
#         else:
#             print("[!]: Very little or no text extracted. Might be scanned or low-quality PDF.")
#
#         print("[✓] Data saved successfully.")
#     except PDFSyntaxError as e:
#         logging.error(f"PDF Syntax Error ...")


