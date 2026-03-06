import os
import json
import pandas as pd
from config import SUPPORTED_FILE_EXTENSIONS, SUPPORTED_IMAGE_EXTENSIONS, MAX_DATA_CHARS


def load_file(file_path: str) -> dict:
    """
    Load any supported file and return a standardized dict.

    Returns:
        {
            raw_text: str,
            dataframe: pd.DataFrame | None,
            type: str,
            filename: str,
            row_count: int,
            col_count: int,
            columns: list[str],
            is_image: bool,
            image_bytes: bytes | None,
        }
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    result = {
        "raw_text": "",
        "dataframe": None,
        "type": ext,
        "filename": filename,
        "row_count": 0,
        "col_count": 0,
        "columns": [],
        "is_image": False,
        "image_bytes": None,
    }

    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return _load_image(file_path, result)
    elif ext == "csv":
        return _load_csv(file_path, result)
    elif ext in ("xlsx", "xls"):
        return _load_excel(file_path, result)
    elif ext == "json":
        return _load_json(file_path, result)
    elif ext == "pdf":
        return _load_pdf(file_path, result)
    elif ext == "txt":
        return _load_txt(file_path, result)
    else:
        raise ValueError(
            f"Unsupported file type: .{ext}\n"
            f"Supported: {', '.join('.' + e for e in SUPPORTED_FILE_EXTENSIONS + SUPPORTED_IMAGE_EXTENSIONS)}"
        )


def _load_image(file_path: str, result: dict) -> dict:
    try:
        from image_handler import process_image
        img_info = process_image(file_path)
        result["is_image"] = True
        result["image_bytes"] = img_info["image_bytes"]
        result["raw_text"] = (
            f"[IMAGE FILE: {result['filename']}]\n"
            f"Dimensions: {img_info['width']}x{img_info['height']} px | Format: {img_info['format']}\n\n"
            f"OCR Extracted Text:\n{img_info['ocr_text'] if img_info['ocr_text'].strip() else '(No text detected by OCR)'}"
        )
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to load image {result['filename']}: {e}")


def _load_csv(file_path: str, result: dict) -> dict:
    try:
        df = pd.read_csv(file_path)
        result["dataframe"] = df
        result["row_count"] = len(df)
        result["col_count"] = len(df.columns)
        result["columns"] = df.columns.tolist()
        result["raw_text"] = _build_data_summary(df, result["filename"])
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to load CSV {result['filename']}: {e}")


def _load_excel(file_path: str, result: dict) -> dict:
    try:
        df = pd.read_excel(file_path)
        result["dataframe"] = df
        result["row_count"] = len(df)
        result["col_count"] = len(df.columns)
        result["columns"] = df.columns.tolist()
        result["raw_text"] = _build_data_summary(df, result["filename"])
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to load Excel {result['filename']}: {e}")


def _load_json(file_path: str, result: dict) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, list) or isinstance(raw, dict):
            df = pd.json_normalize(raw)
            result["dataframe"] = df
            result["row_count"] = len(df)
            result["col_count"] = len(df.columns)
            result["columns"] = df.columns.tolist()
            result["raw_text"] = _build_data_summary(df, result["filename"])
        else:
            result["raw_text"] = f"[JSON FILE: {result['filename']}]\n\n{json.dumps(raw, indent=2)}"
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON {result['filename']}: {e}")


def _load_pdf(file_path: str, result: dict) -> dict:
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(f"--- Page {i + 1} ---\n{text}")

        full_text = "\n\n".join(pages_text)
        result["raw_text"] = f"[PDF FILE: {result['filename']} | {len(reader.pages)} pages]\n\n{full_text}"
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to load PDF {result['filename']}: {e}")


def _load_txt(file_path: str, result: dict) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        result["raw_text"] = f"[TEXT FILE: {result['filename']}]\n\n{content}"
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to load TXT {result['filename']}: {e}")


def _build_data_summary(df: pd.DataFrame, filename: str) -> str:
    """Build a rich text summary of a DataFrame for the LLM prompt."""
    lines = []
    lines.append(f"[DATASET: {filename}]")
    lines.append(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    lines.append(f"Columns: {', '.join(df.columns.tolist())}")
    lines.append("")

    # Column types
    lines.append("Column Types:")
    for col in df.columns:
        lines.append(f"  {col}: {df[col].dtype}")
    lines.append("")

    # Null counts
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        lines.append("Missing Values:")
        for col, count in null_counts[null_counts > 0].items():
            lines.append(f"  {col}: {count} nulls")
        lines.append("")

    # First 10 rows
    lines.append("First 10 Rows:")
    lines.append(df.head(10).to_string(index=False))
    lines.append("")

    # Numeric stats
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        lines.append("Numeric Statistics:")
        lines.append(df[numeric_cols].describe().round(2).to_string())
        lines.append("")

    # Categorical value counts
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        unique_count = df[col].nunique()
        if unique_count <= 20:
            lines.append(f"Value Counts — {col}:")
            vc = df[col].value_counts().head(10)
            for val, cnt in vc.items():
                lines.append(f"  {val}: {cnt}")
            lines.append("")

    return "\n".join(lines)


def get_data_summary(data: dict, max_chars: int = MAX_DATA_CHARS) -> str:
    """Return truncated raw_text suitable for LLM prompt injection."""
    text = data.get("raw_text", "")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n... [truncated — {len(text) - max_chars} chars omitted]"
