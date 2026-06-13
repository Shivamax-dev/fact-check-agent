# FactGuard AI — PDF Fact-Checking Web App

A web app I built to automatically verify factual claims in PDF documents against live web data. Upload any PDF and get a detailed report showing which claims are accurate, outdated, or false.

## 🔍 What it does

Marketing reports, press releases, and whitepapers are often full of outdated statistics or unverified claims. I built this tool to act as a **"Truth Layer"** — it reads a PDF, pulls out every specific factual claim, and checks each one against live web sources in real time.

## ✨ Features

- **PDF Upload** — works with any PDF (reports, whitepapers, press releases)
- **Smart Claim Extraction** — identifies stats, percentages, dates, and financial figures
- **Live Verification** — checks each claim against real-time web data
- **Clear Verdicts** — ✅ Verified / ⚠️ Inaccurate / ❌ False / ❓ Unverifiable
- **Real Facts** — shows the correct data when a claim is wrong
- **Integrity Score** — overall accuracy percentage for the document
- **Download Report** — export results as JSON or CSV

## 🛠️ Tech Stack

- **Frontend + Backend** — Streamlit
- **AI Model** — Google Gemini 2.0 Flash
- **Web Search** — Google Search Grounding (real-time)
- **PDF Parsing** — PyMuPDF
- **Deployment** — Streamlit Community Cloud

## 🚀 How to Run Locally

### Prerequisites
- Python 3.9+
- A free Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Setup

```bash
# Clone the repo
git clone https://github.com/Shivamax-dev/fact-check-agent.git
cd fact-check-agent

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### API Key (Local)

Create a file at `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_key_here"
```

Or just enter your key directly in the app sidebar when it opens.

## ☁️ Deployment

Deployed on **Streamlit Community Cloud**.

Steps I followed:
1. Pushed code to this GitHub repo
2. Connected the repo on [share.streamlit.io](https://share.streamlit.io)
3. Added `GEMINI_API_KEY` under app secrets
4. Deployed and got a live URL

## 📁 Project Structure

```
fact-check-agent/
├── app.py                  # Main application
├── requirements.txt        # Dependencies
├── README.md               # This file
└── .streamlit/
    └── config.toml         # Theme config
```

## 💡 How I Built It

I designed the pipeline in 4 stages:

1. **Extract** — PyMuPDF pulls all text from the uploaded PDF
2. **Identify** — Gemini reads the text and returns a structured list of verifiable claims (only stats, dates, figures — not opinions)
3. **Verify** — For each claim, Gemini searches the web and compares the claim to live sources
4. **Report** — Results are displayed with verdicts, evidence, and corrected facts where needed

## 📬 Contact

Made by **Shivam Maurya**
