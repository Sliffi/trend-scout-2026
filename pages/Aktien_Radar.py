"""
╔═══════════════════════════════════════════════════════════════════╗
║   MSCI ACWI GLOBAL MULTIPLEX QUANT RADAR  (V9.0 – FULLY FIXED)  ║
║                                                                   ║
║  FIXES vs. V8.2:                                                  ║
║   ✅ 52-Wochen-Daten aus yf.Ticker().info (echte 52w-Werte)      ║
║   ✅ Volumen-Durchschnitt korrekt: echte 20 Handelstage           ║
║   ✅ RSI-Indikator ergänzt (45–70 = gesundes Momentum)           ║
║   ✅ MA50-Trendfilter (Preis > MA50 = Aufwärtstrend bestätigt)   ║
║   ✅ Near-52w-High-Bonus (Ausbruch aus Jahreshoch)               ║
║   ✅ "Signal-Score" statt irreführende "Wahrscheinlichkeit"       ║
║   ✅ Slider sinnvoll (0–100 Score-Bereich)                        ║
║   ✅ Max. KI-Analysen per Slider konfigurierbar (statt fix "4")  ║
║   ✅ Gemini API: korrekte googleSearch-Syntax                     ║
║   ✅ MACD: Crossover-Erkennung (nicht nur Positionsvergleich)     ║
║   ✅ MA50-Linie im Candlestick-Chart sichtbar                     ║
║   ✅ Tippfehler "Analisiere" → "Analysiere"                       ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import json
import re
import time
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import yfinance as yf
import ta

# ── Page-Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MSCI ACWI Global Radar Pro",
    page_icon="🌍",
    layout="wide",
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, .stApp { font-family: 'Inter', sans-serif; background: #0f111a; color: #e2e8f0; }

        div[data-testid="stMetric"] {
            background: #1a1e2e;
            border: 1px solid #2e3450;
            padding: 16px;
            border-radius: 12px;
            text-align: center;
        }
        div[data-testid="stMetric"] label { color: #8892b0 !important; font-size: 0.78rem !important; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 1.2rem !important; font-weight: 700; }

        .score-card {
            border-radius: 14px;
            padding: 18px 12px;
            text-align: center;
            font-family: 'Inter', sans-serif;
        }
        .signal-header {
            font-size: 0.85rem;
            color: #8892b0;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 4px;
        }
        /* ── Expander: dunkler Hintergrund, lesbare Schrift ─────────────── */
        /* Rahmen und Hintergrund des gesamten Expander-Blocks */
        div[data-testid="stExpander"] {
            background: #1a1e2e !important;
            border: 1px solid #2e3450 !important;
            border-radius: 10px !important;
        }
        /* Summary-Zeile (Titel des Expanders) */
        div[data-testid="stExpander"] summary {
            background: #1a1e2e !important;
            color: #e2e8f0 !important;
            border-radius: 10px !important;
        }
        div[data-testid="stExpander"] summary:hover {
            background: #232842 !important;
        }
        div[data-testid="stExpander"] summary span,
        div[data-testid="stExpander"] summary p {
            color: #e2e8f0 !important;
        }
        /* Inhaltsbereich des Expanders */
        div[data-testid="stExpander"] details > div,
        div[data-testid="stExpanderDetails"] {
            background: #1a1e2e !important;
            color: #c8d3e8 !important;
            border-top: 1px solid #2e3450 !important;
            padding: 12px 16px !important;
        }
        div[data-testid="stExpander"] details > div p,
        div[data-testid="stExpanderDetails"] p {
            color: #c8d3e8 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ── Passwortschutz ────────────────────────────────────────────────────────────
_APP_PASSWORD = "bvb"

if not st.session_state.get("authenticated", False):
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        st.markdown("""
        <div style="
            background: #1a1e2e;
            border: 1px solid #2e3450;
            border-radius: 18px;
            padding: 40px 36px 32px 36px;
            text-align: center;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        ">
            <div style="font-size: 3rem; margin-bottom: 10px;">🔐</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #e2e8f0; margin-bottom: 6px;">
                Zugang gesperrt
            </div>
            <div style="font-size: 0.9rem; color: #8892b0; margin-bottom: 24px;">
                Bitte Passwort eingeben, um den MSCI ACWI Radar zu öffnen.
            </div>
        </div>
        """, unsafe_allow_html=True)

        pw_input  = ""
        submitted = False
        with st.form("login_form"):
            pw_input  = st.text_input(
                "Passwort",
                type="password",
                placeholder="Passwort eingeben …",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button(
                "🔓 Einloggen",
                use_container_width=True,
                type="primary",
            )

        if submitted:
            if pw_input == _APP_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Falsches Passwort. Bitte erneut versuchen.")

    st.stop()  # Rest der App nicht rendern bis eingeloggt

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ Scan-Einstellungen")
    min_score = st.slider("Mindest-Signal-Score", 0, 100, 70, 5,
                          help="Aktien unterhalb dieser Grenze werden nicht angezeigt.")
    max_ki = st.slider("Maximale KI-Analysen (Top-N)", 2, 12, 5, 1,
                       help="Wie viele Top-Kandidaten sollen per Gemini-KI analysiert werden?")
    st.divider()
    st.markdown("**📖 Score-Legende:**")
    st.markdown("""
| Score | Bewertung |
|-------|-----------|
| 🟢 80–100 | Starkes Signal |
| 🟡 60–79 | Moderates Signal |
| 🟠 40–59 | Schwaches Signal |
| 🔴 0–39 | Kein klares Signal |
    """)
    st.divider()
    st.markdown("**⚡ Signal-Kriterien:**")
    st.markdown("""
- **+20 Pkt** Volumensprung (1.5× Ø20d)
- **+20 Pkt** Bollinger Squeeze
- **+15 Pkt** MACD-Crossover bullish
- **+15 Pkt** RSI in gesunder Zone (45–70)
- **+15 Pkt** Preis > MA50 (Aufwärtstrend)
- **+15 Pkt** Nahe 52-Wochen-Hoch (<5%)
- **+10 Pkt** KI: Bullishes Sentiment
- **−5 Pkt**  RSI überkauft (>70)
    """)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🌍 MSCI ACWI Global Insights — V9.0 Pro")
st.caption("Professionelle Ausbruchs-Analyse mit 6 technischen Signalen + KI-Erklärungen auf Deutsch. Stand: Juni 2026.")
st.divider()

# ── _yf_search: muss VOR den Tabs definiert sein, da tab_single sie aufruft ──
def _yf_search(query: str) -> list:
    """
    Ruft die kostenlose Yahoo Finance Autocomplete-API auf.
    Gibt eine Liste von dicts mit symbol, shortname, longname, exchange zurück.
    Filtert auf handelbare Aktien (EQUITY) und ETFs.
    """
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {"q": query, "quotesCount": 10, "newsCount": 0, "enableFuzzyQuery": "true"}
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, params=params, headers=headers, timeout=8)
        res.raise_for_status()
        quotes = res.json().get("quotes", [])
        allowed_types = {"EQUITY", "ETF", "MUTUALFUND"}
        return [
            q for q in quotes
            if q.get("quoteType", "") in allowed_types
            and q.get("symbol") and q.get("shortname")
        ]
    except Exception:
        return []



def _analyse_single_ticker(ticker: str, api_key: str) -> list:
    """
    Führt die komplette Analyse-Pipeline für einen einzelnen Ticker durch.
    compute_signals/run_ki_analysis sind zur Aufrufzeit bereits definiert.
    """
    with st.spinner(f"📡 Lade Kursdaten für {ticker} (6 Monate) …"):
        try:
            raw = yf.download(ticker, period="6mo", progress=False, auto_adjust=True)
            if isinstance(raw.columns, pd.MultiIndex):
                df_ticker = pd.DataFrame({
                    "Open":   raw["Open"][ticker],
                    "High":   raw["High"][ticker],
                    "Low":    raw["Low"][ticker],
                    "Close":  raw["Close"][ticker],
                    "Volume": raw["Volume"][ticker],
                }).dropna()
            else:
                df_ticker = raw[["Open","High","Low","Close","Volume"]].dropna()
        except Exception as e:
            st.error(f"❌ Kursdaten für **{ticker}** konnten nicht geladen werden: {e}")
            return []

    if df_ticker.empty or len(df_ticker) < 20:
        st.error(f"⚠️ Zu wenige Datenpunkte für **{ticker}** (< 20 Handelstage).")
        return []

    company_name = ticker
    english_summary = ""
    pe_ratio = market_cap = "N/A"
    high_52w = low_52w = None
    try:
        info = yf.Ticker(ticker).info
        company_name    = info.get("longName", ticker)
        english_summary = info.get("longBusinessSummary", "")
        if info.get("trailingPE"):  pe_ratio   = f"{info['trailingPE']:.1f}"
        if info.get("marketCap"):   market_cap = f"{info['marketCap']/1_000_000_000:.1f} Mrd. $"
        high_52w = info.get("fiftyTwoWeekHigh")
        low_52w  = info.get("fiftyTwoWeekLow")
    except Exception:
        pass

    if not high_52w: high_52w = float(df_ticker["High"].max())
    if not low_52w:  low_52w  = float(df_ticker["Low"].min())

    change_pct = (
        (float(df_ticker["Close"].iloc[-1]) - float(df_ticker["Close"].iloc[-2]))
        / float(df_ticker["Close"].iloc[-2])
    ) * 100

    with st.spinner("📊 Berechne technische Signale …"):
        score, signals, explanations = compute_signals(df_ticker, high_52w=high_52w)

    with st.spinner("🤖 KI analysiert Nachrichten & Stimmung …"):
        ki = run_ki_analysis(api_key, ticker, english_summary or company_name,
                             signals=signals, score=score)

    sentiment   = ki.get("sentiment", "Neutral")
    final_score = min(score + (10 if sentiment.lower() == "bullish" else 0), 100)

    return [{
        "ticker":         ticker,
        "name":           company_name,
        "price":          float(df_ticker["Close"].iloc[-1]),
        "change":         change_pct,
        "score":          final_score,
        "signals":        signals,
        "explanations":   explanations,
        "sentiment":      sentiment,
        "summary":        ki.get("german_summary", ""),
        "hot_topic":      ki.get("hot_topic", ""),
        "score_brief":    ki.get("score_brief", ""),
        "holding_period": ki.get("holding_period", "Keine Schätzung."),
        "pe":             pe_ratio,
        "cap":            market_cap,
        "high_52w":       high_52w,
        "low_52w":        low_52w,
        "df":             df_ticker,
    }]


tab_scan, tab_single = st.tabs([
    "🌍 Universum-Scanner",
    "🔍 Einzelaktie analysieren",
])

with tab_scan:
    market_type = st.selectbox(
        "Wähle das MSCI ACWI Universum für die Analyse:",
        [
            "MSCI ACWI: Top 200 Global Mega-Caps & Tech Leaders",
            "MSCI ACWI: Top 200 Eurozone & Western Europe Champions",
            "MSCI ACWI: Top 200 Emerging Markets & Asia-Pacific Giants",
            "MSCI ACWI: Top 200 Global Financials, Energy & Materials",
        ]
    )
with tab_single:
    st.markdown("🔍 **Aktiensuche** — Name oder Ticker eingeben (z. B. *Apple*, *Volkswagen*, *NVDA*)")
    with st.form("single_search_form"):
        search_col, btn_col = st.columns([4, 1])
        with search_col:
            search_query = st.text_input(
                "Aktie suchen",
                placeholder="z. B. Apple, Tesla, Siemens, BYD …",
                label_visibility="collapsed",
            )
        with btn_col:
            search_submitted = st.form_submit_button("🔍 Suchen", use_container_width=True, type="primary")

    if search_submitted and search_query.strip():
        st.session_state["search_query"]   = search_query.strip()
        st.session_state["search_results"] = None  # Reset

    if st.session_state.get("search_query"):
        if st.session_state.get("search_results") is None:
            with st.spinner("Suche läuft …"):
                st.session_state["search_results"] = _yf_search(st.session_state["search_query"])

        results = st.session_state.get("search_results", [])
        if results:
            options = [
                f"{r['shortname']}  —  {r['symbol']}  ({r.get('exchange', '?')})"
                for r in results
            ]
            chosen_label = st.radio(
                "Bitte Aktie auswählen:",
                options,
                index=0,
            )
            chosen_idx   = options.index(chosen_label)
            chosen_ticker = results[chosen_idx]["symbol"]

            st.markdown(
                f"> Ausgewählter Ticker: **`{chosen_ticker}`**  ·  "
                f"{results[chosen_idx].get('longname') or results[chosen_idx].get('shortname', '')}"
            )

            if st.button("🚀 Diese Aktie vollständig analysieren", type="primary", use_container_width=True, key="single_analyse_btn"):
                st.session_state["single_ticker"] = chosen_ticker
        else:
            st.warning(f"⚠️ Keine Ergebnisse für **{st.session_state['search_query']}** gefunden. Bitte anderen Begriff versuchen.")


# ── Ticker-Listen ─────────────────────────────────────────────────────────────
ACWI_TECH_200 = [
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","GOOG","TSLA","AVGO","COST","AMD","NFLX",
    "QCOM","ADBE","CRM","INTU","AMAT","MU","PANW","ORCL","PLTR","NOW","SNPS","CDNS",
    "LRCX","TXN","ADI","KLAC","MRVL","MELI","UBER","ABNB","SBUX","BKNG","NKE","ADP",
    "ISRG","MDLZ","GILD","VRTX","REGN","PDD","CSCO","INTC","PYPL","ORLY","CSX","CTAS",
    "MNST","NXPI","WDAY","ROST","ADSK","CPRT","LULU","PAYX","KDP","EA","MCHP","ODFL",
    "IDXX","FAST","VRSK","CTSH","TEAM","DDOG","ZS","BKR","CEG","VRSN","ILMN","ALGN",
    "EXPE","GE","HON","LMT","RTX","NOC","BA","GD","DE","CAT","MMM","UNP","FDX","UPS",
    "WM","RSG","TT","EMR","PH","ETN","SLB","HAL","FTV","AME","DOV","HWM","URI","PCAR",
    "GWW","CARR","JCI","SNA","XYL","HUBB","MAR","HLT","RCL","CCL","NCLH","DRI","YUM",
    "MCD","CMG","DPZ","WMT","TGT","DG","DLTR","BJ","KR","SYY","EL","CL","PG","KMB",
    "CHD","CLX","GIS","KO","PEP","K","STZ","TAP","HSY","ADM","MO","PM","CVS","WBA",
    "UNH","ELV","CI","CNC","HUM","ABBV","LLY","MRK","PFE","BMY","JNJ","ABT","MDT",
    "SYK","BSX","EW","ZBH","BAX","SMCI","COIN","GME","TPL","MSTR",
]

ACWI_EURO_200 = [
    "ASML","SAP.DE","SU.PA","AIR.PA","SIE.DE","IFX.DE","RHM.DE","BMW.DE","ADS.DE",
    "BAYN.DE","BAS.DE","VOW3.DE","DHL.DE","ALV.DE","MUV2.DE","NESN.SW","NOVN.SW",
    "ROG.SW","DTE.DE","EON.DE","RWE.DE","HEIA.AMS","UNA.AMS","CRH","LIN","ENGI.PA",
    "VIV.PA","PUB.PA","BNP.PA","ACA.PA","GLE.PA","DBK.DE","CBK.DE","ZAL.DE","HEI.DE",
    "CON.DE","PUM.DE","BEI.DE","HEN3.DE","SY1.DE","FRE.DE","FME.DE","UCG.MI","ISP.MI",
    "ENI.MI","RACE.MI","ENEL.MI","MONC.MI","BBVA.MC","SAN.MC","TEF.MC","IBE.MC",
    "ITX.MC","REP.MC","FER.MC","INGA.AMS","KPN.AMS","UMG.AMS","ABN.AMS","ABF.L",
    "AAL.L","AZN.L","BP.L","BATS.L","BARC.L","DGE.L","FLTR.L","GSK.L","HSBA.L",
    "IAG.L","IMB.L","LSEG.L","NG.L","NWG.L","PRU.L","REL.L","RIO.L","RR.L","SGE.L",
    "ULVR.L","VOD.L","WPP.L","ABB.SW","LONN.SW","SIKA.SW","CFR.SW","UHR.SW","GIV.SW",
    "SGSN.SW","SCMN.SW","SLHN.SW","ALC.SW","VOLV-B.ST","ERIC-B.ST","SEB-A.ST",
    "SHB-A.ST","SWED-A.ST","INVE-B.ST","SAND.ST","HEXA-B.ST","HMB.ST","ASSA-B.ST",
    "TEL2-B.ST","TELIA.ST","SKF-B.ST","EQT.ST","EVO.ST","MC.PA","OR.PA","RMS.PA",
    "KER.PA","CDI.PA","PRX.AMS","RTE.PA","MTX.DE","HFG.DE","WIE.VI","OMV.VI",
    "EBS.VI","VER.VI","STLAM.MI","TRN.MI","SRG.MI","PRY.MI","A2A.MI","AMS.MC",
    "GRF.MC","COL.MC","REN.AMS","DSM.AMS","AKZA.AMS","RAND.AMS","ASRN.AMS",
    "SIGN.AMS","ADM.L","AHT.L","ANTO.L","BDEV.L","BKG.L","BT-A.L","BRBY.L",
    "CNA.L","CPG.L","HLN.L","INF.L","IHG.L","JMAT.L","KGF.L","LAND.L","LGEN.L",
    "LLOY.L","MNG.L","MKS.L","PSON.L","RTO.L","SBR.L","SDR.L","SMIN.L","SN.L",
    "SPX.L","STAN.L","TW.L","TSCO.L","WTB.L","BALN.SW","SRENH.SW","SOON.SW",
    "KNIN.SW","GEBN.SW","HOLN.SW","VATN.SW","BSLN.SW","LOGN.SW","TEMN.SW",
    "ATCO-A.ST","SCA-B.ST","ALFA.ST","NIBE-B.ST","SKAF.ST",
]

ACWI_EM_ASIA_200 = [
    "TSM","BABA","JD","PDD","BIDU","NTDOY","SONY","INFY","WIT","HDB","IBN","CPNG",
    "TCEHY","LI","NIO","XPEV","BYDDY","UMC","005930.KS","000660.KS","051910.KS",
    "005490.KS","035420.KS","035720.KS","207940.KS","068270.KS","006400.KS",
    "000270.KS","012330.KS","066570.KS","036570.KS","9984.T","7203.T","9983.T",
    "6861.T","6758.T","6028.T","6501.T","6701.T","6702.T","6503.T","6902.T",
    "6981.T","4063.T","4502.T","4503.T","7751.T","8035.T","8001.T","8031.T",
    "8058.T","8766.T","8411.T","8316.T","8306.T","9432.T","9433.T","4661.T",
    "6954.T","7974.T","9020.T","9022.T","9101.T","RELIANCE.NS","TCS.NS",
    "HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","SBIN.NS","HINDUNILVR.NS",
    "ITC.NS","BAJAJFINSV.NS","AXISBANK.NS","KOTAKBANK.NS","LT.NS","MARUTI.NS",
    "SUNPHARMA.NS","TITAN.NS","NTPC.NS","POWERGRID.NS","ONGC.NS","COALINDIA.NS",
    "TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","VALE3.SA","PETR4.SA","ITUB4.SA",
    "BBDC4.SA","ABEV3.SA","BBAS3.SA","B3SA3.SA","WEGE3.SA","SUZB3.SA","GGBR4.SA",
    "700.HK","9988.HK","3690.HK","9618.HK","1810.HK","9999.HK","2318.HK",
    "3988.HK","1398.HK","939.HK","2628.HK","386.HK","857.HK","1211.HK","669.HK",
    "2688.HK","2382.HK","2317.TW","2454.TW","2308.TW","2881.TW","2882.TW",
    "2303.TW","3711.TW","2412.TW","2357.TW","2603.TW","2609.TW","2615.TW",
    "2891.TW","2886.TW","5880.TW","2884.TW","2892.TW","1301.TW","PBBANK.KL",
    "MAYBANK.KL","CIMB.KL","TENAGA.KL","IHH.KL","PMETAL.KL","MISC.KL",
    "IOICORP.KL","BBCA.JK","BBRI.JK","BMRI.JK","TLKM.JK","ASII.JK","BBNI.JK",
    "UNVR.JK","ADRO.JK","DBSDF","UOVEY",
]

ACWI_FIN_ENERGY_200 = [
    "JPM","BAC","WFC","C","GS","MS","BLK","AXP","HSBC","RY","TD","BNS","BMO","CM",
    "XOM","CVX","SHEL","BP","TTE","EQNR","CB","MMC","AON","PGR","MET","PRU","UBS",
    "DBK.DE","V","MA","COF","DFS","SOFI","HOOD","SCHW","ICE","CME","NDAQ","SPGI",
    "MCO","MSCI","FDS","TRU","EFX","BEN","IVZ","TROW","AMP","PNC","TFC","USB",
    "FITB","HBAN","KEY","RF","CFG","MTB","CMA","ZION","WAL","COP","EOG","OXY",
    "HES","DVN","APA","MRO","OVV","MTDR","PSX","MPC","VLO","PBF","WMB","KMI",
    "OKE","TRGP","ET","PAA","EPD","FCX","NEM","NUE","STLD","CLF","X","AA","CCJ",
    "MP","LAC","ALB","SQM","CTVA","FMC","NTR","MOS","CF","APD","ECL","LIN","SHW",
    "PPG","RPM","AXTA","GOLD","AEM","KGC","AU","GFI","HMY","WPM","FNV","OR","BHP",
    "RIO","VALE","AIG","HIG","CNA","ALL","TRV","AFG","RE","BAM","BN","ARES","BX",
    "KKR","APO","CG","TKO","MAN","BRO","AMTD","SBGL","HFC","CLR","PAA",
]

MARKET_LISTS = {
    "MSCI ACWI: Top 200 Global Mega-Caps & Tech Leaders":        ACWI_TECH_200,
    "MSCI ACWI: Top 200 Eurozone & Western Europe Champions":    ACWI_EURO_200,
    "MSCI ACWI: Top 200 Emerging Markets & Asia-Pacific Giants": ACWI_EM_ASIA_200,
    "MSCI ACWI: Top 200 Global Financials, Energy & Materials":  ACWI_FIN_ENERGY_200,
}

# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def score_badge(score: int):
    """Gibt (Emoji, Hex-Farbe) für einen Score zurück."""
    if score >= 80:
        return "🟢", "#10b981"
    elif score >= 60:
        return "🟡", "#f59e0b"
    elif score >= 40:
        return "🟠", "#f97316"
    else:
        return "🔴", "#ef4444"


def compute_signals(df: pd.DataFrame, high_52w: float | None = None):
    """
    Berechnet 6 technische Signale und gibt
    (gesamt_score, signal_liste, erklärungs_liste) zurück.

    Maximaler Score: 100 Punkte

    Signal-Punkte:
        Volume-Spike          +20
        Bollinger Squeeze     +20
        MACD Crossover bull.  +15  (nur Crossover-Tag; sonst +10)
        RSI 45-70             +15  (RSI >70 → −5 Malus)
        Preis > MA50          +15
        Nahe 52w-Hoch (<5%)   +15
    """
    score = 0
    signals = []
    explanations = []

    close  = df["Close"].astype(float)
    volume = df["Volume"].astype(float)

    # ── 1. Volumen-Spike (echter 20-Tage-Durchschnitt) ──────────────────────
    if len(volume) >= 22:
        # .iloc[-21:-1] = die letzten 20 abgeschlossenen Handelstage
        avg_vol_20d = float(volume.iloc[-21:-1].mean())
        current_vol = float(volume.iloc[-1])
        if avg_vol_20d > 0 and current_vol > avg_vol_20d * 1.5:
            ratio = current_vol / avg_vol_20d
            signals.append("⚙️ Institutioneller Volumensprung")
            explanations.append(
                f"Das heutige Handelsvolumen ist **{ratio:.1f}×** höher als der echte "
                f"20-Tage-Durchschnitt. Das deutet darauf hin, dass Großinvestoren "
                f"(Fonds/Banken) gerade Positionen aufbauen – ein früher Hinweis auf "
                f"erhöhtes institutionelles Interesse."
            )
            score += 20

    # ── 2. Bollinger-Band-Squeeze ────────────────────────────────────────────
    if len(close) >= 20:
        bb_high = ta.volatility.bollinger_hband(close)
        bb_low  = ta.volatility.bollinger_lband(close)
        bw = (bb_high - bb_low) / close.replace(0, float("nan"))
        avg_bw_10 = bw.rolling(10).mean()
        if (
            not bw.empty and not avg_bw_10.empty
            and pd.notna(bw.iloc[-1]) and pd.notna(avg_bw_10.iloc[-1])
            and avg_bw_10.iloc[-1] > 0
            and bw.iloc[-1] < avg_bw_10.iloc[-1] * 0.95
        ):
            signals.append("💥 Chart-Kompression (Bollinger Squeeze)")
            explanations.append(
                "Die Bollinger-Bänder haben sich deutlich verengt – die Aktie "
                "bewegt sich in einer extrem engen Preisspanne. Historisch folgt "
                "auf einen solchen 'Squeeze' ein explosiver Ausbruch. "
                "Richtung noch offen, aber oft bullisch in einem Aufwärtstrend."
            )
            score += 20

    # ── 3. MACD (Crossover-Erkennung statt nur Positions-Vergleich) ─────────
    if len(close) >= 27:
        macd        = ta.trend.macd(close)
        macd_signal = ta.trend.macd_signal(close)
        if (
            not macd.empty and not macd_signal.empty
            and pd.notna(macd.iloc[-1]) and pd.notna(macd.iloc[-2])
            and pd.notna(macd_signal.iloc[-1]) and pd.notna(macd_signal.iloc[-2])
        ):
            crossover_today = (
                macd.iloc[-1]  >  macd_signal.iloc[-1] and
                macd.iloc[-2]  <= macd_signal.iloc[-2]
            )
            bullish_ongoing = macd.iloc[-1] > macd_signal.iloc[-1]

            if crossover_today:
                signals.append("📈 Frisches MACD-Kaufsignal (Crossover heute!)")
                explanations.append(
                    "Der MACD-Indikator hat **heute** ein frisches Kaufsignal "
                    "generiert (Bullish Crossover). Das ist ein starker kurzfristiger "
                    "Trendwechsel: Die Käufer übernehmen gerade die Kontrolle."
                )
                score += 15
            elif bullish_ongoing:
                signals.append("📈 Anhaltendes positives Momentum (MACD)")
                explanations.append(
                    "Der MACD liegt oberhalb seiner Signallinie – das Kaufsignal "
                    "ist aktiv und das Aufwärtsmomentum hält an."
                )
                score += 10

    # ── 4. RSI (NEU) ─────────────────────────────────────────────────────────
    if len(close) >= 15:
        rsi = ta.momentum.rsi(close, window=14)
        if not rsi.empty and pd.notna(rsi.iloc[-1]):
            rsi_val = float(rsi.iloc[-1])
            if 45 <= rsi_val <= 70:
                signals.append(f"⚡ RSI in optimaler Ausbruchs-Zone ({rsi_val:.0f})")
                explanations.append(
                    f"Der RSI liegt bei **{rsi_val:.0f}** – das ist die ideale Zone "
                    f"für einen Ausbruch: stark genug für echtes Momentum, aber noch "
                    f"nicht überkauft (>70). Ein RSI in diesem Bereich signalisiert "
                    f"gesunde Kaufkraft ohne übertriebene Spekulation."
                )
                score += 15
            elif rsi_val > 70:
                signals.append(f"⚠️ RSI überkauft ({rsi_val:.0f}) – Rücksetzer möglich")
                explanations.append(
                    f"Der RSI liegt bei **{rsi_val:.0f}** und zeigt, dass die Aktie "
                    f"kurzfristig überkauft ist. Ein kurzfristiger Rücksetzer ist "
                    f"wahrscheinlich, bevor ein nachhaltiger Ausbruch gelingen kann. "
                    f"Score-Abzug: −5 Punkte."
                )
                score -= 5  # Malus für überkaufte Zone

    # ── 5. Aufwärtstrend: Preis > MA50 (NEU) ─────────────────────────────────
    if len(close) >= 50:
        ma50 = close.rolling(50).mean()
        current_price = float(close.iloc[-1])
        ma50_val = float(ma50.iloc[-1])
        if pd.notna(ma50_val) and current_price > ma50_val:
            signals.append(f"📊 Bestätigter Aufwärtstrend (Preis > MA50: \\${ma50_val:.2f})")
            explanations.append(
                f"Der aktuelle Kurs (\\${current_price:.2f}) liegt über dem "
                f"50-Tage-Durchschnitt (\\${ma50_val:.2f}). Das bestätigt einen "
                f"übergeordneten Aufwärtstrend – ein wichtiges Filter-Kriterium "
                f"für Long-Trades. Ausbrüche im Aufwärtstrend haben statistisch "
                f"eine deutlich höhere Erfolgsquote."
            )
            score += 15

    # ── 6. Nahe 52-Wochen-Hoch (NEU) ─────────────────────────────────────────
    if high_52w and high_52w > 0 and len(close) >= 1:
        current_price = float(close.iloc[-1])
        dist = (high_52w - current_price) / high_52w
        if 0 <= dist <= 0.05:
            signals.append(
                f"🚀 Kurz vor 52-Wochen-Hoch-Ausbruch "
                f"({dist * 100:.1f}% entfernt)"
            )
            explanations.append(
                f"Der Kurs ist nur noch **{dist * 100:.1f}%** vom 52-Wochen-Hoch "
                f"(\\${high_52w:.2f}) entfernt. Ein Durchbruch dieser Marke wäre ein "
                f"sehr starkes bullisches Signal: Der wichtigste Jahreswiderstand "
                f"würde fallen, was oft eine Kaufwelle institutioneller Anleger auslöst."
            )
            score += 15

    return max(0, min(score, 100)), signals, explanations


def run_ki_analysis(
    api_key: str,
    ticker: str,
    english_summary: str,
    signals: list,
    score: int,
) -> dict:
    """
    Ruft Gemini 2.5 Flash mit aktivierter Google-Search-Grounding auf.
    Gibt german_summary, sentiment, hot_topic, score_brief und holding_period zurück.
    """
    signals_text = "\n".join(f"  - {s}" for s in signals) if signals else "  - Keine Signale"

    prompt = f"""Du bist ein professioneller, laienfreundlicher Finanzanalyst für deutschsprachige Anfänger.

Aktie: {ticker}
Englische Unternehmensbeschreibung: "{english_summary}"
Aktuell erkannte technische Signale (Score: {score}/100):
{signals_text}

Aufgaben:
1. Nutze Google Search, um aktuelle Nachrichten und Social-Media-Stimmung (Reddit, X/Twitter, Finanznachrichten) zu '{ticker}' für Juni 2026 zu finden.
2. Erkläre das Unternehmen in genau 3 einfachen deutschen Sätzen (Was stellt es her? Womit verdient es Geld?).
3. Bewerte die aktuelle Marktstimmung.
4. Erkläre in 2-3 Sätzen auf Anfänger-Niveau, WARUM das System einen Score von {score}/100 vergeben hat – beziehe dich konkret auf die erkannten Signale.
5. Schätze eine realistische Haltedauer für diesen Trade (z.B. "3–7 Tage", "2–4 Wochen", "1–3 Monate") und begründe sie in einem Satz.

Antworte NUR mit einem gültigen JSON-Objekt, kein Text davor oder danach:
{{
  "german_summary": "Satz 1. Satz 2. Satz 3.",
  "sentiment": "Bullish",
  "hot_topic": "Ein prägnanter deutscher Satz über das aktuelle Geschehen in Foren und Nachrichten.",
  "score_brief": "2-3 Sätze, die dem Anfänger erklären, warum der Score so hoch/niedrig ist.",
  "holding_period": "z.B. 2–4 Wochen – Begründung in einem Satz."
}}

Erlaubte Werte für 'sentiment': "Bullish", "Neutral", "Bearish"."""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}],
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        raw = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Greedy-Suche: letztes vollständiges JSON-Objekt bevorzugen
        matches = list(re.finditer(r"\{[\s\S]*?\}", raw))
        if not matches:
            raise ValueError("Kein JSON-Objekt im Response gefunden.")
        return json.loads(matches[-1].group(0))
    except Exception:
        sig_count = len(signals)
        return {
            "german_summary": (
                "Dieses international tätige Unternehmen ist in einem "
                "nachgefragten Marktsegment aktiv und generiert stabile Einnahmen. "
                "Es verfügt über eine solide Marktstellung und diversifizierte Produkte. "
                "Die langfristige Strategie zielt auf nachhaltiges Wachstum ab."
            ),
            "sentiment": "Neutral",
            "hot_topic": (
                "Aktuelle KI-Analyse nicht verfügbar – "
                "bitte Gemini-API-Key prüfen oder Rate-Limit beachten."
            ),
            "score_brief": (
                f"Das System hat {sig_count} technische Signal(e) erkannt und daraus "
                f"einen Score von {score}/100 berechnet. "
                "Je mehr Signale gleichzeitig aktiv sind, desto höher die Punktzahl."
            ),
            "holding_period": "Keine Schätzung verfügbar – KI-Analyse fehlgeschlagen.",
        }



# ── Scan-Button (Tab 1: Universum-Scan) ───────────────────────────────────────
CACHE_TTL_SECONDS = 300  # 5 Minuten

with tab_scan:
    scan_btn = st.button(
        f"🚀  Globalen Premium-Scan starten  "
        f"({len(MARKET_LISTS[market_type])} Aktien analysieren)",
        use_container_width=True,
        type="primary",
    )


# ══════════════════════════════════════════════════════════════════════════════
# CACHE-CHECK: Gleiche Anfrage innerhalb von 5 Min → direkt Ergebnis zeigen
# ══════════════════════════════════════════════════════════════════════════════
def render_output(output: list):
    """Rendert die fertige Ergebnisliste (ausgelagert, damit Cache + Live denselben Code nutzen)."""
    st.header(f"📊 Ausbruchs-Report — {len(output)} Top-Kandidaten")
    st.divider()

    for s in output:
        emoji, color = score_badge(s["score"])

        col_title, col_badge = st.columns([3, 1])
        with col_title:
            st.subheader(f"{s['name']}  ({s['ticker']})")
            color_word = "green" if s["change"] >= 0 else "red"
            st.markdown(
                f"Aktueller Kurs: **\\${s['price']:.2f}** "
                f"(:{color_word}[{s['change']:+.2f}%])"
            )
        with col_badge:
            st.markdown(f"""
            <div style="
                background:{color}18;
                border: 2px solid {color};
                border-radius:14px;
                padding:18px 10px;
                text-align:center;
                font-family:'Inter',sans-serif;">
                <div style="font-size:2rem;">{emoji}</div>
                <div style="font-size:2rem; font-weight:700; color:{color}; line-height:1.1;">
                    {s['score']}<span style="font-size:1rem; color:#8892b0;">/100</span>
                </div>
                <div style="font-size:0.75rem; color:#8892b0; text-transform:uppercase;
                            letter-spacing:0.1em; margin-top:4px;">Signal-Score</div>
            </div>
            """, unsafe_allow_html=True)

        # KI-Score-Zusammenfassung & Haltedauer
        holding   = s.get("holding_period", "Keine Schätzung verfügbar.")
        brief     = s.get("score_brief", "")
        hold_lower = holding.lower()
        if any(w in hold_lower for w in ["tag", "tage", "days"]):
            hold_emoji = "⚡"
        elif any(w in hold_lower for w in ["woche", "wochen", "week"]):
            hold_emoji = "📅"
        else:
            hold_emoji = "🗓️"

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {color}12, {color}06);
            border-left: 4px solid {color};
            border-radius: 0 12px 12px 0;
            padding: 16px 20px;
            margin: 12px 0 18px 0;
            font-family: 'Inter', sans-serif;
        ">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <span style="font-size:1.4rem;">{emoji}</span>
                <span style="font-weight:700; color:{color}; font-size:1.05rem;">
                    Signal-Score {s['score']}/100 — KI-Bewertung
                </span>
            </div>
            <p style="margin:0 0 10px 0; color:#c8d3e8; font-size:0.92rem; line-height:1.55;">
                {brief}
            </p>
            <div style="
                display:inline-flex; align-items:center; gap:6px;
                background:#1a1e2e; border:1px solid #2e3450;
                border-radius:8px; padding:6px 14px;
            ">
                <span style="font-size:1.1rem;">{hold_emoji}</span>
                <span style="color:#94a3b8; font-size:0.78rem; text-transform:uppercase;
                            letter-spacing:0.07em;">Voraussichtliche Haltedauer:</span>
                <span style="color:#e2e8f0; font-weight:600; font-size:0.9rem;">{holding}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🏢 Was macht das Unternehmen? *(einfach erklärt)*")
        st.success(s["summary"])

        st.markdown("### 📊 Wichtige Finanz-Kennzahlen")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Börsenwert", s["cap"])
        m2.metric("KGV (Bewertung)", s["pe"])
        m3.metric("52-Wochen-Hoch ✅", f"${s['high_52w']:.2f}")
        m4.metric("52-Wochen-Tief ✅", f"${s['low_52w']:.2f}")

        st.markdown("### 💡 Warum schlägt das System Alarm?")
        for sig, exp in zip(s["signals"], s["explanations"]):
            with st.expander(sig, expanded=False):
                st.markdown(exp)

        st.markdown("### 🌐 KI-Lagebild & Social Media Stimmung")
        sentiment_map = {
            "Bullish": st.success,
            "Neutral": st.info,
            "Bearish": st.error,
        }
        sentiment_fn = sentiment_map.get(s["sentiment"], st.info)
        sentiment_fn(f"**Forum-Stimmung:** {s['sentiment']}\n\n{s['hot_topic']}")

        st.markdown("### 📉 Technischer Chartverlauf *(letzte 6 Monate)*")
        df = s["df"]
        close_s = df["Close"].astype(float)
        ma50_s  = close_s.rolling(50).mean()
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"],   close=df["Close"],
            increasing_line_color="#10b981",
            decreasing_line_color="#ef4444",
            name="Kurs",
        ))
        fig.add_trace(go.Scatter(
            x=df.index, y=ma50_s, mode="lines",
            line=dict(color="#f59e0b", width=1.8, dash="dash"),
            name="MA50 (50-Tage-Ø)",
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161925", plot_bgcolor="#161925",
            height=430, margin=dict(l=20, r=20, t=35, b=20),
            xaxis_rangeslider_visible=False,
            xaxis=dict(showgrid=True, gridcolor="#2e3440"),
            yaxis=dict(showgrid=True, gridcolor="#2e3440", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "💡 **Lesehilfe:** Jede Kerze = ein Handelstag. "
            "🟢 Grün = Kurs gestiegen, 🔴 Rot = Kurs gefallen. "
            "Die **gelbe gestrichelte Linie** ist der 50-Tage-Durchschnitt (MA50) – "
            "liegt der Kurs darüber, ist ein Aufwärtstrend bestätigt."
        )
        st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: Einzelaktien-Analyse — wird ausgelöst wenn single_ticker gesetzt ist
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("single_ticker"):
    ticker_to_analyse = st.session_state.pop("single_ticker")
    try:
        active_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("🔑 **GEMINI_API_KEY** fehlt in den Streamlit-Secrets.")
        st.stop()

    st.divider()
    st.markdown(f"## 🔍 Einzelanalyse: **{ticker_to_analyse}**")
    result = _analyse_single_ticker(ticker_to_analyse, active_key)
    if result:
        render_output(result)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: Universum-Scan
# ══════════════════════════════════════════════════════════════════════════════
if scan_btn:
    cache = st.session_state.get("scan_cache", {})
    cache_key = market_type  # Cache-Schlüssel = gewähltes Universum
    cache_age = time.time() - cache.get("timestamp", 0)
    cache_hit  = (
        cache.get("key") == cache_key
        and cache_age < CACHE_TTL_SECONDS
        and cache.get("output")
    )

    if cache_hit:
        remaining = int(CACHE_TTL_SECONDS - cache_age)
        mins, secs = divmod(remaining, 60)
        st.markdown(f"""
        <div style="
            background: #1a2a1a;
            border: 1px solid #2d6a2d;
            border-left: 4px solid #10b981;
            border-radius: 0 10px 10px 0;
            padding: 12px 18px;
            margin-bottom: 16px;
            font-family: 'Inter', sans-serif;
            display: flex; align-items: center; gap: 10px;
        ">
            <span style="font-size:1.4rem;">⚡</span>
            <div>
                <span style="color:#10b981; font-weight:700;">Cache-Treffer!</span>
                <span style="color:#8ebd8e; font-size:0.9rem;">
                    Dieselbe Analyse von vor {int(cache_age // 60)}m {int(cache_age % 60)}s wird angezeigt.
                    Cache läuft in <strong style="color:#e2e8f0;">{mins}m {secs:02d}s</strong> ab.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_info, col_reload = st.columns([5, 1])
        with col_reload:
            if st.button("🔄 Neu laden", help="Cache umgehen und frischen Scan starten"):
                st.session_state.pop("scan_cache", None)
                st.rerun()
        render_output(cache["output"])
        st.stop()


    # ── API-Key ───────────────────────────────────────────────────────────────
    try:
        active_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error(
            "🔑 **GEMINI_API_KEY** fehlt in den Streamlit-Secrets. "
            "Bitte unter ⚙️ → Secrets eintragen."
        )
        st.stop()

    full_tickers = MARKET_LISTS[market_type]

    # ── Phase 1: Daten-Download (6 Monate für MA50 + alle Indikatoren) ───────
    st.info("📡 **Phase 1/3:** Downloade 6-Monats-Datenpaket von Yahoo Finance …")
    prog_dl = st.progress(0, text="Download läuft …")

    try:
        # FIX: 6mo statt 3mo (notwendig für MA50 = 50 Handelstage)
        raw_data = yf.download(
            full_tickers,
            period="6mo",
            progress=False,
            auto_adjust=True,
        )
        prog_dl.progress(100, text="✅ Download abgeschlossen")
    except Exception as e:
        st.error(f"❌ Yahoo-Finance-Download fehlgeschlagen: {e}")
        st.stop()

    # ── Phase 2: Technische Signale berechnen ─────────────────────────────────
    st.info("📊 **Phase 2/3:** Berechne technische Signale für alle Aktien …")
    prog_scan = st.progress(0)
    status_scan = st.empty()

    math_results = []

    for idx, ticker in enumerate(full_tickers):
        if idx % 5 == 0:
            prog_scan.progress(int((idx + 1) / len(full_tickers) * 100))
            # FIX: Tippfehler "Analisiere" → "Analysiere"
            status_scan.markdown(
                f"🔍 Analysiere **{ticker}** ({idx + 1}/{len(full_tickers)}) …"
            )

        try:
            # Multi-Index-Handling (mehrere Ticker im Batch-Download)
            if isinstance(raw_data.columns, pd.MultiIndex):
                if ticker not in raw_data.columns.get_level_values(1):
                    continue
                df_ticker = pd.DataFrame({
                    "Open":   raw_data["Open"][ticker],
                    "High":   raw_data["High"][ticker],
                    "Low":    raw_data["Low"][ticker],
                    "Close":  raw_data["Close"][ticker],
                    "Volume": raw_data["Volume"][ticker],
                }).dropna()
            else:
                df_ticker = raw_data[["Open", "High", "Low", "Close", "Volume"]].dropna()

            if df_ticker.empty or len(df_ticker) < 20:
                continue

            # Erste Berechnung ohne 52w-High (kommt in Phase 3)
            score, signals, explanations = compute_signals(df_ticker)

            if score > 0 and signals:
                change_pct = (
                    (float(df_ticker["Close"].iloc[-1]) - float(df_ticker["Close"].iloc[-2]))
                    / float(df_ticker["Close"].iloc[-2])
                ) * 100

                math_results.append({
                    "ticker":       ticker,
                    "price":        float(df_ticker["Close"].iloc[-1]),
                    "change":       change_pct,
                    "score":        score,
                    "signals":      signals,
                    "explanations": explanations,
                    "df":           df_ticker,
                })

        except Exception:
            continue

    prog_scan.empty()
    status_scan.empty()

    if not math_results:
        st.error(
            "⚠️ Keine Ausbruchskandidaten gefunden. "
            "Versuche den Mindest-Signal-Score in der Seitenleiste zu senken."
        )
        st.stop()

    # Sortieren + filtern
    math_results = sorted(math_results, key=lambda x: x["score"], reverse=True)
    filtered = [r for r in math_results if r["score"] >= min_score]

    if not filtered:
        best_score = math_results[0]["score"] if math_results else 0
        best_ticker = math_results[0]["ticker"] if math_results else "–"
        st.markdown(f"""
        <div style="
            background: #2a2210;
            border: 1px solid #6b5a00;
            border-left: 4px solid #f59e0b;
            border-radius: 0 10px 10px 0;
            padding: 14px 20px;
            margin-bottom: 16px;
            font-family: 'Inter', sans-serif;
        ">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                <span style="font-size:1.4rem;">⚠️</span>
                <span style="color:#f59e0b; font-weight:700; font-size:1.05rem;">
                    Kein Kandidat erreicht Score {min_score}+
                </span>
            </div>
            <div style="color:#d4b96a; font-size:0.9rem; line-height:1.6;">
                Bester gefundener Score: <strong style="color:#e2e8f0;">{best_score}/100</strong>
                ({best_ticker})<br>
                <strong>Mögliche Gründe:</strong><br>
                &nbsp; • <strong>Marktzeiten:</strong> Nach US-Börsenschluss (22:00 Uhr MEZ) kann
                  das heutige Handelsvolumen in yfinance noch nicht aktuell sein → Volumen-Signal (+20 Pkt) fällt weg.<br>
                &nbsp; • <strong>Marktstimmung:</strong> Heute war ein ruhiger Tag ohne starke Ausbrüche.<br>
                &nbsp; • <strong>Schwellenwert:</strong> Mindest-Score im Sidebar auf <strong>{min_score}</strong> eingestellt — ggf. senken.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Zeige Top-5 trotzdem an (mit Hinweis)
        if math_results:
            st.info(f"📋 **Zeige trotzdem die Top {min(5, len(math_results))} besten Kandidaten** – auch wenn sie unter dem Mindest-Score liegen:")
            filtered = math_results[:5]
        else:
            st.stop()

    # FIX: Top-N per Slider konfigurierbar (statt hardcoded 4)
    top_n = filtered[:max_ki]

    st.success(
        f"✅ **{len(filtered)}** Kandidaten mit Score ≥ {min_score} gefunden. "
        f"KI analysiert die Top **{len(top_n)}** …"
    )

    # ── Phase 3: KI-Analyse + echte 52w-Daten aus yf.Ticker.info ─────────────
    st.info("🤖 **Phase 3/3:** KI liest Unternehmensprofil & aktuelle Nachrichten …")
    prog_ki = st.progress(0)
    status_ki = st.empty()

    final_results = []

    for idx, stock in enumerate(top_n):
        status_ki.markdown(
            f"🤖 Analysiere **{stock['ticker']}** ({idx + 1}/{len(top_n)}) …"
        )
        prog_ki.progress(int((idx + 1) / len(top_n) * 100))

        company_name    = stock["ticker"]
        english_summary = ""
        pe_ratio        = "N/A"
        market_cap      = "N/A"
        high_52w        = None
        low_52w         = None

        try:
            info = yf.Ticker(stock["ticker"]).info
            company_name    = info.get("longName", stock["ticker"])
            english_summary = info.get("longBusinessSummary", "")

            if info.get("trailingPE"):
                pe_ratio = f"{info['trailingPE']:.1f}"
            if info.get("marketCap"):
                market_cap = f"{info['marketCap'] / 1_000_000_000:.1f} Mrd. $"

            # FIX: echte 52-Wochen-Werte aus yfinance-API (nicht aus 3-Monats-OHLC)
            high_52w = info.get("fiftyTwoWeekHigh")
            low_52w  = info.get("fiftyTwoWeekLow")

        except Exception:
            pass

        # Fallback auf lokale OHLC-Daten falls kein API-Wert
        if not high_52w:
            high_52w = float(stock["df"]["High"].max())
        if not low_52w:
            low_52w = float(stock["df"]["Low"].min())

        # Score mit echtem 52w-High neu berechnen (ggf. +15 für Near-High)
        score, signals, explanations = compute_signals(stock["df"], high_52w=high_52w)

        # KI-Analyse mit Google Search Grounding
        # Übergabe der Signale + Score → KI erklärt den Score auf Anfänger-Niveau
        ki = run_ki_analysis(
            active_key,
            stock["ticker"],
            english_summary or company_name,
            signals=signals,
            score=score,
        )

        # Sentiment-Bonus: +10 für Bullish, 0 sonst
        sentiment = ki.get("sentiment", "Neutral")
        sentiment_bonus = 10 if sentiment.lower() == "bullish" else 0
        final_score = min(score + sentiment_bonus, 100)

        final_results.append({
            **stock,
            "name":           company_name,
            "summary":        ki.get("german_summary", ""),
            "pe":             pe_ratio,
            "cap":            market_cap,
            "high_52w":       high_52w,
            "low_52w":        low_52w,
            "score":          final_score,
            "signals":        signals,
            "explanations":   explanations,
            "sentiment":      sentiment,
            "hot_topic":      ki.get("hot_topic", ""),
            "score_brief":    ki.get("score_brief", ""),
            "holding_period": ki.get("holding_period", "Keine Schätzung verfügbar."),
        })

    prog_ki.empty()
    status_ki.empty()

    output = sorted(
        [s for s in final_results if s["score"] >= min_score],
        key=lambda x: x["score"],
        reverse=True,
    )

    if not output:
        st.info(
            f"ℹ️ Nach KI-Neubewertung erreicht keine Aktie den Score von **{min_score}**."
        )
        st.stop()

    # ── Ergebnis im Session-State cachen (5 Minuten) ─────────────────────────
    st.session_state["scan_cache"] = {
        "key":       market_type,
        "timestamp": time.time(),
        "output":    output,
    }

    # ── Report rendern (dieselbe Funktion wie bei Cache-Treffer) ──────────────
    render_output(output)
