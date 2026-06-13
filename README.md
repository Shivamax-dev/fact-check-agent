# FactGuard AI — Automated Fact-Checking Web App

> **Live Demo**: Deploy your own instance in 5 minutes →  [Streamlit Cloud](https://streamlit.io/cloud)

A production-ready fact-checking web app built for the Product Management Trainee assessment. Upload any PDF — the AI extracts specific factual claims and cross-references them against live web data using Google Search grounding.

---

## ✨ Features

| Feature | Details |
|---|---|
| **PDF Upload** | Extract text from any PDF — reports, press releases, whitepapers |
| **AI Claim Extraction** | Gemini 2.0 Flash identifies specific stats, dates, and verifiable figures |
| **Live Web Verification** | Google Search grounding cross-checks claims in real-time |
| **Verdict System** | ✅ Verified / ⚠️ Inaccurate / ❌ False / ❓ Unverifiable |
| **Integrity Score** | Overall document accuracy score (0–100%) |
| **Download Report** | Export results as JSON or CSV |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- A [Google Gemini API Key](https://aistudio.google.com) (free tier available)

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/fact-check-agent.git
cd fact-check-agent

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### API Key Setup (Local)

Create a `.streamlit/secrets.toml` file (never commit this!):

```toml
GEMINI_API_KEY = "AIza..."
```

Or set it as an environment variable:
```bash
export GEMINI_API_KEY="AIza..."
```

Or simply enter it in the app sidebar when prompted.

---

## ☁️ Deploy to Streamlit Cloud (5 minutes)

1. **Push to GitHub**: Create a public repo and push this code
2. **Go to** [share.streamlit.io](https://share.streamlit.io)
3. **Connect your repo** → select `app.py` as the main file
4. **Add your API key** as a Secret:
   - In Streamlit Cloud dashboard → your app → `⋮` → **Edit secrets**
   - Add: `GEMINI_API_KEY = "AIza..."`
5. **Deploy** → get your permanent URL!

---

## 🧪 Testing with the "Trap Document"

The app is specifically designed to catch:
- **Outdated statistics** (marked ⚠️ INACCURATE with the correct current figure)
- **Fabricated numbers** (marked ❌ FALSE with evidence)
- **Plausible-but-wrong claims** (cross-referenced against authoritative sources)

**Test it**: Upload a document with intentional lies and watch the AI flag them with evidence and corrected facts.

---

## 🏗️ Architecture

```
PDF Upload → Text Extraction (PyMuPDF)
                    ↓
          Claim Extraction (Gemini 2.0 Flash)
          [identifies stats, dates, figures]
                    ↓
          For each claim:
          Fact Verification (Gemini + Google Search Grounding)
          [live web search + verdict]
                    ↓
          Report: Verified ✅ | Inaccurate ⚠️ | False ❌
```

---

## 📦 Tech Stack

- **Frontend/Backend**: [Streamlit](https://streamlit.io)
- **AI Model**: Google Gemini 2.0 Flash
- **Search Grounding**: Google Search (via Gemini API)
- **PDF Parsing**: PyMuPDF (fitz)
- **Deployment**: Streamlit Community Cloud

---

## 📁 Project Structure

```
fact-check-agent/
├── app.py                  # Main application
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── .streamlit/
    └── config.toml         # Theme configuration
```

---

*Built as Part 2 of the Product Management Trainee Assessment — FactGuard AI*
