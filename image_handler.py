import base64
import io
import warnings
from PIL import Image


def process_image(file_path: str) -> dict:
    """
    Load an image, run OCR, return metadata dict.

    Returns:
        {image_bytes, ocr_text, width, height, format}
    """
    try:
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        img = Image.open(io.BytesIO(image_bytes))
        img_format = img.format or "PNG"
        width, height = img.size

        ocr_text = extract_text_ocr(file_path)

        return {
            "image_bytes": image_bytes,
            "ocr_text": ocr_text,
            "width": width,
            "height": height,
            "format": img_format,
        }
    except Exception as e:
        raise RuntimeError(f"Failed to process image: {e}")


def extract_text_ocr(file_path: str) -> str:
    """Extract text from image using pytesseract. Returns empty string if unavailable."""
    try:
        import pytesseract
        img = Image.open(file_path)
        # Convert to RGB if needed (handles RGBA, palette images)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        text = pytesseract.image_to_string(img)
        return text.strip()
    except ImportError:
        warnings.warn("pytesseract not installed — OCR unavailable.")
        return ""
    except Exception as e:
        warnings.warn(f"OCR failed: {e}")
        return ""


def resize_for_llm(image_bytes: bytes, max_size: int = 1024) -> bytes:
    """Resize image so longest side <= max_size, preserving aspect ratio."""
    img = Image.open(io.BytesIO(image_bytes))
    w, h = img.size
    if max(w, h) <= max_size:
        return image_bytes

    if w >= h:
        new_w = max_size
        new_h = int(h * max_size / w)
    else:
        new_h = max_size
        new_w = int(w * max_size / h)

    img = img.resize((new_w, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    fmt = img.format or "PNG"
    img.save(buf, format=fmt)
    return buf.getvalue()


def image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    resized = resize_for_llm(image_bytes)
    return base64.b64encode(resized).decode("utf-8")
