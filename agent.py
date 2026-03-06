import warnings
import streamlit as st
from data_loader import get_data_summary
from language_utils import detect_language, get_language_instruction
from utils import detect_output_format, format_chat_history, get_output_hint
from config import (
    OLLAMA_MODEL, OLLAMA_VISION_MODEL, OLLAMA_BASE_URL,
    GROQ_MODEL, GROQ_VISION_MODEL,
    GEMINI_MODEL, GEMINI_VISION_MODEL,
    OPENAI_MODEL, OPENAI_VISION_MODEL,
    ANTHROPIC_MODEL, ANTHROPIC_VISION_MODEL,
    MAX_DATA_CHARS,
)

# ─── Prompt Templates ──────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """\
You are a precise Report Generator AI. Analyze data and answer questions accurately.

## DATA
{data_summary}

## LANGUAGE RULE
{language_instruction}

## CONVERSATION HISTORY
{chat_history}

## OUTPUT FORMAT
{output_hint}

## QUESTION
{user_question}

## STRICT RULES
1. Answer ONLY from the provided data. Never fabricate numbers.
2. Respond in the SAME language as the question.
3. For charts: output ONLY the JSON — no other text before or after.
4. Be concise and precise. Quote exact values from the data.
5. If data is insufficient, say so clearly in the user's language.
"""

IMAGE_PROMPT_TEMPLATE = """\
You are an AI analyzing an image. Be thorough and precise.

## IMAGE METADATA
Format: {img_format} | Size: {width}x{height}px

## OCR EXTRACTED TEXT
{ocr_text}

## LANGUAGE RULE
{language_instruction}

## QUESTION
{user_question}

## RULES
1. Describe what you see in detail.
2. Use the OCR text to answer questions about numbers, names, dates.
3. Respond in the SAME language as the question.
4. If something is unclear in the image, say so.
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_provider() -> str:
    return st.session_state.get("llm_provider", "ollama")

def _get_api_key(provider: str) -> str:
    return st.session_state.get(f"{provider}_api_key", "")


# ─── LLM Factories (cached) ────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _groq_llm(api_key: str, model: str):
    from langchain_groq import ChatGroq
    return ChatGroq(api_key=api_key, model=model, temperature=0.1, streaming=True)

@st.cache_resource(show_spinner=False)
def _openai_llm(api_key: str, model: str):
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(api_key=api_key, model=model, temperature=0.1, streaming=True)

@st.cache_resource(show_spinner=False)
def _anthropic_llm(api_key: str, model: str):
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(api_key=api_key, model=model, temperature=0.1, streaming=True)

@st.cache_resource(show_spinner=False)
def _ollama_llm(model: str, base_url: str):
    from langchain_ollama import OllamaLLM
    return OllamaLLM(model=model, base_url=base_url, temperature=0.1)


def get_llm():
    provider = _get_provider()
    if provider == "groq":
        return _groq_llm(_get_api_key("groq"), GROQ_MODEL)
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(google_api_key=_get_api_key("gemini"), model=GEMINI_MODEL, temperature=0.1)
    if provider == "openai":
        return _openai_llm(_get_api_key("openai"), OPENAI_MODEL)
    if provider == "anthropic":
        return _anthropic_llm(_get_api_key("anthropic"), ANTHROPIC_MODEL)
    # Ollama
    try:
        return _ollama_llm(OLLAMA_MODEL, OLLAMA_BASE_URL)
    except Exception as e:
        raise RuntimeError(f"Ollama unavailable: {e}. Run: ollama serve")


# ─── Streaming output ──────────────────────────────────────────────────────────

def _stream_response(prompt: str) -> str:
    provider = _get_provider()
    full = ""
    placeholder = st.empty()

    # Gemini — native streaming
    if provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=_get_api_key("gemini"))
        model = genai.GenerativeModel(GEMINI_MODEL)
        for chunk in model.generate_content(prompt, stream=True):
            if chunk.text:
                full += chunk.text
                placeholder.markdown(full + "▌")
        placeholder.markdown(full)
        return full

    # Anthropic — native streaming
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=_get_api_key("anthropic"))
        with client.messages.stream(
            model=ANTHROPIC_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                full += text
                placeholder.markdown(full + "▌")
        placeholder.markdown(full)
        return full

    # Groq / OpenAI — LangChain streaming
    if provider in ("groq", "openai"):
        llm = get_llm()
        for chunk in llm.stream(prompt):
            text = chunk.content if hasattr(chunk, "content") else str(chunk)
            full += text
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)
        return full

    # Ollama — invoke (streaming optional)
    llm = get_llm()
    with st.spinner("Generating…"):
        resp = llm.invoke(prompt)
    full = resp.content if hasattr(resp, "content") else str(resp)
    placeholder.markdown(full)
    return full


# ─── Vision calls ─────────────────────────────────────────────────────────────

def _call_vision_with_image(image_bytes: bytes, question: str, lang_instruction: str, ocr_text: str) -> str:
    from image_handler import image_to_base64, resize_for_llm
    provider = _get_provider()
    b64 = image_to_base64(image_bytes)
    resized = resize_for_llm(image_bytes)
    prompt_text = f"{lang_instruction}\n\nOCR text: {ocr_text or '(none)'}\n\nQuestion: {question}"
    placeholder = st.empty()
    full = ""

    if provider == "gemini":
        import google.generativeai as genai, PIL.Image, io
        genai.configure(api_key=_get_api_key("gemini"))
        model = genai.GenerativeModel(GEMINI_VISION_MODEL)
        img_pil = PIL.Image.open(io.BytesIO(resized))
        for chunk in model.generate_content([prompt_text, img_pil], stream=True):
            if chunk.text:
                full += chunk.text
                placeholder.markdown(full + "▌")
        placeholder.markdown(full)
        return full

    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=_get_api_key("openai"))
        response = client.chat.completions.create(
            model=OPENAI_VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": prompt_text},
            ]}],
            max_tokens=1024,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            full += delta
            if full:
                placeholder.markdown(full + "▌")
        placeholder.markdown(full)
        return full

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=_get_api_key("anthropic"))
        with client.messages.stream(
            model=ANTHROPIC_VISION_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": prompt_text},
            ]}],
        ) as stream:
            for text in stream.text_stream:
                full += text
                placeholder.markdown(full + "▌")
        placeholder.markdown(full)
        return full

    if provider == "groq":
        from groq import Groq
        client = Groq(api_key=_get_api_key("groq"))
        resp = client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": prompt_text},
            ]}],
            temperature=0.1,
        )
        full = resp.choices[0].message.content.strip()
        placeholder.markdown(full)
        return full

    # Ollama vision
    import ollama as ollama_sdk
    response = ollama_sdk.chat(
        model=OLLAMA_VISION_MODEL,
        messages=[{"role": "user", "content": prompt_text, "images": [b64]}]
    )
    full = response["message"]["content"].strip()
    placeholder.markdown(full)
    return full


# ─── Public API ────────────────────────────────────────────────────────────────

def ask_agent(data: dict, question: str, chat_history: list[dict] = None) -> str:
    if chat_history is None:
        chat_history = []
    lang_info = detect_language(question)
    prompt = PROMPT_TEMPLATE.format(
        data_summary=get_data_summary(data, MAX_DATA_CHARS),
        language_instruction=get_language_instruction(lang_info["code"]),
        chat_history=format_chat_history(chat_history),
        output_hint=get_output_hint(detect_output_format(question)),
        user_question=question,
    )
    return _stream_response(prompt)


def ask_vision_agent(image_data: dict, question: str, chat_history: list[dict] = None) -> str:
    if chat_history is None:
        chat_history = []
    lang_info = detect_language(question)
    lang_instruction = get_language_instruction(lang_info["code"])

    raw = image_data.get("raw_text", "")
    ocr_text = raw.split("OCR Extracted Text:", 1)[1].strip() if "OCR Extracted Text:" in raw else ""
    img_format = image_data.get("type", "image").upper()
    width = height = 0
    if "Dimensions:" in raw:
        try:
            dim = raw.split("Dimensions:")[1].split("|")[0].strip().replace("px", "")
            width, height = (int(x.strip()) for x in dim.split("x"))
        except Exception:
            pass

    image_bytes = image_data.get("image_bytes")
    if image_bytes:
        try:
            return _call_vision_with_image(image_bytes, question, lang_instruction, ocr_text)
        except Exception as e:
            warnings.warn(f"Vision model failed, falling back to OCR text: {e}")

    # OCR-only fallback via text LLM
    prompt = IMAGE_PROMPT_TEMPLATE.format(
        img_format=img_format, width=width, height=height,
        ocr_text=ocr_text or "(No text detected)",
        language_instruction=lang_instruction,
        user_question=question,
    )
    return _stream_response(prompt)
