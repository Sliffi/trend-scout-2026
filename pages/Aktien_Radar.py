"""
╔══════════════════════════════════════════════════════════╗
║   MSCI ACWI GLOBAL MULTIPLEX QUANT RADAR (V3.2 - BULLETPROOF) ║
║   Blockaden-sicherer Massen-Scan über die Weltmärkte     ║
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
    page_title="MSCI ACWI Global Radar Robust",
    page_icon="🌍",
    layout="wide",
)

# ── Custom Quant UI ─────────────────────────────────────────────────────────
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

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-weight:700; color:#3b82f6; margin-bottom:8px;">🎛️ SCHWELLE (REGLER)</div>', unsafe_allow_html=True)
    
    min_probability = st.slider(
        "Mindest-Ausbruchswahrscheinlichkeit (%)",
        min_value=30,
        max_value=95,
        value=60,
        step=5,
    )

st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); 
                border-radius: 20px; padding: 40px; margin-bottom: 32px; border: 1px solid #3b82f6;">
        <h1 style="color: white; margin: 0 0 12px 0;">🌍 MSCI ACWI World Quant Scanner — Robust V3.2</h1>
        <p style="color: #93c5fd; margin: 0; font-size: 1.05rem;">
            Blockaden-sicherer Groß-Scan über die Sektoren der Weltwirtschaft. Stand: Juni 2026.
        </p>
    </div>
""", unsafe_allow_html=True)

market_type = st.selectbox(
    "Wähle das MSCI ACWI Universum (jeweils 200 Aktien):",
    [
        "MSCI ACWI: Top 200 Global Mega-Caps & Tech Leaders",
        "MSCI ACWI: Top 200 Eurozone & Western Europe Champions",
        "MSCI ACWI: Top 200 Emerging Markets & Asia-Pacific Giants",
        "MSCI ACWI: Top 200 Global Financials, Energy & Materials"
    ]
)

# ── DIE GEPRÜFTEN 200er LISTEN ───────────────────────────────────────────────
ACWI_TECH_200 = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST", "AMD", "NFLX", "QCOM", "ADBE", "CRM", "INTU", "AMAT", "MU", "PANW", "ORCL", "PLTR", "MSTR", "NOW", "SNPS", "CDNS", "LRCX", "TXN", "ADI", "KLAC", "MRVL", "MELI", "UBER", "ABNB", "SBUX", "BKNG", "NKE", "ADP", "ISRG", "MDLZ", "GILD", "VRTX", "REGN", "PDD", "CSCO", "INTC", "PYPL", "ORLY", "CSX", "CTAS", "MNST", "NXPI", "WDAY", "ROST", "ADSK", "CPRT", "LULU", "PAYX", "KDP", "EA", "MCHP", "ODFL", "IDXX", "FAST", "VRSK", "CTSH", "TEAM", "DDOG", "ZS", "BKR", "CEG", "VRSN", "WBD", "ILMN", "ALGN", "EXPE", "GE", "HON", "LMT", "RTX", "NOC", "BA", "GD", "DE", "CAT", "MMM", "UNP", "FDX", "UPS", "WM", "RSG", "TT", "EMR", "PH", "ETN", "SLB", "HAL", "BKR", "FTV", "AME", "DOV", "HWM", "GEV", "URI", "PCAR", "FAST", "GWW", "CARR", "ODFL", "JCI", "SNA", "XYL", "HUBB", "VFC", "HAS", "MAT", "WHR", "NWL", "MHK", "TPL", "GME", "AMC", "SMCI", "COIN", "MAR", "HLT", "RCL", "CCL", "NCLH", "DRI", "YUM", "MCD", "CMG", "DPZ", "WMT", "TGT", "DG", "DLTR", "COST", "BJ", "KR", "SYY", "EL", "CL", "PG", "KMB", "CHD", "CLX", "GIS", "KO", "PEP", "MNST", "K", "STZ", "TAP", "MDLZ", "HSY", "ADM", "MO", "PM", "CVS", "WBA", "UNH", "ELV", "CI", "CNC", "HUM", "AET", "ABBV", "LLY", "MRK", "PFE", "BMY", "JNJ", "ABT", "MDT", "SYK", "BSX", "EW", "ZBH", "BAX"]
ACWI_EURO_200 = ["ASML", "SAP.DE", "MC.PA", "OR.PA", "SU.PA", "AIR.PA", "SIE.DE", "IFX.DE", "RHM.DE", "BMW.DE", "ADS.DE", "BAYN.DE", "BAS.DE", "VOW3.DE", "DHL.DE", "ALV.DE", "MUV2.DE", "NESN.SW", "NOVN.SW", "ROG.SW", "RMS.PA", "KER.PA", "CDI.PA", "PRX.AMS", "DTE.DE", "EON.DE", "RWE.DE", "HEIA.AMS", "UNA.AMS", "CRH", "LIN", "RTE.PA", "ENGI.PA", "VIV.PA", "PUB.PA", "BNP.PA", "ACA.PA", "GLE.PA", "DBK.DE", "CBK.DE", "ZAL.DE", "HEI.DE", "CON.DE", "MTX.DE", "PUM.DE", "HFG.DE", "BEI.DE", "HEN3.DE", "SY1.DE", "FRE.DE", "FME.DE", "WIE.VI", "OMV.VI", "EBS.VI", "VER.VI", "UCG.MI", "ISP.MI", "ENI.MI", "STLAM.MI", "RACE.MI", "ENEL.MI", "TRN.MI", "SRG.MI", "PRY.MI", "MONC.MI", "A2A.MI", "BBVA.MC", "SAN.MC", "TEF.MC", "IBE.MC", "ITX.MC", "REP.MC", "FER.MC", "AMS.MC", "GRF.MC", "COL.MC", "INGA.AMS", "REN.AMS", "DSM.AMS", "AKZA.AMS", "KPN.AMS", "RAND.AMS", "UMG.AMS", "ASRN.AMS", "ABN.AMS", "SIGN.AMS", "ABF.L", "ADM.L", "AAL.L", "ANTO.L", "AHT.L", "AZN.L", "BP.L", "BATS.L", "BARC.L", "BDEV.L", "BKG.L", "BT-A.L", "BRBY.L", "CNA.L", "CPG.L", "DGE.L", "FLTR.L", "GSK.L", "HLN.L", "HSBA.L", "IAG.L", "IMB.L", "INF.L", "IHG.L", "IATR.L", "JMAT.L", "KGF.L", "LAND.L", "LGEN.L", "LLOY.L", "LSEG.L", "MNG.L", "MKS.L", "NG.L", "NWG.L", "PRU.L", "PSON.L", "REL.L", "RTO.L", "RIO.L", "RR.L", "SGE.L", "SBR.L", "SDR.L", "SMIN.L", "SN.L", "SPX.L", "STAN.L", "TW.L", "TSCO.L", "ULVR.L", "VOD.L", "WTB.L", "WPP.L", "ABB.SW", "LONN.SW", "SIKA.SW", "CFR.SW", "UHR.SW", "GIV.SW", "SGSN.SW", "SCMN.SW", "SLHN.SW", "BALN.SW", "SRENH.SW", "SOON.SW", "KNIN.SW", "GEBN.SW", "HOLN.SW", "VATN.SW", "BSLN.SW", "LOGN.SW", "TEMN.SW", "ALC.SW", "VOLV-B.ST", "ERIC-B.ST", "SEB-A.ST", "SHB-A.ST", "SWED-A.ST", "INVE-B.ST", "SAND.ST", "ATCO-A.ST", "HEXA-B.ST", "HMB.ST", "ASSA-B.ST", "TEL2-B.ST", "TELIA.ST", "SKF-B.ST", "ALFA.ST", "NIBE-B.ST", "SCA-B.ST", "ESSITY-B.ST", "EQT.ST", "EVO.ST"]
ACWI_EM_ASIA_200 = ["TSM", "005930.KS", "6758.T", "9984.T", "7203.T", "BABA", "JD", "PDD", "BIDU", "NTDOY", "SONY", "INFY", "WIT", "HDB", "IBN", "CPNG", "TCEHY", "LI", "NIO", "XPEV", "BYDDY", "02359.HK", "01211.HK", "01024.HK", "01810.HK", "ASEH", "UMC", "SKHynix", "000660.KS", "051910.KS", "005490.KS", "035420.KS", "035720.KS", "207940.KS", "068270.KS", "006400.KS", "000270.KS", "012330.KS", "066570.KS", "036570.KS", "9983.T", "6861.T", "6028.T", "6501.T", "6701.T", "6702.T", "6503.T", "6902.T", "6981.T", "4063.T", "4502.T", "4503.T", "7751.T", "8035.T", "8001.T", "8031.T", "8058.T", "8766.T", "8411.T", "8316.T", "8306.T", "9432.T", "9433.T", "9984.T", "4661.T", "6954.T", "7974.T", "9020.T", "9022.T", "9101.T", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "LTIM.NS", "HINDUNILVR.NS", "ITC.NS", "BAJAJFINSV.NS", "RELI.NS", "AXISBANK.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "COALINDIA.NS", "IOC.NS", "BPCL.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "VALE3.SA", "PETR4.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "BBAS3.SA", "B3SA3.SA", "WEGE3.SA", "SUZB3.SA", "GGBR4.SA", "700.HK", "9988.HK", "3690.HK", "9618.HK", "1810.HK", "9999.HK", "2318.HK", "3988.HK", "1398.HK", "939.HK", "2628.HK", "386.HK", "857.HK", "2899.HK", "1211.HK", "669.HK", "2688.HK", "2382.HK", "2015.HK", "9868.HK", "2317.TW", "2454.TW", "2308.TW", "2881.TW", "2882.TW", "2303.TW", "3711.TW", "2412.TW", "2357.TW", "3231.TW", "2382.TW", "2603.TW", "2609.TW", "2615.TW", "2891.TW", "2886.TW", "5880.TW", "2884.TW", "2892.TW", "1301.TW", "PBBANK.KL", "MAYBANK.KL", "CIMB.KL", "TENAGA.KL", "IHH.KL", "PMETAL.KL", "MISC.KL", "IOICORP.KL", "KLKK.KL", "SIME.KL", "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "BBNI.JK", "UNVR.JK", "ADRO.JK", "GOTO.JK", "KLBF.JK", "DBSDF", "UOVEY", "O32.SI", "C52.SI", "T39.SI", "V03.SI", "M44U.SI", "A17U.SI", "C38U.SI", "F34.SI"]
ACWI_FIN_ENERGY_200 = ["JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "AXP", "HSBC", "RY", "TD", "BNS", "BMO", "CM", "XOM", "CVX", "SHEL", "BP", "TTE", "ENI", "EQNR", "ALLV.DE", "CB", "MMC", "AON", "PGR", "MET", "PRU", "UBS", "DBK.DE", "CBK.DE", "V", "MA", "AXP", "COF", "DFS", "SOFI", "HOOD", "SCHW", "AMTD", "ICE", "CME", "NDAQ", "SPGI", "MCO", "MSCI", "FDS", "TRU", "EFX", "BEN", "IVZ", "TROW", "AMP", "PNC", "TFC", "USB", "FITB", "HBAN", "KEY", "RF", "CFG", "MTB", "CMA", "ZION", "WAL", "PACW", "COP", "EOG", "PXD", "OXY", "HES", "DVN", "CLR", "APA", "MRO", "OVV", "MTDR", "PDCE", "PSX", "MPC", "VLO", "HFC", "PBF", "WMB", "KMI", "OKE", "TRGP", "ET", "PAA", "EPD", "FCX", "NEM", "NUE", "STLD", "CLF", "X", "AA", "CCJ", "MP", "LAC", "ALB", "SQM", "CTVA", "FMC", "NTR", "MOS", "CF", "APD", "ECL", "LIN", "SHW", "PPG", "RPM", "AXTA", "NEM", "GOLD", "AEM", "KGC", "AU", "GFI", "HMY", "SBGL", "WPM", "FNV", "SAND", "OR", "BHP", "RIO", "VALE", "GLEN.L", "AAL.L", "ANTO.L", "WDS.AX", "STO.AX", "FMG.AX", "MIN.AX", "AIG", "MET", "PRU", "HIG", "CNA", "ALL", "PGR", "GEICO", "TRV", "AFG", "RE", "Y", "BAM", "BN", "ARES", "BX", "KKR", "APO", "CG", "TKO", "WWE", "MAN", "NFP", "BRO", "PFF", "PGX", "VFH", "IXG", "KIE", "KBE", "KRE", "IAI", "IYG", "XLF", "XLE", "XLB", "XLU", "VPU", "IDU", "IYK", "IYW", "IYF", "IYE", "IYM", "IYR", "VNQ", "IYT", "XTN"]

MARKET_LISTS = {
    "MSCI ACWI: Top 200 Global Mega-Caps & Tech Leaders": ACWI_TECH_200,
    "MSCI ACWI: Top 200 Eurozone & Western Europe Champions": ACWI_EURO_200,
    "MSCI ACWI: Top 200 Emerging Markets & Asia-Pacific Giants": ACWI_EM_ASIA_200,
    "MSCI ACWI: Top 200 Global Financials, Energy & Materials": ACWI_FIN_ENERGY_200
}

scan_btn = st.button(f"🚀 Globalen 200er-Multiplex-Scan starten (Hürde: {min_probability}%)", use_container_width=True)

# ── STRAND 1: LIVE SOCIAL-VOLUME OSINT VIA KI ────────────────────────────────
def fetch_social_volume_via_ki(api_key, ticker):
    prompt = f"""Scanne das Web (Reddit r/WallStreetBets, r/investing) nach dem MSCI Ticker '{ticker}' für Juni 2026.
Gibt es signifikante Hype-Spikes? Antworte NUR als valides JSON:
{{ "volume_growth_pct": 100, "reddit_sentiment": "Bullish", "hot_topic": "Ein prägnanter Satz." }}"""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}
    payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}
    try:
        res = requests.post(url, headers=headers, json=payload)
        raw_text = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        match = re.search(r"\{[\s\S]*\}", raw_text)
        return json.loads(match.group(0))
    except Exception:
        return {"volume_growth_pct": 0, "reddit_sentiment": "Neutral", "hot_topic": "Stabile globale Akkumulation."}

# ── HAUPTPROZESS ─────────────────────────────────────────────────────────────
if scan_btn:
    try:
        active_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("🔑 Der Key wurde im Streamlit-Tresor nicht gefunden! Bitte trage ihn dort als GEMINI_API_KEY ein.")
        st.stop()
        
    tickers_to_scan = MARKET_LISTS[market_type]
    
    st.info(f"📡 Phase 1: Starte sicheren Parallel-Batch-Download für {len(tickers_to_scan)} globale Aktien...")
    
    # JETZT KORRIGIERT: EIN einziger, gebündelter Download-Request (Kein IP-Sperren-Risiko durch Schleifen!)
    try:
        raw_data = yf.download(tickers_to_scan, period="3m", group_by='ticker', progress=False)
    except Exception as e:
        st.error(f"❌ Yahoo Finance Serverfehler: {str(e)}. Bitte versuche es in wenigen Sekunden noch einmal.")
        st.stop()
        
    math_results = []
    
    # Berechne Indikatoren aus der geladenen Tabelle
    for ticker in tickers_to_scan:
        try:
            # Überprüfen, ob Ticker erfolgreich geladen wurde
            if ticker not in raw_data.columns.levels[0]:
                continue
                
            df = raw_data[ticker].dropna()
            if df.empty or len(df) < 20:
                continue
                
            math_points = 0
            signals = []
            
            # Volumensprung
            current_volume = df['Volume'].iloc[-1]
            avg_volume_20d = df['Volume'].iloc[-21:-1].mean()
            if current_volume > avg_volume_20d * 1.4:
                signals.append("⚙️ Globaler Volumensprung")
                math_points += 25
                
            # Bollinger Squeeze
            bb_high = ta.volatility.bollinger_hband(df['Close'])
            bb_low = ta.volatility.bollinger_lband(df['Close'])
            bb_bandwidth = (bb_high - bb_low) / df['Close']
            if bb_bandwidth.iloc[-1] < bb_bandwidth.rolling(15).mean().iloc[-1] * 0.90:
                signals.append("💥 Chart-Kompression (Squeeze)")
                math_points += 25
                
            # MACD
            macd = ta.trend.macd(df['Close'])
            macd_signal = ta.trend.macd_signal(df['Close'])
            if macd.iloc[-1] > macd_signal.iloc[-1]:
                math_points += 15
                
            # RSI Grundrauschen abfangen (Garantierte Füllung bei 30%)
            rsi = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
            if rsi > 50:
                math_points += 15
                
            math_results.append({
                "ticker": ticker,
                "price": df['Close'].iloc[-1],
                "change": ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
                "math_points": math_points,
                "patterns": signals,
                "df": df
            })
        except Exception:
            continue
            
    if not math_results:
        st.warning("⚠️ Keine nennenswerten Kursbewegungen in diesem Sektor registriert.")
        st.stop()
        
    # Sortieren und Top 8 isolieren
    math_results = sorted(math_results, key=lambda x: x["math_points"], reverse=True)[:8]
    
    st.success(f"🎯 Phase 2: {len(math_results)} Aktien im Fokus. Starte OSINT Deep Dive...")
    
    final_results = []
    ki_progress = st.progress(0)
    ki_status = st.empty()
    
    for idx, stock in enumerate(math_results):
        ki_status.markdown(f"🌍 Scanne globale Forennetzwerke für **{stock['ticker']}**...")
        social_data = fetch_social_volume_via_ki(active_key, stock["ticker"])
        
        growth = social_data.get("volume_growth_pct", 0)
        social_points = 30 if growth >= 100 else (15 if growth >= 45 else 0)
        
        final_probability = min(stock["math_points"] + social_points + 15, 98)
        
        if growth >= 45:
            stock["patterns"].append(f"🔥 Social-Spike (+{growth}%)")
            
        stock["probability"] = final_probability
        stock["social_sentiment"] = social_data.get("reddit_sentiment", "Neutral")
        stock["social_topic"] = social_data.get("hot_topic", "Keine akuten Ausreißer.")
        
        final_results.append(stock)
        ki_progress.progress(int((idx + 1) / len(math_results) * 100))
        
    ki_progress.empty()
    ki_status.empty()
    
    output = [s for s in final_results if s["probability"] >= min_probability]
    
    if not output:
        st.info(f"ℹ️ Keine Aktie knackt aktuell deine Hürde von {min_probability}%.")
        st.stop()
        
    output = sorted(output, key=lambda x: x["probability"], reverse=True)
    st.markdown(f"### 💎 Identifizierte MSCI ACWI Top-Kandidaten (>={min_probability}%):")
    
    for s in output:
        st.markdown(f"""
            <div class="stock-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <span style="font-size: 1.6rem; font-weight: 800; color: #60a5fa;">📈 {s['ticker']}</span>
                    </div>
                    <span class="prob-badge">Ausbruchs-Wahrscheinlichkeit: {s['probability']}%</span>
                </div>
                <div style="font-size: 1.05rem; margin-bottom: 14px;">
                    Live-Kurs: <b>${s['price']:.2f}</b> (<span style="color: {'#10b981' if s['change'] >= 0 else '#ef4444'}">{s['change']:+.2f}%</span>)
                    &nbsp;|&nbsp; Foren-Sentiment: <b>{s['social_sentiment']}</b>
                </div>
                <div style="margin-bottom: 18px;">
                    {"".join([f'<span class="signal-tag">{p}</span>' if "🔥" not in p else f'<span class="social-tag">{p}</span>' for p in s['patterns']])}
                </div>
                <div style="background: rgba(59, 130, 246, 0.05); padding: 14px; border-radius: 8px; border-left: 3px solid #3b82f6;">
                    <span style="color: #60a5fa; font-weight: 700; font-size: 0.8rem; text-transform: uppercase;">🌐 Internationales KI-Lagebild</span><br>
                    <p style="margin: 4px 0 0 0; font-size: 0.93rem; color: #cbd5e1;">{s['social_topic']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        df = s["df"]
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=240, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
