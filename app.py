import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import hmac
import secrets
import math
import json
import os
import time
from datetime import datetime, timedelta, timezone

# ==================================================
# 1. CONFIGURATIE
# ==================================================

st.set_page_config(
    page_title="Global Trading Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "GLOBAL TRADING INTELLIGENCE"
ADMIN_EMAIL = "veenstajann@gmail.com"
DB_PATH = "trading_platform.db"
PBKDF2_ITERATIONS = 260_000
SCAN_MAX_AGE_MINUTES = 15
NEWS_MAX_AGE_MINUTES = 5
DEFAULT_STARTING_BALANCE = 10_000.0

st.markdown(
    """
    <style>
    .stApp { background: #0b0f19; color: #f3f4f6; }
    [data-testid="stSidebar"] { background: #111827; }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg,#111827,#172033);
        border: 1px solid #273449; border-radius: 14px; padding: 14px;
    }
    .gti-card { background:#111827; border:1px solid #273449; border-radius:14px; padding:16px; margin:8px 0; }
    .gti-buy { border-left:5px solid #22c55e; }
    .gti-watch { border-left:5px solid #f59e0b; }
    .gti-sell { border-left:5px solid #ef4444; }
    .gti-info { border-left:5px solid #3b82f6; }
    .small-muted { color:#9ca3af; font-size:.86rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

DISCLAIMER = (
    "De scanner rangschikt uitsluitend mogelijke paper-tradingopstellingen. "
    "Een hoge score is geen garantie op koerswinst. Dit platform is uitsluitend "
    "bedoeld voor educatie, historische marktanalyse en paper trading."
)

# ==================================================
# 2. MARKTUNIVERSUM, CIRCA 200 ASSETS
# ==================================================

MARKET_UNIVERSE = {
    "Nederland": ["ASML.AS","SHELL.AS","INGA.AS","ADYEN.AS","PHIA.AS","HEIA.AS","UNA.AS","WKL.AS","KPN.AS","NN.AS","AGN.AS","ASM.AS","BESI.AS","AKZA.AS","RAND.AS","DSFIR.AS","IMCD.AS","MT.AS","PRX.AS","LIGHT.AS"],
    "US Mega Cap": ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK-B","AVGO","LLY","JPM","V","MA","WMT","XOM","COST","ORCL","NFLX","HD","PG"],
    "US Technology": ["AMD","INTC","QCOM","MU","ARM","SMCI","PLTR","CRM","ADBE","NOW","SNOW","PANW","CRWD","NET","DDOG","SHOP","UBER","ABNB","PYPL","SQ"],
    "US Industrial": ["CAT","DE","GE","HON","BA","LMT","RTX","NOC","UPS","FDX","UNP","CSX","WM","ETN","EMR"],
    "US Financial": ["BAC","WFC","GS","MS","C","BLK","SCHW","AXP","COF","SPGI","ICE","CME","BK","PNC","USB"],
    "US Healthcare": ["JNJ","UNH","MRK","ABBV","PFE","TMO","ABT","DHR","BMY","AMGN","GILD","VRTX","REGN","ISRG","MDT"],
    "US Consumer": ["KO","PEP","MCD","SBUX","NKE","DIS","LOW","TGT","CVS","PM","MO","MDLZ","CL","EL","LULU"],
    "Europe": ["SAP.DE","SIE.DE","ALV.DE","BAS.DE","BMW.DE","MBG.DE","VOW3.DE","DTE.DE","DBK.DE","RWE.DE","AIR.PA","MC.PA","OR.PA","SAN.PA","BNP.PA","SU.PA","TTE.PA","ADS.DE","NESN.SW","NOVN.SW","ROG.SW","UBSG.SW","AZN.L","HSBA.L","BP.L","SHEL.L","ULVR.L","GSK.L","RIO.L","BARC.L"],
    "Asia": ["7203.T","6758.T","9984.T","8306.T","6861.T","6501.T","7201.T","7267.T","9432.T","8035.T","005930.KS","000660.KS","035420.KS","035720.KS","TSM","BABA","JD","PDD","BIDU","NIO"],
    "Crypto": ["BTC-USD","ETH-USD","SOL-USD","XRP-USD","ADA-USD","DOGE-USD","BNB-USD","AVAX-USD","LINK-USD","DOT-USD","LTC-USD","BCH-USD","ATOM-USD","UNI-USD","AAVE-USD","NEAR-USD","ETC-USD","XLM-USD","FIL-USD","APT-USD"],
    "Forex": ["EURUSD=X","GBPUSD=X","USDJPY=X","EURGBP=X","AUDUSD=X","USDCAD=X","USDCHF=X","NZDUSD=X","EURJPY=X","GBPJPY=X"],
    "Indices": ["^AEX","^GSPC","^IXIC","^DJI","^RUT","^VIX","^GDAXI","^FTSE","^FCHI","^N225","^HSI","000001.SS"],
    "Commodities": ["GC=F","SI=F","CL=F","BZ=F","NG=F","HG=F","PL=F","PA=F","ZC=F","ZW=F"],
    "ETF": ["SPY","QQQ","DIA","IWM","VTI","VOO","XLK","XLF","XLE","XLV","ARKK","SMH","SOXX","GLD","SLV","TLT","HYG","EEM","VEA","VNQ"],
}

TICKER_CATEGORY = {}
for category, symbols in MARKET_UNIVERSE.items():
    for symbol in symbols:
        symbol = str(symbol).strip().upper()
        if symbol:
            TICKER_CATEGORY.setdefault(symbol, category)
ALL_TICKERS = list(TICKER_CATEGORY.keys())

# ==================================================
# 3. DATABASE EN MIGRATIES
# ==================================================

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def add_column_if_missing(conn, table, column, definition):
    if column not in table_columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_database():
    conn = db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT DEFAULT '',
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'USER',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login TEXT
        );
        CREATE TABLE IF NOT EXISTS paper_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT 'Hoofdaccount',
            initial_balance REAL NOT NULL,
            cash_balance REAL NOT NULL,
            realized_pnl REAL NOT NULL DEFAULT 0,
            risk_pct REAL NOT NULL DEFAULT 1,
            max_allocation_pct REAL NOT NULL DEFAULT 20,
            max_positions INTEGER NOT NULL DEFAULT 5,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            stop_loss REAL,
            take_profit REAL,
            strategy TEXT,
            original_score REAL,
            original_signal TEXT,
            opened_at TEXT NOT NULL,
            last_reviewed TEXT,
            status TEXT NOT NULL DEFAULT 'OPEN',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(account_id) REFERENCES paper_accounts(id)
        );
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL NOT NULL,
            pnl REAL NOT NULL,
            pnl_pct REAL NOT NULL,
            strategy TEXT,
            close_reason TEXT,
            opened_at TEXT,
            closed_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(user_id,ticker)
        );
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trade_id INTEGER,
            ticker TEXT,
            entry_reason TEXT,
            followed_plan TEXT,
            went_well TEXT,
            went_wrong TEXT,
            lesson TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS scanner_results (
            ticker TEXT PRIMARY KEY,
            category TEXT,
            price REAL,
            daily_change REAL,
            weekly_change REAL,
            monthly_change REAL,
            ema9 REAL,
            ema21 REAL,
            sma50 REAL,
            sma200 REAL,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            volume_ratio REAL,
            atr REAL,
            volatility REAL,
            technical_score REAL,
            news_score REAL,
            total_score REAL,
            signal TEXT,
            confidence REAL,
            entry_zone REAL,
            stop_loss REAL,
            target_1 REAL,
            target_2 REAL,
            risk_reward REAL,
            data_quality REAL,
            last_update TEXT,
            scan_error TEXT,
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS signal_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticker TEXT NOT NULL,
            signal TEXT,
            technical_score REAL,
            news_score REAL,
            total_score REAL,
            price REAL,
            entry_zone REAL,
            stop_loss REAL,
            target_1 REAL,
            target_2 REAL,
            risk_reward REAL,
            confidence REAL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            kind TEXT,
            message TEXT,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            risk_pct REAL NOT NULL DEFAULT 1,
            max_allocation_pct REAL NOT NULL DEFAULT 20,
            max_positions INTEGER NOT NULL DEFAULT 5,
            min_rr REAL NOT NULL DEFAULT 1.8
        );
        """
    )
    add_column_if_missing(conn, "users", "role", "TEXT NOT NULL DEFAULT 'USER'")
    add_column_if_missing(conn, "users", "active", "INTEGER NOT NULL DEFAULT 1")
    add_column_if_missing(conn, "positions", "original_score", "REAL")
    add_column_if_missing(conn, "positions", "original_signal", "TEXT")
    add_column_if_missing(conn, "positions", "last_reviewed", "TEXT")
    conn.execute("UPDATE users SET role='ADMIN' WHERE lower(email)=lower(?)", (ADMIN_EMAIL,))
    conn.commit()
    conn.close()


init_database()

# ==================================================
# 4. PERSOONLIJK DASHBOARD ZONDER INLOGGEN
# ==================================================

PERSONAL_USER_ID = 1
PERSONAL_EMAIL = "veenstajann@gmail.com"
PERSONAL_NAME = "Stiffan"


def initialize_personal_dashboard():
    conn = db()
    now = datetime.now(timezone.utc).isoformat()

    user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (PERSONAL_USER_ID,),
    ).fetchone()

    if user is None:
        conn.execute(
            """
            INSERT INTO users(
                id, first_name, last_name, email,
                password_hash, password_salt,
                role, active, created_at, last_login
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                PERSONAL_USER_ID,
                PERSONAL_NAME,
                "",
                PERSONAL_EMAIL,
                "LOCAL_NO_LOGIN",
                "LOCAL_NO_LOGIN",
                "ADMIN",
                1,
                now,
                now,
            ),
        )
    else:
        conn.execute(
            """
            UPDATE users
            SET first_name=?, email=?, role='ADMIN', active=1
            WHERE id=?
            """,
            (PERSONAL_NAME, PERSONAL_EMAIL, PERSONAL_USER_ID),
        )

    account = conn.execute(
        """
        SELECT * FROM paper_accounts
        WHERE user_id=? AND active=1
        ORDER BY id DESC LIMIT 1
        """,
        (PERSONAL_USER_ID,),
    ).fetchone()

    if account is None:
        conn.execute(
            """
            INSERT INTO paper_accounts(
                user_id, name, initial_balance, cash_balance,
                realized_pnl, risk_pct, max_allocation_pct,
                max_positions, active, created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                PERSONAL_USER_ID,
                "Mijn Paper Trading Account",
                DEFAULT_STARTING_BALANCE,
                DEFAULT_STARTING_BALANCE,
                0.0,
                1.0,
                20.0,
                5,
                1,
                now,
            ),
        )

    conn.execute(
        "INSERT OR IGNORE INTO user_settings(user_id) VALUES(?)",
        (PERSONAL_USER_ID,),
    )

    default_watchlist = [
        "ASML.AS", "AAPL", "MSFT", "NVDA", "AMZN",
        "GOOGL", "META", "TSLA", "BTC-USD", "ETH-USD", "SOL-USD"
    ]
    for ticker in default_watchlist:
        conn.execute(
            """
            INSERT OR IGNORE INTO watchlists(user_id,ticker,created_at)
            VALUES(?,?,?)
            """,
            (PERSONAL_USER_ID, ticker, now),
        )

    conn.commit()
    conn.close()


def current_user():
    conn = db()
    row = conn.execute(
        "SELECT * FROM users WHERE id=? AND active=1",
        (PERSONAL_USER_ID,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def current_account(user_id=PERSONAL_USER_ID):
    conn = db()
    row = conn.execute(
        """
        SELECT * FROM paper_accounts
        WHERE user_id=? AND active=1
        ORDER BY id DESC LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


initialize_personal_dashboard()

# ==================================================
# 5. MARKTDATA EN INDICATOREN
# ==================================================

@st.cache_data(ttl=900, show_spinner=False)
def ticker_history(ticker, period="1y", interval="1d"):
    try:
        frame = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False, threads=False)
        if frame is None or frame.empty:
            return pd.DataFrame()
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
        needed = ["Open", "High", "Low", "Close", "Volume"]
        if not all(c in frame.columns for c in needed):
            return pd.DataFrame()
        return frame[needed].replace([np.inf, -np.inf], np.nan).dropna(subset=["Close"])
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def ticker_news(ticker):
    try:
        raw = yf.Ticker(ticker).news or []
        clean = []
        for item in raw[:10]:
            content = item.get("content", item)
            provider = content.get("provider", {}) or {}
            canonical = content.get("canonicalUrl", {}) or {}
            clean.append({
                "title": content.get("title", item.get("title", "Geen titel")),
                "publisher": provider.get("displayName", item.get("publisher", "Onbekende bron")),
                "url": canonical.get("url", item.get("link", "")),
                "summary": content.get("summary", content.get("description", "")),
                "published": str(content.get("pubDate", item.get("providerPublishTime", ""))),
            })
        return clean
    except Exception:
        return []


def indicators(df):
    x = df.copy()
    c = x["Close"]
    x["EMA9"] = c.ewm(span=9, adjust=False).mean()
    x["EMA21"] = c.ewm(span=21, adjust=False).mean()
    x["SMA50"] = c.rolling(50).mean()
    x["SMA200"] = c.rolling(200).mean()
    delta = c.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    x["RSI"] = (100 - 100 / (1 + gain / loss.replace(0, np.nan))).fillna(50)
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    x["MACD"] = ema12 - ema26
    x["MACD_SIGNAL"] = x["MACD"].ewm(span=9, adjust=False).mean()
    prev = c.shift(1)
    tr = pd.concat([(x["High"] - x["Low"]), (x["High"] - prev).abs(), (x["Low"] - prev).abs()], axis=1).max(axis=1)
    x["ATR"] = tr.rolling(14).mean()
    x["VOL_AVG"] = x["Volume"].rolling(20).mean()
    x["VOLUME_RATIO"] = x["Volume"] / x["VOL_AVG"].replace(0, np.nan)
    x["VOLATILITY"] = c.pct_change().rolling(20).std() * np.sqrt(252) * 100
    return x

POSITIVE = ["beat", "growth", "upgrade", "approval", "partnership", "record", "profit", "buyback", "dividend", "strong", "surge"]
NEGATIVE = ["miss", "warning", "downgrade", "lawsuit", "investigation", "hack", "loss", "weak", "bankruptcy", "layoff", "decline"]


def news_score(news):
    if not news:
        return 50.0
    points = 0
    for item in news:
        text = (item.get("title", "") + " " + item.get("summary", "")).lower()
        points += sum(w in text for w in POSITIVE)
        points -= sum(w in text for w in NEGATIVE)
    return float(max(0, min(100, 50 + points * 5)))


def analyze_ticker(ticker, category=None, include_news=False):
    df = ticker_history(ticker)
    category = category or TICKER_CATEGORY.get(ticker, "Overig")
    if df.empty or len(df) < 60:
        return {"ticker": ticker, "category": category, "signal": "ONVOLDOENDE DATA", "scan_error": "Minder dan 60 candles", "data_quality": 0}
    x = indicators(df)
    last = x.iloc[-1]
    prev = x.iloc[-2]
    values = {k: float(last[k]) if pd.notna(last[k]) else np.nan for k in ["Close","EMA9","EMA21","SMA50","SMA200","RSI","MACD","MACD_SIGNAL","VOLUME_RATIO","ATR","VOLATILITY"]}
    essentials = [values["Close"], values["EMA9"], values["EMA21"], values["SMA50"], values["RSI"], values["MACD"], values["MACD_SIGNAL"], values["ATR"]]
    quality = 100.0 * sum(np.isfinite(v) for v in essentials) / len(essentials)
    score = 0.0
    reasons_for, reasons_against = [], []
    if values["EMA9"] > values["EMA21"]:
        score += 12; reasons_for.append("EMA9 ligt boven EMA21")
    else:
        reasons_against.append("EMA9 ligt onder EMA21")
    if values["Close"] > values["SMA50"]:
        score += 13; reasons_for.append("Koers noteert boven SMA50")
    else:
        reasons_against.append("Koers noteert onder SMA50")
    if np.isfinite(values["SMA200"]) and values["SMA50"] > values["SMA200"]:
        score += 8; reasons_for.append("Langetermijntrend is positief")
    if values["MACD"] > values["MACD_SIGNAL"]:
        score += 10; reasons_for.append("MACD bevestigt positief momentum")
    else:
        reasons_against.append("MACD is bearish")
    rsi = values["RSI"]
    if 45 <= rsi <= 68:
        score += 10; reasons_for.append(f"RSI {rsi:.1f} ligt in gunstige zone")
    elif rsi > 75:
        reasons_against.append(f"RSI {rsi:.1f} is relatief hoog")
    elif rsi < 30:
        score += 4; reasons_for.append(f"RSI {rsi:.1f} is relatief laag")
    vr = values["VOLUME_RATIO"] if np.isfinite(values["VOLUME_RATIO"]) else 1.0
    if vr >= 1.2:
        score += 10; reasons_for.append(f"Volume is {vr:.2f}x gemiddeld")
    elif vr < 0.7:
        reasons_against.append("Volume is laag")
    atr = values["ATR"] if values["ATR"] > 0 else values["Close"] * 0.02
    entry = values["Close"]
    stop = max(0.0001, entry - 1.5 * atr)
    target1 = entry + 2.7 * atr
    target2 = entry + 4.0 * atr
    rr = (target1 - entry) / max(entry - stop, 1e-9)
    if rr >= 1.8:
        score += 10; reasons_for.append(f"Risk/reward is {rr:.2f}")
    else:
        reasons_against.append(f"Risk/reward is slechts {rr:.2f}")
    score += min(5, quality / 20)
    nscore = news_score(ticker_news(ticker)) if include_news else 50.0
    technical_score = max(0, min(100, score * 100 / 78))
    total_score = technical_score * 0.9 + nscore * 0.1
    if quality < 75:
        signal = "ONVOLDOENDE DATA"
    elif total_score >= 78 and technical_score >= 70 and rr >= 1.8:
        signal = "STERKE PAPER BUY SETUP"
    elif total_score >= 68 and technical_score >= 65 and rr >= 1.5:
        signal = "PAPER BUY SETUP"
    elif total_score >= 55:
        signal = "WACHT OP BEVESTIGING"
    elif total_score >= 40:
        signal = "HOLD / BEWAKEN"
    else:
        signal = "PAPER SELL / REDUCE"
    daily = (values["Close"] / float(prev["Close"]) - 1) * 100 if prev["Close"] else 0
    weekly = (values["Close"] / float(x["Close"].iloc[-6]) - 1) * 100 if len(x) >= 6 else 0
    monthly = (values["Close"] / float(x["Close"].iloc[-22]) - 1) * 100 if len(x) >= 22 else 0
    confidence = min(95.0, 35 + len(reasons_for) * 7 + quality * 0.2)
    return {
        "ticker": ticker, "category": category, "price": entry, "daily_change": daily, "weekly_change": weekly,
        "monthly_change": monthly, "ema9": values["EMA9"], "ema21": values["EMA21"], "sma50": values["SMA50"],
        "sma200": values["SMA200"], "rsi": rsi, "macd": values["MACD"], "macd_signal": values["MACD_SIGNAL"],
        "volume_ratio": vr, "atr": atr, "volatility": values["VOLATILITY"], "technical_score": technical_score,
        "news_score": nscore, "total_score": total_score, "signal": signal, "confidence": confidence,
        "entry_zone": entry, "stop_loss": stop, "target_1": target1, "target_2": target2, "risk_reward": rr,
        "data_quality": quality, "last_update": datetime.now(timezone.utc).isoformat(), "scan_error": "",
        "reasons_for": reasons_for, "reasons_against": reasons_against,
    }

# ==================================================
# 6. SCANNER
# ==================================================

SCANNER_COLUMNS = ["ticker","category","price","daily_change","weekly_change","monthly_change","ema9","ema21","sma50","sma200","rsi","macd","macd_signal","volume_ratio","atr","volatility","technical_score","news_score","total_score","signal","confidence","entry_zone","stop_loss","target_1","target_2","risk_reward","data_quality","last_update","scan_error"]


def save_scan(result):
    conn = db()
    payload = [result.get(c) for c in SCANNER_COLUMNS]
    placeholders = ",".join("?" for _ in SCANNER_COLUMNS)
    updates = ",".join(f"{c}=excluded.{c}" for c in SCANNER_COLUMNS[1:])
    conn.execute(f"INSERT INTO scanner_results({','.join(SCANNER_COLUMNS)}) VALUES({placeholders}) ON CONFLICT(ticker) DO UPDATE SET {updates}", payload)
    conn.commit(); conn.close()


def last_scan_time():
    conn = db(); row = conn.execute("SELECT MAX(last_update) AS t FROM scanner_results WHERE scan_error='' ").fetchone(); conn.close()
    return row["t"] if row and row["t"] else None


def scanner_is_stale():
    latest = last_scan_time()
    if not latest: return True
    try:
        return datetime.now(timezone.utc) - datetime.fromisoformat(latest) > timedelta(minutes=SCAN_MAX_AGE_MINUTES)
    except Exception:
        return True


def scan_market_universe(limit=None, progress=None):
    tickers = ALL_TICKERS[:limit] if limit else ALL_TICKERS
    for index, ticker in enumerate(tickers):
        result = analyze_ticker(ticker, TICKER_CATEGORY[ticker], include_news=False)
        save_scan(result)
        if progress:
            progress.progress((index + 1) / len(tickers), text=f"Scan {index+1}/{len(tickers)}: {ticker}")
    return len(tickers)


def load_scan_results():
    conn = db()
    frame = pd.read_sql_query("SELECT * FROM scanner_results WHERE active=1", conn)
    conn.close()
    return frame

# ==================================================
# 7. PORTFOLIO EN PAPER TRADING
# ==================================================

def open_positions(user_id, account_id):
    conn = db(); rows = conn.execute("SELECT * FROM positions WHERE user_id=? AND account_id=? AND status='OPEN' ORDER BY opened_at DESC", (user_id, account_id)).fetchall(); conn.close()
    return [dict(r) for r in rows]


def trade_history(user_id, account_id):
    conn = db(); rows = conn.execute("SELECT * FROM trades WHERE user_id=? AND account_id=? ORDER BY closed_at DESC", (user_id, account_id)).fetchall(); conn.close()
    return [dict(r) for r in rows]


def position_size(account_value, cash, entry, stop, risk_pct, allocation_pct):
    risk_eur = account_value * risk_pct / 100
    risk_unit = abs(entry - stop)
    if entry <= 0 or risk_unit <= 0:
        return 0, risk_eur
    by_risk = math.floor(risk_eur / risk_unit)
    by_cash = math.floor(cash / entry)
    by_allocation = math.floor(account_value * allocation_pct / 100 / entry)
    return max(0, min(by_risk, by_cash, by_allocation)), risk_eur


def create_position(user, account, ticker, quantity, entry, stop, target, strategy, analysis):
    cost = quantity * entry
    if quantity <= 0 or cost > account["cash_balance"]:
        return False, "Ongeldig aantal of onvoldoende virtueel saldo."
    conn = db()
    conn.execute("UPDATE paper_accounts SET cash_balance=cash_balance-? WHERE id=?", (cost, account["id"]))
    conn.execute(
        "INSERT INTO positions(user_id,account_id,ticker,quantity,entry_price,stop_loss,take_profit,strategy,original_score,original_signal,opened_at,last_reviewed,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?, 'OPEN')",
        (user["id"], account["id"], ticker, quantity, entry, stop, target, strategy, analysis.get("total_score"), analysis.get("signal"), datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit(); conn.close()
    return True, "Virtuele positie geopend."


def close_position_fraction(user_id, account_id, position_id, fraction, exit_price, reason):
    conn = db(); pos = conn.execute("SELECT * FROM positions WHERE id=? AND user_id=? AND account_id=? AND status='OPEN'", (position_id, user_id, account_id)).fetchone()
    if not pos:
        conn.close(); return False, "Positie niet gevonden."
    qty_close = float(pos["quantity"]) * fraction
    qty_left = float(pos["quantity"]) - qty_close
    pnl = (exit_price - float(pos["entry_price"])) * qty_close
    pnl_pct = (exit_price / float(pos["entry_price"]) - 1) * 100 if pos["entry_price"] else 0
    conn.execute("UPDATE paper_accounts SET cash_balance=cash_balance+?, realized_pnl=realized_pnl+? WHERE id=?", (qty_close * exit_price, pnl, account_id))
    if qty_left <= 1e-9:
        conn.execute("UPDATE positions SET status='CLOSED', quantity=0 WHERE id=?", (position_id,))
    else:
        conn.execute("UPDATE positions SET quantity=? WHERE id=?", (qty_left, position_id))
    conn.execute("INSERT INTO trades(user_id,account_id,ticker,quantity,entry_price,exit_price,pnl,pnl_pct,strategy,close_reason,opened_at,closed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (user_id,account_id,pos["ticker"],qty_close,pos["entry_price"],exit_price,pnl,pnl_pct,pos["strategy"],reason,pos["opened_at"],datetime.now(timezone.utc).isoformat()))
    conn.commit(); conn.close(); return True, "Paperpositie aangepast."


def portfolio_summary(user, account):
    positions = open_positions(user["id"], account["id"])
    invested = 0.0; open_pnl = 0.0; live = []
    for p in positions:
        analysis = analyze_ticker(p["ticker"], TICKER_CATEGORY.get(p["ticker"], "Watchlist"), include_news=False)
        price = analysis.get("price", p["entry_price"]) if not analysis.get("scan_error") else p["entry_price"]
        value = price * p["quantity"]
        pnl = (price - p["entry_price"]) * p["quantity"]
        invested += value; open_pnl += pnl
        live.append({**p, "current_price": price, "market_value": value, "open_pnl": pnl, "analysis": analysis})
    return {"cash": account["cash_balance"], "invested": invested, "open_pnl": open_pnl, "equity": account["cash_balance"] + invested, "positions": live}

# ==================================================
# 8. PERSOONLIJKE SESSIE ZONDER INLOGSCHERM
# ==================================================

user = current_user()
account = current_account()

if user is None or account is None:
    st.error("Het persoonlijke dashboard kon niet worden geladen.")
    st.stop()

portfolio = portfolio_summary(user, account)

# ==================================================
# 9. NAVIGATIE
# ==================================================

st.sidebar.title("📈 GLOBAL TRADING")
st.sidebar.caption("Persoonlijk Paper Trading Dashboard")
pages = ["🏠 Home","🔎 Market Scanner","📊 Assetanalyse","📰 Nieuws","🎮 Paper Trading","💼 Open Posities","📓 Trading Journal","📈 Performance","⭐ Watchlist","⚙️ Instellingen"]
if user["role"] == "ADMIN":
    pages.append("🛡️ Beheer")
page = st.sidebar.radio("Navigatie", pages)

watch_conn = db(); watch = [r["ticker"] for r in watch_conn.execute("SELECT ticker FROM watchlists WHERE user_id=? ORDER BY ticker", (user["id"],)).fetchall()]; watch_conn.close()
if not watch:
    watch = ["ASML.AS"]
selected = st.sidebar.selectbox("Geselecteerde asset", watch)

# ==================================================
# 10. ALGEMENE HEADER
# ==================================================

st.title(f"🌐 {APP_NAME}")
m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("Virtueel cash", f"€ {portfolio['cash']:,.2f}")
m2.metric("Belegde waarde", f"€ {portfolio['invested']:,.2f}")
m3.metric("Open P&L", f"€ {portfolio['open_pnl']:,.2f}")
m4.metric("Accountwaarde", f"€ {portfolio['equity']:,.2f}")
m5.metric("Open posities", len(portfolio["positions"]))
st.caption(DISCLAIMER)
st.divider()

# ==================================================
# 11. HOME
# ==================================================

if page == "🏠 Home":
    st.header("Marktactiecentrum")
    scan_df = load_scan_results()
    if scan_df.empty:
        st.info("Er zijn nog geen scannerresultaten. Start hieronder de eerste scan.")
        scan_limit = st.selectbox("Eerste scan", [25,50,100,len(ALL_TICKERS)], format_func=lambda n: f"{n} tickers")
        if st.button("Scanner starten", type="primary"):
            bar = st.progress(0, text="Scanner voorbereiden")
            scan_market_universe(scan_limit, bar)
            st.rerun()
    else:
        scan_errors = int((scan_df["scan_error"].fillna("") != "").sum())
        h1,h2,h3 = st.columns(3)
        h1.metric("Gescande assets", len(scan_df))
        h2.metric("Scanproblemen", scan_errors)
        h3.metric("Laatste scan", str(last_scan_time())[:19] if last_scan_time() else "Nog niet")

        buy = scan_df[(scan_df["total_score"] >= 68) & (scan_df["technical_score"] >= 65) & (scan_df["risk_reward"] >= 1.5) & (scan_df["data_quality"] >= 75)].sort_values(["total_score","confidence","risk_reward"], ascending=False).head(10)
        watch_df = scan_df[(scan_df["total_score"] >= 55) & (scan_df["total_score"] < 68) & (scan_df["risk_reward"] >= 1.5)].sort_values("total_score", ascending=False).head(15)

        st.subheader("🟢 Hoogste actuele paper-buy setups")
        if buy.empty:
            st.info("Geen setup voldoet momenteel aan alle ingestelde voorwaarden.")
        for rank, (_, row) in enumerate(buy.iterrows(), 1):
            units, risk_eur = position_size(portfolio["equity"], portfolio["cash"], row["entry_zone"], row["stop_loss"], account["risk_pct"], account["max_allocation_pct"])
            with st.expander(f"#{rank} {row['ticker']} | {row['signal']} | {row['total_score']:.0f}/100"):
                a,b,c,d = st.columns(4)
                a.metric("Koers", f"{row['price']:.4f}", f"{row['daily_change']:.2f}%")
                b.metric("Confidence", f"{row['confidence']:.0f}%")
                c.metric("Risk/reward", f"{row['risk_reward']:.2f}")
                d.metric("Paper-aantal", units)
                st.write(f"**Entry:** {row['entry_zone']:.4f} | **Stop:** {row['stop_loss']:.4f} | **Target 1:** {row['target_1']:.4f} | **Target 2:** {row['target_2']:.4f}")
                st.caption(f"Maximaal paper-risico: € {risk_eur:.2f}. Nieuwsbevestiging wordt pas opgehaald bij detailanalyse.")
                if st.button("Open paper-order ticket", key=f"ticket_{row['ticker']}"):
                    st.session_state.ticket_ticker = row["ticker"]
                    st.session_state.ticket_analysis = row.to_dict()
                    st.success("Orderticket voorbereid. Open het menu Paper Trading.")

        st.subheader("🔴 Verkopen, verlagen of winst beschermen")
        if not portfolio["positions"]:
            st.info("Je hebt geen open paperposities.")
        for pos in portfolio["positions"]:
            a = pos["analysis"]
            urgency = "GEEN ACTIE"
            reasons = []
            if pos["current_price"] <= (pos["stop_loss"] or 0): urgency = "DIRECT SLUITEN"; reasons.append("Stop-loss is geraakt")
            elif pos["current_price"] >= (pos["take_profit"] or 1e99): urgency = "WINST BESCHERMEN"; reasons.append("Take-profit is bereikt")
            elif a.get("total_score", 50) < 35: urgency = "GEDEELTELIJK VERLAGEN"; reasons.append("Marktscore is onder 35")
            elif a.get("ema9", 0) < a.get("ema21", 0): urgency = "STOP-LOSS AANSCHERPEN"; reasons.append("EMA9 ligt onder EMA21")
            pnl_pct = (pos["current_price"] / pos["entry_price"] - 1) * 100 if pos["entry_price"] else 0
            with st.expander(f"{pos['ticker']} | {urgency} | P&L {pnl_pct:.2f}%"):
                st.write("; ".join(reasons) if reasons else "Geen directe verkoopvoorwaarde geactiveerd.")
                st.write(f"Instap {pos['entry_price']:.4f} | Huidig {pos['current_price']:.4f} | Stop {pos['stop_loss']:.4f} | Target {pos['take_profit']:.4f}")

        st.subheader("🟠 Dit nu bewaken")
        if watch_df.empty:
            st.info("Geen bijna-signalen beschikbaar.")
        else:
            st.dataframe(watch_df[["ticker","category","price","total_score","rsi","volume_ratio","risk_reward","signal"]], use_container_width=True, hide_index=True)

# ==================================================
# 12. MARKET SCANNER
# ==================================================
elif page == "🔎 Market Scanner":
    st.header("🔎 Markt Scanner")
    c1,c2,c3 = st.columns(3)
    category = c1.selectbox("Categorie", ["Alle"] + list(MARKET_UNIVERSE.keys()))
    query = c2.text_input("Zoek ticker").upper().strip()
    signal_filter = c3.selectbox("Signaal", ["Alle","STERKE PAPER BUY SETUP","PAPER BUY SETUP","WACHT OP BEVESTIGING","HOLD / BEWAKEN","PAPER SELL / REDUCE","ONVOLDOENDE DATA"])
    scan_count = st.selectbox("Aantal tickers scannen", [25,50,100,len(ALL_TICKERS)], index=1)
    if st.button("Scan nu uitvoeren", type="primary"):
        bar = st.progress(0, text="Scanner gestart")
        scanned = scan_market_universe(scan_count, bar)
        st.success(f"{scanned} tickers gescand.")
    frame = load_scan_results()
    if not frame.empty:
        if category != "Alle": frame = frame[frame["category"] == category]
        if query: frame = frame[frame["ticker"].str.contains(query, na=False)]
        if signal_filter != "Alle": frame = frame[frame["signal"] == signal_filter]
        st.dataframe(frame.sort_values("total_score", ascending=False), use_container_width=True, hide_index=True)

# ==================================================
# 13. ASSETANALYSE EN NIEUWS
# ==================================================
elif page == "📊 Assetanalyse":
    st.header(f"📊 Uitgebreide analyse: {selected}")
    analysis = analyze_ticker(selected, TICKER_CATEGORY.get(selected, "Watchlist"), include_news=True)
    if analysis.get("scan_error"):
        st.error(analysis["scan_error"])
    else:
        a,b,c,d = st.columns(4)
        a.metric("Actie", analysis["signal"])
        b.metric("Totaalscore", f"{analysis['total_score']:.0f}/100")
        c.metric("Confidence", f"{analysis['confidence']:.0f}%")
        d.metric("Datakwaliteit", f"{analysis['data_quality']:.0f}%")
        st.subheader("Duidelijk paper-tradingplan")
        st.write(f"**Entryzone:** {analysis['entry_zone']:.4f}")
        st.write(f"**Stop-loss:** {analysis['stop_loss']:.4f}")
        st.write(f"**Target 1:** {analysis['target_1']:.4f}")
        st.write(f"**Target 2:** {analysis['target_2']:.4f}")
        st.write(f"**Risk/reward:** {analysis['risk_reward']:.2f}")
        st.success("Positief: " + "; ".join(analysis["reasons_for"]))
        st.error("Risico's: " + ("; ".join(analysis["reasons_against"]) or "Geen sterke technische tegenargumenten"))
        frame = indicators(ticker_history(selected))
        st.line_chart(frame[["Close","EMA9","EMA21","SMA50"]].dropna().tail(180), use_container_width=True)

elif page == "📰 Nieuws":
    st.header(f"📰 Nieuws: {selected}")
    news = ticker_news(selected)
    score = news_score(news)
    st.metric("Nieuws-score", f"{score:.0f}/100")
    if not news:
        st.info("Geen gecontroleerd recent nieuws beschikbaar.")
    for item in news:
        with st.container(border=True):
            st.subheader(item["title"])
            st.caption(f"{item['publisher']} | {item['published']}")
            if item["summary"]: st.write(item["summary"])
            if item["url"]: st.link_button("Open origineel", item["url"])

# ==================================================
# 14. PAPER TRADING EN POSITIES
# ==================================================
elif page == "🎮 Paper Trading":
    ticker = st.session_state.get("ticket_ticker", selected)
    analysis = st.session_state.get("ticket_analysis") or analyze_ticker(ticker, TICKER_CATEGORY.get(ticker, "Watchlist"), include_news=True)
    st.header(f"🎮 Paper-order ticket: {ticker}")
    entry = st.number_input("Instapprijs", min_value=0.0001, value=float(analysis.get("entry_zone", analysis.get("price", 1))), format="%.4f")
    stop = st.number_input("Stop-loss", min_value=0.0001, value=float(analysis.get("stop_loss", entry * .97)), format="%.4f")
    target = st.number_input("Take-profit", min_value=0.0001, value=float(analysis.get("target_1", entry * 1.05)), format="%.4f")
    units, risk_eur = position_size(portfolio["equity"], portfolio["cash"], entry, stop, account["risk_pct"], account["max_allocation_pct"])
    qty = st.number_input("Aantal", min_value=1, value=max(1, units), step=1)
    rr = (target-entry)/max(entry-stop,1e-9)
    st.write(f"Aanbevolen aantal: **{units}** | Maximaal risico: **€ {risk_eur:.2f}** | Risk/reward: **{rr:.2f}**")
    errors = []
    if stop >= entry: errors.append("Stop-loss moet onder de instapprijs liggen.")
    if target <= entry: errors.append("Take-profit moet boven de instapprijs liggen.")
    if qty * entry > portfolio["cash"]: errors.append("Onvoldoende virtueel cashsaldo.")
    if rr < 1.5: errors.append("Risk/reward is lager dan 1,5.")
    for e in errors: st.error(e)
    if st.button("Virtuele kooporder bevestigen", type="primary", disabled=bool(errors)):
        ok,msg = create_position(user,account,ticker,qty,entry,stop,target,"Home/Scanner",analysis)
        st.success(msg) if ok else st.error(msg)
        if ok: st.rerun()

elif page == "💼 Open Posities":
    st.header("💼 Open paperposities")
    if not portfolio["positions"]: st.info("Geen open posities.")
    for pos in portfolio["positions"]:
        pnl_pct = (pos["current_price"]/pos["entry_price"]-1)*100 if pos["entry_price"] else 0
        with st.container(border=True):
            st.subheader(f"{pos['ticker']} | {pos['quantity']:.4f} eenheden")
            st.write(f"Instap {pos['entry_price']:.4f} | Huidig {pos['current_price']:.4f} | P&L € {pos['open_pnl']:.2f} ({pnl_pct:.2f}%)")
            c1,c2,c3 = st.columns(3)
            if c1.button("Sluit 25%", key=f"c25_{pos['id']}"):
                close_position_fraction(user["id"],account["id"],pos["id"],.25,pos["current_price"],"PARTIAL_25"); st.rerun()
            if c2.button("Sluit 50%", key=f"c50_{pos['id']}"):
                close_position_fraction(user["id"],account["id"],pos["id"],.50,pos["current_price"],"PARTIAL_50"); st.rerun()
            if c3.button("Sluit volledig", key=f"c100_{pos['id']}"):
                close_position_fraction(user["id"],account["id"],pos["id"],1.0,pos["current_price"],"MANUAL_CLOSE"); st.rerun()

# ==================================================
# 15. JOURNAL, PERFORMANCE, WATCHLIST EN INSTELLINGEN
# ==================================================
elif page == "📓 Trading Journal":
    st.header("📓 Trading Journal")
    trades = trade_history(user["id"], account["id"])
    if not trades: st.info("Nog geen gesloten papertrades.")
    else:
        frame = pd.DataFrame(trades)
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.download_button("Download CSV", frame.to_csv(index=False).encode(), "trading_journal.csv", "text/csv")

elif page == "📈 Performance":
    st.header("📈 Performance")
    trades = trade_history(user["id"], account["id"])
    if not trades: st.info("Nog onvoldoende trades.")
    else:
        pnl = np.array([t["pnl"] for t in trades], dtype=float)
        wins = pnl[pnl>0]; losses = pnl[pnl<0]
        winrate = len(wins)/len(pnl)*100
        pf = wins.sum()/abs(losses.sum()) if len(losses) else float(wins.sum())
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Trades",len(pnl)); c2.metric("Winrate",f"{winrate:.1f}%"); c3.metric("Profit factor",f"{pf:.2f}"); c4.metric("Totaal P&L",f"€ {pnl.sum():.2f}")
        equity = pd.DataFrame({"Cumulatief P&L": np.flip(pnl).cumsum()})
        st.line_chart(equity)
        if len(pnl)<20: st.warning("Minimaal 20 gesloten papertrades nodig voor persoonlijke patroonanalyse.")

elif page == "⭐ Watchlist":
    st.header("⭐ Watchlist")
    new = st.text_input("Ticker toevoegen").upper().strip()
    if st.button("Toevoegen") and new:
        if ticker_history(new,"5d","1d").empty: st.error("Ticker niet gevonden.")
        else:
            conn=db(); conn.execute("INSERT OR IGNORE INTO watchlists(user_id,ticker,created_at) VALUES(?,?,?)",(user["id"],new,datetime.now(timezone.utc).isoformat())); conn.commit(); conn.close(); st.rerun()
    st.dataframe(pd.DataFrame({"Ticker":watch}), use_container_width=True, hide_index=True)

elif page == "⚙️ Instellingen":
    st.header("⚙️ Risico-instellingen")
    risk = st.slider("Risico per trade (%)",.1,5.0,float(account["risk_pct"]),.1)
    allocation = st.slider("Maximale allocatie per positie (%)",5.0,50.0,float(account["max_allocation_pct"]),1.0)
    max_pos = st.slider("Maximaal aantal open posities",1,20,int(account["max_positions"]))
    if st.button("Instellingen opslaan"):
        conn=db(); conn.execute("UPDATE paper_accounts SET risk_pct=?,max_allocation_pct=?,max_positions=? WHERE id=?",(risk,allocation,max_pos,account["id"])); conn.commit(); conn.close(); st.success("Opgeslagen.")
    st.warning("SQLite is geschikt voor testen. Streamlit Community Cloud garandeert geen permanente lokale database na een herbouw. Gebruik Supabase voor productie.")

# ==================================================
# 16. ADMIN
# ==================================================
elif page == "🛡️ Beheer":
    if user["role"] != "ADMIN" or not user["active"]:
        st.error("Geen toegang."); st.stop()
    st.header("🛡️ Beheerdersdashboard")
    conn = db()
    counts = {
        "Gebruikers": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "Actieve gebruikers": conn.execute("SELECT COUNT(*) FROM users WHERE active=1").fetchone()[0],
        "Open posities": conn.execute("SELECT COUNT(*) FROM positions WHERE status='OPEN'").fetchone()[0],
        "Gesloten trades": conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0],
        "Scannerassets": conn.execute("SELECT COUNT(*) FROM scanner_results").fetchone()[0],
    }
    cols = st.columns(len(counts))
    for col,(label,value) in zip(cols,counts.items()): col.metric(label,value)
    users = pd.read_sql_query("SELECT id,first_name,last_name,email,role,active,created_at,last_login FROM users ORDER BY created_at DESC",conn)
    st.subheader("Gebruikers")
    st.dataframe(users,use_container_width=True,hide_index=True)
    selected_user = st.selectbox("Gebruiker beheren", users["id"].tolist(), format_func=lambda uid: users.loc[users.id==uid,"email"].iloc[0]) if not users.empty else None
    b1,b2 = st.columns(2)
    if selected_user and b1.button("Activeren"):
        conn.execute("UPDATE users SET active=1 WHERE id=?",(int(selected_user),)); conn.execute("INSERT INTO admin_logs(admin_user_id,action,details,created_at) VALUES(?,?,?,?)",(user["id"],"ACTIVATE_USER",str(selected_user),datetime.now(timezone.utc).isoformat())); conn.commit(); st.rerun()
    if selected_user and b2.button("Blokkeren"):
        if int(selected_user)==user["id"]: st.error("Je kunt je eigen adminaccount niet blokkeren.")
        else:
            conn.execute("UPDATE users SET active=0 WHERE id=?",(int(selected_user),)); conn.execute("INSERT INTO admin_logs(admin_user_id,action,details,created_at) VALUES(?,?,?,?)",(user["id"],"BLOCK_USER",str(selected_user),datetime.now(timezone.utc).isoformat())); conn.commit(); st.rerun()
    st.subheader("Systeem")
    st.write(f"Unieke tickers: {len(ALL_TICKERS)}")
    st.write(f"Laatste scan: {last_scan_time() or 'Nog niet'}")
    if st.button("Cache legen"):
        st.cache_data.clear(); st.success("Cache geleegd.")
    conn.close()

st.divider()
st.caption(DISCLAIMER)
