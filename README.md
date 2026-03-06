# 📊 Report Generator AI

A chatbot-style web app that analyzes data files and images, answers questions in **any language**, and exports professional reports — powered by your choice of AI engine.

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=bestnaveen/report-agent&branch=main&mainModule=app.py)

---

## ✨ Features

| Feature | Details |
|---------|---------|
| **Multi-format upload** | CSV, Excel, JSON, PDF, TXT, PNG, JPG, WEBP |
| **Vision AI** | Upload images → AI describes content + OCR text extraction |
| **Multi-lingual** | Ask in Hindi, Spanish, Arabic, Japanese, 35+ languages — responds in the same language |
| **Smart charts** | Bar, Line, Pie, Scatter, Heatmap (Plotly, dark theme) |
| **Export** | PDF, DOCX, CSV reports + PNG chart images |
| **Streaming output** | Responses appear token-by-token — feels instant |
| **3 AI Providers** | Groq (fastest), Gemini Flash (best vision), Ollama (local & private) |
| **Phase 2** | RAG (ChromaDB), chat persistence (SQLite) |

---

## 🚀 How to Run the App (Step by Step)

> No technical experience needed. Follow each step one at a time.

---

### Step 1 — Open Terminal

Press **`Cmd + Space`** → type **Terminal** → press **Enter**

---

### Step 2 — Go to the App Folder

```bash
cd /Users/mobility-server/Desktop/ai_agent/report-agent
```

---

### Step 3 — Activate the App Environment

```bash
source venv/bin/activate
```

> You will see `(venv)` appear at the start of the line. That means it worked.

---

### Step 4 — Start Ollama (Local AI Engine)

```bash
ollama serve &
```

> Wait 3 seconds. You can ignore any text that appears.

---

### Step 5 — Launch the App

```bash
streamlit run app.py
```

> Wait about 5 seconds. You will see:
> ```
> Local URL: http://localhost:8501
> ```

---

### Step 6 — Open in Browser

The browser **opens automatically**. If it does not, open **Google Chrome** and go to:

```
http://localhost:8501
```

---

### Step 7 — Choose Your AI Provider

On the screen you will see **5 options**:

| Option | Speed | What to do |
|--------|-------|-----------|
| ⚡ **Groq** | ~500 tok/s · FASTEST FREE | Click → paste free API key from [console.groq.com](https://console.groq.com) |
| ✨ **Gemini Flash** | ~400 tok/s · BEST VISION | Click → paste free API key from [aistudio.google.com](https://aistudio.google.com) |
| 🤖 **OpenAI** | ~200 tok/s · GPT-4o | Click → paste API key from [platform.openai.com](https://platform.openai.com/api-keys) |
| 🧠 **Claude** | ~180 tok/s · SMARTEST | Click → paste API key from [console.anthropic.com](https://console.anthropic.com) |
| 🖥️ **Ollama** | Varies · 100% LOCAL | Click → no key needed → click Start |

---

### Step 8 — Upload a File & Ask Questions

1. In the **left sidebar** → click **Browse files**
2. Upload any file from the `sample_data/` folder (e.g. `sample_sales.csv`)
3. Type your question in the chat box at the bottom
4. Press **Enter**

---

### To Stop the App

Press **`Ctrl + C`** in the Terminal window.

---

### Next Time — One-Line Shortcut

```bash
cd /Users/mobility-server/Desktop/ai_agent/report-agent && source venv/bin/activate && ollama serve & sleep 2 && streamlit run app.py
```

Paste this one line and the app opens automatically.

---

## 🧪 Sample Files Included

| File | Type | What to Ask |
|------|------|-------------|
| `sample_sales.csv` | CSV | *"Bar chart of sales by region"* |
| `sample_revenue_by_country.csv` | CSV | *"Which country grew fastest?"* |
| `sample_hr_employees.xlsx` | Excel | *"Average salary by department"* |
| `sample_ecommerce_orders.json` | JSON | *"Top 3 products by revenue"* |
| `sample_business_report.pdf` | PDF | *"What was the Q1 net profit?"* |
| `sample_market_analysis.txt` | TXT | *"What are the top 3 tech trends?"* |
| `sample_invoice.png` | Image | *"What is the total amount due?"* |
| `sample_dashboard_screenshot.png` | Image | *"Who is the top sales rep?"* |

**Multi-lingual test prompts:**
- `इस डेटा का सारांश दीजिए` → Hindi summary
- `Muestre las ventas por región` → Spanish chart
- `كم عدد الصفوف؟` → Arabic row count

---

## 🔧 First-Time Setup (Developers)

```bash
# Create environment
python -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (macOS)
brew install tesseract

# Pull Ollama models (optional — only for local AI)
ollama pull llama3
ollama pull llama3.2-vision

# Generate sample invoice image
python generate_sample_image.py

# Copy environment config
cp .env.example .env

# Run
streamlit run app.py
```

---

## ☁️ Cloud Deployment — Streamlit Community Cloud

> Ollama is local-only and will not work on cloud. Use **Groq** or **Gemini** (both free).

### ⚡ One-Click Deploy

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=bestnaveen/report-agent&branch=main&mainModule=app.py)

Click the button above → sign in with GitHub → add your API keys in **Advanced settings → Secrets** → click **Deploy**.

---

### Step 1 — Push code to GitHub

The repo is already published at:
```
https://github.com/bestnaveen/report-agent
```

### Step 2 — Open Streamlit Community Cloud

Go to **https://share.streamlit.io** and sign in with your GitHub account.

### Step 3 — Create a new app

Click **"Create app"** and fill in:

| Field | Value |
|-------|-------|
| **Repository** | `bestnaveen/report-agent` |
| **Branch** | `main` |
| **Main file path** | `app.py` |

### Step 4 — Add API keys as Secrets

Click **"Advanced settings"** → **Secrets** tab and paste:

```toml
LLM_PROVIDER = "groq"
GROQ_API_KEY = "your_groq_key_here"
GEMINI_API_KEY = "your_gemini_key_here"
OPENAI_API_KEY = "your_openai_key_here"
ANTHROPIC_API_KEY = "your_anthropic_key_here"
```

Get free keys:
- Groq → [console.groq.com](https://console.groq.com)
- Gemini → [aistudio.google.com](https://aistudio.google.com)
- OpenAI → [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Anthropic → [console.anthropic.com](https://console.anthropic.com)

### Step 5 — Deploy

Click **"Deploy"**. Your app will be live in ~2 minutes at:
```
https://bestnaveen-report-agent.streamlit.app
```

### Updating the deployed app

Any `git push` to the `main` branch automatically redeploys:

```bash
git add .
git commit -m "your changes"
git push origin main
```

---

## 📁 File Structure

```
report-agent/
├── app.py                    # Streamlit UI + provider selection
├── agent.py                  # AI brain — text, vision, streaming
├── data_loader.py            # File parser (all formats)
├── image_handler.py          # Image processing + OCR
├── language_utils.py         # 35+ language detection
├── chart_maker.py            # Plotly chart renderer + PNG export
├── report_exporter.py        # PDF / DOCX / CSV export
├── utils.py                  # Format detection, JSON extraction
├── config.py                 # All settings & provider metadata
├── rag_engine.py             # Phase 2: ChromaDB RAG
├── memory.py                 # Phase 2: SQLite chat persistence
├── generate_sample_image.py  # Script to generate sample invoice PNG
├── requirements.txt
├── .env.example
├── .streamlit/
│   └── config.toml           # Forces dark theme
└── sample_data/
    ├── sample_sales.csv
    ├── sample_revenue_by_country.csv
    ├── sample_hr_employees.xlsx
    ├── sample_ecommerce_orders.json
    ├── sample_business_report.pdf
    ├── sample_market_analysis.txt
    ├── sample_invoice.png
    └── sample_dashboard_screenshot.png
```

---

## 🤖 AI Providers Compared

| Provider | Speed | Accuracy | Vision | Cost | Get Key |
|----------|-------|----------|--------|------|---------|
| ⚡ **Groq** | ~500 tok/s | ⭐⭐⭐⭐⭐ | ✅ | Free tier | [console.groq.com](https://console.groq.com) |
| ✨ **Gemini Flash** | ~400 tok/s | ⭐⭐⭐⭐⭐ | ✅ Best | Free tier | [aistudio.google.com](https://aistudio.google.com) |
| 🤖 **OpenAI GPT-4o** | ~200 tok/s | ⭐⭐⭐⭐⭐ | ✅ | Paid (cheap) | [platform.openai.com](https://platform.openai.com/api-keys) |
| 🧠 **Claude Sonnet** | ~180 tok/s | ⭐⭐⭐⭐⭐ | ✅ | Paid | [console.anthropic.com](https://console.anthropic.com) |
| 🖥️ **Ollama** | Varies | ⭐⭐⭐⭐ | ✅ | Free | No key — runs locally |

> **Recommendation:** Use **Groq** or **Gemini** for free fast responses. Use **Claude** for best reasoning on complex data analysis.

https://mobility.streamlit.app/
