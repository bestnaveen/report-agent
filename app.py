import os
import tempfile
import streamlit as st
import streamlit.components.v1 as components

from config import (
    ALL_SUPPORTED_EXTENSIONS, SUPPORTED_IMAGE_EXTENSIONS,
    MULTILINGUAL_ENABLED, RAG_ENABLED, PROVIDER_INFO
)
from data_loader import load_file
from chart_maker import try_make_chart, chart_to_png
from report_exporter import export_to_csv, export_to_docx, export_to_pdf
from language_utils import detect_language, get_language_flag

st.set_page_config(
    page_title="Report Generator AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session State ─────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "messages": [], "loaded_data": None, "all_data": {},
        "chart_pngs": [], "last_df": None, "last_response": "",
        "llm_provider": None,
        "groq_api_key": "", "gemini_api_key": "",
        "openai_api_key": "", "anthropic_api_key": "", "mistral_api_key": "",
        "provider_confirmed": False,
        "theme": "dark",  # default dark
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

dark = st.session_state.theme == "dark"

# ─── Theme Colors ──────────────────────────────────────────────────────────────
if dark:
    BG       = "#0a0a1a"
    SURFACE  = "rgba(22,22,48,0.85)"
    SURFACE2 = "rgba(30,30,60,0.75)"
    BORDER   = "rgba(99,102,241,0.15)"
    TEXT     = "#e8ecf4"
    MUTED    = "#8892b0"
    ACCENT   = "#7c3aed"
    ACCENT2  = "#6d28d9"
    CARD     = "rgba(26,26,52,0.9)"
    SIDEBAR  = "rgba(12,12,28,0.95)"
    SBORDER  = "rgba(99,102,241,0.12)"
    INPUT_BG = "rgba(30,30,60,0.6)"
    BADGE_BG = "rgba(124,58,237,0.15)"
    CHAT_USER  = "rgba(30,30,60,0.6)"
    CHAT_ASST  = "rgba(22,22,48,0.7)"
    TOP_BAR  = "rgba(12,12,28,0.9)"
    CHIP_BG  = "rgba(124,58,237,0.1)"
    CHIP_BR  = "rgba(124,58,237,0.25)"
    SHADOW   = "rgba(0,0,0,.6)"
    GLOW     = "rgba(124,58,237,0.3)"
    TOGGLE_LABEL = "☀️  Light"
else:
    BG       = "#f0f2f9"
    SURFACE  = "rgba(255,255,255,0.85)"
    SURFACE2 = "rgba(245,247,255,0.8)"
    BORDER   = "rgba(124,58,237,0.12)"
    TEXT     = "#1a1a2e"
    MUTED    = "#64748b"
    ACCENT   = "#7c3aed"
    ACCENT2  = "#6d28d9"
    CARD     = "rgba(255,255,255,0.9)"
    SIDEBAR  = "rgba(255,255,255,0.92)"
    SBORDER  = "rgba(124,58,237,0.1)"
    INPUT_BG = "rgba(245,247,255,0.7)"
    BADGE_BG = "rgba(124,58,237,0.08)"
    CHAT_USER  = "rgba(245,247,255,0.8)"
    CHAT_ASST  = "rgba(255,255,255,0.85)"
    TOP_BAR  = "rgba(255,255,255,0.9)"
    CHIP_BG  = "rgba(124,58,237,0.06)"
    CHIP_BR  = "rgba(124,58,237,0.15)"
    SHADOW   = "rgba(124,58,237,.08)"
    GLOW     = "rgba(124,58,237,0.12)"
    TOGGLE_LABEL = "🌙  Dark"

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, *::before, *::after {{ box-sizing: border-box; }}

/* ── Base ── */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
.main, .main > div {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: {BG} !important;
    color: {TEXT} !important;
}}

/* ── Animated gradient background ── */
.stApp {{
    background: {'linear-gradient(135deg, #0a0a1a 0%, #0f0f2e 40%, #150d25 70%, #0a0a1a 100%)' if dark else 'linear-gradient(135deg, #f0f2f9 0%, #e8e6f6 40%, #f0eef9 70%, #f0f2f9 100%)'} !important;
}}

/* ── Sidebar (glass) ── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div {{
    background: {SIDEBAR} !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid {SBORDER} !important;
}}

/* ── Typography ── */
p, span, label, li, td, th, div {{ color: {TEXT} !important; }}
h1, h2, h3, h4 {{ color: {TEXT} !important; font-weight: 700 !important; }}
a {{ color: {ACCENT} !important; text-decoration: none !important; }}
a:hover {{ text-decoration: underline !important; }}
code {{
    color: {ACCENT} !important;
    background: {'rgba(124,58,237,.15)' if dark else 'rgba(124,58,237,.08)'} !important;
    border-radius: 6px !important; padding: 2px 7px !important; font-size: .85em !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {'rgba(124,58,237,.4)' if dark else 'rgba(124,58,237,.25)'}; border-radius: 4px; }}

/* ── Block container ── */
.main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

/* ══ SIDEBAR COMPONENTS ══ */
.logo-bar {{
    padding: 20px 16px 16px; border-bottom: 1px solid {SBORDER};
    display: flex; align-items: center; gap: 12px;
}}
.logo-icon {{
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #7c3aed, #a855f7, #6366f1);
    border-radius: 12px; display: flex; align-items: center;
    justify-content: center; font-size: 1.2rem; flex-shrink: 0;
    box-shadow: 0 4px 15px rgba(124,58,237,.4), 0 0 30px rgba(124,58,237,.15);
    transform: perspective(500px) rotateY(-5deg);
    transition: transform .3s;
}}
.logo-icon:hover {{ transform: perspective(500px) rotateY(5deg) scale(1.05); }}
.logo-text {{ font-size: 1.05rem; font-weight: 800; color: {TEXT} !important; line-height: 1.1; }}
.logo-sub  {{ font-size: .65rem; color: {MUTED} !important; margin-top: 2px; letter-spacing: .5px; }}

.pill-row {{ display: flex; gap: 5px; flex-wrap: wrap; padding: 12px 14px 4px; }}
.pill {{
    font-size: .62rem; font-weight: 600; letter-spacing: .4px;
    background: {CHIP_BG}; border: 1px solid {CHIP_BR};
    border-radius: 20px; padding: 3px 10px; color: {TEXT} !important;
    backdrop-filter: blur(10px);
}}
.sec-label {{
    font-size: .62rem !important; font-weight: 700 !important;
    letter-spacing: 1.3px !important; text-transform: uppercase !important;
    color: {MUTED} !important; padding: 14px 16px 6px;
    display: flex; align-items: center; gap: 6px;
}}
.model-card {{
    margin: 0 10px 8px; background: {SURFACE2};
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid {BORDER}; border-radius: 14px;
    padding: 12px 14px; display: flex; align-items: center; gap: 10px;
    box-shadow: 0 4px 20px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.05)' if dark else 'rgba(255,255,255,.6)'};
    transition: transform .2s, box-shadow .2s;
}}
.model-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 30px {GLOW};
}}
.model-icon {{
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    box-shadow: 0 2px 8px {SHADOW};
}}
.model-name {{ font-size: .85rem; font-weight: 700; color: {TEXT} !important; }}
.model-sub  {{ font-size: .7rem; color: {MUTED} !important; }}
.badge-local {{ background: {'rgba(16,185,129,.2)' if dark else '#d1fae5'}; color: {'#6ee7b7' if dark else '#065f46'} !important; font-size: .6rem; font-weight: 700; padding: 2px 8px; border-radius: 20px; }}
.badge-cloud {{ background: {'rgba(124,58,237,.2)' if dark else '#ede9fe'}; color: {'#c4b5fd' if dark else '#5b21b6'} !important; font-size: .6rem; font-weight: 700; padding: 2px 8px; border-radius: 20px; }}

/* ── File uploader (glass + 3D border) ── */
[data-testid="stFileUploader"] {{
    background: {SURFACE} !important;
    backdrop-filter: blur(12px) !important;
    border: 1.5px dashed {'rgba(124,58,237,.3)' if dark else 'rgba(124,58,237,.2)'} !important;
    border-radius: 14px !important; margin: 0 10px !important;
    transition: all .3s !important;
    box-shadow: 0 2px 12px {SHADOW} !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {ACCENT} !important;
    box-shadow: 0 4px 20px {GLOW} !important;
    transform: translateY(-1px) !important;
}}
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploaderDropzoneInstructions"] * {{ color: {MUTED} !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] svg {{ stroke: {MUTED} !important; }}
[data-testid="stFileUploader"] button {{
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: .8rem !important;
    box-shadow: 0 2px 8px rgba(124,58,237,.3) !important;
}}

/* ── File card (3D float) ── */
.file-card {{
    margin: 6px 10px 0; background: {SURFACE2};
    backdrop-filter: blur(10px);
    border: 1px solid {BORDER};
    border-radius: 12px; padding: 10px 14px;
    display: flex; align-items: center; gap: 10px;
    box-shadow: 0 4px 16px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.05)' if dark else 'rgba(255,255,255,.5)'};
    transition: transform .2s;
}}
.file-card:hover {{ transform: translateY(-2px) translateX(2px); }}
.file-icon {{ font-size: 1.5rem; flex-shrink: 0; filter: drop-shadow(0 2px 4px {SHADOW}); }}
.file-name-text {{ font-size: .78rem !important; font-weight: 600 !important; color: {TEXT} !important;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.file-meta {{ font-size: .67rem !important; color: {MUTED} !important; margin-top: 1px; }}

/* ── Sidebar buttons (3D gradient) ── */
.stButton > button {{
    background: linear-gradient(135deg, #7c3aed, #a855f7, #6366f1) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; padding: 10px 16px !important;
    font-size: .82rem !important; font-weight: 600 !important;
    width: 100% !important; transition: all .3s !important;
    box-shadow: 0 4px 15px rgba(124,58,237,.35), inset 0 1px 0 rgba(255,255,255,.2) !important;
    text-shadow: 0 1px 2px rgba(0,0,0,.2) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,.5), inset 0 1px 0 rgba(255,255,255,.2) !important;
}}
.stButton > button:active {{
    transform: translateY(0px) !important;
    box-shadow: 0 2px 8px rgba(124,58,237,.3), inset 0 2px 4px rgba(0,0,0,.15) !important;
}}
.stButton > button p, .stButton > button span {{ color: #fff !important; }}
.clear-btn .stButton > button {{
    background: {'rgba(30,30,60,.5)' if dark else 'rgba(245,247,255,.8)'} !important;
    color: {MUTED} !important;
    border: 1px solid {BORDER} !important;
    box-shadow: 0 2px 8px {SHADOW} !important;
    text-shadow: none !important;
    backdrop-filter: blur(8px) !important;
}}
.clear-btn .stButton > button p,
.clear-btn .stButton > button span {{ color: {MUTED} !important; }}
.clear-btn .stButton > button:hover {{
    background: {SURFACE2} !important; border-color: {'rgba(124,58,237,.3)' if dark else 'rgba(124,58,237,.2)'} !important;
    transform: translateY(-1px) !important; box-shadow: 0 4px 12px {SHADOW} !important;
}}

/* ── Theme toggle — fixed near Deploy button ── */
[data-testid="element-container"]:has(.theme-marker) {{
    height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important;
}}
[data-testid="element-container"]:has(.theme-marker) + [data-testid="element-container"] {{
    position: fixed !important;
    top: 10px !important;
    right: 108px !important;
    z-index: 99999 !important;
    width: auto !important;
}}
[data-testid="element-container"]:has(.theme-marker) + [data-testid="element-container"] .stButton > button {{
    background: {SURFACE2} !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT} !important;
    box-shadow: 0 2px 10px {SHADOW} !important;
    border-radius: 10px !important;
    padding: 5px 14px !important;
    font-size: .8rem !important;
    font-weight: 600 !important;
    width: auto !important;
    min-width: 90px !important;
    transform: none !important;
    text-shadow: none !important;
}}
[data-testid="element-container"]:has(.theme-marker) + [data-testid="element-container"] .stButton > button:hover {{
    background: {CHIP_BG} !important;
    box-shadow: 0 4px 16px {GLOW} !important;
    transform: none !important;
}}
[data-testid="element-container"]:has(.theme-marker) + [data-testid="element-container"] .stButton > button p,
[data-testid="element-container"]:has(.theme-marker) + [data-testid="element-container"] .stButton > button span {{
    color: {TEXT} !important;
}}

/* ── Status dot (enhanced glow) ── */
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.4}} }}
@keyframes glow-pulse {{ 0%,100%{{box-shadow:0 0 5px rgba(16,185,129,.5),0 0 15px rgba(16,185,129,.2)}} 50%{{box-shadow:0 0 10px rgba(16,185,129,.8),0 0 30px rgba(16,185,129,.3)}} }}
.dot-green {{ display:inline-block;width:8px;height:8px;background:#10b981;border-radius:50%;
    animation:glow-pulse 2s infinite;margin-right:5px; }}

/* ── Download buttons ── */
[data-testid="stDownloadButton"] button {{
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important; color: #fff !important;
    border: none !important; border-radius: 10px !important;
    font-size: .78rem !important; font-weight: 600 !important; width: 100% !important;
    box-shadow: 0 3px 12px rgba(124,58,237,.3) !important;
    transition: all .2s !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,.45) !important;
}}
[data-testid="stDownloadButton"] button p,
[data-testid="stDownloadButton"] button span {{ color: #fff !important; }}

/* ══ MAIN AREA ══ */
.top-bar {{
    background: {TOP_BAR};
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid {BORDER};
    padding: 14px 24px; display: flex; align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px {SHADOW};
}}
.top-bar-title {{ font-size: 1.05rem; font-weight: 700; color: {TEXT} !important; }}
.top-bar-sub   {{ font-size: .72rem; color: {MUTED} !important; margin-top: 2px; }}
.top-badges    {{ display: flex; gap: 8px; }}
.top-badge {{
    background: {CHIP_BG}; border: 1px solid {CHIP_BR};
    border-radius: 20px; padding: 5px 14px;
    font-size: .72rem; font-weight: 500; color: {TEXT} !important;
    backdrop-filter: blur(8px);
    transition: all .2s;
}}
.top-badge:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px {GLOW}; }}

/* ── Hero (3D text + floating effect) ── */
.hero-area {{
    text-align: center; padding: 50px 32px 32px;
    max-width: 720px; margin: 0 auto;
}}
.hero-title {{
    font-size: 2.6rem; font-weight: 800; color: {TEXT} !important;
    letter-spacing: -.5px; line-height: 1.15; margin: 0 0 14px;
    text-shadow: 0 2px 10px {SHADOW};
}}
.hero-gradient {{
    background: linear-gradient(135deg, #7c3aed, #a855f7, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 2px 8px rgba(124,58,237,.3));
}}
.hero-sub {{ font-size: .95rem; color: {MUTED} !important; margin: 0 0 22px; }}
.hero-pills {{ display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }}
.hero-pill {{
    background: {CHIP_BG}; border: 1px solid {CHIP_BR};
    border-radius: 22px; padding: 6px 16px;
    font-size: .75rem; color: {TEXT} !important; font-weight: 500;
    display: inline-flex; align-items: center; gap: 5px;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.05)' if dark else 'rgba(255,255,255,.5)'};
    transition: all .25s;
}}
.hero-pill:hover {{
    transform: translateY(-3px) scale(1.03);
    box-shadow: 0 6px 20px {GLOW};
}}

/* ── Step bar ── */
.step-bar {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 24px 2px;
}}
.step-left  {{ font-size: .72rem; font-weight: 700; color: {ACCENT} !important; letter-spacing: .8px; text-shadow: 0 0 20px {GLOW}; }}
.step-right {{ font-size: .7rem; font-weight: 500; color: {MUTED} !important; letter-spacing: .6px; }}

/* ══ PROVIDER CARDS (3D glass) ══ */
.pcard {{
    background: {CARD};
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 2px solid {BORDER};
    border-bottom: none;
    border-radius: 18px 18px 0 0;
    padding: 22px 18px 18px;
    transition: all .3s cubic-bezier(.25,.8,.25,1);
    min-height: 190px;
    box-shadow: 0 4px 20px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.05)' if dark else 'rgba(255,255,255,.5)'};
    position: relative;
    overflow: hidden;
}}
.pcard::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, transparent, {'rgba(124,58,237,.3)' if dark else 'rgba(124,58,237,.2)'}, transparent);
    opacity: 0; transition: opacity .3s;
}}
.pcard:hover::before {{ opacity: 1; }}
.pcard.sel {{
    border-color: {ACCENT};
    background: {'rgba(124,58,237,.12)' if dark else 'rgba(124,58,237,.05)'};
    box-shadow: 0 0 0 4px {'rgba(124,58,237,.15)' if dark else 'rgba(124,58,237,.1)'}, 0 8px 30px {GLOW};
}}
.pcard.sel::before {{ opacity: 1; background: linear-gradient(90deg, #7c3aed, #a855f7, #ec4899); }}
.pcard:not(.sel):hover {{
    border-color: {'rgba(124,58,237,.4)' if dark else 'rgba(124,58,237,.25)'};
    box-shadow: 0 8px 30px {GLOW};
    transform: translateY(-4px);
}}

/* Provider SELECT button as card footer */
.element-container:has(.pcard) + .element-container .stButton > button {{
    background: {SURFACE2} !important;
    backdrop-filter: blur(10px) !important;
    border: 2px solid {BORDER} !important;
    border-top: 1px solid {BORDER} !important;
    border-radius: 0 0 16px 16px !important;
    margin-top: 0px !important;
    color: {TEXT} !important;
    box-shadow: 0 4px 16px {SHADOW} !important;
    transform: none !important;
    font-size: .82rem !important;
    font-weight: 600 !important;
    text-shadow: none !important;
}}
.element-container:has(.pcard) + .element-container .stButton > button p,
.element-container:has(.pcard) + .element-container .stButton > button span {{
    color: {TEXT} !important;
}}
.element-container:has(.pcard.sel) + .element-container .stButton > button {{
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    border-color: {ACCENT} !important;
    color: #fff !important;
    box-shadow: 0 6px 20px rgba(124,58,237,.4), inset 0 1px 0 rgba(255,255,255,.2) !important;
    text-shadow: 0 1px 2px rgba(0,0,0,.2) !important;
}}
.element-container:has(.pcard.sel) + .element-container .stButton > button p,
.element-container:has(.pcard.sel) + .element-container .stButton > button span {{
    color: #fff !important;
}}

/* Custom API placeholder card */
.pcard-custom {{
    background: {SURFACE2};
    backdrop-filter: blur(12px);
    border: 2px dashed {'rgba(124,58,237,.25)' if dark else 'rgba(124,58,237,.15)'};
    border-radius: 18px;
    padding: 20px 16px;
    min-height: 238px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 8px; color: {MUTED} !important;
    font-size: .82rem; text-align: center;
    transition: all .3s;
}}
.pcard-custom:hover {{ border-color: {ACCENT}; transform: translateY(-2px); }}

/* ── Key section (glass) ── */
.key-section {{
    background: {SURFACE};
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid {BORDER};
    border-radius: 16px; padding: 20px 22px; margin: 14px 24px 0;
    box-shadow: 0 4px 20px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.05)' if dark else 'rgba(255,255,255,.5)'};
}}
.key-title {{
    font-size: .65rem !important; font-weight: 700 !important;
    letter-spacing: 1.2px !important; text-transform: uppercase !important;
    color: {MUTED} !important; margin-bottom: 10px !important;
    display: flex; align-items: center; gap: 6px;
}}

/* ── Text input (glow focus) ── */
[data-testid="stTextInput"] input {{
    background: {INPUT_BG} !important;
    backdrop-filter: blur(8px) !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important; color: {TEXT} !important;
    font-size: .88rem !important; padding: 10px 14px !important;
    transition: all .3s !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,.15), 0 4px 16px {GLOW} !important;
}}
[data-testid="stTextInput"] input::placeholder {{ color: {MUTED} !important; }}

/* ── Prompt chips (3D interactive) ── */
.prompts-area {{
    background: {SURFACE};
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid {BORDER};
    border-radius: 16px; padding: 20px 22px; margin: 18px 24px;
    box-shadow: 0 4px 20px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.05)' if dark else 'rgba(255,255,255,.5)'};
}}
.prompts-head {{
    font-size: .62rem !important; font-weight: 700 !important;
    letter-spacing: 1.4px !important; text-transform: uppercase !important;
    color: {MUTED} !important; margin-bottom: 12px !important;
}}
.prompt-grid {{ display: grid; grid-template-columns: repeat(2,1fr); gap: 8px; }}
.p-chip {{
    background: {CHIP_BG}; border: 1px solid {CHIP_BR};
    border-radius: 12px; padding: 10px 14px;
    font-size: .8rem; color: {TEXT} !important; line-height: 1.4;
    transition: all .25s cubic-bezier(.25,.8,.25,1);
    box-shadow: 0 2px 8px {SHADOW};
    cursor: pointer;
}}
.p-chip:hover {{
    background: {'rgba(124,58,237,.12)' if dark else 'rgba(124,58,237,.06)'};
    border-color: {'rgba(124,58,237,.4)' if dark else 'rgba(124,58,237,.25)'};
    transform: translateY(-3px) scale(1.01);
    box-shadow: 0 6px 20px {GLOW};
}}
.p-lang {{ font-size: .67rem; color: {MUTED} !important; display: block; margin-top: 2px; }}

/* ── Chat messages (glass + depth) ── */
[data-testid="stChatMessage"] {{
    background: {CHAT_ASST} !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 16px !important; padding: 16px 20px !important;
    margin: 8px 24px !important;
    box-shadow: 0 4px 20px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.04)' if dark else 'rgba(255,255,255,.5)'} !important;
    transition: transform .2s !important;
}}
[data-testid="stChatMessage"]:hover {{
    transform: translateX(3px) !important;
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    background: {CHAT_USER} !important;
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]):hover {{
    transform: translateX(-3px) !important;
}}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] span {{ color: {TEXT} !important; }}

/* ── Avatars (3D spheres) ── */
[data-testid="chatAvatarIcon-user"] {{
    background: linear-gradient(135deg, #f97316, #fb923c, #fbbf24) !important;
    border-radius: 50% !important; width: 36px !important; height: 36px !important;
    box-shadow: 0 3px 12px rgba(249,115,22,.4), inset 0 -2px 4px rgba(0,0,0,.15), inset 0 2px 4px rgba(255,255,255,.3) !important;
}}
[data-testid="chatAvatarIcon-assistant"] {{
    background: linear-gradient(135deg, #7c3aed, #a855f7, #6366f1) !important;
    border-radius: 50% !important; width: 36px !important; height: 36px !important;
    box-shadow: 0 3px 12px rgba(124,58,237,.4), inset 0 -2px 4px rgba(0,0,0,.15), inset 0 2px 4px rgba(255,255,255,.3) !important;
}}

/* ── Lang badge (glow) ── */
.lang-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    background: {'rgba(124,58,237,.2)' if dark else 'rgba(124,58,237,.08)'};
    border: 1px solid {'rgba(124,58,237,.4)' if dark else 'rgba(124,58,237,.2)'};
    border-radius: 20px; padding: 3px 12px;
    font-size: .72rem; font-weight: 600; color: {'#c4b5fd' if dark else '#6d28d9'} !important;
    margin-bottom: 6px;
    box-shadow: 0 0 12px {'rgba(124,58,237,.15)' if dark else 'rgba(124,58,237,.08)'};
}}

/* ── Chat input & bottom bar (glass) ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] section,
.stBottom, .stBottom > div {{
    background: {SURFACE} !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-top: 1px solid {BORDER} !important;
}}
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {{
    background: transparent !important;
    border-top: none !important;
}}
[data-testid="stChatInput"] textarea {{
    background: {INPUT_BG} !important;
    backdrop-filter: blur(8px) !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 16px !important; color: {TEXT} !important;
    font-size: .9rem !important; caret-color: {ACCENT} !important;
    box-shadow: 0 2px 12px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.04)' if dark else 'rgba(255,255,255,.4)'} !important;
    transition: all .3s !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,.12), 0 4px 20px {GLOW} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: {MUTED} !important; }}
[data-testid="stChatInput"] button {{
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    border-radius: 14px !important; border: none !important;
    box-shadow: 0 4px 15px rgba(124,58,237,.4), inset 0 1px 0 rgba(255,255,255,.2) !important;
    transition: all .2s !important;
}}
[data-testid="stChatInput"] button:hover {{
    transform: scale(1.05) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,.5) !important;
}}
[data-testid="stChatInput"] button svg {{ fill: #fff !important; }}

/* ── Footer (glass) ── */
.footer-bar {{
    background: {SURFACE};
    backdrop-filter: blur(12px);
    border-top: 1px solid {BORDER};
    padding: 10px 28px; display: flex; align-items: center;
    gap: 20px; justify-content: center;
    box-shadow: 0 -2px 12px {SHADOW};
}}
.footer-item {{ font-size: .68rem; color: {MUTED} !important; display: flex; align-items: center; gap: 5px; }}

/* ── Misc (enhanced) ── */
details[data-testid="stExpander"] {{
    background: {SURFACE2} !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important; margin: 4px 10px !important;
    box-shadow: 0 2px 10px {SHADOW} !important;
}}
details summary {{ color: {MUTED} !important; font-size: .8rem !important; }}
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER} !important; border-radius: 12px !important; overflow: hidden !important;
    box-shadow: 0 4px 16px {SHADOW} !important;
}}
[data-testid="stDataFrame"] th {{ background: {SURFACE2} !important; color: {TEXT} !important; }}
[data-testid="stPlotlyChart"] {{
    background: {SURFACE} !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 16px !important; padding: 10px !important;
    box-shadow: 0 4px 20px {SHADOW}, inset 0 1px 0 {'rgba(255,255,255,.04)' if dark else 'rgba(255,255,255,.4)'} !important;
}}
[data-testid="stAlert"] {{ border-radius: 12px !important; }}
[data-testid="stCaptionContainer"] p {{ color: {MUTED} !important; font-size: .74rem !important; }}
[data-testid="stImage"] img {{ border-radius: 14px !important; border: 1px solid {BORDER} !important; box-shadow: 0 4px 16px {SHADOW} !important; }}
hr {{ border: none !important; border-top: 1px solid {BORDER} !important; margin: 6px 0 !important; }}

/* ── Streamlit native header bar (glass) ── */
header[data-testid="stHeader"] {{
    background: {TOP_BAR} !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-bottom: 1px solid {BORDER} !important;
}}
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] svg,
header[data-testid="stHeader"] span,
header[data-testid="stHeader"] p {{
    color: {TEXT} !important;
    fill: {TEXT} !important;
    stroke: {TEXT} !important;
}}
[data-testid="stDecoration"] {{
    background: linear-gradient(135deg, #7c3aed, #a855f7, #ec4899) !important;
    height: 2px !important;
}}
/* Main menu button in header */
[data-testid="stMainMenuButton"] button {{
    background: transparent !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    backdrop-filter: blur(8px) !important;
}}
[data-testid="stStatusWidget"] {{
    color: {TEXT} !important;
}}

/* ── File uploader — force theme colors ── */
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"] {{
    background: {SURFACE} !important;
    color: {TEXT} !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] div,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] span {{
    color: {MUTED} !important;
}}
[data-testid="stFileUploaderDropzone"] svg {{
    stroke: {MUTED} !important;
    fill: none !important;
}}

/* ── Sidebar text overrides ── */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {{
    color: {TEXT} !important;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#   SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="logo-bar">
        <div class="logo-icon">🚀</div>
        <div>
            <div class="logo-text">Report AI</div>
            <div class="logo-sub">Next-gen Analytics</div>
        </div>
    </div>
    <div class="pill-row">
        <span class="pill">35 LANGUAGES</span>
        <span class="pill">5 CHART TYPES</span>
        <span class="pill">PDF • DOCX • CSV</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.provider_confirmed and st.session_state.llm_provider:
        p = st.session_state.llm_provider
        info = PROVIDER_INFO[p]
        is_local = p == "ollama"
        badge_cls = "badge-local" if is_local else "badge-cloud"
        badge_txt = "100% LOCAL" if is_local else "CLOUD API"
        st.markdown(f"""
        <div class="sec-label">⚡ Active Engine &nbsp;
            <span class="{badge_cls}">{badge_txt}</span>
        </div>
        <div class="model-card">
            <div class="model-icon" style="background:{'rgba(124,58,237,.2)' if is_local else 'rgba(99,102,241,.2)'};">
                {info['icon']}
            </div>
            <div>
                <div class="model-name">{info['label']}</div>
                <div class="model-sub">{info['speed']} &nbsp;·&nbsp; Active</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="sec-label">☁️ Upload Data</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("upload", type=ALL_SUPPORTED_EXTENSIONS,
        accept_multiple_files=False, label_visibility="collapsed")
    st.markdown(f'<p style="text-align:center;font-size:.65rem;color:{MUTED};padding:4px 10px;">CSV • Excel • JSON • PDF • TXT • Images</p>', unsafe_allow_html=True)

    if uploaded:
        suffix = "." + uploaded.name.rsplit(".", 1)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read()); tmp_path = tmp.name
        try:
            with st.spinner("Parsing…"):
                data = load_file(tmp_path)
                data["filename"] = uploaded.name
                st.session_state.loaded_data = data
                st.session_state.all_data[uploaded.name] = data
        except Exception as e:
            st.error(f"Failed: {e}"); data = None
        finally:
            os.unlink(tmp_path)

        if data:
            ext = uploaded.name.rsplit(".", 1)[-1].lower()
            icons = {"pdf":"📕","csv":"📗","xlsx":"📘","xls":"📘","json":"📒","txt":"📄",
                     "png":"🖼️","jpg":"🖼️","jpeg":"🖼️","webp":"🖼️"}
            ficon = icons.get(ext, "📄")
            meta = f"{data['row_count']} rows · {data['col_count']} cols" if data['row_count'] else ext.upper()
            st.markdown(f"""
            <div class="file-card">
                <div class="file-icon">{ficon}</div>
                <div style="min-width:0;">
                    <div class="file-name-text">{uploaded.name}</div>
                    <div class="file-meta">{meta}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if ext in SUPPORTED_IMAGE_EXTENSIONS:
                st.image(data["image_bytes"], use_container_width=True)
                ocr = data["raw_text"].split("OCR Extracted Text:", 1)
                if len(ocr) > 1 and ocr[1].strip():
                    with st.expander("🔤 OCR Text"): st.text(ocr[1].strip())
            else:
                if data["columns"]:
                    with st.expander("📊 Columns"):
                        st.markdown(" · ".join(f"`{c}`" for c in data["columns"]))
                if data["dataframe"] is not None:
                    with st.expander("👁 Preview"):
                        st.dataframe(data["dataframe"].head(5), use_container_width=True)

    if st.session_state.loaded_data or st.session_state.messages:
        st.markdown(f'<div class="sec-label">⬇️ Export Report</div>', unsafe_allow_html=True)
        lr = st.session_state.last_response
        ldf = st.session_state.last_df
        cpngs = [m.get("chart_png") for m in st.session_state.messages if m.get("chart_png")]

        exp_dark = dark
        components.html(f"""
        <style>
        *{{font-family:'Inter',-apple-system,sans-serif;box-sizing:border-box;margin:0;padding:0;}}
        body{{background:transparent;padding:0 10px;}}
        .grid{{display:grid;grid-template-columns:1fr 1fr;gap:7px;}}
        .btn{{display:flex;align-items:center;gap:7px;border:1px solid;border-radius:9px;
            padding:9px 12px;font-size:.78rem;font-weight:600;cursor:pointer;width:100%;background:none;}}
        .pdf {{background:{'#2d0a0a' if exp_dark else '#fef2f2'};color:{'#fca5a5' if exp_dark else '#991b1b'};border-color:{'#7f1d1d' if exp_dark else '#fecaca'};}}
        .docx{{background:{'#0a1a2d' if exp_dark else '#eff6ff'};color:{'#93c5fd' if exp_dark else '#1e40af'};border-color:{'#1e3a5f' if exp_dark else '#bfdbfe'};}}
        .csv {{background:{'#0a2d0a' if exp_dark else '#f0fdf4'};color:{'#86efac' if exp_dark else '#166534'};border-color:{'#14532d' if exp_dark else '#bbf7d0'};}}
        .png {{background:{'#2d1a0a' if exp_dark else '#fff7ed'};color:{'#fdba74' if exp_dark else '#9a3412'};border-color:{'#7c2d12' if exp_dark else '#fed7aa'};}}
        </style>
        <div class="grid">
            <div class="btn pdf">📕 PDF</div>
            <div class="btn docx">📘 DOCX</div>
            <div class="btn csv">📗 CSV</div>
            <div class="btn png">🖼 PNG</div>
        </div>
        """, height=80)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("PDF", key="xpdf", use_container_width=True):
                try:
                    b = export_to_pdf("Report AI", lr or "No content.", ldf, cpngs or None)
                    st.download_button("⬇ Download", b, "report.pdf", "application/pdf", key="dl_pdf")
                except Exception as e: st.error(str(e))
            if st.button("CSV", key="xcsv", use_container_width=True):
                if ldf is not None:
                    st.download_button("⬇ Download", export_to_csv(ldf), "data.csv", "text/csv", key="dl_csv")
                else: st.warning("No table.")
        with c2:
            if st.button("DOCX", key="xdocx", use_container_width=True):
                try:
                    b = export_to_docx("Report AI", lr or "No content.", ldf, cpngs or None)
                    st.download_button("⬇ Download", b, "report.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="dl_docx")
                except Exception as e: st.error(str(e))
            if cpngs:
                st.download_button("🖼 PNG", cpngs[-1], "chart.png", "image/png", key="dl_chart")

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    if st.button("⊞ Change Provider", use_container_width=True):
        st.session_state.llm_provider = None
        st.session_state.provider_confirmed = False
        st.session_state.messages = []
        st.rerun()
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("↺ Clear Chat & Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_response = ""
        st.session_state.last_df = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="padding:10px 14px 4px;"><span class="dot-green"></span><span style="font-size:.68rem;color:{MUTED};">LOCAL &amp; PRIVATE</span></div>', unsafe_allow_html=True)


# ── Single fixed-position theme toggle (renders on all screens) ────────────
st.markdown('<div class="theme-marker"></div>', unsafe_allow_html=True)
if st.button(TOGGLE_LABEL, key="theme_toggle"):
    st.session_state.theme = "light" if dark else "dark"
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#   MAIN — TOP BAR (after provider confirmed)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.provider_confirmed:
    p = st.session_state.llm_provider
    info = PROVIDER_INFO[p]
    st.markdown(f"""
    <div class="top-bar">
        <div>
            <div class="top-bar-title">Report Generator AI</div>
            <div class="top-bar-sub">Ask in any language &nbsp;·&nbsp; Charts, tables &amp; reports instantly</div>
        </div>
        <div class="top-badges">
            <span class="top-badge">🌐 35+ LANGUAGES</span>
            <span class="top-badge">📊 5 CHART TYPES</span>
            <span class="top-badge" style="background:{'rgba(99,102,241,.2)' if dark else '#eef2ff'};border-color:{'rgba(99,102,241,.4)' if dark else '#c7d2fe'};color:{'#a5b4fc' if dark else '#4338ca'};">{info['icon']} {info['label']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#   PROVIDER SELECTION
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.provider_confirmed:

    # Hero
    st.markdown(f"""
    <div class="hero-area">
        <div class="hero-title">
            <span class="hero-gradient">Report Generator</span> AI
        </div>
        <div class="hero-sub">Upload data or images · Ask in any language · Get charts, tables &amp; reports instantly</div>
        <div class="hero-pills">
            <span class="hero-pill">🧠 Multi-LLM</span>
            <span class="hero-pill">🌐 35+ Languages</span>
            <span class="hero-pill">📊 5 Chart Types</span>
            <span class="hero-pill">📤 PDF · DOCX · CSV · PNG</span>
            <span class="hero-pill">⚡ Streaming Output</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="step-bar">
        <span class="step-left">STEP 1 OF 2</span>
        <span class="step-right">CHOOSE YOUR AI ENGINE</span>
    </div>
    """, unsafe_allow_html=True)

    chosen = st.session_state.llm_provider or ""

    # ── Provider card helper ────────────────────────────────────────────────
    def _card_html(pkey, sel):
        info = PROVIDER_INFO[pkey]
        cls = "pcard sel" if sel else "pcard"
        badge_colors = {
            "groq":      ("#14532d" if dark else "#d1fae5", "#6ee7b7" if dark else "#065f46"),
            "gemini":    ("#1e3a5f" if dark else "#dbeafe", "#93c5fd" if dark else "#1e40af"),
            "openai":    ("#164e63" if dark else "#cffafe", "#67e8f9" if dark else "#155e75"),
            "anthropic": ("#78350f" if dark else "#fef3c7", "#fcd34d" if dark else "#92400e"),
            "mistral":   ("#7c2d12" if dark else "#ffedd5", "#fdba74" if dark else "#9a3412"),
            "ollama":    ("#2e1065" if dark else "#ede9fe", "#c4b5fd" if dark else "#5b21b6"),
        }
        spd_colors = {
            "groq": "#10b981", "gemini": "#3b82f6",
            "openai": "#06b6d4", "anthropic": "#f59e0b", "mistral": "#f97316", "ollama": "#8b5cf6",
        }
        bc, btc = badge_colors.get(pkey, (CHIP_BG, TEXT))
        sc = spd_colors.get(pkey, MUTED)
        return f"""
        <div class="{cls}">
            <div style="font-size:2rem;margin-bottom:10px;line-height:1;">{info['icon']}</div>
            <div style="font-size:1.05rem;font-weight:700;color:{TEXT};margin-bottom:3px;">{info['label']}</div>
            <div style="font-size:.73rem;font-weight:700;color:{sc};margin-bottom:8px;">{info['speed']}</div>
            <div style="display:inline-block;background:{bc};color:{btc};border-radius:20px;
                padding:2px 10px;font-size:.62rem;font-weight:700;letter-spacing:.5px;margin-bottom:10px;">{info['badge']}</div>
            <div style="font-size:.77rem;color:{MUTED};line-height:1.5;">{info['desc']}</div>
        </div>"""

    # ── Row 1: Groq · Gemini · OpenAI ──────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    for col, pkey in zip([col1, col2, col3], ["groq", "gemini", "openai"]):
        with col:
            st.markdown(_card_html(pkey, chosen == pkey), unsafe_allow_html=True)
            lbl = f"✓  {PROVIDER_INFO[pkey]['label']} Selected" if chosen == pkey else f"Select {PROVIDER_INFO[pkey]['label']}"
            if st.button(lbl, key=f"sel_{pkey}", use_container_width=True):
                st.session_state.llm_provider = pkey; st.rerun()

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # ── Row 2: Claude · Mistral · Ollama ─────────────────────────────────
    col4, col5, col6 = st.columns(3)
    for col, pkey in zip([col4, col5, col6], ["anthropic", "mistral", "ollama"]):
        with col:
            st.markdown(_card_html(pkey, chosen == pkey), unsafe_allow_html=True)
            lbl = f"✓  {PROVIDER_INFO[pkey]['label']} Selected" if chosen == pkey else f"Select {PROVIDER_INFO[pkey]['label']}"
            if st.button(lbl, key=f"sel_{pkey}", use_container_width=True):
                st.session_state.llm_provider = pkey; st.rerun()

    # ── API Key Panel ────────────────────────────────────────────────────────
    if chosen and chosen != "ollama":
        info = PROVIDER_INFO[chosen]
        st.markdown(f"""
        <div class="key-section">
            <div class="key-title">🔑 &nbsp;{info['label'].upper()} API KEY</div>
        </div>
        """, unsafe_allow_html=True)
        key_val = st.text_input("apikey",
            value=st.session_state.get(f"{chosen}_api_key", ""),
            type="password", placeholder=info["key_placeholder"],
            label_visibility="collapsed", key=f"inp_{chosen}")
        st.markdown(f'<a href="{info["key_url"]}" target="_blank" style="font-size:.75rem;padding:0 24px;">🔗 Get free API key → {info["key_url"].replace("https://","")}</a>', unsafe_allow_html=True)
        if key_val:
            st.session_state[f"{chosen}_api_key"] = key_val
        if st.button(
            f"✅  Start with {info['label']}" if key_val else "Enter API key above to continue",
            disabled=not key_val, use_container_width=True, key="confirm_btn"):
            st.session_state.provider_confirmed = True; st.rerun()

    elif chosen == "ollama":
        st.markdown(f"""
        <div class="key-section">
            <div class="key-title">🖥️ &nbsp;OLLAMA — NO API KEY NEEDED</div>
            <div style="font-size:.82rem;color:{MUTED};line-height:1.8;">
                Make sure Ollama is running:<br>
                <code>ollama serve</code> &nbsp;&nbsp; <code>ollama pull llama3</code>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🖥️  Start with Ollama", use_container_width=True, key="confirm_ollama"):
            st.session_state.provider_confirmed = True; st.rerun()

    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#   CHAT INTERFACE
# ══════════════════════════════════════════════════════════════════════════════
from agent import ask_agent, ask_vision_agent

if not st.session_state.messages:
    st.markdown(f"""
    <div class="hero-area" style="padding-top:36px;">
        <div class="hero-title"><span class="hero-gradient">Report Generator</span> AI</div>
        <div class="hero-sub">Upload data, ask questions, and get beautiful charts instantly.</div>
        <div class="hero-pills">
            <span class="hero-pill">🧠 Multi-LLM</span>
            <span class="hero-pill">🌐 35+ Languages</span>
            <span class="hero-pill">📊 5 Chart Types</span>
            <span class="hero-pill">📤 Export Ready</span>
        </div>
    </div>
    <div class="prompts-area">
        <div class="prompts-head">✨ Example Prompts</div>
        <div class="prompt-grid">
            <div class="p-chip">📊 Bar chart of sales by region</div>
            <div class="p-chip">📋 Table of average rating by product</div>
            <div class="p-chip">📝 Summarize this data</div>
            <div class="p-chip">🔍 What is the highest Q4 sales value?</div>
            <div class="p-chip">इस डेटा का सारांश दीजिए<span class="p-lang">🇮🇳 Hindi</span></div>
            <div class="p-chip">Muestre ventas por producto<span class="p-lang">🇪🇸 Spanish</span></div>
            <div class="p-chip">كم عدد الصفوف في هذا الملف؟<span class="p-lang">🇸🇦 Arabic</span></div>
            <div class="p-chip">このデータを詳しく分析して<span class="p-lang">🇯🇵 Japanese</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if not st.session_state.loaded_data:
        st.info("👈 Upload a file from the sidebar to get started")

# Chat history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            lang = msg.get("lang")
            if lang and lang["code"] != "en":
                st.markdown(f'<span class="lang-badge">{get_language_flag(lang["code"])}&nbsp;{lang["name"]}</span>', unsafe_allow_html=True)
            fig = try_make_chart(msg["content"])
            if fig:
                st.plotly_chart(fig, use_container_width=True, key=f"chart_hist_{i}")
                if msg.get("chart_png"):
                    st.caption("📸 Chart PNG saved — download from sidebar")
            else:
                st.markdown(msg["content"])

# Chat input
question = st.chat_input("Ask anything about your data… (any language supported)")

if question:
    data = st.session_state.loaded_data
    if data is None:
        st.warning("👈 Upload a file from the sidebar first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    lang_info = detect_language(question)

    with st.chat_message("assistant"):
        if lang_info["code"] != "en":
            st.markdown(f'<span class="lang-badge">{get_language_flag(lang_info["code"])}&nbsp;{lang_info["name"]}</span>', unsafe_allow_html=True)
        try:
            if data.get("is_image"):
                response = ask_vision_agent(data, question, st.session_state.messages[:-1])
            else:
                if RAG_ENABLED:
                    try:
                        from rag_engine import query_vector_store, build_vector_store
                        import copy
                        if "rag_collection" not in st.session_state:
                            st.session_state.rag_collection = build_vector_store(data["raw_text"])
                        chunks = query_vector_store(st.session_state.rag_collection, question)
                        rag_data = copy.deepcopy(data); rag_data["raw_text"] = "\n\n".join(chunks)
                        response = ask_agent(rag_data, question, st.session_state.messages[:-1])
                    except Exception:
                        response = ask_agent(data, question, st.session_state.messages[:-1])
                else:
                    response = ask_agent(data, question, st.session_state.messages[:-1])
        except Exception as e:
            response = f"⚠️ **Error:** {e}"
            st.markdown(response)

        fig = try_make_chart(response)
        chart_png_bytes = None
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=f"chart_new_{len(st.session_state.messages)}")
            chart_png_bytes = chart_to_png(fig)
            if chart_png_bytes:
                st.session_state.chart_pngs.append(chart_png_bytes)
                st.caption("📸 Chart PNG saved — download from sidebar")

    st.session_state.last_response = response
    if data.get("dataframe") is not None:
        st.session_state.last_df = data["dataframe"]
    st.session_state.messages.append({
        "role": "assistant", "content": response,
        "lang": lang_info, "chart_png": chart_png_bytes,
    })

if st.session_state.messages:
    st.markdown(f"""
    <div class="footer-bar">
        <span class="footer-item">🔒 PRIVATE &amp; SECURE</span>
        <span style="color:{BORDER};">|</span>
        <span class="footer-item">⚡ REAL-TIME PROCESSING</span>
        <span style="color:{BORDER};">|</span>
        <span class="footer-item">🌐 35+ LANGUAGES</span>
    </div>
    """, unsafe_allow_html=True)
