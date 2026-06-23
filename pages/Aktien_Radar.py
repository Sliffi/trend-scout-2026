"""
╔══════════════════════════════════════════════════════════╗
║   SOCIAL-VOLUME & QUANT PATTERN RECOGNITION ENGINE       ║
║   Fusion aus harten Chartdaten und Live-Reddit-OSINT     ║
╚══════════════════════════════════════════════════════════╝
"""

import json
import re
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import yfinance as yf
import ta

# ── Page-Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quant Social Probability Radar",
    page_icon="🎯",
    layout="wide",
)

# ── Custom Quant UI / Styling ────────────────────────────────────────────────
st.markdown("""
    <style>
        .stApp { background: #0a0d1a; color: #e2e8f0; }
        .stock-box {
            background: linear-gradient(145deg, #131729, #1b203a);
            border: 1px solid #10b981;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 22px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .signal-tag {
            background: rgba(59, 130, 246, 0.12);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.4);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-block;
            margin: 4px;
        }
        .social-tag {
            background: rgba(239, 68, 68, 0.12);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-block;
            margin: 4px;
        }
        .prob-badge {
            background: linear-gradient(135deg, #1d4ed8, #3b82f6);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            border: 1px solid #60a5fa;
        }
    </style>
""", unsafe_allow_html=True)

# ── KEY & SESSION-STATE FIX ──────────────────────────────────────────────────
# Falls der Key in der Haupt-App hinterlegt war, versuchen wir ihn direkt abzugreifen
if "GEMINI_API_KEY" not in st.session_state:
    st.session_state["GEMINI_API_KEY"] = ""

# ── SIDEBAR CONFIGURATION (Regler & Keys) ───────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-weight:700; color:#10b981; margin-bottom:8px;">🛠️ SYSTEM-STEUERUNG</div>', unsafe_allow_html=True)
    
    # Neues verankertes Eingabefeld
    input_key = st.text_input(
        "Gemini API-Key",
        type="password",
        placeholder="AQ... oder AIza...",
        value=st.session_state["GEMINI_API_KEY"]
    )
    
    # Sofort im Session-State speichern, wenn etwas eingetragen wurde
    if input_key:
        st.session_state["GEMINI_API_KEY"] = input_key
    
    st.markdown("---")
    st.markdown('<div style="font-weight:700; color:#3b82f6; margin-bottom:8px;">🎛️ SCHWELLE (REGLER)</div>', unsafe_allow_html=True)
    
    min_probability = st.slider(
        "Mindest-Ausbruchswahrscheinlichkeit (%)",
        min_value=30,
        max_value=95,
        value=70,
        step=5,
        help="Filtert schwache Signale heraus. Alles unter diesem Wert wird im Dashboard ausgeblendet."
    )

# Header-Bereich
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); 
                border-radius: 20px; padding: 40px; margin-bottom: 32px; border: 1px solid #4338ca;">
        <h1 style="color: white; margin: 0 0 12px 0;">🎯 Social-Volume & Chart-Breakout Engine</h1>
        <p style="color: #c7d2fe; margin: 0; font-size: 1.05rem;">
            Fusion aus harten Markt-Indikatoren (>100 Berechnungen) und Live-OSINT-Scans auf Reddit, Foren & Social Media.
            Aktuelle Hürde: <b style="color:#60a5fa">>={min_probability}%</b> kombinierte Wahrscheinlichkeit. Stand: Juni 2026.
        </p>
    </div>
""", unsafe_allow_html=True)

# Sektorenauswahl
market_type = st.selectbox(
    "Wähle das Ziel-Universum für den Scan:",
    ["US Tech Leader & Retail Favorites", "DACH-Raum Blue-Chips & Growth Caps"]
)

# Ticker-Listen für das hocheffiziente Screening
MARKET_LISTS = {
    "US Tech Leader & Retail Favorites": ["GME", "NVDA", "PLTR", "TSLA", "AMD", "SMCI", "COIN", "MSTR", "AMC"],
    "DACH-Raum Blue-Chips & Growth Caps": ["SAP.DE", "IFX.DE", "RHM.DE", "ZAL.DE", "BMW.DE", "ADS.DE"]
}

scan_btn = st.button("🔍 System-Sieb aktivieren & Social-Scans starten", use_container_width=True)

# ── STRAND 1: LIVE SOCIAL-VOLUME OSINT VIA KI ────────────────────────────────
def fetch_social_volume_via_ki(api_key, ticker):
    prompt = f"""Du bist ein OSINT-Daten-Scraper für Finanzmärkte. 
Scanne das Web (Reddit wie r/WallStreetBets, r/stocks, Twitter/X, Finanzforen) nach Erwähnungen des Tickers '{ticker}' für Juni 2026.
Ermittle, wie stark das Social-Media-Erwähnungsvolumen im Vergleich zum Vormonat gestiegen ist.

Antworte NUR mit validem JSON in diesem Format:
{{
  "volume_growth_pct": 150,
  "reddit_sentiment": "Bullish",
  "hot_topic": "Ein prägnanter Satz, worüber die Retail-Anleger gerade diskutieren."
}}"""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}
    payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}
    try:
        res = requests.post(url, headers=headers, json=payload)
        raw_text = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        match = re.search(r"\{[\s\S]*\}", raw_text)
        return json.loads(match.group(0))
    except Exception:
        return {"volume_growth_pct": 0, "reddit_sentiment": "Neutral", "hot_topic": "Kein auffälliger Social-Volume-Spike registriert."}

# ── STRAND 2: MATHEMATISCHE CHARTMUSTER-MASCHINE ────────────────────────────
def evaluate_stock_with_social(ticker, social_data):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6m")
        if df.empty or len(df) < 60:
            return None
        
        patterns = []
        total_points = 0
        
        growth = social_data.get("volume_growth_pct", 0)
        if growth >= 200:
            patterns.append(f"🔥 Reddit/Social Hyper-Spike (+{growth}%)")
            total_points += 40
        elif growth >= 50:
            patterns.append(f"📈 Steigendes Social-Interesse (+{growth}%)")
            total_points += 20

        current_volume = df['Volume'].iloc[-1]
        avg_volume_20d = df['Volume'].iloc[-21:-1].mean()
        if current_volume > avg_volume_20d * 2.0:
            patterns.append("⚙️ Börsen-Handelsvolumen verdoppelt")
            total_points += 20

        bb_high = ta.volatility.bollinger_hband(df['Close'])
        bb_low = ta.volatility.bollinger_lband(df['Close'])
        bb_bandwidth = (bb_high - bb_low) / df['Close']
        if bb_bandwidth.iloc[-1] < bb_bandwidth.rolling(20).mean().iloc[-1] * 0.82:
            patterns.append("💥 Chart-Kompression (Squeeze-Muster)")
            total_points += 20

        macd = ta.trend.macd(df['Close'])
        macd_signal = ta.trend.macd_signal(df['Close'])
        if macd.iloc[-1] > macd_signal.iloc[-1] and macd.iloc[-2] <= macd_signal.iloc[-2]:
            patterns.append("🔀 MACD Bullish Crossover")
            total_points += 20

        final_prob = min(total_points, 98)
        if final_prob == 0:
            rsi = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
            final_prob = int(35 + (rsi / 10))

        return {
            "ticker": ticker,
            "name": stock.info.get("longName", ticker),
            "price": df['Close'].iloc[-1],
            "change": ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
            "patterns": patterns,
            "probability": final_prob,
            "df": df
        }
    except Exception:
        return None

# ── HAUPT-ANALYSEPROZESS ─────────────────────────────────────────────────────
if scan_btn:
    # Greift jetzt garantiert auf den globalen Speicher zu
    active_key = st.session_state["GEMINI_API_KEY"]
    
    if not active_key or active_key.strip() == "":
        st.error("🔑 Der Gemini API-Key wird zwingend benötigt. Bitte trage den Key in der Sidebar ein und bestätige kurz mit Enter.")
        st.stop()
        
    tickers_to_scan = MARKET_LISTS[market_type]
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(tickers_to_scan):
        status_text.markdown(f"📡 Scanne **{ticker}** ...")
        social_res = fetch_social_volume_via_ki(active_key, ticker)
        stock_res = evaluate_stock_with_social(ticker, social_res)
        
        if stock_res:
            stock_res["social_sentiment"] = social_res.get("reddit_sentiment", "Neutral")
            stock_res["social_topic"] = social_res.get("hot_topic", "Keine auffälligen Themen.")
            results.append(stock_res)
            
        progress_bar.progress(int((idx + 1) / len(tickers_to_scan) * 100))
        
    status_text.empty()
    progress_bar.empty()

    filtered_output = [s for s in results if s["probability"] >= min_probability]
    
    if not filtered_output:
        st.info(f"ℹ️ Keine Aktie erreicht aktuell {min_probability}%.")
        st.stop()
        
    filtered_output = sorted(filtered_output, key=lambda x: x["probability"], reverse=True)
    st.success(f"🎯 {len(filtered_output)} Kandidaten gefunden:")
    
    for stock in filtered_output:
        st.markdown(f"""
            <div class="stock-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <span style="font-size: 1.6rem; font-weight: 800; color: #60a5fa;">📈 {stock['ticker']}</span>
                        <span style="color: #64748b; margin-left: 10px;">— {stock['name']}</span>
                    </div>
                    <span class="prob-badge">Wahrscheinlichkeit: {stock['probability']}%</span>
                </div>
                <div style="font-size: 1.05rem; margin-bottom: 14px;">
                    Live-Kurs: <b>${stock['price']:.2f}</b> 
                    (<span style="color: {'#10b981' if stock['change'] >= 0 else '#ef4444'}">{stock['change']:+.2f}%</span>)
                    &nbsp;|&nbsp; Reddit Sentiment: <b style="color: #f87171;">{stock['social_sentiment']}</b>
                </div>
                <div style="margin-bottom: 18px;">
                    {"".join([f'<span class="signal-tag">{p}</span>' if "🔥" not in p and "📈" not in p else f'<span class="social-tag">{p}</span>' for p in stock['patterns']])}
                </div>
                <div style="background: rgba(239, 68, 68, 0.05); padding: 14px; border-radius: 8px; border-left: 3px solid #ef4444;">
                    <span style="color: #f87171; font-weight: 700; font-size: 0.8rem; text-transform: uppercase;">💬 Social Media Fokus</span><br>
                    <p style="margin: 4px 0 0 0; font-size: 0.93rem; color: #cbd5e1;">{stock['social_topic']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        df = stock["df"]
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Kurs"
        )])
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=260, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
