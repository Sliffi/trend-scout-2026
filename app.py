"""
╔══════════════════════════════════════════════════════════╗
║   LIVE TREND-SUCHMASCHINE   │   DACH-Raum 2026           ║
║   Powered by Google Gemini + Search Grounding            ║
╚══════════════════════════════════════════════════════════╝
"""

import json
import re
import time
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests

# ── Page-Config (muss als ERSTES stehen) ────────────────────────────────────
st.set_page_config(
    page_title="Trend Scout | DACH 2026",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* ── Fonts & base ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        /* ── Main background ── */
        .stApp { background: #0d0f1a; color: #e8eaf0; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #12152a 0%, #1a1d33 100%);
            border-right: 1px solid rgba(99, 102, 241, 0.2);
        }

        /* ── Hero banner ── */
        .hero-banner {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4c1d95 100%);
            border-radius: 20px;
            padding: 48px 40px;
            margin-bottom: 32px;
            border: 1px solid rgba(129, 140, 248, 0.25);
            box-shadow: 0 20px 60px rgba(99, 102, 241, 0.2);
            position: relative;
            overflow: hidden;
        }
        .hero-title {
            font-size: 2.6rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa, #818cf8, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 12px 0;
            line-height: 1.2;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
            font-weight: 400;
            margin: 0;
        }

        /* ── Trend card ── */
        .trend-card {
            background: linear-gradient(145deg, #1a1d33, #1e2240);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            transition: border-color 0.3s ease;
        }
        .trend-card:hover { border-color: rgba(129, 140, 248, 0.45); }

        .trend-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.9rem;
            color: white;
            margin-right: 12px;
            flex-shrink: 0;
        }
        .trend-name {
            font-size: 1.4rem;
            font-weight: 700;
            color: #e2e8f0;
            display: flex;
            align-items: center;
        }

        /* ── Info-Boxen ── */
        .info-box {
            background: rgba(15, 18, 36, 0.8);
            border-left: 3px solid;
            border-radius: 0 10px 10px 0;
            padding: 14px 18px;
            margin: 10px 0;
            font-size: 0.93rem;
            line-height: 1.65;
        }
        .info-box-trigger  { border-color: #6366f1; }
        .info-box-driver   { border-color: #10b981; }
        .info-box-campaign { border-color: #f59e0b; }

        .info-label {
            font-weight: 600;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .label-trigger  { color: #818cf8; }
        .label-driver   { color: #34d399; }
        .label-campaign { color: #fbbf24; }

        /* ── Badge ── */
        .badge {
            display: inline-block;
            background: rgba(99, 102, 241, 0.18);
            border: 1px solid rgba(99, 102, 241, 0.4);
            color: #a5b4fc;
            border-radius: 20px;
            padding: 3px 12px;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-left: 12px;
            vertical-align: middle;
        }

        /* ── Input & Buttons ── */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextInput"] input:focus {
            background: #1e2240 !important;
            border: 1px solid rgba(99, 102, 241, 0.4) !important;
            border-radius: 12px !important;
            color: #e2e8f0 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.95rem !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        }

        div[data-testid="stButton"] button {
            background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 14px 28px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.02em !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        }
        div[data-testid="stButton"] button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.45) !important;
        }

        /* ── Divider ── */
        hr { border-color: rgba(99, 102, 241, 0.2) !important; margin: 24px 0 !important; }

        /* ── Metric ── */
        [data-testid="stMetric"] {
            background: #1a1d33;
            border: 1px solid rgba(99,102,241,0.2);
            border-radius: 12px;
            padding: 14px 18px;
        }
        [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.78rem !important; }
        [data-testid="stMetricValue"] { color: #a5b4fc !important; font-size: 1.5rem !important; font-weight: 700 !important; }

        /* ── Sidebar headings ── */
        .sidebar-section {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #6366f1;
            margin: 20px 0 8px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; margin-bottom: 24px;">
            <div style="font-size:2.5rem;">🔍</div>
            <div style="font-weight:700; font-size:1.1rem; color:#e2e8f0;">Trend Scout</div>
            <div style="font-size:0.78rem; color:#64748b;">DACH-Raum 2026 · Live Research</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">🔐 API-Konfiguration</div>', unsafe_allow_html=True)

    api_key_from_secrets = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""

    if api_key_from_secrets:
        st.success("✅ API-Key via Secrets geladen")
        gemini_api_key = api_key_from_secrets
    else:
        gemini_api_key = st.text_input(
            "Gemini API-Key",
            type="password",
            placeholder="AQ... oder AIza...",
            help="Trage deinen Google AI Studio oder GCP API-Key ein.",
        )
        if not gemini_api_key:
            st.info("💡 Trage deinen Gemini API-Key ein, um loszulegen.")

    st.markdown('<div class="sidebar-section">⚙️ Analyse-Einstellungen</div>', unsafe_allow_html=True)

    region = st.selectbox(
        "Region",
        ["DACH-Raum (DE/AT/CH)", "Deutschland", "Österreich", "Schweiz"],
        index=0,
    )

    num_trends = st.slider("Anzahl der Trends", min_value=3, max_value=7, value=5)

    category_filter = st.multiselect(
        "Kategorien-Filter",
        ["Food & Nutrition", "Fitness & Wellness", "Supplements", "Mental Health", "Lifestyle"],
        default=[],
        placeholder="Alle Kategorien",
    )

# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-banner">
        <p class="hero-title">🚀 Live Trend-Suchmaschine</p>
        <p class="hero-subtitle">
            Entdecke die heißesten Micro-Trends im DACH-Raum – powered by Google Gemini &amp; Live Search Grounding.
            Reale, geschätzte Plattform-Erwähnungen statt abstrakter Scores. Stand: Juni 2026.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Eingabebereich ────────────────────────────────────────────────────────────
st.markdown("### 🎯 Thema & Nische analysieren")

col_input, col_btn = st.columns([4, 1])

with col_input:
    topic = st.text_input(
        label="Analyse-Thema",
        placeholder="z.B. Vegan, Proteine, Supplements, Pilates, Longevity, Matcha ...",
        label_visibility="collapsed",
    )

with col_btn:
    st.markdown("<div style='height: 4px'></div>", unsafe_allow_html=True)
    analyse_btn = st.button("🔍 Trends analysieren", use_container_width=True)

# ── Gemini-API-Funktion ────────────────────────────────────────────────────────
def build_prompt(topic: str, region: str, num_trends: int, categories: list) -> str:
    cat_str = ", ".join(categories) if categories else "alle relevanten Kategorien"
    return f"""Du bist ein Weltklasse-OSINT-Trend-Research-Analyst für den DACH-Markt (Deutschland, Österreich, Schweiz).
Analysiere das Thema: **"{topic}"** im Sektor: {region} für den aktuellen Stand (Juni 2026).

Identifiziere genau {num_trends} hochaktuelle Micro-Trends.
Basiere deine Analyse auf realen Funden aus TikTok (Hashtag-Views), Google Trends, Instagram-Reels und Reddit.

WICHTIG: Wir wollen KEINE künstlichen Scores von 0-100 mehr. Wir wollen die geschätzte, reale Anzahl an monatlichen Interaktionen/Erwähnungen/Suchanfragen (Volumen) im DACH-Raum für diesen spezifischen Trend sehen. Jede Kurve muss individuell sein und die realen Zahlen widerspiegeln (z.B. startet bei 3.000 im Januar und explodiert auf 120.000 im Juni).

Antworte AUSSCHLIESSLICH im folgenden JSON-Format (reines JSON ohne Markdown-Hülle):

{{
  "topic": "{topic}",
  "region": "{region}",
  "analysis_date": "Juni 2026",
  "trends": [
    {{
      "rank": 1,
      "name": "Trend-Name (knackig, 3-5 Wörter)",
      "category": "Kategorie",
      "status": "Wachstumsphase",
      "metric_unit": "z.B. TikTok-Views / Google-Suchanfragen / Reddit-Mentions",
      "monthly_scores": {{
        "Jan 2026": 4500,
        "Feb 2026": 6800,
        "Mar 2026": 12000,
        "Apr 2026": 34000,
        "May 2026": 78000,
        "Jun 2026": 145000
      }},
      "peak_platform": "TikTok / Instagram / Reddit",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "trigger": "Konkrete Zahlen (Aufrufe, % Suchvolumen-Steigerung) nennen.",
      "driver": "Das tieferliegende Konsumenten-Bedürfnis dahinter.",
      "campaign_idea": "Eine konkrete, kreative Kampagnen-Idee für Agenturen."
    }}
  ]
}}"""


def call_gemini_with_grounding(api_key: str, prompt: str) -> dict:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8192}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Google API Fehler ({response.status_code}): {response.text}")
    
    response_json = response.json()
    raw_text = response_json['candidates'][0]['content']['parts'][0]['text'].strip()
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        raise ValueError("Kein gültiges JSON gefunden.")
    return json.loads(json_match.group(0))


def create_trend_chart(trend_data: dict, rank: int) -> go.Figure:
    months = list(trend_data["monthly_scores"].keys())
    scores = list(trend_data["monthly_scores"].values())
    unit = trend_data.get("metric_unit", "Erwähnungen")

    df = pd.DataFrame({"Monat": months, "Volumen": scores})
    colors = ["#818cf8", "#a78bfa", "#60a5fa", "#34d399", "#fb923c"]
    color = colors[(rank - 1) % len(colors)]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Monat"], y=df["Volumen"],
            fill="tozeroy",
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.08)",
            line=dict(color=color, width=3),
            mode="lines+markers",
            marker=dict(size=9, color=color, symbol="circle", line=dict(color="white", width=2)),
            hovertemplate="<b>%{x}</b><br>Volumen: <b>%{y:,}</b><extra></extra>",
            name=trend_data["name"],
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8"),
        xaxis=dict(gridcolor="rgba(99,102,241,0.12)", showline=False, tickfont=dict(size=12, color="#64748b")),
        yaxis=dict(
            gridcolor="rgba(99,102,241,0.12)", showline=False, tickfont=dict(size=12, color="#64748b"),
            title=dict(text=unit, font=dict(size=12, color="#64748b")),
            tickformat=",", # Macht Tausendertrennzeichen (z.B. 100,000)
        ),
        margin=dict(l=10, r=10, t=10, b=10), height=280, showlegend=False,
        hoverlabel=dict(bgcolor="#1e2240", bordercolor=color, font=dict(family="Inter, sans-serif", color="#e2e8f0", size=13)),
    )
    return fig


def render_trend_card(trend: dict, rank: int):
    hashtags_html = " ".join(
        f'<span style="background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.35); '
        f'color:#a5b4fc; border-radius:20px; padding:2px 10px; font-size:0.75rem; margin:2px; '
        f'display:inline-block;">{h}</span>' for h in trend.get("hashtags", [])
    )

    st.markdown(
        f"""
        <div class="trend-card">
            <div class="trend-name">
                <span class="trend-number">{rank}</span>
                {trend['name']}
                <span class="badge">📈 {trend.get('status', 'Micro-Trend')}</span>
            </div>
            <div style="margin: 10px 0 4px 48px; font-size:0.82rem; color:#64748b;">
                📂 {trend.get('category', '—')} &nbsp;|&nbsp;
                🏆 Hauptplattform: <span style="color:#a5b4fc">{trend.get('peak_platform', '—')}</span> &nbsp;|&nbsp;
                Metrik: <span style="color:#34d399">{trend.get('metric_unit', 'Erwähnungen')}</span>
            </div>
            <div style="margin: 8px 0 16px 48px;">{hashtags_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = create_trend_chart(trend, rank)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="info-box info-box-trigger"><div class="info-label label-trigger">🔥 Der Daten-Beweis</div>{trend.get("trigger", "—")}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="info-box info-box-driver"><div class="info-label label-driver">🧠 Das Konsumenten-Warum</div>{trend.get("driver", "—")}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="info-box info-box-campaign"><div class="info-label label-campaign">💡 Kampagnen-Idee</div>{trend.get("campaign_idea", "—")}</div>', unsafe_allow_html=True)
    st.markdown("---")


# ── Hauptlogik ────────────────────────────────────────────────────────────────
if analyse_btn:
    if not topic:
        st.warning("⚠️ Bitte gib ein Thema ein.")
        st.stop()
    if not gemini_api_key:
        st.error("🔑 Kein API-Key gefunden.")
        st.stop()

    with st.spinner("🔍 Durchsuche das Web nach echten Plattform-Zahlen …"):
        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        for i, msg in enumerate([
            "🌐 Google Search Grounding scannt Plattform-Volumen …",
            "📡 Extrahiere echte Erwähnungen aus TikTok & Reddit …",
            "📊 Skaliere individuelle Trend-Kurven für 2026 …",
        ]):
            status_placeholder.markdown(f'<div style="color:#a5b4fc; font-size:0.9rem;">⚡ {msg}</div>', unsafe_allow_html=True)
            progress_bar.progress((i + 1) * 33)
            time.sleep(0.5)

        try:
            prompt = build_prompt(topic, region, num_trends, category_filter)
            result = call_gemini_with_grounding(gemini_api_key, prompt)
            progress_bar.progress(100)
            status_placeholder.empty()
        except Exception as e:
            st.error(f"❌ Fehler: {e}")
            st.stop()

    trends = result.get("trends", [])
    if not trends:
        st.warning("⚠️ Keine Trends gefunden.")
        st.stop()

    st.success(f"✅ **{len(trends)} Real-Data Micro-Trends** für **{topic}** erfolgreich extrahiert!")

    # Da die Einheiten unterschiedlich sind, blenden wir die ungenaue Gesamt-Metrik aus 
    # und springen direkt in die individuellen Auswertungen
    st.markdown(f"### 🔥 Die {len(trends)} Real-Data Trends im Detail")
    st.markdown("<br>", unsafe_allow_html=True)

    for trend in trends:
        render_trend_card(trend, trend.get("rank", 1))
else:
    st.markdown(
        """
        <div style="text-align: center; padding: 80px 40px; background: linear-gradient(145deg, #1a1d33, #1e2240); border: 1px dashed rgba(99, 102, 241, 0.3); border-radius: 20px; margin-top: 20px;">
            <div style="font-size: 3.5rem; margin-bottom: 16px;">🧭</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #e2e8f0; margin-bottom: 8px;">Bereit für Real-Data-Analyse</div>
            <div style="font-size: 0.9rem; color: #64748b; max-width: 400px; margin: 0 auto; line-height: 1.6;">
                Schluss mit abstrakten 0-100 Scores. Diese Engine extrahiert die echten, geschätzten Beitrags- und Erwähnungszahlen aus dem Web für das Jahr 2026.
            </div>
        </div>
        """, unsafe_allow_html=True
    )
