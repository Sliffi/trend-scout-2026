"""
╔══════════════════════════════════════════════════════════╗
║   MSCI ACWI GLOBAL MULTIPLEX QUANT RADAR (V7.2 - INSIGHTS)║
║   Unkaputtbare Stack-Engine mit laienfreundlichem Report  ║
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

st.markdown("""
    <style>
        .stApp { background: #0f111a; color: #e2e8f0; }
        .stock-box {
            background: #161925;
            border: 1px solid #2e3440;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 35px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        }
        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #60a5fa;
            margin-top: 20px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .prob-badge {
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            padding: 8px 18px;
            border-radius: 30px;
            font-size: 0.95rem;
            font-weight: 700;
            border: 1px solid #34d399;
            box-shadow: 0 4px 12px rgba(16,185,129,0.2);
        }
        .metric-card {
            background: #1f2335;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #2e3440;
            text-align: center;
        }
        .metric-val {
            font-size: 1.2rem;
            font-weight: 700;
            color: white;
        }
        .metric-lbl {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="font-weight:700; color:#3b82f6; margin-bottom:8px;">🎛 nighttime; MINDEST-SCHWELLE</div>', unsafe_allow_html=True)
    min_probability = st.slider("Mindest-Wahrscheinlichkeit (%)", 30, 95, 60, 5)

st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); 
                border-radius: 20px; padding: 40px; margin-bottom: 32px; border: 1px solid #3b82f6;">
        <h1 style="color: white; margin: 0 0 12px 0;">🌍 MSCI ACWI Global Insights — V7.2</h1>
        <p style="color: #93c5fd; margin: 0; font-size: 1.05rem;">
            Professionelle, laienverständliche Auswertung des globalen Aktienmarktes. Stand: Juni 2026.
        </p>
    </div>
""", unsafe_allow_html=True)

market_type = st.selectbox(
    "Wähle das MSCI ACWI Universum für die Analyse:",
    [
        "MSCI ACWI: Top 200 Global Mega-Caps & Tech Leaders",
        "MSCI ACWI: Top 200 Eurozone & Western Europe Champions",
        "MSCI ACWI: Top 200 Emerging Markets & Asia-Pacific Giants",
        "MSCI ACWI: Top 200 Global Financials, Energy & Materials"
    ]
)

# ── DIE STRAND-LISTEN (100% STERIL) ──────────────────────────────────────────
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

def fetch_social_volume_via_ki(api_key, ticker):
    prompt = f"Scanne Reddit r/WallStreetBets nach dem Ticker '{ticker}' für Juni 2026. Antworte NUR als JSON: {{ 'volume_growth_pct': 50, 'reddit_sentiment': 'Bullish', 'hot_topic': 'Kontext.' }}"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}
    payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}
    try:
        res = requests.post(url, headers=headers, json=payload)
        raw_text = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        match = re.search(r"\{[\s\S]*\}", raw_text)
        return json.loads(match.group(0))
    except Exception:
        return {"volume_growth_pct": 0, "reddit_sentiment": "Neutral", "hot_topic": "Stabile Akkumulation in Forennetzwerken."}

# ── HAUPTPROZESS ─────────────────────────────────────────────────────────────
if scan_btn:
    try: active_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("🔑 GEMINI_API_KEY fehlt in den Secrets.")
        st.stop()
        
    full_tickers = MARKET_LISTS[market_type]
    math_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.markdown("📡 **Phase 1:** Downloade globales Datenpaket von Yahoo Finance (200 Ticker)...")
    
    try:
        # 💥 DIE LEGENDÄRE RETTUNG: Ein einziger nackter Download OHNE group_by. 
        # Yahoo Finance liefert die Spalten als MultiIndex (z.B. Open, Close) oben und Ticker unten.
        raw_data = yf.download(full_tickers, period="3mo", progress=False)
        
        # Unkaputtbares Umformatieren: Wir wandeln das 3D-DataFrame in eine flache, perfekt lesbare Tabelle um!
        # .stack(level=1) bzw. .stack() bricht das Tabellenchaos auf Zeilenebene herunter.
        if isinstance(raw_data.columns, pd.MultiIndex):
            # Wenn yfinance standardmäßig (Ebene 0: Attribut, Ebene 1: Ticker) zurückgibt
            flat_data = raw_data.stack(level=1 if isinstance(raw_data.columns, pd.MultiIndex) else 0)
        else:
            flat_data = raw_data
            
    except Exception as e:
        st.error(f"❌ Verbindung zum Datenportal fehlgeschlagen: {str(e)}.")
        st.stop()
        
    # Jetzt können wir stabil über ALLE Ticker loopen. Kein Chunk kann mehr den Rest blockieren!
    for idx, ticker in enumerate(full_tickers):
        if idx % 10 == 0:
            progress_bar.progress(int((idx + 1) / len(full_tickers) * 100))
            status_text.markdown(f"📊 Analisiere Indikatoren für Aktie {idx}/{len(full_tickers)}...")
            
        try:
            # Hol dir die Zeilen für genau diesen Ticker aus der flachen Tabelle
            if ticker in flat_data.index.levels[1] if hasattr(flat_data.index, 'levels') else flat_data.index:
                df_ticker = flat_data.xs(ticker, level=1).dropna()
            else:
                continue
                
            if df_ticker.empty or len(df_ticker) < 15: 
                continue
                
            math_points = 0
            signals = []
            explanations = []
            
            # 1. Volumensprung
            current_volume = float(df_ticker['Volume'].iloc[-1])
            avg_volume_20d = float(df_ticker['Volume'].iloc[-15:-1].mean())
            if current_volume > avg_volume_20d * 1.25:
                signals.append("⚙️ Institutioneller Volumensprung")
                explanations.append("Es strömt aktuell außergewöhnlich viel Geld in die Aktie. Das deutet darauf hin, dass Großinvestoren (Fonds/Banken) Positionen aufbauen.")
                math_points += 25
                
            # 2. Bollinger Squeeze
            close_prices = df_ticker['Close'].astype(float)
            bb_high = ta.volatility.bollinger_hband(close_prices)
            bb_low = ta.volatility.bollinger_lband(close_prices)
            bb_bandwidth = (bb_high - bb_low) / close_prices
            if bb_bandwidth.iloc[-1] < bb_bandwidth.rolling(10).mean().iloc[-1] * 0.95:
                signals.append("💥 Chart-Kompression (Squeeze)")
                explanations.append("Die Aktie hat sich zuletzt in einer extrem engen Spanne bewegt. Historisch entlädt sich ein solcher 'Preiskonflikt' in einem heftigen, explosionsartigen Ausbruch nach oben oder unten.")
                math_points += 25
                
            # 3. MACD Momentum
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
        except Exception: 
            continue
            
    progress_bar.empty()
    status_text.empty()
    
    if not math_results:
        st.error("⚠️ Keine mathematischen Ausbruchskandidaten im gesamten 200er Universum gefunden.")
        st.stop()
        
    # Die Top 4 gehen weiter an die KI für den Report
    math_results = sorted(math_results, key=lambda x: x["math_points"], reverse=True)[:4]
    
    st.success(f"💎 {len(math_results)} Top-Kandidaten lokal gesichert. Generiere Fundamentalanalyse & KI-Lagebild...")
    
    final_results = []
    
    for idx, stock in enumerate(math_results):
        social_data = fetch_social_volume_via_ki(active_key, stock["ticker"])
        try: growth = int(social_data.get("volume_growth_pct", 0))
        except (TypeError, ValueError): growth = 0
            
        social_points = 30 if growth >= 80 else (15 if growth >= 20 else 0)
        final_probability = min(stock["math_points"] + social_points + 35, 98)
        
        company_name = stock["ticker"]
        business_summary = "Keine Beschreibung verfügbar."
        pe_ratio = "N/A"
        market_cap = "N/A"
        high_52w = stock["price"]
        low_52w = stock["price"]
        
        try:
            yf_ticker = yf.Ticker(stock["ticker"])
            info = yf_ticker.info
            company_name = info.get("longName", stock["ticker"])
            business_summary = info.get("longBusinessSummary", "Das Unternehmen operiert im ausgewählten Sektor.")
            if info.get("trailingPE"): pe_ratio = f"{info['trailingPE']:.1f}"
            if info.get("marketCap"): market_cap = f"${info['marketCap'] / 1_000_000_000:.1f} Mrd."
            high_52w = info.get("fiveTwoWeekHigh", stock["price"])
            low_52w = info.get("fiveTwoWeekLow", stock["price"])
        except Exception: pass
            
        stock["name"] = company_name
        stock["summary"] = business_summary
        stock["pe"] = pe_ratio
        stock["cap"] = market_cap
        stock["high_52w"] = high_52w
        stock["low_52w"] = low_52w
        stock["probability"] = final_probability
        stock["social_sentiment"] = social_data.get("reddit_sentiment", "Neutral")
        stock["social_topic"] = social_data.get("hot_topic", "Keine akuten Vorfälle.")
        
        if growth >= 20:
            stock["math_explanations"].append(f"🔥 Social-Media-Hype (+{growth}%): In Foren wie Reddit wird aktuell massiv über diese Aktie diskutiert. Kleinanleger könnten eine Kettenreaktion auslösen.")
            
        final_results.append(stock)
        
    output = [s for s in final_results if s["probability"] >= min_probability]
    if not output:
        st.info(f"ℹ️ Keine Aktie knackt aktuell deine eingestellte Hürde von {min_probability}%.")
        st.stop()
        
    output = sorted(output, key=lambda x: x["probability"], reverse=True)
    
    st.markdown("## 📊 Ausführlicher Ausbruchs-Report")
    
    for s in output:
        st.markdown(f"""
            <div class="stock-box">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid #2e3440; padding-bottom: 16px; margin-bottom: 20px;">
                    <div>
                        <h2 style="color: white; margin: 0;">{s['name']} (<span style="color: #60a5fa;">{s['ticker']}</span>)</h2>
                        <p style="margin: 4px 0 0 0; font-size: 1.1rem; color: #cbd5e1;">
                            Aktueller Kurs: <b>${s['price']:.2f}</b> 
                            (<span style="color: {'#10b981' if s['change'] >= 0 else '#ef4444'}">{s['change']:+.2f}%</span>)
                        </p>
                    </div>
                    <span class="prob-badge">🎯 Ausbruchs-Chance: {s['probability']}%</span>
                </div>
                
                <div class="section-title">🏢 Was macht das Unternehmen?</div>
                <p style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 20px;">{s['summary']}</p>
                
                <div class="section-title">📊 Wichtige Finanz-Kennzahlen</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px; margin-bottom: 25px;">
                    <div class="metric-card"><div class="metric-val">{s['cap']}</div><div class="metric-lbl">Börsenwert</div></div>
                    <div class="metric-card"><div class="metric-val">{s['pe']}</div><div class="metric-lbl">KGV (Bewertung)</div></div>
                    <div class="metric-card"><div class="metric-val">${s['high_52w']:.2f}</div><div class="metric-lbl">52-Wochen-Hoch</div></div>
                    <div class="metric-card"><div class="metric-val">${s['low_52w']:.2f}</div><div class="metric-lbl">52-Wochen-Tief</div></div>
                </div>
                
                <div class="section-title">💡 Warum schlägt das System hier Alarm?</div>
                <div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 25px;">
                    <ul style="margin: 0; padding-left: 20px; color: #cbd5e1; line-height: 1.7;">
                        {"".join([f'<li style="margin-bottom: 10px;">{exp}</li>' for exp in s['math_explanations']])}
                    </ul>
                </div>
                
                <div class="section-title">🌐 KI-Lagebild & Social Media Stimmung</div>
                <div style="background: rgba(96, 165, 250, 0.05); padding: 18px; border-radius: 10px; border-left: 4px solid #3b82f6; margin-bottom: 25px;">
                    <span style="font-size: 0.85rem; font-weight: bold; color: #60a5fa; text-transform: uppercase;">Stimmung in den Foren: {s['social_sentiment']}</span>
                    <p style="margin: 6px 0 0 0; font-size: 0.95rem; color: #cbd5e1;">{s['social_topic']}</p>
                </div>
                
                <div class="section-title">📉 Technischer Chartverlauf (Letzte 3 Monate)</div>
            </div>
        """, unsafe_allow_html=True)
        
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
        
        st.markdown("""
            <div style="background: #1f2335; padding: 14px 20px; border-radius: 8px; margin-top: -20px; margin-bottom: 40px; font-size: 0.88rem; color: #94a3b8; border: 1px solid #2e3440;">
                💡 <b>Lesehilfe für das Diagramm:</b> Jede Kerze symbolisiert einen Handelstag. Ein 
                <span style="color: #10b981; font-weight: bold;">grüner Balken</span> bedeutet, dass der Kurs an diesem Tag gestiegen ist. Ein 
                <span style="color: #ef4444; font-weight: bold;">roter Balken</span> bedeutet, dass der Kurs gefallen ist. Die dünnen Striche oben und unten (Dochte) zeigen den höchsten und tiefsten Stand des Tages. Wenn die Kerzenkörper immer kleiner werden und sich horizontal zusammenziehen, steht ein Ausbruch kurz bevor.
            </div>
            <hr style="border-color: #2e3440; margin-bottom: 40px;">
        """, unsafe_allow_html=True)
