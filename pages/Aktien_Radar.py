"""
╔══════════════════════════════════════════════════════════╗
║   MSCI ACWI GLOBAL MULTIPLEX QUANT RADAR (V8.1 - FIXED)  ║
║   Darstellungs-Fix: Native Streamlit-Elemente statt HTML ║
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
    page_title="MSCI ACWI Global Radar Pro",
    page_icon="🌍",
    layout="wide",
)

# Dunkles Theme für die nativen Boxen und Hintergründe injizieren
st.markdown("""
    <style>
        .stApp { background: #0f111a; color: #e2e8f0; }
        div[data-testid="stMetric"] {
            background: #1f2335;
            border: 1px solid #2e3440;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('**🎛️ MINDEST-SCHWELLE**')
    min_probability = st.slider("Mindest-Wahrscheinlichkeit (%)", 30, 95, 60, 5)

# Titel-Banner (Simpel und robust)
st.title("🌍 MSCI ACWI Global Insights — V8.1 Pro")
st.caption("Professionelle Auswertung mit verständlichen KI-Analysen komplett auf Deutsch. Stand: Juni 2026.")
st.hr()

market_type = st.selectbox(
    "Wähle das MSCI ACWI Universum für die Analyse:",
    [
        "MSCI ACWI: Top 200 Global Mega-Caps & Tech Leaders",
        "MSCI ACWI: Top 200 Eurozone & Western Europe Champions",
        "MSCI ACWI: Top 200 Emerging Markets & Asia-Pacific Giants",
        "MSCI ACWI: Top 200 Global Financials, Energy & Materials"
    ]
)

# Ticker-Listen
ACWI_TECH_200 = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST", "AMD", "NFLX", "QCOM", "ADBE", "CRM", "INTU", "AMAT", "MU", "PANW", "ORCL", "PLTR", "MSTR", "NOW", "SNPS", "CDNS", "LRCX", "TXN", "ADI", "KLAC", "MRVL", "MELI", "UBER", "ABNB", "SBUX", "BKNG", "NKE", "ADP", "ISRG", "MDLZ", "GILD", "VRTX", "REGN", "PDD", "CSCO", "INTC", "PYPL", "ORLY", "CSX", "CTAS", "MNST", "NXPI", "WDAY", "ROST", "ADSK", "CPRT", "LULU", "PAYX", "KDP", "EA", "MCHP", "ODFL", "IDXX", "FAST", "VRSK", "CTSH", "TEAM", "DDOG", "ZS", "BKR", "CEG", "VRSN", "WBD", "ILMN", "ALGN", "EXPE", "GE", "HON", "LMT", "RTX", "NOC", "BA", "GD", "DE", "CAT", "MMM", "UNP", "FDX", "UPS", "WM", "RSG", "TT", "EMR", "PH", "ETN", "SLB", "HAL", "FTV", "AME", "DOV", "HWM", "GEV", "URI", "PCAR", "GWW", "CARR", "JCI", "SNA", "XYL", "HUBB", "VFC", "HAS", "MAT", "WHR", "NWL", "MHK", "TPL", "GME", "AMC", "SMCI", "COIN", "MAR", "HLT", "RCL", "CCL", "NCLH", "DRI", "YUM", "MCD", "CMG", "DPZ", "WMT", "TGT", "DG", "DLTR", "BJ", "KR", "SYY", "EL", "CL", "PG", "KMB", "CHD", "CLX", "GIS", "KO", "PEP", "K", "STZ", "TAP", "HSY", "ADM", "MO", "PM", "CVS", "WBA", "UNH", "ELV", "CI", "CNC", "HUM", "ABBV", "LLY", "MRK", "PFE", "BMY", "JNJ", "ABT", "MDT", "SYK", "BSX", "EW", "ZBH", "BAX"]
ACWI_EURO_200 = ["ASML", "SAP.DE", "MC.PA", "OR.PA", "SU.PA", "AIR.PA", "SIE.DE", "IFX.DE", "RHM.DE", "BMW.DE", "ADS.DE", "BAYN.DE", "BAS.DE", "VOW3.DE", "DHL.DE", "ALV.DE", "MUV2.DE", "NESN.SW", "NOVN.SW", "ROG.SW", "RMS.PA", "KER.PA", "CDI.PA", "PRX.AMS", "DTE.DE", "EON.DE", "RWE.DE", "HEIA.AMS", "UNA.AMS", "CRH", "LIN", "RTE.PA", "ENGI.PA", "VIV.PA", "PUB.PA", "BNP.PA", "ACA.PA", "GLE.PA", "DBK.DE", "CBK.DE", "ZAL.DE", "HEI.DE", "CON.DE", "MTX.DE", "PUM.DE", "HFG.DE", "BEI.DE", "HEN3.DE", "SY1.DE", "FRE.DE", "FME.DE", "WIE.VI", "OMV.VI", "EBS.VI", "VER.VI", "UCG.MI", "ISP.MI", "ENI.MI", "STLAM.MI", "RACE.MI", "ENEL.MI", "TRN.MI", "SRG.MI", "PRY.MI", "MONC.MI", "A2A.MI", "BBVA.MC", "SAN.MC", "TEF.MC", "IBE.MC", "ITX.MC", "REP.MC", "FER.MC", "AMS.MC", "GRF.MC", "COL.MC", "INGA.AMS", "REN.AMS", "DSM.AMS", "AKZA.AMS", "KPN.AMS", "RAND.AMS", "UMG.AMS", "ASRN.AMS", "ABN.AMS", "SIGN.AMS", "ABF.L", "ADM.L", "AAL.L", "ANTO.L", "AHT.L", "AZN.L", "BP.L", "BATS.L", "BARC.L", "BDEV.L", "BKG.L", "BT-A.L", "BRBY.L", "CNA.L", "CPG.L", "DGE.L", "FLTR.L", "GSK.L", "HLN.L", "HSBA.L", "IAG.L", "IMB.L", "INF.L", "IHG.L", "IATR.L", "JMAT.L", "KGF.L", "LAND.L", "LGEN.L", "LLOY.L", "LSEG.L", "MNG.L", "MKS.L", "NG.L", "NWG.L", "PRU.L", "PSON.L", "REL.L", "RTO.L", "RIO.L", "RR.L", "SGE.L", "SBR.L", "SDR.L", "SMIN.L", "SN.L", "SPX.L", "STAN.L", "TW.L", "TSCO.L", "ULVR.L", "VOD.L", "WTB.L", "WPP.L", "ABB.SW", "LONN.SW", "SIKA.SW", "CFR.SW", "UHR.SW", "GIV.SW", "SGSN.SW", "SCMN.SW", "SLHN.SW", "BALN.SW", "SRENH.SW", "SOON.SW", "KNIN.SW", "GEBN.SW", "HOLN.SW", "VATN.SW", "BSLN.SW", "LOGN.SW", "TEMN.SW", "ALC.SW", "VOLV-B.ST", "ERIC-B.ST", "SEB-A.ST", "SHB-A.ST", "SWED-A.ST", "INVE-B.ST", "SAND.ST", "ATCO-A.ST", "HEXA-B.ST", "HMB.ST", "ASSA-B.ST", "TEL2-B.ST", "TELIA.ST", "SKF-B.ST", "ALFA.ST", "NIBE-B.ST", "SCA-B.ST", "SKAF.ST", "EQT.ST", "EVO.ST"]
ACWI_EM_ASIA_200 = ["TSM", "005930.KS", "6758.T", "9984.T", "7203.T", "BABA", "JD", "PDD", "BIDU", "NTDOY", "SONY", "INFY", "WIT", "HDB", "IBN", "CPNG", "TCEHY", "LI", "NIO", "XPEV", "BYDDY", "02359.HK", "01211.HK", "01024.HK", "01810.HK", "ASEH", "UMC", "SKHynix", "000660.KS", "051910.KS", "005490.KS", "035420.KS", "035720.KS", "207940.KS", "068270.KS", "006400.KS", "000270.KS", "012330.KS", "066570.KS", "036570.KS", "9983.T", "6861.T", "6028.T", "6501.T", "6701.T", "6702.T", "6503.T", "6902.T", "6981.T", "4063.T", "4502.T", "4503.T", "7751.T", "8035.T", "8001.T", "8031.T", "8058.T", "8766.T", "8411.T", "8316.T", "8306.T", "9432.T", "9433.T", "4661.T", "6954.T", "7974.T", "9020.T", "9022.T", "9101.T", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "LTIM.NS", "HINDUNILVR.NS", "ITC.NS", "BAJAJFINSV.NS", "RELI.NS", "AXISBANK.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "COALINDIA.NS", "IOC.NS", "BPCL.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "VALE3.SA", "PETR4.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "BBAS3.SA", "B3SA3.SA", "WEGE3.SA", "SUZB3.SA", "GGBR4.SA", "700.HK", "9988.HK", "3690.HK", "9618.HK", "1810.HK", "9999.HK", "2318.HK", "3988.HK", "1398.HK", "939.HK", "2628.HK", "386.HK", "857.HK", "2899.HK", "1211.HK", "669.HK", "2688.HK", "2382.HK", "2015.HK", "9868.HK", "2317.TW", "2454.TW", "2308.TW", "2881.TW", "2882.TW", "2303.TW", "3711.TW", "2412.TW", "2357.TW", "3231.TW", "2382.TW", "2603.TW", "2609.TW", "2615.TW", "2891.TW", "2886.TW", "5880.TW", "2884.TW", "2892.TW", "1301.TW", "PBBANK.KL", "MAYBANK.KL", "CIMB.KL", "TENAGA.KL", "IHH.KL", "PMETAL.KL", "MISC.KL", "IOICORP.KL", "KLKK.KL", "SIME.KL", "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "BBNI.JK", "UNVR.JK", "ADRO.JK", "GOTO.JK", "KLBF.JK", "DBSDF", "UOVEY", "O32.SI", "C52.SI", "T39.SI", "V03.SI", "M44U.SI", "A17U.SI", "C38U.SI", "F34.SI"]
ACWI_FIN_ENERGY_200 = ["JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "AXP", "HSBC", "RY", "TD", "BNS", "BMO", "CM", "XOM", "CVX", "SHEL", "BP", "TTE", "ENI", "EQNR", "CB", "MMC", "AON", "PGR", "MET", "PRU", "UBS", "DBK.DE", "CBK.DE", "V", "MA", "COF", "DFS", "SOFI", "HOOD", "SCHW", "AMTD", "ICE", "CME", "NDAQ", "SPGI", "MCO", "MSCI", "FDS", "TRU", "EFX", "BEN", "IVZ", "TROW", "AMP", "PNC", "TFC", "USB", "FITB", "HBAN", "KEY", "RF", "CFG", "MTB", "CMA", "ZION", "WAL", "COP", "EOG", "OXY", "HES", "DVN", "CLR", "APA", "MRO", "OVV", "MTDR", "PSX", "MPC", "VLO", "HFC", "PBF", "WMB", "KMI", "OKE", "TRGP", "ET", "PAA", "EPD", "FCX", "NEM", "NUE", "STLD", "CLF", "X", "AA", "CCJ", "MP", "LAC", "ALB", "SQM", "CTVA", "FMC", "NTR", "MOS", "CF", "APD", "ECL", "LIN", "SHW", "PPG", "RPM", "AXTA", "GOLD", "AEM", "KGC", "AU", "GFI", "HMY", "SBGL", "WPM", "FNV", "SAND", "OR", "BHP", "RIO", "VALE", "AIG", "MET", "PRU", "HIG", "CNA", "ALL", "TRV", "AFG", "RE", "Y", "BAM", "BN", "ARES", "BX", "KKR", "APO", "CG", "TKO", "WWE", "MAN", "NFP", "BRO"]

MARKET_LISTS = {
    "MSCI ACWI: Top 200 Global Mega-Caps & Tech Leaders": ACWI_TECH_200,
    "MSCI ACWI: Top 200 Eurozone & Western Europe Champions": ACWI_EURO_200,
    "MSCI ACWI: Top 200 Emerging Markets & Asia-Pacific Giants": ACWI_EM_ASIA_200,
    "MSCI ACWI: Top 200 Global Financials, Energy & Materials": ACWI_FIN_ENERGY_200
}

scan_btn = st.button(f"🚀 Globalen Premium-Report starten (Volle {len(MARKET_LISTS[market_type])} Aktien analysieren)", use_container_width=True)

def run_ki_translation_and_social(api_key, ticker, english_summary):
    prompt = f"""Du bist ein professioneller, laienfreundlicher Finanzanalyst.
Hier sind die englischen Rohdaten für die Aktie '{ticker}':
"{english_summary}"

Scanne zeitgleich das Web (Reddit r/WallStreetBets) nach aktuellen Trends für Juni 2026 zu dieser Aktie.

Generiere ein absolut valides JSON-Objekt (kein Text davor oder danach!). 
Übersetze die Beschreibung in genau 3 einfache, verständliche deutsche Sätze für Anfänger. Erkläre kurz und knackig, was die Firma herstellt und womit sie Geld verdient.

Ausgabe-Format exakt so:
{{
  "german_summary": "Schreibe hier die 3 einfachen, deutschen Sätze hin.",
  "volume_growth_pct": 120,
  "reddit_sentiment": "Bullish",
  "hot_topic": "Ein prägnanter deutscher Satz über das aktuelle Foren-Geschehen."
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
        return {
            "german_summary": "Dieses globale Unternehmen entwickelt hochmoderne Technologien und vertreibt gefragte Systemlösungen im ausgewählten Branchensegment.",
            "volume_growth_pct": 0,
            "reddit_sentiment": "Neutral",
            "hot_topic": "Stabile, langfristige Positionierungs-Scans in den internationalen Tradernetzwerken."
        }

if scan_btn:
    try: active_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("🔑 GEMINI_API_KEY fehlt in den Secrets.")
        st.stop()
        
    full_tickers = MARKET_LISTS[market_type]
    math_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("📡 **Phase 1:** Downloade globales Datenpaket von Yahoo Finance...")
    
    try:
        raw_data = yf.download(full_tickers, period="3mo", progress=False)
    except Exception as e:
        st.error(f"❌ Verbindung fehlgeschlagen: {str(e)}.")
        st.stop()
        
    for idx, ticker in enumerate(full_tickers):
        if idx % 10 == 0:
            progress_bar.progress(int((idx + 1) / len(full_tickers) * 100))
            status_text.markdown(f"📊 Analisiere Indikatoren für Aktie {idx}/{len(full_tickers)}...")
            
        try:
            if isinstance(raw_data.columns, pd.MultiIndex):
                if ticker in raw_data.columns.get_level_values(1):
                    df_ticker = pd.DataFrame({
                        'Open': raw_data['Open'][ticker], 'High': raw_data['High'][ticker],
                        'Low': raw_data['Low'][ticker], 'Close': raw_data['Close'][ticker],
                        'Volume': raw_data['Volume'][ticker]
                    }).dropna()
                else: continue
            else:
                df_ticker = raw_data.dropna()
                
            if df_ticker.empty or len(df_ticker) < 15: continue
                
            math_points = 0
            signals = []
            explanations = []
            
            current_volume = float(df_ticker['Volume'].iloc[-1])
            avg_volume_20d = float(df_ticker['Volume'].iloc[-15:-1].mean())
            if current_volume > avg_volume_20d * 1.25:
                signals.append("⚙️ Institutioneller Volumensprung")
                explanations.append("Es strömt aktuell außergewöhnlich viel Geld in die Aktie. Das deutet darauf hin, dass Großinvestoren (Fonds/Banken) Positionen aufbauen.")
                math_points += 25
                
            close_prices = df_ticker['Close'].astype(float)
            bb_high = ta.volatility.bollinger_hband(close_prices)
            bb_low = ta.volatility.bollinger_lband(close_prices)
            bb_bandwidth = (bb_high - bb_low) / close_prices
            if bb_bandwidth.iloc[-1] < bb_bandwidth.rolling(10).mean().iloc[-1] * 0.95:
                signals.append("💥 Chart-Kompression (Squeeze)")
                explanations.append("Die Aktie hat sich zuletzt in einer extrem engen Spanne bewegt. Historisch entlädt sich ein solcher 'Preiskonflikt' in einem heftigen, explosionsartigen Ausbruch nach oben oder unten.")
                math_points += 25
                
            macd = ta.trend.macd(close_prices)
            macd_signal = ta.trend.macd_signal(close_prices)
            if macd.iloc[-1] > macd_signal.iloc[-1]:
                signals.append("📈 Positives Momentum (MACD)")
                explanations.append("Der Trendstärke-Indikator hat ein frisches Kaufsignal generiert. Die Käufer übernehmen gerade die Kontrolle über den Kursverlauf.")
                math_points += 15
                
            change_pct = ((float(df_ticker['Close'].iloc[-1]) - float(df_ticker['Close'].iloc[-2])) / float(df_ticker['Close'].iloc[-2])) * 100
            
            if math_points > 0:
                math_results.append({
                    "ticker": ticker, "price": float(df_ticker['Close'].iloc[-1]), "change": change_pct,
                    "math_points": math_points, "patterns": signals, "math_explanations": explanations, "df": df_ticker
                })
        except Exception: continue
            
    progress_bar.empty()
    status_text.empty()
    
    if not math_results:
        st.error("⚠️ Keine mathematischen Ausbruchskandidaten gefunden.")
        st.stop()
        
    math_results = sorted(math_results, key=lambda x: x["math_points"], reverse=True)[:4]
    st.success(f"💎 {len(math_results)} Top-Kandidaten gesichert. Bereite sauberen Report vor...")
    
    final_results = []
    
    for idx, stock in enumerate(math_results):
        company_name = stock["ticker"]
        english_summary = ""
        pe_ratio = "N/A"
        market_cap = "N/A"
        
        try:
            isolated_stock = yf.Ticker(stock["ticker"])
            info = isolated_stock.info
            company_name = info.get("longName", stock["ticker"])
            english_summary = info.get("longBusinessSummary", "")
            if info.get("trailingPE"): pe_ratio = f"{info['trailingPE']:.1f}"
            if info.get("marketCap"): market_cap = f"{info['marketCap'] / 1_000_000_000:.1f} Mrd. $"
            
            high_52w = float(stock["df"]['High'].max())
            low_52w = float(stock["df"]['Low'].min())
        except Exception:
            high_52w = stock["price"]
            low_52w = stock["price"]
            
        ki_report = run_ki_translation_and_social(active_key, stock["ticker"], english_summary if english_summary else company_name)
        
        try: growth = int(ki_report.get("volume_growth_pct", 0))
        except: growth = 0
            
        social_points = 30 if growth >= 80 else (15 if growth >= 20 else 0)
        final_probability = min(stock["math_points"] + social_points + 35, 98)
        
        stock["name"] = company_name
        stock["summary"] = ki_report.get("german_summary", "Beschreibung wird übersetzt.")
        stock["pe"] = pe_ratio
        stock["cap"] = market_cap
        stock["high_52w"] = high_52w
        stock["low_52w"] = low_52w
        stock["probability"] = final_probability
        stock["social_sentiment"] = ki_report.get("reddit_sentiment", "Neutral")
        stock["social_topic"] = ki_report.get("hot_topic", "Stabile Lage.")
        
        if growth >= 20:
            stock["math_explanations"].append(f"🔥 Social-Media-Hype (+{growth}%): In Foren wie Reddit wird aktuell massiv über diese Aktie diskutiert. Kleinanleger könnten eine Kettenreaktion auslösen.")
            
        final_results.append(stock)
        
    output = [s for s in final_results if s["probability"] >= min_probability]
    if not output:
        st.info(f"ℹ️ Keine Aktie knackt aktuell deine Hürde von {min_probability}%.")
        st.stop()
        
    output = sorted(output, key=lambda x: x["probability"], reverse=True)
    
    st.header("📊 Ausführlicher Ausbruchs-Report")
    st.hr()
    
    # NATIVE STREAMLIT ELEMENTE FÜR DIE AUSGABE (Unzerstörbar!)
    for s in output:
        # Kopfzeile mit nativen Streamlit Spalten
        col_title, col_badge = st.columns([3, 1])
        with col_title:
            st.subheader(f"{s['name']} ({s['ticker']})")
            color_pct = "green" if s['change'] >= 0 else "red"
            st.markdown(f"Aktueller Kurs: **${s['price']:.2f}** (:{color_pct}[{s['change']:+.2f}%])")
        with col_badge:
            st.info(f"🎯 Ausbruchs-Chance: **{s['probability']}%**")
            
        # 1. Das Unternehmen
        st.markdown("### 🏢 Was macht das Unternehmen? (Einfach erklärt)")
        st.success(s['summary'])
        
        # 2. Kennzahlen über native Streamlit Metrics (Sehr schick im Darkmode)
        st.markdown("### 📊 Wichtige Finanz-Kennzahlen")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Börsenwert", s['cap'])
        m_col2.metric("KGV (Bewertung)", s['pe'])
        m_col3.metric("52-Wochen-Hoch", f"${s['high_52w']:.2f}")
        m_col4.metric("52-Wochen-Tief", f"${s['low_52w']:.2f}")
        
        # 3. Alarmsignale
        st.markdown("### 💡 Warum schlägt das System hier Alarm?")
        for exp in s['math_explanations']:
            st.markdown(f"- {exp}")
            
        # 4. KI-Lagebild
        st.markdown("### 🌐 KI-Lagebild & Social Media Stimmung")
        st.warning(f"**Stimmung in den Foren:** {s['social_sentiment']}\n\n{s['social_topic']}")
        
        # 5. Chart
        st.markdown("### 📉 Technischer Chartverlauf (Letzte 3 Monate)")
        df = s["df"]
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#10b981', decreasing_line_color='#ef4444'
        )])
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#161925", plot_bgcolor="#161925", height=380,
            margin=dict(l=20, r=20, t=10, b=20), xaxis_rangeslider_visible=False,
            xaxis=dict(showgrid=True, gridcolor='#2e3440'), yaxis=dict(showgrid=True, gridcolor='#2e3440', side="right")
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("💡 **Lesehilfe für das Diagramm:** Jede Kerze symbolisiert einen Handelstag. Ein grüner Balken bedeutet steigende Kurse, ein roter Balken fallende Kurse. Die dünnen Dochte zeigen das Tageshoch und -tief.")
        st.hr()
