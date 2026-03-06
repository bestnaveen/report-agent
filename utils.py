import re
import json
from config import MAX_CHAT_HISTORY

# Keywords that trigger each output format
CHART_KEYWORDS = [
    "chart", "graph", "plot", "visualize", "visualise", "bar", "line", "pie",
    "scatter", "heatmap", "histogram", "trend", "distribution",
    # Multi-lingual chart keywords
    "grafik", "grafico", "gráfico", "diagramme", "गráfic", "चार्ट", "ग्राफ",
]

TABLE_KEYWORDS = [
    "table", "tabular", "grid", "spreadsheet", "rows", "columns", "список",
    "tabela", "tableau", "tabla", "तालिका", "टेबल",
]

SUMMARY_KEYWORDS = [
    "summarize", "summary", "overview", "describe", "explain", "tell me about",
    "what is", "what are", "how many", "analyze", "analyse", "insight",
    "सारांश", "résumé", "resumen", "zusammenfassung", "요약", "概要",
]


def detect_output_format(question: str) -> str:
    """
    Detect the desired output format from the question.

    Returns: 'chart' | 'table' | 'summary' | 'auto'
    """
    q = question.lower()

    if any(kw in q for kw in CHART_KEYWORDS):
        return "chart"
    if any(kw in q for kw in TABLE_KEYWORDS):
        return "table"
    if any(kw in q for kw in SUMMARY_KEYWORDS):
        return "summary"
    return "auto"


def extract_json_from_response(response: str) -> dict | None:
    """
    Try to extract a JSON object from an LLM response string.
    Attempts: direct parse → JSON code block → braces extraction.
    """
    # 1. Direct parse
    try:
        return json.loads(response.strip())
    except Exception:
        pass

    # 2. JSON code block (```json ... ```)
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # 3. Extract first {...} block
    match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    # 4. Greedy search for outer braces
    start = response.find("{")
    end = response.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(response[start : end + 1])
        except Exception:
            pass

    return None


def format_chat_history(messages: list[dict], max_messages: int = MAX_CHAT_HISTORY) -> str:
    """
    Format recent chat messages into a prompt-safe string.

    messages: list of {"role": "user"|"assistant", "content": str}
    """
    if not messages:
        return "(No prior conversation)"

    recent = messages[-max_messages:]
    lines = []
    for msg in recent:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "").strip()
        # Truncate very long messages in history
        if len(content) > 500:
            content = content[:500] + "..."
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def get_output_hint(fmt: str) -> str:
    """Return the output format instruction to inject into the prompt."""
    hints = {
        "chart": (
            "Return ONLY a JSON object with this exact schema — no extra text:\n"
            '{"chart_type": "bar|line|pie|scatter|heatmap", "title": "...", '
            '"x_label": "...", "y_label": "...", "labels": [...], "values": [...], '
            '"secondary_values": []}'
        ),
        "table": (
            "Return a well-formatted Markdown table. "
            "Use | separators and a header row with --- dividers."
        ),
        "summary": (
            "Return a clear, concise text summary in paragraphs. "
            "Use bullet points for lists of facts."
        ),
        "auto": (
            "Choose the most appropriate format: "
            "JSON chart spec if visualization is needed, "
            "Markdown table for comparisons, "
            "or text paragraphs for explanations."
        ),
    }
    return hints.get(fmt, hints["auto"])


def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n[... truncated {len(text) - max_chars} chars ...]"
