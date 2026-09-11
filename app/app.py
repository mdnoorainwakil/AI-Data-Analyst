import os
import re
import json
import sqlite3
import hashlib
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from dotenv import load_dotenv
from groq import Groq
import textwrap

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM UI / UX
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #0a0c12;
        --panel: #12151d;
        --panel-2: #171b25;
        --line: rgba(255, 255, 255, .08);
        --line-soft: rgba(255, 255, 255, .05);
        --text: #f4f5f7;
        --muted: #8b93a7;
        --muted-2: #6b7284;
        --accent: #5468f0;
        --accent-strong: #4256d9;
        --accent-soft: rgba(84, 104, 240, .13);
        --accent-border: rgba(84, 104, 240, .35);
        --green: #34d399;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Calm, near-flat background — a single soft glow behind the hero
       instead of the busy multi-color grid the earlier version used. */
    .stApp {
        background:
            radial-gradient(circle at 50% -8%, rgba(84,104,240,.10), transparent 42%),
            linear-gradient(180deg, #0a0c12 0%, #090a0f 60%, #08090e 100%);
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    /* Calm header — no animated rainbow line; a plain, quiet strip. */
    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.1rem;
        padding-bottom: 3.5rem;
        padding-left: clamp(1rem, 2.4vw, 2.4rem);
        padding-right: clamp(1rem, 2.4vw, 2.4rem);
    }

    /* ---------------- SIDEBAR ---------------- */
    [data-testid="stSidebar"] {
        background: #0b0d13;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div {
        padding-top: 1.4rem;
    }
    .side-brand {
        display: flex;
        align-items: center;
        gap: .65rem;
        padding: 0 .2rem .9rem .2rem;
    }
    .side-logo {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        border-radius: 9px;
        font-size: 1rem;
        background: var(--accent-soft);
        border: 1px solid var(--accent-border);
        color: #dbe1ff;
    }
    .side-name {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: var(--text);
        letter-spacing: -0.01em;
    }
    .side-tag {
        color: var(--muted);
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: .78rem;
        margin-top: .05rem;
    }
    .side-divider {
        height: 1px;
        background: var(--line);
        margin: .85rem 0;
    }
    .side-heading {
        color: var(--muted-2);
        font-size: .7rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .55rem;
    }
    .side-stat {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: .42rem .05rem;
        font-size: .84rem;
        color: #b9bfcc;
        border-bottom: 1px solid var(--line-soft);
    }
    .side-stat b {
        color: var(--text);
        font-weight: 700;
    }
    .side-empty {
        color: var(--muted);
        font-size: .83rem;
        line-height: 1.55;
    }
    .side-step {
        display: flex;
        align-items: center;
        gap: .55rem;
        font-size: .83rem;
        color: #b9bfcc;
        padding: .3rem 0;
    }
    .side-step-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent);
        flex-shrink: 0;
    }

    /* ---------------- PRODUCT NAV BAR ---------------- */
    .product-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: .85rem .1rem;
        margin-bottom: 1.6rem;
        border-bottom: 1px solid var(--line);
        background: transparent;
    }

    .product-brand,
    .product-nav,
    .product-status {
        display: flex;
        align-items: center;
    }

    .product-brand {
        gap: .55rem;
        color: var(--text);
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        font-size: .98rem;
    }

    .product-mark {
        width: 26px;
        height: 26px;
        display: grid;
        place-items: center;
        border-radius: 7px;
        background: var(--accent-soft);
        border: 1px solid var(--accent-border);
        color: #dbe1ff;
        font-size: .66rem;
    }

    .product-nav {
        gap: 1.6rem;
        color: var(--muted);
        font-size: .82rem;
    }

    .product-nav span:first-child {
        color: #cfd4e0;
    }

    .product-status {
        gap: .42rem;
        color: var(--muted);
        font-size: .78rem;
    }

    .product-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 0 4px rgba(52,211,153,.08);
    }

    @media (max-width: 720px) {
        .product-nav { display: none; }
        .product-status { margin-left: auto; }
    }

    /* ---------------- HERO ---------------- */
    /* A quiet, centered editorial hero, closer to a product landing
       page than a boxed dashboard card. */
    .hero {
        position: relative;
        overflow: visible;
        padding: 2.4rem 1.5rem 1.8rem 1.5rem;
        border: none;
        border-radius: 0;
        background: transparent;
        box-shadow: none;
        margin-bottom: 1.8rem;
        text-align: center;
    }

    .hero:before {
        content: none;
    }

    .hero-status {
        position: absolute;
        top: .4rem;
        right: .6rem;
        display: inline-flex;
        align-items: center;
        gap: .42rem;
        padding: .3rem .68rem;
        border-radius: 999px;
        font-size: .7rem;
        font-weight: 600;
        background: var(--panel);
        border: 1px solid var(--line);
        color: var(--muted);
        z-index: 2;
    }
    .hero-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #6b7284;
    }
    .hero-status-live .hero-status-dot {
        background: var(--green);
        box-shadow: 0 0 0 rgba(52,211,153,.6);
        animation: livepulse 1.8s ease-out infinite;
    }
    @keyframes livepulse {
        0%   { box-shadow: 0 0 0 0 rgba(52,211,153,.55); }
        70%  { box-shadow: 0 0 0 7px rgba(52,211,153,0); }
        100% { box-shadow: 0 0 0 0 rgba(52,211,153,0); }
    }

    /* Decorative bar-chart motif dropped — the reference layout keeps
       the hero as plain typography, no illustration behind the text. */
    .hero-motif {
        display: none;
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        padding: .3rem .3rem;
        border-radius: 0;
        background: transparent;
        border: none;
        color: var(--muted);
        font-size: .74rem;
        font-weight: 700;
        letter-spacing: .16em;
        text-transform: uppercase;
    }

    .hero-title {
        font-family: 'Lora', serif;
        font-size: clamp(2.3rem, 4.4vw, 3.6rem);
        font-weight: 700;
        letter-spacing: -0.01em;
        line-height: 1.08;
        margin: .9rem auto .6rem auto;
        max-width: 760px;
        color: #ffffff;
    }

    .hero-subtitle {
        color: var(--muted);
        font-size: 1.02rem;
        max-width: 640px;
        line-height: 1.65;
        margin: 0 auto;
    }

    .hero-chips {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: .5rem;
        margin: 1.3rem auto 0 auto;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        padding: .32rem .72rem;
        border-radius: 999px;
        background: transparent;
        border: 1px solid var(--line);
        color: var(--muted);
        font-size: .74rem;
        font-weight: 600;
    }

    .hero-snapshot {
        display: flex;
        justify-content: center;
        gap: 2.4rem;
        margin: 1.6rem auto 0 auto;
        padding-top: 1.2rem;
        border-top: 1px solid var(--line);
        max-width: 560px;
    }
    .hero-snap-item {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .hero-snap-item b {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
    }
    .hero-snap-item span {
        color: var(--muted-2);
        font-size: .72rem;
        margin-top: .2rem;
    }

    /* ---------------- SECTION TITLES ---------------- */
    .section-title {
        display: flex;
        align-items: center;
        gap: .65rem;
        font-family: 'Lora', serif;
        font-size: 1.35rem;
        font-weight: 600;
        letter-spacing: -0.005em;
        color: var(--text);
        margin: 1.9rem 0 .85rem 0;
    }

    .section-title .section-number {
        display: inline-grid;
        place-items: center;
        width: 27px;
        height: 27px;
        border-radius: 7px;
        background: var(--accent-soft);
        border: 1px solid var(--accent-border);
        color: #c9d1ff;
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .02em;
        font-family: 'Inter', sans-serif;
    }

    .soft-card {
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: var(--panel);
        box-shadow: none;
    }

    /* ---------------- METRIC CARDS ---------------- */
    div[data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        padding: 1rem 1.05rem;
        border-radius: 14px;
        min-height: 104px;
        box-shadow: none;
        transition: border-color .18s ease, transform .18s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: var(--accent-border);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 600;
        font-size: .78rem;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--text);
    }

    /* ---------------- INPUTS ---------------- */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-testid="stFileUploaderDropzone"] {
        background: var(--panel);
        border-color: var(--line);
        border-radius: 10px;
    }

    div[data-testid="stFileUploaderDropzone"] {
        min-height: 92px;
        border: 1px dashed var(--line);
        transition: border-color .18s ease, background .18s ease;
    }

    div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--accent-border);
        background: var(--panel-2);
    }

    /* ---------------- BUTTONS ---------------- */
    /* Default / secondary buttons: quiet outlined chips — used for
       suggested-question buttons so they read as tags, not CTAs. */
    .stButton > button {
        border-radius: 999px;
        min-height: 38px;
        padding: .42rem 1rem;
        font-weight: 600;
        font-size: .85rem;
        border: 1px solid var(--line);
        background: var(--panel);
        color: #c7cbd6;
        box-shadow: none;
        text-align: left;
        justify-content: flex-start;
        transition: background .15s ease, border-color .15s ease, color .15s ease;
    }

    .stButton > button:hover {
        background: var(--panel-2);
        border-color: var(--accent-border);
        color: var(--text);
    }

    /* Primary buttons: flat solid accent fill, matching a real
       product's "Try for free"-style call to action — no gradient. */
    .stButton > button[kind="primary"] {
        border-radius: 10px;
        min-height: 42px;
        padding: .5rem 1.3rem;
        font-weight: 650;
        font-size: .92rem;
        text-align: center;
        justify-content: center;
        border: 1px solid var(--accent);
        background: var(--accent);
        color: #ffffff;
        box-shadow: none;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--accent-strong);
        border-color: var(--accent-strong);
    }

    /* ---------------- EXPANDERS ---------------- */
    details[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--panel);
        overflow: hidden;
        margin-bottom: .55rem;
        transition: border-color .18s ease;
    }

    details[data-testid="stExpander"]:hover {
        border-color: var(--accent-border);
    }

    details[data-testid="stExpander"] summary {
        padding: .85rem 1rem;
    }

    /* ---------------- ASK PANEL ---------------- */
    .ask-box {
        padding: 1.25rem 1.35rem;
        border: 1px solid var(--line);
        border-left: 4px solid var(--accent);
        border-radius: 4px 14px 14px 4px;
        background: var(--panel);
        box-shadow: none;
        margin-bottom: .7rem;
    }

    .ask-heading {
        font-family: 'Lora', serif;
        font-size: 1.08rem;
        font-weight: 600;
        color: var(--text);
    }

    .small-muted {
        color: var(--muted);
        font-size: .84rem;
        line-height: 1.5;
    }

    .answer-card {
        border: 1px solid var(--line);
        border-left: 4px solid var(--green);
        padding: 1.1rem 1.15rem;
        border-radius: 4px 14px 14px 4px;
        background: var(--panel);
        margin: .65rem 0 1rem 0;
    }

    .insight-card {
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.1rem 1.15rem;
        background: var(--panel);
        margin-top: .65rem;
        box-shadow: none;
    }

    .insight-label {
        font-weight: 700;
        color: #d7dbe8;
        margin-top: .65rem;
        margin-bottom: .2rem;
        font-size: .84rem;
    }

    .divider {
        height: 1px;
        background: var(--line);
        margin: 1.1rem 0;
    }

    /* ---------------- QUERY / SUGGESTION POLISH ---------------- */
    .suggestion-shell {
        padding: 1.05rem 1.1rem 0.95rem 1.1rem;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--panel);
        margin: .55rem 0 .8rem 0;
    }
    .suggestion-kicker {
        color: var(--muted);
        font-size: .68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .1em;
        margin-bottom: .25rem;
    }
    .suggestion-title {
        color: var(--text);
        font-family: 'Lora', serif;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: .2rem;
    }
    .suggestion-subtitle {
        color: var(--muted);
        font-size: .82rem;
        line-height: 1.45;
    }
    .query-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: .75rem;
        margin: .35rem 0 .55rem 0;
        color: var(--muted);
        font-size: .78rem;
    }
    .query-meta strong { color: var(--text); }
    .result-shell {
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: .75rem;
        background: var(--panel);
        margin: .25rem 0 .75rem 0;
    }
    .answer-label, .insight-section-label {
        color: var(--muted);
        font-size: .7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-bottom: .35rem;
    }
    div[data-testid='stDataFrame'] {
        border-radius: 10px;
        overflow: hidden;
    }
    .st-key-download_ai_result button {
        min-height: 38px;
    }

    /* ---------------- EMPTY STATE ---------------- */
    .empty-state {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.3rem 1.5rem;
        border: 1px dashed var(--line);
        border-radius: 14px;
        background: var(--panel);
        margin-top: .6rem;
    }
    .empty-state-icon {
        width: 44px;
        height: 44px;
        flex-shrink: 0;
        display: grid;
        place-items: center;
        border-radius: 11px;
        font-size: 1.25rem;
        background: var(--accent-soft);
        border: 1px solid var(--accent-border);
    }
    .empty-state-title {
        font-weight: 700;
        color: var(--text);
        font-size: .98rem;
        margin-bottom: .15rem;
    }
    .empty-state-text {
        color: var(--muted);
        font-size: .85rem;
        line-height: 1.5;
    }

    /* ---------------- BACK TO TOP ---------------- */
    .to-top {
        position: fixed;
        right: 22px;
        bottom: 22px;
        z-index: 998;
        width: 42px;
        height: 42px;
        display: grid;
        place-items: center;
        border-radius: 50%;
        background: var(--accent);
        color: #ffffff;
        text-decoration: none;
        font-size: 1.1rem;
        box-shadow: 0 8px 22px rgba(0,0,0,.35);
        border: 1px solid var(--accent-strong);
        transition: transform .15s ease, background .15s ease;
    }
    .to-top:hover {
        transform: translateY(-3px);
        background: var(--accent-strong);
    }

    /* ---------------- SCROLLBAR ---------------- */
    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: var(--accent-border);
        border-radius: 10px;
    }

    /* ---------------- MISC ---------------- */
    div[data-testid="stPlotlyChart"] {
        border-radius: 12px;
        overflow: hidden;
    }

    @media (max-width: 900px) {
        .block-container { padding-left: .8rem; padding-right: .8rem; }
        .hero { padding: 1.8rem 1rem 1.2rem 1rem; }
        .hero-snapshot { gap: 1.2rem; }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# GROQ SETUP
# ============================================================

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None


def get_groq_model(groq_client):
    """Pick an available, capable model from the account dynamically."""
    if groq_client is None:
        return None

    preferred = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]

    try:
        available = [m.id for m in groq_client.models.list().data]
        for model_name in preferred:
            if model_name in available:
                return model_name
    except Exception:
        pass

    return None


GROQ_MODEL = get_groq_model(client)

# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "file_id": None,
    "original_df": None,
    "cleaned_df": None,
    "cleaning_info": {},
    "question_history": [],
    "last_qa_result": None,
    "suggested_questions": [],
    "suggestion_signature": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# HELPERS
# ============================================================


def normalize_name(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def contains_any(text, terms):
    text = normalize_name(text)
    return any(term in text for term in terms)


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def display_number(value):
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    if isinstance(value, (float, np.floating)):
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{float(value):,.2f}"
    return str(value)


def make_unique_columns(columns):
    seen = {}
    result = []
    for col in columns:
        base = str(col).strip() or "Unnamed"
        count = seen.get(base, 0)
        if count == 0:
            new_name = base
        else:
            new_name = f"{base}_{count}"
        seen[base] = count + 1
        result.append(new_name)
    return result


def detect_date_columns(df):
    hints = ["date", "time", "month", "day", "timestamp", "created", "updated", "joining", "hire"]
    detected = []

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            detected.append(col)
            continue

        name = normalize_name(col)
        if any(h in name.split() for h in hints):
            try:
                parsed = pd.to_datetime(df[col], errors="coerce", format="mixed")
            except Exception:
                parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() >= 0.65:
                detected.append(col)
                continue

        if df[col].dtype == "object" and len(df) > 0:
            sample = df[col].dropna().astype(str).head(500)
            if len(sample) >= 10:
                try:
                    parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
                except Exception:
                    parsed = pd.to_datetime(sample, errors="coerce")
                if parsed.notna().mean() >= 0.90 and sample.nunique() > 5:
                    detected.append(col)

    return list(dict.fromkeys(detected))


def _clean_numeric_series(series):
    """Convert numeric-looking text (currency, commas, %, accounting negatives) to numbers."""
    if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
        return series, False

    text = series.astype("string").str.strip()
    if text.dropna().empty:
        return series, False

    # Common missing-value tokens.
    missing_tokens = {"", "na", "n/a", "null", "none", "nan", "missing", "-"}
    normalized = text.str.lower()
    text = text.mask(normalized.isin(missing_tokens), pd.NA)

    # Accounting negatives: (123.45) -> -123.45
    cleaned = text.str.replace(r"^\s*\((.*)\)\s*$", r"-\1", regex=True)

    # Remove common currency symbols, percent signs, thousands separators and spaces.
    cleaned = cleaned.str.replace(r"[,$€£₹¥₽₩]", "", regex=True)
    cleaned = cleaned.str.replace("%", "", regex=False)
    cleaned = cleaned.str.replace(r"\s+", "", regex=True)

    numeric = pd.to_numeric(cleaned, errors="coerce")
    non_null = text.notna()
    if not non_null.any():
        return series, False

    success_ratio = numeric[non_null].notna().mean()
    if success_ratio < 0.90:
        return series, False

    # If only a tiny fraction failed, keep those as missing rather than
    # leaving the whole column as text. This makes SQL arithmetic reliable.
    return numeric, True


def _looks_like_identifier_name(column_name):
    name = normalize_name(column_name)
    identifier_terms = {
        "id", "identifier", "uuid", "guid", "code", "sku", "zip",
        "zipcode", "postal", "postal code", "pin", "phone", "mobile",
        "account number", "account no", "customer id", "employee id",
        "order id", "transaction id", "invoice id"
    }
    return name in identifier_terms or any(
        term in name.split() for term in {"id", "uuid", "guid", "sku", "zip", "postal", "pin"}
    )


def _infer_and_clean_types(df, info):
    """Infer practical analytical types without changing genuine categorical text."""
    # Date detection happens first so date-like strings are not accidentally
    # converted to numbers.
    date_cols = detect_date_columns(df)
    info["date_columns_detected"] = date_cols

    for col in date_cols:
        try:
            parsed = pd.to_datetime(df[col], errors="coerce", format="mixed")
        except Exception:
            parsed = pd.to_datetime(df[col], errors="coerce")
        if parsed.notna().mean() >= 0.65:
            df[col] = parsed

    for col in df.columns:
        if col in date_cols:
            continue

        series = df[col]
        if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_bool_dtype(series):
            continue

        # Do not turn identifiers/codes into measures even when they contain digits.
        if _looks_like_identifier_name(col):
            df[col] = series.astype("string").str.strip()
            continue

        converted, changed = _clean_numeric_series(series)
        if changed:
            df[col] = converted
            info.setdefault("numeric_columns_converted", []).append(col)
            continue

        # Keep genuine text/category fields as strings and normalize whitespace.
        if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            df[col] = series.astype("string").str.strip()

    return df


def clean_dataset(input_df):
    df = input_df.copy()
    info = {
        "original_rows": len(df),
        "original_columns": len(df.columns),
        "duplicate_rows_removed": 0,
        "empty_columns_removed": [],
        "blank_strings_replaced": 0,
        "missing_values_filled": {},
        "date_columns_detected": [],
        "numeric_columns_converted": [],
    }

    df.columns = make_unique_columns(df.columns)

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        df = df.drop_duplicates().reset_index(drop=True)
    info["duplicate_rows_removed"] = duplicate_count

    empty_cols = [c for c in df.columns if df[c].isna().all()]
    if empty_cols:
        df = df.drop(columns=empty_cols)
    info["empty_columns_removed"] = empty_cols

    # Convert blank strings to missing values before type inference.
    for col in df.select_dtypes(include=["object", "string"]).columns:
        before = int(df[col].isna().sum())
        df[col] = df[col].replace(r"^\s*$", np.nan, regex=True)
        after = int(df[col].isna().sum())
        info["blank_strings_replaced"] += max(0, after - before)

    # Automatically infer dates, numeric text, currency, percentages and
    # ordinary categorical/string columns.
    df = _infer_and_clean_types(df, info)

    # Fill missing values according to the inferred analytical type.
    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            median_val = df[col].median()
            fill_val = 0 if pd.isna(median_val) else median_val
            df[col] = df[col].fillna(fill_val)
            info["missing_values_filled"][col] = f"median ({display_number(fill_val)})"

        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            non_null = df[col].dropna()
            if len(non_null):
                median_date = non_null.sort_values().iloc[len(non_null) // 2]
                df[col] = df[col].fillna(median_date)
                info["missing_values_filled"][col] = f"median date ({median_date.strftime('%Y-%m-%d')})"
            else:
                df[col] = df[col].fillna(pd.Timestamp("2000-01-01"))
                info["missing_values_filled"][col] = "2000-01-01"

        else:
            mode = df[col].mode(dropna=True)
            fill_val = mode.iloc[0] if len(mode) else "Unknown"
            df[col] = df[col].fillna(fill_val)
            info["missing_values_filled"][col] = f"mode ({fill_val})"

    # Final dtype cleanup for stable SQLite/Pandas behavior.
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype(str)

    return df, info


def semantic_roles(df):
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    dates = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
    return numeric, categorical, dates


def is_identifier_column(df, col):
    name = normalize_name(col)
    id_terms = ["id", "identifier", "code", "zip", "postal", "pin", "index", "uuid"]

    if any(term == name or term in name.split() for term in id_terms):
        return True

    if len(df):
        ratio = df[col].nunique(dropna=True) / len(df)
        if ratio >= 0.985 and not contains_any(name, ["price", "rate", "salary", "revenue", "sales"]):
            return True

    return False


REVENUE_TERMS = ["revenue", "sales", "income", "turnover", "earning", "earnings"]
PROFIT_TERMS = ["profit", "net profit", "gross profit", "operating profit"]
COST_TERMS = ["cost", "expense", "expenditure", "spending"]
QUANTITY_TERMS = ["quantity", "qty", "units", "unit", "passenger", "passengers", "booking", "bookings", "ticket", "tickets", "volume", "orders", "order"]
DELAY_TERMS = ["delay", "delayed", "late"]
DURATION_TERMS = ["duration", "hours", "minutes", "days"]
RATING_TERMS = ["rating", "score", "satisfaction", "quality"]
PRICE_TERMS = ["price", "fare", "unit price"]
PERCENT_TERMS = ["percent", "percentage", "margin", "ratio"]
EXPERIENCE_TERMS = ["experience", "tenure"]
INVENTORY_TERMS = ["inventory", "stock", "production", "output"]
YEAR_TERMS = ["year", "fiscal year", "calendar year"]
ENTITY_TERMS = ["customer", "client", "employee", "patient", "product", "supplier", "vendor", "airline", "department", "branch", "store", "region"]


def smart_kpis(df):
    main = []
    more = []
    main_labels = set()
    more_labels = set()

    def add(target, label, value):
        bucket = main if target == "main" else more
        labels = main_labels if target == "main" else more_labels
        if label not in labels:
            bucket.append((label, value))
            labels.add(label)

    add("main", "Total Records", len(df))

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    text_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

    id_cols = {c for c in numeric_cols if is_identifier_column(df, c)}

    for col in numeric_cols:
        if col in id_cols:
            continue

        s = safe_numeric(df[col]).dropna()
        if s.empty:
            continue

        name = normalize_name(col)
        total = s.sum()
        avg = s.mean()
        med = s.median()
        mn = s.min()
        mx = s.max()

        if contains_any(name, YEAR_TERMS):
            years = int(s.nunique())
            add("main", f"Years Covered ({col})", years)
            add("more", f"Latest Year ({col})", int(mx))
            if years > 1:
                add("more", f"Earliest Year ({col})", int(mn))
            continue

        if contains_any(name, REVENUE_TERMS):
            add("main", f"Total {col}", total)
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            add("more", f"{col} per Record", total / len(s))
            continue

        if contains_any(name, PROFIT_TERMS):
            add("main", f"Total {col}", total)
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            add("more", "Profit-Making Records", int((s > 0).sum()))
            if (s < 0).any():
                add("more", "Loss-Making Records", int((s < 0).sum()))
                add("more", "Total Loss", abs(s[s < 0].sum()))
            continue

        if contains_any(name, COST_TERMS):
            add("main", f"Total {col}", total)
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            continue

        if contains_any(name, QUANTITY_TERMS):
            add("main", f"Total {col}", total)
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            continue

        if contains_any(name, DELAY_TERMS):
            add("main", f"Average {col}", avg)
            add("main", f"Delayed Records ({col})", int((s > 0).sum()))
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            add("more", f"Median {col}", med)
            continue

        if contains_any(name, DURATION_TERMS):
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            continue

        if contains_any(name, RATING_TERMS):
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Highest {col}", mx)
            add("more", f"Lowest {col}", mn)
            continue

        if contains_any(name, PRICE_TERMS):
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            continue

        if contains_any(name, PERCENT_TERMS):
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            continue

        if contains_any(name, EXPERIENCE_TERMS):
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            continue

        if contains_any(name, INVENTORY_TERMS):
            add("main", f"Total {col}", total)
            add("main", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)
            continue

        if s.nunique() >= 2:
            add("more", f"Average {col}", avg)
            add("more", f"Median {col}", med)
            add("more", f"Maximum {col}", mx)
            add("more", f"Minimum {col}", mn)

    for col in text_cols:
        n = int(df[col].nunique(dropna=True))
        if contains_any(col, ENTITY_TERMS) or 2 <= n <= 100:
            add("more", f"Unique {col}", n)

    for col in date_cols:
        if df[col].notna().any():
            earliest = df[col].min()
            latest = df[col].max()
            add("more", f"Earliest {col}", earliest.strftime("%d %b %Y"))
            add("more", f"Latest {col}", latest.strftime("%d %b %Y"))
            add("more", f"Days Covered ({col})", int((latest - earliest).days))

    revenue_col = next((c for c in numeric_cols if contains_any(c, REVENUE_TERMS)), None)
    profit_col = next((c for c in numeric_cols if contains_any(c, PROFIT_TERMS)), None)
    if revenue_col and profit_col:
        rev = safe_numeric(df[revenue_col]).sum()
        prof = safe_numeric(df[profit_col]).sum()
        if rev != 0:
            add("main", "Profit Margin", f"{(prof / rev) * 100:.2f}%")

    return main, more

# ============================================================
# SIDEBAR — WORKSPACE PANEL
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="side-brand">
            <div class="side-logo">◆</div>
            <div>
                <div class="side-name">AI Data Analyst</div>
                <div class="side-tag">Decision Workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='side-divider'></div>", unsafe_allow_html=True)

    if st.session_state.cleaned_df is not None:
        _sidebar_df = st.session_state.cleaned_df
        st.markdown("<div class='side-heading'>Current Dataset</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="side-stat"><span>Rows</span><b>{len(_sidebar_df):,}</b></div>
            <div class="side-stat"><span>Columns</span><b>{len(_sidebar_df.columns):,}</b></div>
            <div class="side-stat"><span>Missing values</span><b>{int(_sidebar_df.isna().sum().sum()):,}</b></div>
            <div class="side-stat"><span>Duplicates</span><b>{int(_sidebar_df.duplicated().sum()):,}</b></div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class='side-heading'>Getting Started</div>
            <div class='side-empty'>Upload a dataset to explore, filter, visualize and ask business questions.</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='side-divider'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class='side-heading'>Workflow</div>
        <div class='side-step'><span class='side-step-dot'></span>Upload dataset</div>
        <div class='side-step'><span class='side-step-dot'></span>Auto-clean &amp; explore</div>
        <div class='side-step'><span class='side-step-dot'></span>Filter &amp; visualize</div>
        <div class='side-step'><span class='side-step-dot'></span>Ask questions in plain English</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='side-divider'></div>", unsafe_allow_html=True)
    st.caption("Built for fast, clear business decisions")

# ============================================================
# FILE UPLOAD / CLEANING
# ============================================================

_hero_has_data = st.session_state.cleaned_df is not None
_hero_status_class = "hero-status-live" if _hero_has_data else "hero-status-idle"
_hero_status_text = "Live workspace" if _hero_has_data else "Awaiting dataset"

_hero_snapshot_html = ""
if _hero_has_data:
    _hdf = st.session_state.cleaned_df
    _hero_snapshot_html = f"""
      <div class="hero-snapshot">
        <div class="hero-snap-item"><b>{len(_hdf):,}</b><span>rows loaded</span></div>
        <div class="hero-snap-item"><b>{len(_hdf.columns):,}</b><span>columns</span></div>
        <div class="hero-snap-item"><b>{int(_hdf.isna().sum().sum()):,}</b><span>missing values</span></div>
      </div>
    """

st.markdown(
    """
    <div class="product-bar">
        <div class="product-brand">
            <span class="product-mark">◆</span>
            <span>AI Data Analyst</span>
        </div>
        <div class="product-nav">
            <span>Explore</span>
            <span>Analyze</span>
            <span>Decide</span>
        </div>
        <div class="product-status">
            <span class="product-status-dot"></span>
            Workspace ready
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div id="top"></div>
    <a href="#top" class="to-top" title="Back to top">↑</a>
    <div class="hero">
      <div class="hero-status {_hero_status_class}"><span class="hero-status-dot"></span>{_hero_status_text}</div>
      <svg class="hero-motif" viewBox="0 0 160 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="heroLine" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#38bdf8"/>
            <stop offset="100%" stop-color="#8b5cf6"/>
          </linearGradient>
        </defs>
        <rect x="8"  y="70" width="12" height="22" rx="2.5" fill="rgba(56,189,248,.32)"/>
        <rect x="26" y="58" width="12" height="34" rx="2.5" fill="rgba(139,92,246,.32)"/>
        <rect x="44" y="44" width="12" height="48" rx="2.5" fill="rgba(56,189,248,.28)"/>
        <rect x="62" y="64" width="12" height="28" rx="2.5" fill="rgba(139,92,246,.26)"/>
        <polyline points="6,50 30,34 50,40 72,14 96,26 122,6 154,18" fill="none" stroke="url(#heroLine)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="122" cy="6" r="3.2" fill="#38bdf8"/>
        <circle cx="154" cy="18" r="3.2" fill="#8b5cf6"/>
      </svg>
      <div class="hero-kicker">DECISION INTELLIGENCE</div>
      <div class="hero-title">AI Data Analyst</div>
      <div class="hero-subtitle">Upload a dataset, explore it visually, ask questions in natural language, and turn real data into clear business decisions.</div>
      {_hero_snapshot_html}
      <div class="hero-chips">
        <span class="pill">CSV / XLSX</span>
        <span class="pill">Smart Cleaning</span>
        <span class="pill">Dynamic KPIs</span>
        <span class="pill">SQL Analysis</span>
        <span class="pill">AI Insights</span>
        <span class="pill">15 Chart Types</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='section-title'><span class='section-number'>01</span>Upload Dataset</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload CSV or Excel Dataset",
    type=["csv", "xlsx"],
    help="Maximum upload size is controlled by .streamlit/config.toml.",
)

if uploaded_file is not None:
    current_file_id = (uploaded_file.name, uploaded_file.size)

    if st.session_state.file_id != current_file_id:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                original_df = pd.read_csv(uploaded_file)
            else:
                original_df = pd.read_excel(uploaded_file)

            cleaned_df, cleaning_info = clean_dataset(original_df)

            st.session_state.file_id = current_file_id
            st.session_state.original_df = original_df
            st.session_state.cleaned_df = cleaned_df
            st.session_state.cleaning_info = cleaning_info
            st.session_state.question_history = []
            st.session_state.last_qa_result = None
            st.session_state.suggested_questions = []
            st.session_state.suggestion_signature = None

        except Exception as exc:
            st.error(f"Could not read the uploaded file: {exc}")
            st.stop()

# ============================================================
# DATA WORKSPACE
# ============================================================

if st.session_state.cleaned_df is not None:

    df_clean = st.session_state.cleaned_df.copy()
    info = st.session_state.cleaning_info

    st.success("✅ Dataset automatically cleaned and is ready for analysis.")

    with st.expander("🧹 View Cleaning Details"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Original Rows", info.get("original_rows", 0))
        c2.metric("Rows After Cleaning", len(df_clean))
        c3.metric("Duplicates Removed", info.get("duplicate_rows_removed", 0))
        c4.metric("Columns Removed", len(info.get("empty_columns_removed", [])))

        if info.get("empty_columns_removed"):
            st.write("**Empty columns removed:**", ", ".join(info["empty_columns_removed"]))

        if info.get("numeric_columns_converted"):
            st.write("**Numeric text converted:**", ", ".join(info["numeric_columns_converted"]))

        if info.get("missing_values_filled"):
            st.write("**Missing values handled:**")
            st.dataframe(
                pd.DataFrame(
                    list(info["missing_values_filled"].items()),
                    columns=["Column", "Treatment"],
                ),
                use_container_width=True,
                hide_index=True,
            )

    # --------------------------------------------------------
    # Overview
    # --------------------------------------------------------

    st.markdown("<div class='section-title'><span class='section-number'>02</span>🔎 Dataset Overview</div>", unsafe_allow_html=True)

    missing_total = int(df_clean.isna().sum().sum())
    duplicate_total = int(df_clean.duplicated().sum())

    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Rows", f"{len(df_clean):,}")
    o2.metric("Columns", f"{len(df_clean.columns):,}")
    o3.metric("Missing Values", f"{missing_total:,}")
    o4.metric("Duplicates", f"{duplicate_total:,}")

    with st.expander("👀 Dataset Preview", expanded=False):
        st.dataframe(df_clean.head(100), use_container_width=True)

    with st.expander("🧬 Column Information", expanded=False):
        column_info = pd.DataFrame({
            "Column": df_clean.columns,
            "Data Type": [str(df_clean[c].dtype) for c in df_clean.columns],
            "Missing": [int(df_clean[c].isna().sum()) for c in df_clean.columns],
            "Unique": [int(df_clean[c].nunique(dropna=True)) for c in df_clean.columns],
        })
        st.dataframe(column_info, use_container_width=True, hide_index=True)

    # --------------------------------------------------------
    # Dynamic filters
    # --------------------------------------------------------

    st.markdown("<div class='section-title'><span class='section-number'>03</span>Dynamic Filters</div>", unsafe_allow_html=True)

    working_df = df_clean.copy()
    num_cols = working_df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = working_df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    date_cols = working_df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

    filter_values = {}

    with st.expander("📅 Date Filters", expanded=False):
        if date_cols:
            date_widgets = st.columns(min(3, len(date_cols)))
            for idx, col in enumerate(date_cols):
                with date_widgets[idx % len(date_widgets)]:
                    min_date = working_df[col].min().date()
                    max_date = working_df[col].max().date()
                    selected = st.date_input(
                        f"{col}",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key=f"filter_date_{col}",
                    )
                    filter_values[col] = selected
        else:
            st.caption("No datetime columns detected.")

    with st.expander("🏷️ Category Filters", expanded=False):
        eligible_cat = [c for c in cat_cols if 2 <= working_df[c].nunique(dropna=True) <= 40]
        if eligible_cat:
            cat_widgets = st.columns(3)
            for idx, col in enumerate(eligible_cat):
                with cat_widgets[idx % 3]:
                    options = sorted(working_df[col].dropna().astype(str).unique().tolist())
                    selected = st.multiselect(
                        col,
                        options,
                        default=[],
                        key=f"filter_cat_{col}",
                    )
                    filter_values[col] = selected
        else:
            st.caption("No categorical columns are suitable for a compact filter.")

    with st.expander("🔢 Numeric Filters", expanded=False):
        eligible_num = []
        for col in num_cols:
            if is_identifier_column(working_df, col):
                continue
            unique_count = working_df[col].nunique(dropna=True)
            if 5 <= unique_count <= 1000:
                eligible_num.append(col)

        if eligible_num:
            num_widgets = st.columns(2)
            for idx, col in enumerate(eligible_num):
                with num_widgets[idx % 2]:
                    min_val = float(working_df[col].min())
                    max_val = float(working_df[col].max())
                    if min_val == max_val:
                        st.write(f"{col}: {display_number(min_val)}")
                    else:
                        selected = st.slider(
                            col,
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val),
                            key=f"filter_num_{col}",
                        )
                        filter_values[col] = selected
        else:
            st.caption("No numeric columns are suitable for a compact range filter.")

    # Apply filters
    for col, selected in filter_values.items():
        if col in date_cols and isinstance(selected, tuple) and len(selected) == 2:
            start_date, end_date = selected
            start_ts = pd.Timestamp(start_date)
            end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
            working_df = working_df[(working_df[col] >= start_ts) & (working_df[col] <= end_ts)]
        elif col in cat_cols and selected:
            working_df = working_df[working_df[col].astype(str).isin(selected)]
        elif col in num_cols and isinstance(selected, tuple) and len(selected) == 2:
            working_df = working_df[(working_df[col] >= selected[0]) & (working_df[col] <= selected[1])]

    df_analysis = working_df.copy()

    st.caption(f"Current analysis dataset: **{len(df_analysis):,} rows** after active filters.")

    # --------------------------------------------------------
    # SQLite SQL ENGINE
    # --------------------------------------------------------

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df_analysis.to_sql("data", conn, if_exists="replace", index=False)

    # --------------------------------------------------------
    # KPI section
    # --------------------------------------------------------

    st.markdown("<div class='section-title'><span class='section-number'>04</span>📈 Key Performance Indicators</div>", unsafe_allow_html=True)

    main_kpis, more_kpis = smart_kpis(df_analysis)

    for start in range(0, len(main_kpis), 4):
        row = main_kpis[start:start + 4]
        cols = st.columns(len(row))
        for ui_col, (label, value) in zip(cols, row):
            with ui_col:
                st.metric(label, display_number(value))

    if more_kpis:
        with st.expander("➕ More Relevant KPIs", expanded=False):
            for start in range(0, len(more_kpis), 4):
                row = more_kpis[start:start + 4]
                cols = st.columns(len(row))
                for ui_col, (label, value) in zip(cols, row):
                    with ui_col:
                        st.metric(label, display_number(value))

    # --------------------------------------------------------
    # RESPONSIVE CHART HELPERS
    # --------------------------------------------------------

    def chart_tick_step(series):
        """Choose readable numeric tick spacing without creating huge gaps."""
        s = pd.to_numeric(series, errors="coerce").dropna()
        if s.empty:
            return None
        span = float(s.max() - s.min())
        if span <= 0:
            return None
        if span <= 5000:
            return 250
        if span <= 10000:
            return 500
        if span <= 25000:
            return 1000
        target = span / 8
        magnitude = 10 ** np.floor(np.log10(max(target, 1)))
        for mult in (1, 2, 2.5, 5, 10):
            step = mult * magnitude
            if step >= target:
                return step
        return 10 * magnitude

    def visible_window(df, x_col, key_prefix, max_visible=25):
        """For long categorical axes, show a movable window instead of overlapping labels."""
        work = df.copy()
        n = len(work)
        if n <= max_visible:
            return work
        max_start = n - max_visible
        start_idx = st.slider(
            "Scroll through chart",
            min_value=0,
            max_value=max_start,
            value=0,
            step=1,
            key=f"{key_prefix}_scroll",
            help="Move left/right through the data to view more categories without overlapping labels.",
        )
        return work.iloc[start_idx:start_idx + max_visible].copy()

    def visible_pie_window(df, key_prefix, max_visible=12):
        if len(df) <= max_visible:
            return df
        start_idx = st.slider(
            "Scroll through categories",
            min_value=0,
            max_value=len(df) - max_visible,
            value=0,
            step=1,
            key=f"{key_prefix}_scroll",
        )
        return df.iloc[start_idx:start_idx + max_visible].copy()

    def finish_plotly(fig, x_series=None, y_series=None, *, x_slider=False, date_x=False, dense=False):
        """Apply compact sizing, readable ticks and native range sliders."""
        fig.update_layout(
            autosize=True,
            height=430,
            margin=dict(l=55, r=24, t=55, b=75),
            legend=dict(font=dict(size=11)),
        )
        if x_series is not None and not date_x:
            step = chart_tick_step(x_series)
            if step:
                fig.update_xaxes(dtick=step)
        if x_slider:
            fig.update_xaxes(
                rangeslider=dict(visible=True, thickness=0.055),
            )
        st.plotly_chart(fig, use_container_width=True)

    def finish_matplotlib(fig, ax, *, x_labels=None, key_prefix="chart", dense=False, x_numeric=None):
        """Compact Matplotlib output plus horizontal windowing for dense categorical axes."""
        fig.set_size_inches(9.2, 5.1)
        ax.margins(x=0.02, y=0.04)
        if x_labels is not None:
            labels = [str(v) for v in x_labels]
            if len(labels) > 25:
                # The caller should normally pass a pre-windowed dataset.
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
            else:
                ax.tick_params(axis="x", labelrotation=45, labelsize=8)
        else:
            ax.tick_params(axis="both", labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        fig.tight_layout(pad=1.15)
        st.pyplot(fig, use_container_width=True)

    # --------------------------------------------------------
    # MAIN VISUALIZATIONS
    # --------------------------------------------------------

    st.markdown("<div class='section-title'><span class='section-number'>05</span>📊 Main Visualizations</div>", unsafe_allow_html=True)

    numeric_cols = df_analysis.select_dtypes(include=np.number).columns.tolist()
    category_cols = df_analysis.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    datetime_cols = df_analysis.select_dtypes(include=["datetime64[ns]"]).columns.tolist()
    useful_numeric = [c for c in numeric_cols if not is_identifier_column(df_analysis, c)]

    main_options = []
    if category_cols and useful_numeric:
        main_options.append((f"Bar — {category_cols[0]} vs {useful_numeric[0]}", "bar"))
    if datetime_cols and useful_numeric:
        main_options.append((f"Line — {datetime_cols[0]} vs {useful_numeric[0]}", "line"))
    if len(useful_numeric) >= 2:
        main_options.append((f"Scatter — {useful_numeric[0]} vs {useful_numeric[1]}", "scatter"))
    if useful_numeric:
        main_options.append((f"Histogram — {useful_numeric[0]}", "histogram"))

    main_options = main_options[:4]

    if main_options:
        selected_main = st.radio(
            "Choose a main visualization",
            options=[label for label, _ in main_options],
            horizontal=True,
            key="main_visualization_selector",
        )
        chosen_type = dict(main_options)[selected_main]

        if chosen_type == "bar":
            x, y = category_cols[0], useful_numeric[0]
            temp = (
                df_analysis.groupby(x, dropna=False)[y]
                .mean().reset_index().sort_values(y, ascending=False)
            )
            temp = visible_window(temp, x, "main_bar")
            fig = px.bar(temp, x=x, y=y, title=f"Average {y} by {x}")
            finish_plotly(fig, y_series=temp[y])
        elif chosen_type == "line":
            x, y = datetime_cols[0], useful_numeric[0]
            temp = df_analysis.groupby(x)[y].mean().reset_index().sort_values(x)
            fig = px.line(temp, x=x, y=y, markers=True, title=f"Average {y} over time")
            finish_plotly(fig, y_series=temp[y], x_slider=True, date_x=True)
        elif chosen_type == "scatter":
            x, y = useful_numeric[:2]
            temp = df_analysis[[x, y]].dropna().copy()
            fig = px.scatter(temp, x=x, y=y, title=f"{y} vs {x}", render_mode="webgl")
            finish_plotly(fig, x_series=temp[x], y_series=temp[y], x_slider=True)
        elif chosen_type == "histogram":
            col = useful_numeric[0]
            values = safe_numeric(df_analysis[col]).dropna()
            fig = px.histogram(values, x=values, marginal="box", nbins=30, title=f"Distribution of {col}")
            finish_plotly(fig, x_series=values, x_slider=True)
    else:
        st.info("Not enough compatible columns for an automatic visualization.")

    # --------------------------------------------------------
    # MORE VISUALIZATIONS
    # --------------------------------------------------------

    st.markdown("<div class='section-title'><span class='section-number'>06</span>➕ More Visualizations</div>", unsafe_allow_html=True)

    more_visual_options = []
    if category_cols and useful_numeric:
        more_visual_options.append(("Pie", "pie"))
        more_visual_options.append(("Grouped Average Bar", "group_bar"))
    if useful_numeric:
        more_visual_options.append(("Box Plot", "box"))
    if len(useful_numeric) >= 2:
        more_visual_options.append(("Correlation Heatmap", "corr"))

    more_visual_options = more_visual_options[:4]

    if more_visual_options:
        selected_more = st.radio(
            "Choose an additional visualization",
            options=[label for label, _ in more_visual_options],
            horizontal=True,
            key="more_visualization_selector",
        )
        chosen_more = dict(more_visual_options)[selected_more]

        if chosen_more == "pie":
            c, v = category_cols[0], useful_numeric[0]
            temp = df_analysis.groupby(c, dropna=False)[v].sum().reset_index().sort_values(v, ascending=False)
            temp = visible_pie_window(temp, "more_pie")
            fig = px.pie(temp, names=c, values=v, title=f"{v} by {c}")
            finish_plotly(fig)
        elif chosen_more == "group_bar":
            c, v = category_cols[0], useful_numeric[0]
            temp = df_analysis.groupby(c, dropna=False)[v].mean().reset_index().sort_values(v, ascending=False)
            temp = visible_window(temp, c, "more_group_bar")
            fig = px.bar(temp, x=c, y=v, title=f"Average {v} by {c}")
            finish_plotly(fig, y_series=temp[v])
        elif chosen_more == "box":
            fig = px.box(df_analysis, y=useful_numeric[0], title=f"Box Plot of {useful_numeric[0]}")
            finish_plotly(fig, y_series=df_analysis[useful_numeric[0]])
        elif chosen_more == "corr":
            corr = df_analysis[useful_numeric].corr()
            fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")
            fig.update_layout(height=500, margin=dict(l=55, r=25, t=55, b=85))
            st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # CREATE YOUR OWN VISUALIZATION — 15 TYPES
    # Stateful chart rendering: moving a slider reruns Streamlit, so the
    # generated chart configuration/result is stored and rendered again.
    # The graph therefore stays visible while the user moves left/right.
    # --------------------------------------------------------

    st.markdown("<div class='section-title'><span class='section-number'>07</span>Create Your Own Visualization</div>", unsafe_allow_html=True)
    st.write("Choose a chart style, select your fields, and build a visualization that fits your data.")

    chart_style = st.radio(
        "Chart Style",
        ["Interactive", "Analytical"],
        horizontal=True,
        key="custom_chart_style",
    )
    custom_library = "Plotly" if chart_style == "Interactive" else "Matplotlib"

    chart_type = st.selectbox(
        "Select Chart Type",
        [
            "Bar", "Line", "Area", "Scatter", "Pie", "Donut", "Histogram",
            "Box Plot", "Violin Plot", "Bubble Chart", "Heatmap",
            "Correlation Heatmap", "Density Plot", "Funnel", "Treemap",
        ],
        key="custom_chart_type",
    )

    all_columns = df_analysis.columns.tolist()
    custom_num = df_analysis.select_dtypes(include=np.number).columns.tolist()
    custom_cat = df_analysis.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    if "custom_chart_state" not in st.session_state:
        st.session_state.custom_chart_state = None

    def group_result(x_col, y_col, agg_name):
        temp = df_analysis[[x_col, y_col]].dropna().copy()
        if agg_name == "Sum":
            return temp.groupby(x_col)[y_col].sum().reset_index()
        if agg_name == "Average":
            return temp.groupby(x_col)[y_col].mean().reset_index()
        if agg_name == "Count":
            return temp.groupby(x_col)[y_col].count().reset_index()
        if agg_name == "Minimum":
            return temp.groupby(x_col)[y_col].min().reset_index()
        return temp.groupby(x_col)[y_col].max().reset_index()

    def _state_signature(chart_name, library, params):
        return hashlib.sha256(
            json.dumps(
                {"chart": chart_name, "library": library, "params": params},
                sort_keys=True,
                default=str,
            ).encode("utf-8")
        ).hexdigest()

    def save_custom_chart(chart_name, library, params, data):
        st.session_state.custom_chart_state = {
            "signature": _state_signature(chart_name, library, params),
            "chart": chart_name,
            "library": library,
            "params": params,
            "data": data,
        }

    def current_custom_chart(chart_name, library, params):
        state = st.session_state.custom_chart_state
        if not state:
            return None
        if state["signature"] != _state_signature(chart_name, library, params):
            return None
        return state

    def current_window(df, key, max_visible=25):
        """Return the current window without creating the slider before the chart."""
        if len(df) <= max_visible:
            return df.copy(), 0, 0
        max_start = len(df) - max_visible
        start = int(st.session_state.get(key, 0))
        start = max(0, min(start, max_start))
        return df.iloc[start:start + max_visible].copy(), start, max_start

    def chart_window_slider(key, max_start, start, label="Scroll through chart"):
        if max_start > 0:
            st.slider(
                label,
                min_value=0,
                max_value=max_start,
                value=start,
                step=1,
                key=key,
                help="Move left or right to view the next data points without overlapping labels.",
            )

    def render_matplotlib_chart(fig, ax, x_labels=None, numeric_x=False):
        fig.set_size_inches(8.8, 4.9)
        fig.subplots_adjust(left=0.12, right=0.98, top=0.90, bottom=0.24 if x_labels is not None else 0.16)
        if x_labels is not None:
            labels = [str(v) for v in x_labels]
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.tick_params(axis="y", labelsize=9)
        st.pyplot(fig, use_container_width=True)

    def render_custom_plotly(fig, *, x_series=None, y_series=None):
        fig.update_layout(
            autosize=True,
            height=410,
            margin=dict(l=55, r=24, t=55, b=78),
        )
        if x_series is not None and pd.api.types.is_numeric_dtype(x_series):
            step = chart_tick_step(x_series)
            if step:
                fig.update_xaxes(dtick=step)
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------- BAR ----------------------------
    if chart_type == "Bar":
        if all_columns and custom_num:
            x_col = st.selectbox("X / Category", all_columns, key="cv_bar_x")
            y_col = st.selectbox("Y / Value", custom_num, key="cv_bar_y")
            agg = st.selectbox("Aggregation", ["Sum", "Average", "Count", "Minimum", "Maximum"], key="cv_bar_agg")
            params = {"x": x_col, "y": y_col, "agg": agg}

            if st.button("Generate Bar Chart", key="cv_bar_generate"):
                result = group_result(x_col, y_col, agg).sort_values(y_col, ascending=False).reset_index(drop=True)
                save_custom_chart("Bar", custom_library, params, result)

            state = current_custom_chart("Bar", custom_library, params)
            if state is not None:
                result = state["data"]
                view, start_idx, max_start = current_window(result, "cv_bar_scroll", 25)
                if custom_library == "Plotly":
                    fig = px.bar(view, x=x_col, y=y_col, title=f"{agg} of {y_col} by {x_col}")
                    render_custom_plotly(fig, y_series=view[y_col])
                else:
                    fig, ax = plt.subplots()
                    ax.bar(view[x_col].astype(str), view[y_col])
                    ax.set_xlabel(x_col); ax.set_ylabel(y_col); ax.set_title(f"{agg} of {y_col} by {x_col}")
                    render_matplotlib_chart(fig, ax, view[x_col])
                chart_window_slider("cv_bar_scroll", max_start, start_idx)
        else:
            st.info("Bar chart needs at least one numeric column.")

    # ----------------------- LINE ---------------------------
    elif chart_type == "Line":
        if all_columns and custom_num:
            x_col = st.selectbox("X Axis", all_columns, key="cv_line_x")
            y_col = st.selectbox("Y Axis", custom_num, key="cv_line_y")
            params = {"x": x_col, "y": y_col}

            if st.button("Generate Line Chart", key="cv_line_generate"):
                result = df_analysis[[x_col, y_col]].dropna().sort_values(x_col).reset_index(drop=True)
                save_custom_chart("Line", custom_library, params, result)

            state = current_custom_chart("Line", custom_library, params)
            if state is not None:
                result = state["data"]
                is_date = pd.api.types.is_datetime64_any_dtype(result[x_col])
                view, start_idx, max_start = current_window(result, "cv_line_scroll", 30)
                if custom_library == "Plotly":
                    fig = px.line(view, x=x_col, y=y_col, markers=True, title=f"{y_col} vs {x_col}")
                    render_custom_plotly(fig, y_series=view[y_col])
                else:
                    fig, ax = plt.subplots()
                    ax.plot(range(len(view)), view[y_col])
                    ax.set_xlabel(x_col); ax.set_ylabel(y_col); ax.set_title(f"{y_col} vs {x_col}")
                    render_matplotlib_chart(fig, ax, view[x_col] if not is_date else view[x_col].dt.strftime("%Y-%m-%d"))
                chart_window_slider("cv_line_scroll", max_start, start_idx)
        else:
            st.info("Line chart needs at least one numeric column.")

    # ----------------------- AREA ---------------------------
    elif chart_type == "Area":
        if all_columns and custom_num:
            x_col = st.selectbox("X Axis", all_columns, key="cv_area_x")
            y_col = st.selectbox("Y Axis", custom_num, key="cv_area_y")
            params = {"x": x_col, "y": y_col}

            if st.button("Generate Area Chart", key="cv_area_generate"):
                result = df_analysis[[x_col, y_col]].dropna().sort_values(x_col).reset_index(drop=True)
                save_custom_chart("Area", custom_library, params, result)

            state = current_custom_chart("Area", custom_library, params)
            if state is not None:
                result = state["data"]
                view, start_idx, max_start = current_window(result, "cv_area_scroll", 30)
                if custom_library == "Plotly":
                    fig = px.area(view, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
                    render_custom_plotly(fig, y_series=view[y_col])
                else:
                    fig, ax = plt.subplots()
                    ax.fill_between(range(len(view)), view[y_col].values)
                    ax.set_xlabel(x_col); ax.set_ylabel(y_col); ax.set_title(f"{y_col} vs {x_col}")
                    render_matplotlib_chart(fig, ax, view[x_col].astype(str))
                chart_window_slider("cv_area_scroll", max_start, start_idx)
        else:
            st.info("Area chart needs at least one numeric column.")

    # ----------------------- SCATTER ------------------------
    elif chart_type == "Scatter":
        if len(custom_num) >= 2:
            x_col = st.selectbox("X Axis", custom_num, key="cv_scatter_x")
            y_options = [c for c in custom_num if c != x_col]
            y_col = st.selectbox("Y Axis", y_options, key="cv_scatter_y")
            color_options = ["None"] + custom_cat
            color_col = st.selectbox("Color By (Optional)", color_options, key="cv_scatter_color")
            params = {"x": x_col, "y": y_col, "color": color_col}

            if st.button("Generate Scatter Chart", key="cv_scatter_generate"):
                cols = [x_col, y_col] + ([color_col] if color_col != "None" else [])
                plot_df = df_analysis[cols].dropna().reset_index(drop=True)
                save_custom_chart("Scatter", custom_library, params, plot_df)

            state = current_custom_chart("Scatter", custom_library, params)
            if state is not None:
                plot_df = state["data"]
                view, start_idx, max_start = current_window(plot_df, "cv_scatter_scroll", 500)
                if custom_library == "Plotly":
                    kwargs = {"x": x_col, "y": y_col, "title": f"{y_col} vs {x_col}", "render_mode": "webgl"}
                    if color_col != "None": kwargs["color"] = color_col
                    fig = px.scatter(view, **kwargs)
                    render_custom_plotly(fig, x_series=view[x_col], y_series=view[y_col])
                else:
                    fig, ax = plt.subplots()
                    ax.scatter(view[x_col], view[y_col], s=10, alpha=.65)
                    ax.set_xlabel(x_col); ax.set_ylabel(y_col); ax.set_title(f"{y_col} vs {x_col}")
                    render_matplotlib_chart(fig, ax)
                chart_window_slider("cv_scatter_scroll", max_start, start_idx, "Scroll through points")
        else:
            st.info("Scatter chart needs at least two numeric columns.")

    # ----------------------- PIE ----------------------------
    elif chart_type == "Pie":
        if custom_cat and custom_num:
            c = st.selectbox("Category", custom_cat, key="cv_pie_c")
            v = st.selectbox("Value", custom_num, key="cv_pie_v")
            params = {"c": c, "v": v}
            if st.button("Generate Pie Chart", key="cv_pie_generate"):
                result = df_analysis.groupby(c)[v].sum().reset_index().sort_values(v, ascending=False).reset_index(drop=True)
                save_custom_chart("Pie", custom_library, params, result)
            state = current_custom_chart("Pie", custom_library, params)
            if state is not None:
                result = state["data"]
                view, start_idx, max_start = current_window(result, "cv_pie_scroll", 12)
                if custom_library == "Plotly":
                    fig = px.pie(view, names=c, values=v, title=f"{v} by {c}")
                    render_custom_plotly(fig)
                else:
                    fig, ax = plt.subplots()
                    ax.pie(view[v], labels=view[c].astype(str), autopct="%1.1f%%")
                    ax.set_title(f"{v} by {c}")
                    render_matplotlib_chart(fig, ax)
                chart_window_slider("cv_pie_scroll", max_start, start_idx, "Scroll through categories")
        else:
            st.info("Pie chart needs a categorical and numeric column.")

    # ----------------------- DONUT --------------------------
    elif chart_type == "Donut":
        if custom_cat and custom_num:
            c = st.selectbox("Category", custom_cat, key="cv_donut_c")
            v = st.selectbox("Value", custom_num, key="cv_donut_v")
            params = {"c": c, "v": v}
            if st.button("Generate Donut Chart", key="cv_donut_generate"):
                result = df_analysis.groupby(c)[v].sum().reset_index().sort_values(v, ascending=False).reset_index(drop=True)
                save_custom_chart("Donut", custom_library, params, result)
            state = current_custom_chart("Donut", custom_library, params)
            if state is not None:
                result = state["data"]
                view, start_idx, max_start = current_window(result, "cv_donut_scroll", 12)
                if custom_library == "Plotly":
                    fig = px.pie(view, names=c, values=v, hole=.5, title=f"{v} by {c}")
                    render_custom_plotly(fig)
                else:
                    fig, ax = plt.subplots()
                    ax.pie(view[v], labels=view[c].astype(str), autopct="%1.1f%%")
                    centre = plt.Circle((0, 0), .70, fc="white")
                    ax.add_artist(centre)
                    ax.set_title(f"{v} by {c}")
                    render_matplotlib_chart(fig, ax)
                chart_window_slider("cv_donut_scroll", max_start, start_idx, "Scroll through categories")
        else:
            st.info("Donut chart needs a categorical and numeric column.")

    # ----------------------- HISTOGRAM ----------------------
    elif chart_type == "Histogram":
        if custom_num:
            col = st.selectbox("Numeric Column", custom_num, key="cv_hist_col")
            params = {"col": col}
            if st.button("Generate Histogram", key="cv_hist_generate"):
                save_custom_chart("Histogram", custom_library, params, safe_numeric(df_analysis[col]).dropna().reset_index(drop=True))
            state = current_custom_chart("Histogram", custom_library, params)
            if state is not None:
                values = state["data"]
                if values.empty:
                    st.info("No numeric values available for this histogram.")
                else:
                    lo, hi = float(values.min()), float(values.max())
                    range_key = "cv_hist_range"
                    selected_range = st.session_state.get(range_key, (lo, hi))
                    if not isinstance(selected_range, tuple) or len(selected_range) != 2:
                        selected_range = (lo, hi)
                    vmin, vmax = max(lo, float(selected_range[0])), min(hi, float(selected_range[1]))
                    hist_values = values[(values >= vmin) & (values <= vmax)]
                    if custom_library == "Plotly":
                        fig = px.histogram(hist_values, x=hist_values, marginal="box", nbins=30, title=f"Distribution of {col}")
                        render_custom_plotly(fig, x_series=hist_values)
                    else:
                        fig, ax = plt.subplots()
                        ax.hist(hist_values, bins=30)
                        ax.set_xlabel(col); ax.set_ylabel("Frequency"); ax.set_title(f"Distribution of {col}")
                        step = chart_tick_step(values)
                        if step:
                            ax.xaxis.set_major_locator(MultipleLocator(step))
                        render_matplotlib_chart(fig, ax)
                    if lo < hi:
                        st.slider(
                            "Adjust visible range",
                            min_value=lo,
                            max_value=hi,
                            value=(vmin, vmax),
                            key=range_key,
                            help="Move the range to inspect a different part of the distribution.",
                        )
        else:
            st.info("Histogram needs a numeric column.")

    # ----------------------- BOX PLOT -----------------------
    elif chart_type == "Box Plot":
        if custom_num:
            y_col = st.selectbox("Numeric Column", custom_num, key="cv_box_y")
            group_options = ["None"] + custom_cat
            group_col = st.selectbox("Group By (Optional)", group_options, key="cv_box_group")
            params = {"y": y_col, "group": group_col}
            if st.button("Generate Box Plot", key="cv_box_generate"):
                save_custom_chart("Box Plot", custom_library, params, df_analysis[[y_col] + ([] if group_col == "None" else [group_col])].copy())
            state = current_custom_chart("Box Plot", custom_library, params)
            if state is not None:
                box_df = state["data"]
                if custom_library == "Plotly":
                    if group_col == "None":
                        fig = px.box(box_df, y=y_col, title=f"Box Plot of {y_col}")
                    else:
                        if box_df[group_col].nunique(dropna=True) > 25:
                            keep = box_df[group_col].astype(str).value_counts().head(25).index
                            box_df = box_df[box_df[group_col].astype(str).isin(keep)]
                        fig = px.box(box_df, x=group_col, y=y_col, title=f"Box Plot of {y_col} by {group_col}")
                    render_custom_plotly(fig, y_series=box_df[y_col])
                else:
                    fig, ax = plt.subplots()
                    ax.boxplot(safe_numeric(box_df[y_col]).dropna())
                    ax.set_ylabel(y_col); ax.set_title(f"Box Plot of {y_col}")
                    render_matplotlib_chart(fig, ax)
        else:
            st.info("Box Plot needs a numeric column.")

    # ----------------------- VIOLIN -------------------------
    elif chart_type == "Violin Plot":
        if custom_num:
            y_col = st.selectbox("Numeric Column", custom_num, key="cv_violin_y")
            group_options = ["None"] + custom_cat
            group_col = st.selectbox("Group By (Optional)", group_options, key="cv_violin_group")
            params = {"y": y_col, "group": group_col}
            if st.button("Generate Violin Plot", key="cv_violin_generate"):
                save_custom_chart("Violin Plot", custom_library, params, df_analysis[[y_col] + ([] if group_col == "None" else [group_col])].copy())
            state = current_custom_chart("Violin Plot", custom_library, params)
            if state is not None:
                violin_df = state["data"]
                if custom_library == "Plotly":
                    if group_col != "None" and violin_df[group_col].nunique(dropna=True) > 25:
                        keep = violin_df[group_col].astype(str).value_counts().head(25).index
                        violin_df = violin_df[violin_df[group_col].astype(str).isin(keep)]
                    if group_col == "None":
                        fig = px.violin(violin_df, y=y_col, box=True, points="outliers", title=f"Violin Plot of {y_col}")
                    else:
                        fig = px.violin(violin_df, x=group_col, y=y_col, box=True, points="outliers", title=f"Violin Plot of {y_col} by {group_col}")
                    render_custom_plotly(fig, y_series=violin_df[y_col])
                else:
                    fig, ax = plt.subplots()
                    ax.violinplot(safe_numeric(violin_df[y_col]).dropna())
                    ax.set_ylabel(y_col); ax.set_title(f"Violin Plot of {y_col}")
                    render_matplotlib_chart(fig, ax)
        else:
            st.info("Violin Plot needs a numeric column.")

    # ----------------------- BUBBLE -------------------------
    elif chart_type == "Bubble Chart":
        if len(custom_num) >= 3:
            x_col = st.selectbox("X Axis", custom_num, key="cv_bubble_x")
            y_options = [c for c in custom_num if c != x_col]
            y_col = st.selectbox("Y Axis", y_options, key="cv_bubble_y")
            size_options = [c for c in custom_num if c not in [x_col, y_col]]
            size_col = st.selectbox("Bubble Size", size_options, key="cv_bubble_size")
            params = {"x": x_col, "y": y_col, "size": size_col}
            if st.button("Generate Bubble Chart", key="cv_bubble_generate"):
                plot_df = df_analysis[[x_col, y_col, size_col]].dropna().copy()
                plot_df["_size"] = plot_df[size_col].abs()
                save_custom_chart("Bubble Chart", custom_library, params, plot_df.reset_index(drop=True))
            state = current_custom_chart("Bubble Chart", custom_library, params)
            if state is not None:
                plot_df = state["data"]
                view, start_idx, max_start = current_window(plot_df, "cv_bubble_scroll", 500)
                if custom_library == "Plotly":
                    fig = px.scatter(view, x=x_col, y=y_col, size="_size", hover_data=[size_col], title=f"{y_col} vs {x_col}", render_mode="webgl")
                    render_custom_plotly(fig, x_series=view[x_col], y_series=view[y_col])
                else:
                    fig, ax = plt.subplots()
                    sizes = np.maximum(view["_size"].to_numpy(), 1)
                    ax.scatter(view[x_col], view[y_col], s=sizes)
                    ax.set_xlabel(x_col); ax.set_ylabel(y_col); ax.set_title(f"{y_col} vs {x_col}")
                    render_matplotlib_chart(fig, ax)
                chart_window_slider("cv_bubble_scroll", max_start, start_idx, "Scroll through points")
        else:
            st.info("Bubble Chart needs at least three numeric columns.")

    # ----------------------- HEATMAP ------------------------
    elif chart_type == "Heatmap":
        if all_columns and custom_num:
            x_col = st.selectbox("X Axis", all_columns, key="cv_heat_x")
            y_col = st.selectbox("Y Axis", all_columns, key="cv_heat_y")
            value_col = st.selectbox("Value", custom_num, key="cv_heat_v")
            agg = st.selectbox("Aggregation", ["Mean", "Sum", "Count"], key="cv_heat_agg")
            params = {"x": x_col, "y": y_col, "value": value_col, "agg": agg}
            if st.button("Generate Heatmap", key="cv_heat_generate"):
                if x_col == y_col:
                    st.warning("Choose different X and Y columns for a matrix-style heatmap.")
                else:
                    aggfunc = {"Mean": "mean", "Sum": "sum", "Count": "count"}[agg]
                    pivot = pd.pivot_table(df_analysis, values=value_col, index=y_col, columns=x_col, aggfunc=aggfunc)
                    save_custom_chart("Heatmap", custom_library, params, pivot)
            state = current_custom_chart("Heatmap", custom_library, params)
            if state is not None:
                pivot = state["data"]
                if pivot is not None and not pivot.empty:
                    rmax = min(25, len(pivot.index))
                    cmax = min(25, len(pivot.columns))
                    rstart = int(st.session_state.get("cv_heat_r", 0))
                    cstart = int(st.session_state.get("cv_heat_c", 0))
                    rstart = max(0, min(rstart, len(pivot.index)-rmax))
                    cstart = max(0, min(cstart, len(pivot.columns)-cmax))
                    view = pivot.iloc[rstart:rstart+rmax, cstart:cstart+cmax]
                    if custom_library == "Plotly":
                        fig = px.imshow(view, text_auto=True, aspect="auto", title=f"Heatmap of {agg} {value_col}")
                        fig.update_layout(height=500, margin=dict(l=55, r=25, t=55, b=90))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig, ax = plt.subplots()
                        im = ax.imshow(view.values, aspect="auto")
                        ax.set_xticks(range(len(view.columns))); ax.set_xticklabels(view.columns, rotation=45, ha="right", fontsize=7)
                        ax.set_yticks(range(len(view.index))); ax.set_yticklabels(view.index, fontsize=7)
                        ax.set_title(f"Heatmap of {agg} {value_col}")
                        fig.colorbar(im, ax=ax)
                        render_matplotlib_chart(fig, ax)
                    if len(pivot.index) > rmax:
                        st.slider("Scroll heatmap rows", 0, len(pivot.index)-rmax, rstart, key="cv_heat_r")
                    if len(pivot.columns) > cmax:
                        st.slider("Scroll heatmap columns", 0, len(pivot.columns)-cmax, cstart, key="cv_heat_c")
        else:
            st.info("Heatmap needs at least one numeric column and compatible X/Y columns.")

    # ------------------ CORRELATION HEATMAP -----------------
    elif chart_type == "Correlation Heatmap":
        if len(custom_num) >= 2:
            selected = st.multiselect(
                "Select Numeric Columns",
                custom_num,
                default=custom_num[:min(8, len(custom_num))],
                key="cv_corr_cols",
            )
            params = {"columns": tuple(selected)}
            if st.button("Generate Correlation Heatmap", key="cv_corr_generate"):
                if len(selected) < 2:
                    st.warning("Select at least two numeric columns.")
                else:
                    save_custom_chart("Correlation Heatmap", custom_library, params, df_analysis[selected].corr())
            state = current_custom_chart("Correlation Heatmap", custom_library, params)
            if state is not None and len(selected) >= 2:
                corr = state["data"]
                if custom_library == "Plotly":
                    fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")
                    fig.update_layout(height=500, margin=dict(l=55, r=25, t=55, b=90))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig, ax = plt.subplots()
                    im = ax.imshow(corr.values)
                    ax.set_xticks(range(len(corr.columns))); ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
                    ax.set_yticks(range(len(corr.columns))); ax.set_yticklabels(corr.columns, fontsize=8)
                    ax.set_title("Correlation Heatmap")
                    fig.colorbar(im, ax=ax)
                    render_matplotlib_chart(fig, ax)
        else:
            st.info("Correlation Heatmap needs at least two numeric columns.")

    # ----------------------- DENSITY ------------------------
    elif chart_type == "Density Plot":
        if custom_num:
            col = st.selectbox("Numeric Column", custom_num, key="cv_density_col")
            params = {"col": col}
            if st.button("Generate Density Plot", key="cv_density_generate"):
                save_custom_chart("Density Plot", custom_library, params, safe_numeric(df_analysis[col]).dropna().reset_index(drop=True))
            state = current_custom_chart("Density Plot", custom_library, params)
            if state is not None:
                values = state["data"]
                if custom_library == "Plotly":
                    fig = px.histogram(values, x=values, histnorm="probability density", marginal="rug", nbins=30, title=f"Density Plot of {col}")
                    render_custom_plotly(fig, x_series=values)
                else:
                    fig, ax = plt.subplots()
                    ax.hist(values, bins=30, density=True)
                    ax.set_xlabel(col); ax.set_ylabel("Density"); ax.set_title(f"Density Plot of {col}")
                    render_matplotlib_chart(fig, ax)
        else:
            st.info("Density Plot needs a numeric column.")

    # ----------------------- FUNNEL -------------------------
    elif chart_type == "Funnel":
        if custom_cat and custom_num:
            stage = st.selectbox("Stage / Category", custom_cat, key="cv_funnel_stage")
            value = st.selectbox("Value", custom_num, key="cv_funnel_value")
            params = {"stage": stage, "value": value}
            if st.button("Generate Funnel Chart", key="cv_funnel_generate"):
                result = df_analysis.groupby(stage)[value].sum().reset_index().sort_values(value, ascending=False).reset_index(drop=True)
                save_custom_chart("Funnel", custom_library, params, result)
            state = current_custom_chart("Funnel", custom_library, params)
            if state is not None:
                result = state["data"]
                view, start_idx, max_start = current_window(result, "cv_funnel_scroll", 15)
                if custom_library == "Plotly":
                    fig = px.funnel(view, y=stage, x=value, title=f"Funnel — {value}")
                    render_custom_plotly(fig, x_series=view[value])
                else:
                    st.warning("This chart works best with the Interactive chart style.")
                chart_window_slider("cv_funnel_scroll", max_start, start_idx, "Scroll through stages")
        else:
            st.info("Funnel needs a category/stage column and a numeric value column.")

    # ----------------------- TREEMAP ------------------------
    elif chart_type == "Treemap":
        if custom_cat and custom_num:
            path_col = st.selectbox("Category", custom_cat, key="cv_tree_cat")
            value_col = st.selectbox("Value", custom_num, key="cv_tree_value")
            params = {"path": path_col, "value": value_col}
            if st.button("Generate Treemap", key="cv_tree_generate"):
                result = df_analysis.groupby(path_col)[value_col].sum().reset_index().sort_values(value_col, ascending=False).reset_index(drop=True)
                save_custom_chart("Treemap", custom_library, params, result)
            state = current_custom_chart("Treemap", custom_library, params)
            if state is not None:
                result = state["data"]
                view, start_idx, max_start = current_window(result, "cv_tree_scroll", 25)
                if custom_library == "Plotly":
                    fig = px.treemap(view, path=[path_col], values=value_col, title=f"Treemap — {value_col}")
                    render_custom_plotly(fig)
                else:
                    st.warning("This chart works best with the Interactive chart style.")
                chart_window_slider("cv_tree_scroll", max_start, start_idx)
        else:
            st.info("Treemap needs a category and a numeric value column.")

    # --------------------------------------------------------
    # CURRENT FILTERED DATASET
    # --------------------------------------------------------

    with st.expander("📄 View Current Filtered Dataset", expanded=False):
        st.dataframe(df_analysis, use_container_width=True)

    # ========================================================
    # ASK YOUR DATA
    # ========================================================

    st.markdown(
        "<div class='section-title'><span class='section-number'>08</span>Ask Your Data</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ask-box">
            <div class="ask-heading">Ask a business question in plain English.</div>
            <div class="small-muted" style="margin-top:.3rem;">
                Your question is translated into a safe SQL plan, executed on the current filtered dataset,
                and only the verified SQL result is used for the final answer and insight.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # AI / SQL FUNCTIONS
    # --------------------------------------------------------

    def schema_for_ai(df):
        lines = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            examples = df[col].dropna().astype(str).head(3).tolist()
            examples_text = ", ".join(examples)
            if pd.api.types.is_numeric_dtype(df[col]):
                semantic_type = "NUMERIC_MEASURE"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                semantic_type = "DATE_TIME"
            elif pd.api.types.is_bool_dtype(df[col]):
                semantic_type = "BOOLEAN"
            else:
                semantic_type = "TEXT_CATEGORY"
            lines.append(
                f'- "{col}" | dtype={dtype} | semantic_type={semantic_type} | unique={df[col].nunique(dropna=True)} | examples={examples_text}'
            )
        return "\n".join(lines)

    def safe_json_from_text(text):
        text = (text or "").strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.I)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, flags=re.S)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            match = re.search(r"\[.*\]", text, flags=re.S)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
        return None

    def ai_chat(system_prompt, user_prompt, temperature=0):
        if client is None or GROQ_MODEL is None:
            raise RuntimeError("Groq is not configured.")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    def _suggestion_context(df):
        """Build a compact semantic profile used only by the question recommender."""
        numeric = [
            c for c in df.select_dtypes(include=np.number).columns
            if not is_identifier_column(df, c)
        ]

        categorical = [
            c for c in df.select_dtypes(include=["object", "category", "string"]).columns
            if 2 <= df[c].nunique(dropna=True) <= 25
            and not is_identifier_column(df, c)
        ]

        dates = [
            c for c in df.columns
            if pd.api.types.is_datetime64_any_dtype(df[c])
        ]

        def score_metric(col):
            name = normalize_name(col)

            strong = (
                REVENUE_TERMS,
                PROFIT_TERMS,
                COST_TERMS,
                QUANTITY_TERMS,
                DELAY_TERMS,
                DURATION_TERMS,
                RATING_TERMS,
                PRICE_TERMS,
                PERCENT_TERMS,
                EXPERIENCE_TERMS,
                INVENTORY_TERMS,
            )

            score = 0
            for rank, terms in enumerate(strong[::-1], start=1):
                if contains_any(name, terms):
                    score += rank * 10

            # Prefer measures with useful variation.
            try:
                nunique = int(df[col].nunique(dropna=True))
                if nunique >= 5:
                    score += 4
            except Exception:
                pass

            return score

        numeric = sorted(numeric, key=score_metric, reverse=True)

        # A semantic alias helps the LLM understand why an operation is sensible.
        metric_roles = []
        for col in numeric[:8]:
            name = normalize_name(col)
            if contains_any(name, REVENUE_TERMS):
                role = "revenue/sales measure"
            elif contains_any(name, PROFIT_TERMS):
                role = "profit measure"
            elif contains_any(name, COST_TERMS):
                role = "cost/expense measure"
            elif contains_any(name, QUANTITY_TERMS):
                role = "quantity/volume measure"
            elif contains_any(name, DELAY_TERMS):
                role = "delay measure"
            elif contains_any(name, DURATION_TERMS):
                role = "duration measure"
            elif contains_any(name, RATING_TERMS):
                role = "rating/score measure"
            elif contains_any(name, PRICE_TERMS):
                role = "price/fare measure"
            elif contains_any(name, PERCENT_TERMS):
                role = "percentage/rate measure"
            elif contains_any(name, EXPERIENCE_TERMS):
                role = "experience/tenure measure"
            elif contains_any(name, INVENTORY_TERMS):
                role = "inventory/production measure"
            else:
                role = "numeric measure (use with caution)"
            metric_roles.append(f'"{col}" → {role}')

        dimension_roles = []
        for col in categorical[:8]:
            unique = int(df[col].nunique(dropna=True))
            dimension_roles.append(f'"{col}" → categorical dimension ({unique} values)')

        date_roles = [f'"{c}" → date/time dimension' for c in dates[:5]]

        return {
            "metrics": numeric,
            "dimensions": categorical,
            "dates": dates,
            "metric_roles": metric_roles,
            "dimension_roles": dimension_roles,
            "date_roles": date_roles,
        }


    def _question_is_usable(question, df):
        q = str(question).strip()

        if not q or len(q) < 18 or len(q) > 170:
            return False

        if not q.endswith("?"):
            return False

        normalized_q = normalize_name(q)
        normalized_columns = {
            normalize_name(c): c for c in df.columns
        }

        # Basic dataset questions do not need a column name.
        if any(term in normalized_q for term in [
            "records", "rows", "dataset"
        ]):
            return True

        # A real dataset column/concept must be present.
        if not any(
            col_name and col_name in normalized_q
            for col_name in normalized_columns
        ):
            return False

        # Reject common low-quality LLM patterns.
        bad_phrases = [
            "average of the sum",
            "value of the sum",
            "sum column",
            "average value of",
            "change with",
            "what is the value of",
            "what is the metric of",
            "what is the data of",
        ]

        if any(phrase in normalized_q for phrase in bad_phrases):
            return False

        # Never recommend high-cardinality identifier dimensions.
        for col in df.columns:
            if is_identifier_column(df, col):
                col_name = normalize_name(col)
                if col_name and col_name in normalized_q:
                    return False

        return True


    def _question_quality(question, kind, df, context):
        """Additional quality gate for AI-generated suggestions."""
        q = normalize_name(question)

        if not _question_is_usable(question, df):
            return False

        metrics = context["metrics"]
        dimensions = context["dimensions"]
        dates = context["dates"]

        mentioned_metrics = [
            c for c in metrics if normalize_name(c) in q
        ]
        mentioned_dimensions = [
            c for c in dimensions if normalize_name(c) in q
        ]
        mentioned_dates = [
            c for c in dates if normalize_name(c) in q
        ]

        if kind.lower() == "trend":
            if not mentioned_dates or not mentioned_metrics:
                return False

        if kind.lower() in {"ranking", "top n", "bottom n", "comparison"}:
            if not mentioned_metrics:
                return False
            if not mentioned_dimensions and len(metrics) < 1:
                return False

        if kind.lower() == "relationship":
            if len(mentioned_metrics) < 2:
                return False

        # Do not let the model turn continuous numeric variables into fake categories.
        grouping_verbs = [
            "for each", "by each", "for every", "each distinct",
            "across every",
        ]
        continuous_numeric = [
            c for c in metrics if c not in dimensions
        ]
        if any(phrase in q for phrase in grouping_verbs):
            if any(normalize_name(c) in q for c in continuous_numeric):
                if not any(
                    normalize_name(d) in q for d in dimensions
                ):
                    return False

        return True


    def _fallback_questions(df):
        context = _suggestion_context(df)

        metrics = context["metrics"]
        dimensions = context["dimensions"]
        dates = context["dates"]

        questions = [
            ("Overview", "How many records are in the current dataset?")
        ]

        # 1–2 high-value overall measures.
        for metric in metrics[:2]:
            name = normalize_name(metric)

            if contains_any(name, PERCENT_TERMS) or contains_any(name, RATING_TERMS):
                questions.append(("Measure", f"What is the average {metric}?"))
                questions.append(("Ranking", f"Which values of {metric} are highest?"))
            elif contains_any(name, REVENUE_TERMS + PROFIT_TERMS + COST_TERMS + QUANTITY_TERMS):
                questions.append(("Measure", f"What is the total {metric}?"))
                questions.append(("Measure", f"What is the average {metric}?"))
            else:
                questions.append(("Measure", f"What is the average {metric}?"))

        # Category-based business questions.
        if dimensions and metrics:
            for dim in dimensions[:2]:
                metric = metrics[0]
                questions.append(
                    ("Ranking", f"Which {dim} has the highest average {metric}?")
                )
                questions.append(
                    ("Ranking", f"Which {dim} has the lowest average {metric}?")
                )
                questions.append(
                    ("Top N", f"What are the top 5 {dim} by {metric}?")
                )
                break

        # Trend question only when a genuine date exists.
        if dates and metrics:
            questions.append(
                ("Trend", f"How does total {metrics[0]} change over {dates[0]}?")
            )

        # Relationship question only between genuine continuous measures.
        if len(metrics) >= 2:
            questions.append(
                ("Relationship", f"What is the relationship between {metrics[0]} and {metrics[1]}?")
            )

        # Volume question for a low-cardinality business dimension.
        if dimensions:
            questions.append(
                ("Volume", f"Which {dimensions[0]} has the most records?")
            )

        seen = set()
        result = []
        for kind, question in questions:
            if question in seen:
                continue
            if _question_quality(question, kind, df, context):
                result.append({"type": kind, "question": question})
                seen.add(question)

        return result[:8]


    def generate_smart_questions(df):
        fallback = _fallback_questions(df)

        if client is None or GROQ_MODEL is None:
            return fallback

        context = _suggestion_context(df)

        schema_lines = []

        for item in context["metric_roles"]:
            schema_lines.append(item)

        for item in context["dimension_roles"]:
            schema_lines.append(item)

        for item in context["date_roles"]:
            schema_lines.append(item)

        ignored = [
            str(c) for c in df.columns
            if is_identifier_column(df, c)
        ]

        prompt = f"""
You are a senior business analyst designing the "Suggested Questions"
for an AI Data Analyst.

Your job is NOT to describe the dataset generically.
Your job is to propose the most useful questions a real analyst would
ask THIS dataset.

DATASET COLUMNS / SEMANTIC ROLES:
{chr(10).join(schema_lines)}

IDENTIFIER-LIKE COLUMNS TO AVOID AS BUSINESS DIMENSIONS:
{", ".join(ignored) if ignored else "None"}

Generate exactly 8 questions.

QUALITY STANDARD:
- Every question must lead to a useful decision, comparison, trend,
  ranking, measurement, or relationship.
- Use ONLY exact column names shown above.
- Never invent a metric, business concept, category, formula, or date.
- Never use ID / identifier / code / UUID / index / postal fields as
  analytical groupings.
- Do not create meaningless aggregations such as total age, total year,
  total rating, total percentage, or total identifier.
- Never turn a continuous numeric measure into "for each distinct value".
- For top/bottom questions, group by a real categorical business
  dimension, not a high-cardinality ID.
- Use SUM for naturally additive measures such as sales, revenue,
  profit, cost, passengers, quantity, units, bookings, etc.
- Use AVG for rates, percentages, ratings, prices, duration, delay,
  salary-like or other non-additive measures.
- Use COUNT for record-volume questions.
- Use trends only when a genuine date/time column exists.
- Use relationships/correlation only between meaningful numeric measures.
- Prefer questions that expose differences between categories or reveal
  trends rather than asking many simple averages.
- Questions must be short, natural English.
- Do NOT write phrases such as "average value of the sum column",
  "what is the value of", or artificial formulas in the question.
- Do not repeat the same analytical intent with different wording.

GOOD STYLE EXAMPLES:
- Which [category] has the highest total [additive metric]?
- Which [category] has the lowest average [non-additive metric]?
- What are the top 5 [category] by total [metric]?
- How does total [metric] change over [date]?
- What is the relationship between [metric 1] and [metric 2]?
- Which [category] has the most records?
- What is the average [metric] across all records?

BAD STYLE:
- What is the average of the sum column?
- What is [numeric measure] for each distinct value of [numeric measure]?
- Which identifier has the highest value? (unless the user explicitly asks
  about identifiers)
- What is the average value of [field] for each random continuous value?

DIVERSITY:
Return a useful mix of:
Overview, Measure, Ranking, Top N, Trend, Relationship, Comparison,
Volume.
Do not return more than two questions of the same analytical type.

Return JSON ONLY:
[
  {{"type":"Overview|Measure|Ranking|Top N|Trend|Relationship|Comparison|Volume",
    "question":"..."}}
]
"""

        try:
            raw = ai_chat(
                "You are an exacting business-question generator. "
                "Use only the provided dataset fields. Never hallucinate. "
                "Return JSON only.",
                prompt,
                temperature=0.15,
            )

            parsed = safe_json_from_text(raw)

            if not isinstance(parsed, list):
                return fallback

            cleaned = []
            seen = set()
            type_counts = {}

            # Preserve a balanced analytical mix.
            for item in parsed:
                if not isinstance(item, dict):
                    continue

                question = str(item.get("question", "")).strip()
                qtype = str(item.get("type", "Explore")).strip() or "Explore"

                normalized_type = qtype.lower()

                if question in seen:
                    continue

                if type_counts.get(normalized_type, 0) >= 2:
                    continue

                if _question_quality(question, qtype, df, context):
                    cleaned.append({
                        "type": qtype,
                        "question": question
                    })
                    seen.add(question)
                    type_counts[normalized_type] = (
                        type_counts.get(normalized_type, 0) + 1
                    )

                if len(cleaned) >= 8:
                    break

            if len(cleaned) >= 6:
                return cleaned[:8]

            return fallback

        except Exception:
            return fallback

    def validate_sql(sql_text, df):
        sql = (sql_text or "").strip()
        sql = re.sub(r"^```sql\s*", "", sql, flags=re.I)
        sql = re.sub(r"^```\s*", "", sql)
        sql = re.sub(r"\s*```$", "", sql).strip()

        if not sql:
            raise ValueError("AI returned an empty SQL query.")
        if ";" in sql.rstrip(";"):
            raise ValueError("Multiple SQL statements are not allowed.")

        lowered = sql.lower().strip()
        if not (lowered.startswith("select") or lowered.startswith("with")):
            raise ValueError("Only SELECT/WITH queries are allowed.")

        forbidden = [
            "insert", "update", "delete", "drop", "alter", "create",
            "replace", "pragma", "attach", "detach", "vacuum"
        ]
        for word in forbidden:
            if re.search(rf"\b{re.escape(word)}\b", lowered):
                raise ValueError(f"Unsafe SQL keyword detected: {word}")

        if not re.search(r"\bfrom\s+[\"`]?data[\"`]?\b", lowered):
            raise ValueError("SQL must query the temporary table named data.")

        return sql.rstrip(";").strip()

    def result_text(result_df):
        if result_df.empty:
            return "The query returned no rows."
        return result_df.head(30).to_string(index=False)

    def _format_result_value(value):
        if pd.isna(value):
            return "N/A"
        if isinstance(value, (int, np.integer)):
            return f"{int(value):,}"
        if isinstance(value, (float, np.floating)):
            return f"{float(value):,.2f}"
        return str(value)

    def deterministic_answer(question, result_df):
        if result_df.empty:
            return "No matching records were found for this question."

        if len(result_df) == 1 and len(result_df.columns) >= 2:
            entity = _format_result_value(result_df.iloc[0, 0])
            value = _format_result_value(result_df.iloc[0, 1])
            value_label = str(result_df.columns[1]).replace("_", " ")
            q = question.lower()
            if any(term in q for term in ["highest", "maximum", "most", "top 1"]):
                return f"**{entity}** has the highest {value_label}, with **{value}**."
            if any(term in q for term in ["lowest", "minimum", "least", "bottom 1"]):
                return f"**{entity}** has the lowest {value_label}, with **{value}**."
            return f"**{entity}** has **{value}** for {value_label}."

        if len(result_df) == 1:
            value = _format_result_value(result_df.iloc[0, 0])
            return f"**Result: {value}**"

        return f"The analysis returned **{len(result_df):,} rows**. The exact values are shown in the table below."

    def ai_answer(question, result_df):
        fallback = deterministic_answer(question, result_df)
        if result_df.empty or client is None or GROQ_MODEL is None:
            return fallback

        prompt = f"""
Answer the user's question using ONLY the verified SQL result below.
Never invent numbers, categories, or explanations that are not supported by the result.
Keep the answer to 1–2 sentences. Use the exact values from the result.
If the result has multiple rows, say that the result is shown in the table rather than pretending there is only one answer.
Do not mention SQL or the AI process.

USER QUESTION:
{question}

VERIFIED SQL RESULT:
{result_text(result_df)}
"""
        try:
            answer = ai_chat(
                "You write concise, data-grounded answers. Never fabricate or estimate values.",
                prompt,
                temperature=0,
            )
            return answer or fallback
        except Exception:
            return fallback

    # --------------------------------------------------------
    # GROQ STATUS + SMART QUESTIONS
    # --------------------------------------------------------

    if client is None or GROQ_MODEL is None:
        st.warning("Groq is not configured or no available Groq model was found. Check your .env API key.")

    # Generate once per dataset schema and reuse until a new file is uploaded.
    suggestion_signature = hashlib.sha256(
        "||".join(f"{c}:{df_analysis[c].dtype}" for c in df_analysis.columns).encode("utf-8")
    ).hexdigest()

    if (
        not st.session_state.suggested_questions
        or st.session_state.suggestion_signature != suggestion_signature
    ):
        with st.spinner("Preparing useful questions for this dataset..."):
            st.session_state.suggested_questions = generate_smart_questions(df_analysis)
            st.session_state.suggestion_signature = suggestion_signature

    suggested_question = None

    if st.session_state.suggested_questions:
        st.markdown(
            """
            <div class="suggestion-shell">
                <div class="suggestion-kicker">Smart question ideas</div>
                <div class="suggestion-title">Start with a question that fits your data</div>
                <div class="suggestion-subtitle">
                    Suggestions are generated from the available columns and are designed to be directly answerable by the analyst engine.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Browse suggested questions", expanded=True):
            qs = st.session_state.suggested_questions[:8]
            for start in range(0, len(qs), 2):
                row = qs[start:start + 2]
                cols_ui = st.columns(2)
                for ui_col, item in zip(cols_ui, row):
                    with ui_col:
                        st.caption(item.get("type", "Explore"))
                        if st.button(
                            item["question"],
                            key=f"suggested_q_{start}_{hashlib.md5(item['question'].encode()).hexdigest()[:8]}",
                            use_container_width=True,
                        ):
                            suggested_question = item["question"]

    if suggested_question:
        st.session_state["user_question"] = suggested_question

    user_question = st.text_input(
        "Ask your data question:",
        placeholder="e.g. Which department has the highest average salary?",
        key="user_question",
    )

    ask_button = st.button(
        "Ask",
        type="primary",
        use_container_width=False,
        key="ask_data_button",
    )

    # --------------------------------------------------------
    # ASK EXECUTION
    # --------------------------------------------------------

    if ask_button:
        if not user_question.strip():
            st.warning("Please enter a question.")
        elif client is None or GROQ_MODEL is None:
            st.error("Groq is not available. Check the GROQ_API_KEY in your .env file.")
        else:
            with st.spinner("Understanding the question, generating SQL, and checking the result..."):
                try:
                    dataset_schema = schema_for_ai(df_analysis)
                    recent_history = st.session_state.question_history[-3:]
                    history_text = "\n".join(
                        f"Q: {item['question']}\nA: {item.get('answer', '')}"
                        for item in recent_history
                    ) or "No previous questions."

                    plan_prompt = f"""
You are the SQL ANALYSIS ENGINE of a professional AI Data Analyst.

The user has a temporary SQLite table named data.

IMPORTANT:
The SQL result is the ONLY source of truth.
Never calculate, estimate, guess, invent, or modify numbers outside SQL.

DATASET SCHEMA:
{dataset_schema}

RECENT CHAT:
{history_text}

USER QUESTION:
{user_question}


========================
CORE SQL RULES
========================

1. Use ONLY the table named data.

2. SQL must be SQLite-compatible.

3. Generate ONLY ONE read-only SQL statement.

4. The SQL statement must start with SELECT or WITH.

5. Never use:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   CREATE
   REPLACE
   PRAGMA
   ATTACH
   DETACH
   VACUUM

6. Use ONLY columns that actually exist in the supplied schema.

7. Never invent column names.

8. Never invent values or categories.

9. Always perform the requested calculation inside SQL.

10. The SQL result must directly answer the user's question.

11. Never use an unrelated numeric column just because it exists.

12. Never use an ID, identifier, code, ZIP, postal code, UUID, index, or similar identifier as an analytical measure.

13. If the question asks for:
    - highest
    - lowest
    - maximum
    - minimum
    - most
    - least
    - top
    - bottom

    use ORDER BY and LIMIT whenever appropriate.

14. If the question asks for comparison between categories, use GROUP BY.

15. If the question asks for a total of a genuine measure, use SUM.

16. If the question asks for an average/rate/ratio/price/rating/duration, use AVG when appropriate.

17. If the question asks how many records exist, use COUNT(*).

18. If the question asks for number of records/flights/orders/etc., do NOT SUM a numeric column that merely happens to have a similar name.

19. If a date/time column actually exists, use it for trend/time questions.

20. Never create a date or category that does not exist.


========================
DERIVED METRIC RULES
========================

The dataset has already been cleaned and typed before SQL execution.
Use cleaned numeric columns directly. Do NOT use REPLACE, CAST, or other
string-cleaning functions on columns that are already numeric.

If the user asks for a derived business metric and the required source
columns actually exist, calculate it inside SQL. Common unambiguous examples:
- revenue / sales = unit_price * quantity
- total_value = price * quantity
- profit = revenue - cost
- profit_margin = profit * 100.0 / revenue when revenue is non-zero
- utilization / occupancy = passengers * 100.0 / seats when seats is non-zero

Only use a derived formula when all required source columns exist and the
formula is unambiguous. Never invent a formula or source column.

For derived metrics, use a clear alias such as revenue, total_value, profit,
profit_margin, or utilization.

========================
AIRLINE DATA RULES
========================

These rules are especially important for airline datasets.

If the dataset contains columns such as:

origin_airport
destination_airport
Flights
Passengers
Seats
Distance
Fly_date
Origin_city
Destination_city

then follow these rules.

A. "number of flights"
   = COUNT(*)

B. "most active airport by flights"
   = count flight records by origin_airport:

   SELECT
       "origin_airport",
       COUNT(*) AS "Total_flights"
   FROM data
   GROUP BY "origin_airport"
   ORDER BY "Total_flights" DESC
   LIMIT 1

C. "top airports by flights"
   = COUNT(*) grouped by origin_airport,
     ordered DESC.

D. DO NOT SUM("Flights") when the question means
   number of flight records.

E. DO NOT UNION origin_airport and destination_airport
   for a simple "most active airport" question.

F. Only use destination_airport when the user explicitly asks
   for destination airport activity.

G. If the user asks for a route, use BOTH:
   origin_airport + destination_airport.

H. If the user asks for passengers on a route:
   SUM("Passengers")
   GROUP BY origin_airport, destination_airport.

I. If the user asks for total passengers:
   SUM("Passengers").

J. If the user asks for average passengers:
   AVG("Passengers").

K. If the user asks for passenger-to-seat ratio:
   calculate it from the actual passenger and seat columns.
   Do not use an unrelated numeric column.

L. If the user asks for flight distribution at an airport,
   filter the requested airport and count the actual flight records.

M. "most active airport" means airport with the highest
   number of flight records, NOT the airport with the highest
   sum of a numeric Flights column.

N. "number of flights" and "flight records" mean COUNT(*)
   unless the user explicitly asks for a numeric Flights measure.


========================
GENERAL ANALYTICS RULES
========================

For "which category has the highest X":

SELECT category, AVG/SUM/MAX(X) AS metric
FROM data
GROUP BY category
ORDER BY metric DESC
LIMIT 1

Choose SUM or AVG according to the meaning of X.

For "top N":

GROUP BY the requested business dimension,
calculate the correct metric,
ORDER BY metric DESC,
LIMIT N.

For "bottom N":

GROUP BY the requested business dimension,
calculate the correct metric,
ORDER BY metric ASC,
LIMIT N.

For "how many":

use COUNT(*) for records.

For "total":

use SUM only when the requested field is a genuine additive measure.

For "average":

use AVG.

For "highest value":

use MAX or ORDER BY DESC depending on whether
the user wants the value itself or the category/record having it.

For trends:

GROUP BY the actual date/time field at an appropriate level.

For relationships/correlation:

use only meaningful numeric measures that actually exist.

Do not calculate correlation between IDs or identifiers.


========================
FILTER RULES
========================

If the user specifies a category/value:

- use the exact value from the dataset when available.
- do not invent spelling or values.
- use WHERE for filtering.

If the requested value does not exist in the schema/data,
do not fabricate a result.


========================
RESULT QUALITY RULE
========================

Before returning SQL, mentally verify:

1. Does every referenced column exist?
2. Is the table exactly data?
3. Is the aggregation correct?
4. Is COUNT(*) being used for record counts?
5. Am I accidentally using SUM for number of records?
6. Did I group by the correct business dimension?
7. Did I use origin_airport vs destination_airport correctly?
8. Did I use the correct passenger/seat measure?
9. Does ORDER BY match highest/lowest/top/bottom?
10. Does LIMIT match the requested number?
11. Is the SQL read-only?
12. Does the SQL directly answer the user's exact question?


========================
IMPORTANT
========================

Do NOT explain the SQL.

Return JSON only.

JSON FORMAT:

{{
    "supported": true,
    "operation": "group_by | aggregate | filter | compare | trend | correlation | other",
    "group_by": [],
    "metrics": [],
    "aggregation": "SUM | AVG | MIN | MAX | COUNT | NONE",
    "filters": [],
    "sort": "ASC | DESC | NONE",
    "limit": 1,
    "analysis_explanation": "brief explanation",
    "sql": "one SQLite SELECT/WITH statement"
}}

If the question cannot be answered from the available schema,
return:

{{
    "supported": false,
    "operation": "other",
    "group_by": [],
    "metrics": [],
    "aggregation": "NONE",
    "filters": [],
    "sort": "NONE",
    "limit": 0,
    "analysis_explanation": "Explain exactly why the question cannot be answered from the available columns.",
    "sql": ""
}}
"""

                    raw_plan = ai_chat(
                        "You are a careful SQL planning engine. Return valid JSON only and never fabricate data.",
                        plan_prompt,
                        temperature=0,
                    )
                    plan = safe_json_from_text(raw_plan)

                    if not isinstance(plan, dict):
                        raise ValueError("The AI did not return a valid analysis plan.")

                    with st.expander("Analysis Plan", expanded=True):
                        st.json(plan)

                    if not plan.get("supported", True):
                        st.warning(
                            plan.get(
                                "analysis_explanation",
                                "This question cannot be answered from the current dataset.",
                            )
                        )
                    else:
                        generated_sql = plan.get("sql", "")
                        safe_sql = validate_sql(generated_sql, df_analysis)

                        with st.expander("Generated SQL (for transparency)", expanded=True):
                            st.code(safe_sql, language="sql")

                        # Execute once; if the model makes a dialect/query mistake,
                        # allow exactly one constrained repair attempt.
                        try:
                            result_df = pd.read_sql_query(safe_sql, conn)
                        except Exception as sql_exc:
                            repair_prompt = f"""
The following SQLite query failed.

SCHEMA:
{dataset_schema}

USER QUESTION:
{user_question}

FAILED SQL:
{safe_sql}

ERROR:
{sql_exc}

Return ONLY one corrected SQLite SELECT/WITH query.
Rules:
- Use only table data.
- Use only columns from the schema.
- Do not invent values.
- Use already-cleaned numeric columns directly; do not use REPLACE/CAST for numeric arithmetic.
- If the question asks for revenue/value and the schema contains unit_price and quantity, calculate unit_price * quantity.
- No write operations.
"""
                            repaired_sql_raw = ai_chat(
                                "Repair the SQL safely. Return only one SQLite SELECT/WITH query.",
                                repair_prompt,
                                temperature=0,
                            )
                            repaired_sql = validate_sql(repaired_sql_raw, df_analysis)
                            result_df = pd.read_sql_query(repaired_sql, conn)
                            safe_sql = repaired_sql

                        # ------------------------------------------------
                        # VERIFIED QUERY RESULT — ALWAYS SHOWN AS A TABLE
                        # ------------------------------------------------
                        st.markdown("### Query Result")
                        st.markdown(
                            f"<div class='query-meta'><span><strong>{len(result_df):,}</strong> result row(s)</span><span>Source: verified SQL result</span></div>",
                            unsafe_allow_html=True,
                        )

                        with st.container(border=True):
                            if result_df.empty:
                                st.info("The query returned no rows.")
                            else:
                                st.dataframe(
                                    result_df,
                                    use_container_width=True,
                                    hide_index=True,
                                    height=min(420, max(120, 38 + len(result_df.head(12)) * 35)),
                                )

                        # ------------------------------------------------
                        # NATURAL-LANGUAGE ANSWER
                        # ------------------------------------------------
                        answer_text = ai_answer(user_question, result_df)
                        st.markdown("### Answer")
                        st.markdown(
                            f"<div class='answer-card'>{answer_text}</div>",
                            unsafe_allow_html=True,
                        )

                        csv_data = result_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "Download Result CSV",
                            data=csv_data,
                            file_name="ai_data_result.csv",
                            mime="text/csv",
                            key="download_ai_result",
                        )

                        # ------------------------------------------------
                        # SMART VISUAL SUMMARY
                        # ------------------------------------------------
                        if not result_df.empty and len(result_df) >= 2 and len(result_df.columns) >= 2:
                            chart_df = result_df.copy()
                            numeric_result_cols = [
                                c for c in chart_df.columns
                                if pd.api.types.is_numeric_dtype(chart_df[c])
                            ]
                            non_numeric_result_cols = [
                                c for c in chart_df.columns
                                if c not in numeric_result_cols
                            ]

                            if numeric_result_cols and non_numeric_result_cols:
                                x_col = non_numeric_result_cols[0]
                                y_col = numeric_result_cols[0]
                                operation = str(plan.get("operation", "")).lower()

                                if operation in {"trend"} or contains_any(x_col, ["date", "time", "month", "year", "week", "day", "period"]):
                                    fig = px.line(
                                        chart_df,
                                        x=x_col,
                                        y=y_col,
                                        markers=True,
                                        title=f"{y_col} over {x_col}",
                                    )
                                else:
                                    plot_df = chart_df.head(20)
                                    fig = px.bar(
                                        plot_df,
                                        x=x_col,
                                        y=y_col,
                                        title=f"{y_col} by {x_col}",
                                    )
                                st.markdown("### Visual Summary")
                                st.plotly_chart(fig, use_container_width=True)

                            elif len(numeric_result_cols) >= 2:
                                st.markdown("### Visual Summary")
                                fig = px.scatter(
                                    chart_df,
                                    x=numeric_result_cols[0],
                                    y=numeric_result_cols[1],
                                    title=f"{numeric_result_cols[1]} vs {numeric_result_cols[0]}",
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        # ------------------------------------------------
                        # AI INSIGHT FROM ACTUAL RESULT ONLY
                        # ------------------------------------------------
                        insight_prompt = f"""
You are the insight layer of an AI Data Analyst.

Use ONLY the verified SQL result below. Never invent a number or claim a cause that the result does not establish.
For WHY, use cautious language (may/could/possible) unless the result directly proves the statement.

USER QUESTION:
{user_question}

VERIFIED SQL RESULT:
{result_text(result_df)}

Return JSON only with exactly these fields:
{{
  "finding": "what the verified result says",
  "why": "what the result may indicate; clearly distinguish possible causes from proven evidence",
  "business_impact": "why this result matters for a practical decision",
  "recommendation": "one practical next action grounded in the available result"
}}
"""

                        try:
                            raw_insight = ai_chat(
                                "You explain verified data without fabricating. Return JSON only.",
                                insight_prompt,
                                temperature=0.1,
                            )
                            insight = safe_json_from_text(raw_insight)
                        except Exception:
                            insight = None

                        if not isinstance(insight, dict):
                            insight = {
                                "finding": "The verified SQL result above answers the requested question.",
                                "why": "The result is the direct evidence; additional causes should be checked against other available fields before making a causal claim.",
                                "business_impact": "This result can support a focused comparison or business decision.",
                                "recommendation": "Validate the result against relevant time, segment, geography, product, or other available dimensions.",
                            }

                        st.markdown("### Insight")
                        st.markdown(
                            f"""
                            <div class='insight-card'>
                                <div class='insight-label'>Finding</div>
                                <div>{insight.get('finding', '')}</div>
                                <div class='insight-label'>Why</div>
                                <div>{insight.get('why', '')}</div>
                                <div class='insight-label'>Business Impact</div>
                                <div>{insight.get('business_impact', '')}</div>
                                <div class='insight-label'>Recommendation</div>
                                <div>{insight.get('recommendation', '')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        qa_entry = {
                            "question": user_question,
                            "answer": answer_text,
                            "sql": safe_sql,
                        }
                        st.session_state.question_history.append(qa_entry)
                        st.session_state.question_history = st.session_state.question_history[-10:]

                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
                    st.caption(
                        "Try using a question tied to the available columns, such as a metric, category, date, or record count."
                    )

    # --------------------------------------------------------
    # QUESTION HISTORY
    # --------------------------------------------------------

    if st.session_state.question_history:
        with st.expander("🕘 Recent Questions", expanded=False):
            history_df = pd.DataFrame([
                {"Question": x["question"], "Answer": x["answer"]}
                for x in reversed(st.session_state.question_history)
            ])
            st.dataframe(history_df, use_container_width=True, hide_index=True)

    conn.close()

else:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-state-icon">📂</div>
            <div>
                <div class="empty-state-title">No dataset loaded yet</div>
                <div class="empty-state-text">Use the uploader above to add a CSV or XLSX file — cleaning, KPIs, charts and AI Q&amp;A will unlock automatically once it's in.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    "<div style='text-align:center;color:#6f8198;font-size:.8rem;margin-top:2rem;'>AI Data Analyst • Clean → Explore → Visualize → Ask → Analyze → Explain</div>",
    unsafe_allow_html=True,
)

# ============================================================

# ============================================================

# ============================================================

# ============================================================
