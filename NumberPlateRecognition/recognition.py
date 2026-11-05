"""
recognition.py - Image processing and OCR pipeline for Number Plate Recognition System
Handles preprocessing, plate detection, and text extraction.
"""

import cv2
import numpy as np
from PIL import Image
import io
import re
import os

# ── Tesseract path check ─────────────────────────────────────────────────────

TESSERACT_AVAILABLE = False
TESSERACT_ERROR_MSG = ""

try:
    import pytesseract

    # Common Tesseract installation paths on Windows
    TESSERACT_PATHS = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(
            os.environ.get("USERNAME", "")
        ),
    ]

    # Check if tesseract is on PATH first
    import shutil
    if shutil.which("tesseract"):
        TESSERACT_AVAILABLE = True
    else:
        # Try common Windows install paths
        for path in TESSERACT_PATHS:
            if os.path.isfile(path):
                pytesseract.pytesseract.tesseract_cmd = path
                TESSERACT_AVAILABLE = True
                break

    if not TESSERACT_AVAILABLE:
        TESSERACT_ERROR_MSG = (
            "Tesseract OCR executable not found.\n\n"
            "**Windows Installation:**\n"
            "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "2. Run the installer (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`)\n"
            "3. During installation, note the install path (default: `C:\\Program Files\\Tesseract-OCR`)\n"
            "4. Add Tesseract to your system PATH **or** set the path in `recognition.py`\n"
            "5. Restart this application\n\n"
            "**Quick test:** Open a terminal and run `tesseract --version`"
        )

except ImportError:
    TESSERACT_ERROR_MSG = "pytesseract library not installed. Run: `pip install pytesseract`"


# ── Image Conversion Helpers ──────────────────────────────────────────────────

def pil_to_cv(pil_img: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV BGR numpy array."""
    img = pil_img.convert("RGB")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def cv_to_pil(cv_img: np.ndarray) -> Image.Image:
    """Convert OpenCV BGR numpy array to PIL Image."""
    if len(cv_img.shape) == 2:
        return Image.fromarray(cv_img)
    return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))


# ── Stage 1: Preprocessing ────────────────────────────────────────────────────

def preprocess_image(pil_img: Image.Image) -> dict:
    """
    Full preprocessing pipeline.
    Returns a dict with each intermediate stage as a PIL Image.
    """
    stages = {}

    # 1. Resize (cap at 1200px wide for consistent processing)
    orig_w, orig_h = pil_img.size
    if orig_w > 1200:
        ratio = 1200 / orig_w
        pil_img = pil_img.resize((1200, int(orig_h * ratio)), Image.LANCZOS)
    stages["resized"] = pil_img.copy()

    img = pil_to_cv(pil_img)

    # 2. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    stages["grayscale"] = cv_to_pil(gray)

    # 3. Noise reduction (bilateral filter preserves edges)
    denoised = cv2.bilateralFilter(gray, 11, 17, 17)
    stages["denoised"] = cv_to_pil(denoised)

    # 4. Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    stages["threshold"] = cv_to_pil(thresh)

    # 5. Edge detection
    edges = cv2.Canny(denoised, 30, 200)
    stages["edges"] = cv_to_pil(edges)

    return stages, img, gray, denoised


# ── Stage 2: Plate Detection ──────────────────────────────────────────────────

def detect_plate_region(img_bgr: np.ndarray, gray: np.ndarray) -> tuple:
    """
    Attempt to locate the number plate region using contour analysis.
    Returns (cropped_plate_bgr, bounding_box, confidence_note) or (None, None, reason).
    """
    # Bilateral filter + edge detection
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    edges = cv2.Canny(filtered, 30, 200)

    # Find contours
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

    img_h, img_w = img_bgr.shape[:2]
    plate_contour = None
    plate_bbox = None

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.018 * peri, True)

        if len(approx) == 4:  # rectangular shape
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            area = w * h
            img_area = img_h * img_w

            # Number plate heuristics: aspect ratio 1.5–6, area 0.5%–25% of image
            if (1.5 <= aspect_ratio <= 6.0 and
                    0.005 * img_area <= area <= 0.25 * img_area):
                plate_contour = approx
                plate_bbox = (x, y, w, h)
                break

    if plate_bbox is None:
        # Fallback: try broader aspect ratio search
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h) if h > 0 else 0
            area = w * h
            img_area = img_h * img_w
            if (1.2 <= aspect_ratio <= 7.0 and
                    0.003 * img_area <= area <= 0.30 * img_area):
                plate_bbox = (x, y, w, h)
                break

    if plate_bbox:
        x, y, w, h = plate_bbox
        # Add small padding
        pad = 5
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img_w, x + w + pad)
        y2 = min(img_h, y + h + pad)
        cropped = img_bgr[y1:y2, x1:x2]
        note = "Plate region detected via contour analysis (verify visually)"
        return cropped, plate_bbox, note

    return None, None, "No plate region found automatically. Try manual crop."


def draw_plate_box(img_bgr: np.ndarray, bbox: tuple) -> np.ndarray:
    """Draw a green bounding box around the detected plate."""
    annotated = img_bgr.copy()
    x, y, w, h = bbox
    cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 3)
    cv2.putText(annotated, "Plate Region", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return annotated


# ── Stage 3: OCR Preprocessing ────────────────────────────────────────────────

def preprocess_for_ocr(plate_bgr: np.ndarray) -> np.ndarray:
    """
    Additional preprocessing specifically for the cropped plate before OCR.
    Returns a grayscale numpy array optimised for Tesseract.
    """
    # Scale up for better OCR (Tesseract works better at ~300 DPI equivalent)
    h, w = plate_bgr.shape[:2]
    # Cap scale to avoid memory issues with pathologically small crops.
    # Target ~120px tall; scale capped at 8x to prevent OOM on tiny inputs.
    if h < 120:
        scale = min(8, max(2, 120 // max(h, 1)))
    else:
        scale = 2
    resized = cv2.resize(plate_bgr, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # Denoise
    gray = cv2.fastNlMeansDenoising(gray, h=10)

    # Sharpening kernel
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, kernel)

    # Otsu thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh


# ── Stage 4: OCR ──────────────────────────────────────────────────────────────

def run_ocr(plate_bgr: np.ndarray) -> dict:
    """
    Run Tesseract OCR on the cropped plate image.
    Returns a dict with raw_text, cleaned_text, confidence notes.
    """
    if not TESSERACT_AVAILABLE:
        return {"success": False, "error": TESSERACT_ERROR_MSG, "raw": "", "cleaned": ""}

    import pytesseract

    processed = preprocess_for_ocr(plate_bgr)

    # Tesseract configs:
    # --psm 7 = single text line,  --psm 8 = single word
    # -c tessedit_char_whitelist restricts to plate chars
    configs = [
        r"--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        r"--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        r"--oem 3 --psm 6",
    ]

    best_raw = ""
    best_cleaned = ""

    for config in configs:
        try:
            raw = pytesseract.image_to_string(
                Image.fromarray(processed), config=config
            ).strip()
            cleaned = re.sub(r"[^A-Z0-9]", "", raw.upper())
            if len(cleaned) > len(best_cleaned):
                best_raw = raw
                best_cleaned = cleaned
        except Exception as e:
            continue

    if not best_cleaned:
        return {
            "success": False,
            "error": (
                "OCR could not extract text from this plate region. "
                "This may be due to low image quality, unusual plate format, "
                "poor lighting, or angle distortion.\n\n"
                "**Tips:** Try uploading a clearer, well-lit front-facing image of the vehicle."
            ),
            "raw": best_raw,
            "cleaned": "",
        }

    return {
        "success":  True,
        "raw":      best_raw,
        "cleaned":  best_cleaned,
        "error":    None,
    }


# ── Full Pipeline ─────────────────────────────────────────────────────────────

def full_pipeline(pil_img: Image.Image) -> dict:
    """
    Run the complete recognition pipeline on a PIL image.
    Returns a structured result dict.
    """
    result = {
        "stages":          {},
        "plate_detected":  False,
        "plate_image":     None,     # PIL
        "annotated_image": None,     # PIL  (original + bounding box)
        "bbox":            None,
        "detection_note":  "",
        "ocr_raw":         "",
        "ocr_cleaned":     "",
        "ocr_success":     False,
        "ocr_error":       None,
        "tesseract_ok":    TESSERACT_AVAILABLE,
        "tesseract_error": TESSERACT_ERROR_MSG,
    }

    # Preprocessing
    try:
        stages, img_bgr, gray, _ = preprocess_image(pil_img)
        result["stages"] = stages
    except Exception as e:
        result["ocr_error"] = f"Preprocessing error: {e}"
        return result

    # Detection
    try:
        plate_bgr, bbox, note = detect_plate_region(img_bgr, gray)
        result["detection_note"] = note

        if plate_bgr is not None:
            result["plate_detected"] = True
            result["plate_image"] = cv_to_pil(plate_bgr)
            result["bbox"] = bbox
            # Annotated original
            annotated = draw_plate_box(img_bgr, bbox)
            result["annotated_image"] = cv_to_pil(annotated)
        else:
            # No plate found – fall back to full image OCR as last resort
            result["annotated_image"] = cv_to_pil(img_bgr)
    except Exception as e:
        result["detection_note"] = f"Detection error: {e}"
        result["annotated_image"] = cv_to_pil(img_bgr)

    # OCR
    if not TESSERACT_AVAILABLE:
        result["ocr_error"] = TESSERACT_ERROR_MSG
        return result

    ocr_input = plate_bgr if plate_bgr is not None else img_bgr
    try:
        ocr_result = run_ocr(ocr_input)
        result["ocr_raw"]     = ocr_result.get("raw", "")
        result["ocr_cleaned"] = ocr_result.get("cleaned", "")
        result["ocr_success"] = ocr_result.get("success", False)
        result["ocr_error"]   = ocr_result.get("error")
    except Exception as e:
        result["ocr_error"] = f"OCR error: {e}"

    return result
