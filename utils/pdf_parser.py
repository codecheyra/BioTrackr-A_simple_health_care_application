import io
import re
from datetime import datetime
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdf2image import convert_from_bytes
import pytesseract


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file. Tries native text extraction first;
    if that fails, renders pages as images and OCRs them via Tesseract.
    """

    try:
        return pdfminer_extract_text(io.BytesIO(file_bytes)) or ""
    except Exception:
        pass


    try:
        images = convert_from_bytes(file_bytes)
        text_pages = [pytesseract.image_to_string(img) for img in images]
        return "\n".join(text_pages)
    except Exception:
        return ""


def extract_date(text: str) -> datetime.date:
    """
    Parse a date from text, matching common formats.
    Returns the first successful parse or today() as fallback.
    """
    date_patterns = [
        (r"\b(\d{2}/\d{2}/\d{4})\b", "%d/%m/%Y"),
        (r"\b(\d{4}-\d{2}-\d{2})\b", "%Y-%m-%d"),
        (r"\b(\d{1,2} [A-Za-z]+ \d{4})\b", "%d %B %Y")
    ]
    for pattern, fmt in date_patterns:
        for match in re.findall(pattern, text):
            try:
                return datetime.strptime(match, fmt).date()
            except Exception:
                continue
    return datetime.today().date()


def extract_biomarkers(text: str) -> list[dict]:
    """
    Identify biomarker values in text using regex patterns.
    Returns a list of entries with keys: biomarker, value, date, unit.
    """
    entries = []
    date_found = extract_date(text).isoformat()


    expected_units = {
        "Glucose": "mg/dL",
        "WBC count": "/mm³",
        "Hemoglobin": "g/dL"
    }


    patterns = {
        "Glucose":    r"glucose[^0-9]*([\d\.]+)\s*([A-Za-z/%µ°³]*)",
        "WBC count":  r"wbc[^0-9]*([\d\.]+)\s*([A-Za-z/%µ°³]*)",
        "Hemoglobin": r"hemoglobin[^0-9]*([\d\.]+)\s*([A-Za-z/%µ°³]*)"
    }

    for biomarker, pattern in patterns.items():
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            raw_val, raw_unit = match[0], match[1]
            try:
                value = float(raw_val)
            except ValueError:
                continue


            exp_unit = expected_units.get(biomarker, "")
            unit = exp_unit if raw_unit.strip().lower() == exp_unit.lower() else raw_unit.strip() or exp_unit

            entries.append({
                "biomarker": biomarker,
                "value": value,
                "date": date_found,
                "unit": unit
            })
    return entries
