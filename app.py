import streamlit as st
import fitz  # PyMuPDF
import json
import time
import re
import pandas as pd
import os
from google import genai
from google.genai import types

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactGuard AI — Automated Fact-Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 50%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}
.hero-subtitle {
    color: #888;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

/* Verdict badges */
.badge-verified {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.5px;
}
.badge-inaccurate {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.5px;
}
.badge-false {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.5px;
}
.badge-unverifiable {
    background: linear-gradient(135deg, #6b7280, #4b5563);
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.5px;
}

/* Claim cards */
.claim-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2d2d4e;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.claim-card:hover { border-color: #6C63FF; }
.claim-text {
    font-size: 1rem;
    font-weight: 500;
    color: #e8e8f0;
    margin-bottom: 0.5rem;
    font-style: italic;
}
.claim-evidence {
    font-size: 0.88rem;
    color: #a0a0b8;
    line-height: 1.6;
    margin-top: 0.5rem;
}
.claim-real-fact {
    font-size: 0.88rem;
    color: #7dd3fc;
    line-height: 1.6;
    margin-top: 0.4rem;
    padding: 0.5rem 0.8rem;
    background: rgba(56, 189, 248, 0.08);
    border-left: 3px solid #38bdf8;
    border-radius: 4px;
}
.claim-source {
    font-size: 0.78rem;
    color: #6c63ff;
    margin-top: 0.4rem;
}

/* Stats bar */
.stats-container {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.stat-box {
    flex: 1;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
}
.stat-verified { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); }
.stat-inaccurate { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); }
.stat-false { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); }
.stat-number { font-size: 2rem; font-weight: 700; }
.stat-label { font-size: 0.8rem; color: #888; margin-top: 0.2rem; }
.stat-verified .stat-number { color: #10b981; }
.stat-inaccurate .stat-number { color: #f59e0b; }
.stat-false .stat-number { color: #ef4444; }

.step-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #a78bfa;
    font-size: 0.9rem;
    margin: 0.5rem 0;
}
.divider { border-top: 1px solid #2d2d4e; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — API KEY
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 FactGuard AI")
    st.markdown("*Automated Fact-Checking powered by Gemini*")
    st.markdown("---")

    # Try secrets first, then env var, then manual input
    # Use try/except because st.secrets.get() still raises if no secrets file exists at all
    try:
        api_key_from_secret = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key_from_secret = ""
    api_key_from_env = os.environ.get("GEMINI_API_KEY", "")
    default_key = api_key_from_secret or api_key_from_env

    if default_key:
        st.success("✅ API Key loaded from secrets")
        gemini_api_key = default_key
    else:
        gemini_api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            placeholder="AIza...",
            help="Get your free key at aistudio.google.com",
        )
        if not gemini_api_key:
            st.info("💡 Enter your Gemini API key to get started.\nGet a free key at [aistudio.google.com](https://aistudio.google.com)")

    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
1. 📄 **Upload** a PDF document
2. 🔬 **Extract** factual claims (stats, dates, figures)
3. 🌐 **Verify** each claim via live web search
4. 📊 **Report** with verdicts & real facts
    """)

    st.markdown("---")
    st.markdown("### Verdict Legend")
    st.markdown('<span class="badge-verified">✅ VERIFIED</span> — Claim matches live data', unsafe_allow_html=True)
    st.markdown('<br><span class="badge-inaccurate">⚠️ INACCURATE</span> — Outdated or wrong figure', unsafe_allow_html=True)
    st.markdown('<br><span class="badge-false">❌ FALSE</span> — No evidence / contradicted', unsafe_allow_html=True)
    st.markdown('<br><span class="badge-unverifiable">❓ UNVERIFIABLE</span> — Cannot confirm', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Built with Gemini 2.0 Flash + Google Search Grounding")


# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🔍 FactGuard AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Upload any PDF — our AI extracts claims and cross-references them against live web data in seconds.</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from an uploaded PDF file."""
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        if text.strip():
            full_text.append(f"[Page {page_num}]\n{text}")
    doc.close()
    return "\n\n".join(full_text)


def extract_claims(client: genai.Client, pdf_text: str) -> list[dict]:
    """Use Gemini to extract specific factual claims from the PDF text."""
    prompt = f"""You are a meticulous fact-checking analyst. Analyze the following document text and extract ALL specific, verifiable factual claims.

Focus ONLY on claims that contain:
- Statistics or percentages (e.g., "X% of users...", "revenue grew by X%")
- Specific numbers or financial figures (e.g., "the market is worth $X billion")
- Dates and timelines (e.g., "launched in 2021", "by 2025")
- Named data points or rankings (e.g., "the #1 platform", "fastest growing")
- Technical specifications or benchmarks
- Named research findings or survey results

Do NOT include vague statements, opinions, or claims that cannot be verified with data.

For each claim, output a JSON array with this exact structure:
{{
  "claims": [
    {{
      "id": 1,
      "claim": "The exact claim as stated in the document",
      "claim_type": "statistic|date|ranking|financial|technical|research",
      "source_quote": "The surrounding sentence from the document for context",
      "page_hint": "Page number if mentioned, otherwise 'unknown'"
    }}
  ]
}}

DOCUMENT TEXT:
---
{pdf_text[:15000]}
---

Return ONLY valid JSON. Extract between 5 and 20 of the most important verifiable claims."""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    raw = response.text.strip() if response.text else ""
    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
        claims = data.get("claims", [])
        # Handle case where model returned the array directly instead of wrapped
        if isinstance(data, list):
            claims = data
        return claims
    except json.JSONDecodeError:
        # Try to find a JSON array or object anywhere in the response
        array_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if array_match:
            try:
                return json.loads(array_match.group())
            except Exception:
                pass
        obj_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if obj_match:
            try:
                data = json.loads(obj_match.group())
                return data.get("claims", [])
            except Exception:
                pass
        st.error(f"❌ Could not parse claim extraction response. Raw response: {raw[:300]}")
        st.stop()


def verify_claim(client: genai.Client, claim: dict) -> dict:
    """Verify a single claim using Gemini with Google Search grounding."""
    prompt = f"""You are a rigorous fact-checker with access to real-time web search. 

CLAIM TO VERIFY: "{claim['claim']}"
CONTEXT: "{claim.get('source_quote', '')}"

Your task:
1. Search the web to find current, authoritative information about this claim.
2. Compare the claim against the real data you find.
3. Give a verdict:
   - VERIFIED: The claim is accurate and supported by current data
   - INACCURATE: The claim has the wrong number/date/figure (outdated or wrong stat)
   - FALSE: The claim is contradicted by evidence or fabricated
   - UNVERIFIABLE: Cannot find enough information to confirm or deny

Respond with ONLY this JSON structure:
{{
  "verdict": "VERIFIED|INACCURATE|FALSE|UNVERIFIABLE",
  "confidence": "HIGH|MEDIUM|LOW",
  "evidence": "1-2 sentences explaining what you found and why you gave this verdict",
  "real_fact": "If INACCURATE or FALSE: state the correct fact here. If VERIFIED: leave empty string.",
  "source_hint": "Brief mention of the type of source that confirms your finding (e.g., 'World Bank data', 'company press release')"
}}

Be precise. If a statistic is even slightly wrong (e.g., 45% vs the real 38%), mark it INACCURATE."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )

        # Extract text from response
        raw = response.text.strip() if response.text else ""

        # Strip markdown code fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        # Find outermost JSON object using bracket matching (handles nested JSON correctly)
        result = None
        start = raw.find('{')
        if start != -1:
            depth = 0
            for i, ch in enumerate(raw[start:], start):
                if ch == '{': depth += 1
                elif ch == '}': depth -= 1
                if depth == 0:
                    try:
                        result = json.loads(raw[start:i+1])
                    except Exception:
                        pass
                    break

        if not result:
            result = {
                "verdict": "UNVERIFIABLE",
                "confidence": "LOW",
                "evidence": "Could not parse verification response.",
                "real_fact": "",
                "source_hint": ""
            }
    except Exception as e:
        result = {
            "verdict": "UNVERIFIABLE",
            "confidence": "LOW",
            "evidence": f"Verification error: {str(e)[:100]}",
            "real_fact": "",
            "source_hint": ""
        }

    return {**claim, **result}


def render_verdict_badge(verdict: str) -> str:
    badge_map = {
        "VERIFIED": '<span class="badge-verified">✅ VERIFIED</span>',
        "INACCURATE": '<span class="badge-inaccurate">⚠️ INACCURATE</span>',
        "FALSE": '<span class="badge-false">❌ FALSE</span>',
        "UNVERIFIABLE": '<span class="badge-unverifiable">❓ UNVERIFIABLE</span>',
    }
    return badge_map.get(verdict.upper(), '<span class="badge-unverifiable">❓ UNKNOWN</span>')


def render_claim_card(result: dict):
    verdict = result.get("verdict", "UNVERIFIABLE").upper()
    badge = render_verdict_badge(verdict)
    confidence = result.get("confidence", "LOW")
    conf_color = {"HIGH": "#10b981", "MEDIUM": "#f59e0b", "LOW": "#ef4444"}.get(confidence, "#888")

    real_fact_html = ""
    if result.get("real_fact"):
        real_fact_html = f'<div class="claim-real-fact">💡 <strong>Real Fact:</strong> {result["real_fact"]}</div>'

    source_html = ""
    if result.get("source_hint"):
        source_html = f'<div class="claim-source">🔗 Source: {result["source_hint"]}</div>'

    st.markdown(f"""
    <div class="claim-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.6rem;">
            <div style="flex:1;">{badge}</div>
            <div style="font-size:0.75rem; color:{conf_color};">Confidence: {confidence}</div>
        </div>
        <div class="claim-text">"{result.get('claim', '')}"</div>
        <div class="claim-evidence">📌 {result.get('evidence', '')}</div>
        {real_fact_html}
        {source_html}
    </div>
    """, unsafe_allow_html=True)


def build_download_report(results: list[dict]) -> str:
    """Build a JSON report for download."""
    summary = {
        "total_claims": len(results),
        "verified": sum(1 for r in results if r.get("verdict") == "VERIFIED"),
        "inaccurate": sum(1 for r in results if r.get("verdict") == "INACCURATE"),
        "false": sum(1 for r in results if r.get("verdict") == "FALSE"),
        "unverifiable": sum(1 for r in results if r.get("verdict") == "UNVERIFIABLE"),
    }
    report = {
        "report_name": "FactGuard AI — Fact-Check Report",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "summary": summary,
        "claims": results,
    }
    return json.dumps(report, indent=2)


def build_csv_report(results: list[dict]) -> str:
    rows = []
    for r in results:
        rows.append({
            "Claim": r.get("claim", ""),
            "Type": r.get("claim_type", ""),
            "Verdict": r.get("verdict", ""),
            "Confidence": r.get("confidence", ""),
            "Evidence": r.get("evidence", ""),
            "Real Fact": r.get("real_fact", ""),
            "Source": r.get("source_hint", ""),
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

uploaded_file = st.file_uploader(
    "📄 Upload your PDF document",
    type=["pdf"],
    help="Upload any PDF — marketing reports, research papers, press releases, or 'trap documents'",
)

if uploaded_file is not None and not gemini_api_key:
    st.warning("⚠️ Please enter your Gemini API key in the sidebar to proceed.")
    st.stop()

if uploaded_file is not None and gemini_api_key:
    # Initialize Gemini client
    try:
        client = genai.Client(api_key=gemini_api_key)
    except Exception as e:
        st.error(f"❌ Failed to initialize Gemini client: {e}")
        st.stop()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── STEP 1: Extract PDF text ──────────────────────────────────────────────
    with st.spinner("📄 Extracting text from PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    if not pdf_text.strip():
        st.error("❌ Could not extract text from this PDF. It may be image-only or encrypted.")
        st.stop()

    word_count = len(pdf_text.split())
    st.success(f"✅ PDF loaded — {word_count:,} words extracted across {pdf_text.count('[Page')} pages")

    with st.expander("📄 View extracted text (preview)", expanded=False):
        st.text(pdf_text[:3000] + ("..." if len(pdf_text) > 3000 else ""))

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── STEP 2: Extract Claims ────────────────────────────────────────────────
    st.markdown("### 🔬 Step 1: Extracting Factual Claims")
    st.markdown('<div class="step-indicator">⚡ Gemini AI is scanning for statistics, dates, and verifiable figures...</div>', unsafe_allow_html=True)

    claims_placeholder = st.empty()

    with st.spinner("Analyzing document for factual claims..."):
        try:
            claims = extract_claims(client, pdf_text)
        except Exception as e:
            st.error(f"❌ Claim extraction failed: {e}")
            st.stop()

    if not claims:
        st.warning("⚠️ No verifiable claims found in this document. Try a document with specific statistics, dates, or figures.")
        st.stop()

    claims_placeholder.success(f"✅ Found **{len(claims)} verifiable claims** — starting fact-check...")

    with st.expander(f"📋 View all {len(claims)} extracted claims", expanded=False):
        for i, claim in enumerate(claims, 1):
            st.markdown(f"**{i}.** {claim.get('claim', '')}  \n*Type: {claim.get('claim_type', 'unknown')} | Context: {claim.get('source_quote', '')[:100]}...*")
            st.markdown("---")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── STEP 3: Verify each claim ─────────────────────────────────────────────
    st.markdown("### 🌐 Step 2: Live Web Verification")
    st.markdown('<div class="step-indicator">🔍 Cross-referencing each claim against live web data via Google Search...</div>', unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status_text = st.empty()

    results = []
    total = len(claims)

    for i, claim in enumerate(claims):
        status_text.markdown(f'<div class="step-indicator">🔍 Verifying claim {i+1}/{total}: *"{claim["claim"][:80]}..."*</div>', unsafe_allow_html=True)
        result = verify_claim(client, claim)
        results.append(result)
        progress_bar.progress((i + 1) / total)
        # Small delay to avoid rate limits
        if i < total - 1:
            time.sleep(0.5)

    status_text.empty()
    progress_bar.empty()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── STEP 4: Results ───────────────────────────────────────────────────────
    st.markdown("### 📊 Fact-Check Report")

    # Summary stats
    n_verified = sum(1 for r in results if r.get("verdict") == "VERIFIED")
    n_inaccurate = sum(1 for r in results if r.get("verdict") == "INACCURATE")
    n_false = sum(1 for r in results if r.get("verdict") == "FALSE")
    n_unverifiable = sum(1 for r in results if r.get("verdict") == "UNVERIFIABLE")

    integrity_score = int((n_verified / total) * 100) if total > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📋 Total Claims", total)
    col2.metric("✅ Verified", n_verified, delta=None)
    col3.metric("⚠️ Inaccurate", n_inaccurate, delta=None)
    col4.metric("❌ False", n_false, delta=None)
    col5.metric("🎯 Integrity Score", f"{integrity_score}%")

    # Integrity interpretation
    if integrity_score >= 80:
        st.success(f"🟢 **High Integrity** — {integrity_score}% of claims verified. This document appears largely accurate.")
    elif integrity_score >= 50:
        st.warning(f"🟡 **Moderate Integrity** — {integrity_score}% verified. Some claims need updating or correction.")
    else:
        st.error(f"🔴 **Low Integrity** — Only {integrity_score}% verified. This document contains significant inaccuracies.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Filter tabs
    tab_all, tab_false, tab_inaccurate, tab_verified = st.tabs([
        f"🔍 All ({total})",
        f"❌ False ({n_false})",
        f"⚠️ Inaccurate ({n_inaccurate})",
        f"✅ Verified ({n_verified})",
    ])

    with tab_all:
        for result in results:
            render_claim_card(result)

    with tab_false:
        false_results = [r for r in results if r.get("verdict") == "FALSE"]
        if false_results:
            for result in false_results:
                render_claim_card(result)
        else:
            st.info("🎉 No claims marked as FALSE.")

    with tab_inaccurate:
        inaccurate_results = [r for r in results if r.get("verdict") == "INACCURATE"]
        if inaccurate_results:
            for result in inaccurate_results:
                render_claim_card(result)
        else:
            st.info("🎉 No claims marked as INACCURATE.")

    with tab_verified:
        verified_results = [r for r in results if r.get("verdict") == "VERIFIED"]
        if verified_results:
            for result in verified_results:
                render_claim_card(result)
        else:
            st.info("No claims could be fully verified.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── DOWNLOAD REPORT ───────────────────────────────────────────────────────
    st.markdown("### 💾 Download Report")
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
        json_report = build_download_report(results)
        st.download_button(
            label="⬇️ Download JSON Report",
            data=json_report,
            file_name="factguard_report.json",
            mime="application/json",
            use_container_width=True,
        )

    with dl_col2:
        csv_report = build_csv_report(results)
        st.download_button(
            label="⬇️ Download CSV Report",
            data=csv_report,
            file_name="factguard_report.csv",
            mime="text/csv",
            use_container_width=True,
        )

elif uploaded_file is None:
    # Landing state
    st.markdown("""
    <div style="text-align:center; padding: 3rem 2rem; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius:16px; border: 1px solid #2d2d4e;">
        <div style="font-size:4rem; margin-bottom:1rem;">📄</div>
        <div style="font-size:1.3rem; font-weight:600; color:#e8e8f0; margin-bottom:0.5rem;">Upload a PDF to get started</div>
        <div style="color:#888; font-size:0.95rem; max-width:500px; margin: 0 auto;">
            Works with marketing reports, press releases, research papers, whitepapers — or any document with specific stats and claims.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🔬 Smart Extraction**  
        Gemini AI identifies specific, verifiable claims — stats, dates, financial figures — not opinions.
        """)
    with col2:
        st.markdown("""
        **🌐 Live Verification**  
        Each claim is cross-checked against live web data via Google Search grounding in real-time.
        """)
    with col3:
        st.markdown("""
        **📊 Clear Reports**  
        Results are color-coded and downloadable as JSON or CSV for easy sharing.
        """)
