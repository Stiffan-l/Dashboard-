import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import secrets
import json
import math
from datetime import datetime

# ==================================================
# 1. PAGINA-INSTELLINGEN
# ==================================================

st.set_page_config(
    page_title="Global Trading Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #273244;
        border-radius: 12px;
        padding: 16px;
    }

    .signal-card {
        background-color: #111827;
        border: 1px solid #273244;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .bullish {
        border-left: 5px solid #22C55E;
    }

    .bearish {
        border-left: 5px solid #EF4444;
    }

    .neutral {
        border-left: 5px solid #F59E0B;
    }

    .disclaimer {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 14px;
        color: #D1D5DB;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# 2. DATABASE
# ==================================================

DATABASE_FILE = "trading_platform.db"


def get_connection():
    connection = sqlite3.connect(
        DATABASE_FILE,
        check_same_thread=False
    )
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            country TEXT,
            experience TEXT,
            trading_style TEXT,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS paper_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_name TEXT NOT NULL,
            initial_balance REAL NOT NULL,
            cash_balance REAL NOT NULL,
            realized_pnl REAL DEFAULT 0,
            risk_percentage REAL DEFAULT 1,
            created_at TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            direction TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            stop_loss REAL,
            take_profit REAL,
            strategy TEXT,
            opened_at TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (account_id) REFERENCES paper_accounts (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            direction TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL NOT NULL,
            stop_loss REAL,
            take_profit REAL,
            pnl REAL NOT NULL,
            pnl_percentage REAL NOT NULL,
            strategy TEXT,
            close_reason TEXT,
            opened_at TEXT,
            closed_at TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (account_id) REFERENCES paper_accounts (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            added_at TEXT NOT NULL,
            UNIQUE(user_id, ticker),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trade_id INTEGER,
            ticker TEXT,
            reason_entry TEXT,
            followed_plan TEXT,
            went_well TEXT,
            went_wrong TEXT,
            lesson TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            score REAL,
            signal TEXT,
            price REAL,
            summary TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_value REAL NOT NULL,
            cash_balance REAL NOT NULL,
            invested_value REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    connection.commit()
    connection.close()


init_database()

# ==================================================
# 3. HULPFUNCTIES
# ==================================================


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.sha256(
        (password + salt).encode("utf-8")
    ).hexdigest()

    return password_hash, salt


def verify_password(password, stored_hash, salt):
    calculated_hash, _ = hash_password(password, salt)
    return calculated_hash == stored_hash


def valid_email(email):
    return "@" in email and "." in email.split("@")[-1]


def format_money(value, currency="€"):
    if value is None or not np.isfinite(float(value)):
        return f"{currency} 0,00"

    return (
        f"{currency} "
        f"{float(value):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_percentage(value):
    if value is None or not np.isfinite(float(value)):
        return "0,00%"

    return f"{float(value):.2f}%".replace(".", ",")


def safe_float(value, default=0.0):
    try:
        converted = float(value)
        if np.isfinite(converted):
            return converted
        return default
    except (TypeError, ValueError):
        return default


# ==================================================
# 4. GEBRUIKERSFUNCTIES
# ==================================================


def create_user(
    first_name,
    last_name,
    email,
    password,
    country,
    experience,
    trading_style,
    starting_balance
):
    connection = get_connection()
    cursor = connection.cursor()

    password_hash, salt = hash_password(password)
    now = datetime.now().isoformat()

    try:
        cursor.execute(
            """
            INSERT INTO users (
                first_name,
                last_name,
                email,
                password_hash,
                password_salt,
                country,
                experience,
                trading_style,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                first_name.strip(),
                last_name.strip(),
                email.lower().strip(),
                password_hash,
                salt,
                country,
                experience,
                trading_style,
                now
            )
        )

        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO paper_accounts (
                user_id,
                account_name,
                initial_balance,
                cash_balance,
                realized_pnl,
                risk_percentage,
                created_at,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                "Hoofdaccount",
                starting_balance,
                starting_balance,
                0.0,
                1.0,
                now,
                1
            )
        )

        standard_watchlist = [
            "ASML.AS",
            "AAPL",
            "MSFT",
            "NVDA",
            "BTC-USD",
            "ETH-USD"
        ]

        for ticker in standard_watchlist:
            cursor.execute(
                """
                INSERT OR IGNORE INTO watchlists (
                    user_id,
                    ticker,
                    added_at
                )
                VALUES (?, ?, ?)
                """,
                (user_id, ticker, now)
            )

        connection.commit()
        return True, "Account succesvol aangemaakt."

    except sqlite3.IntegrityError:
        return False, "Dit e-mailadres is al geregistreerd."

    except Exception as error:
        return False, f"Account kon niet worden aangemaakt: {error}"

    finally:
        connection.close()


def login_user(email, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email.lower().strip(),)
    )

    user = cursor.fetchone()

    if user is None:
        connection.close()
        return None

    if not verify_password(
        password,
        user["password_hash"],
        user["password_salt"]
    ):
        connection.close()
        return None

    cursor.execute(
        """
        UPDATE users
        SET last_login = ?
        WHERE id = ?
        """,
        (datetime.now().isoformat(), user["id"])
    )

    connection.commit()
    connection.close()

    return dict(user)


def get_user(user_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None


def get_account(user_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM paper_accounts
        WHERE user_id = ? AND active = 1
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None


# ==================================================
# 5. MARKTDATA
# ==================================================


@st.cache_data(ttl=20)
def get_market_data(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=False
        )

        if data is None or data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        required_columns = ["Open", "High", "Low", "Close", "Volume"]

        for column in required_columns:
            if column not in data.columns:
                if column == "Volume":
                    data[column] = 0
                else:
                    return pd.DataFrame()

        data = data[required_columns].copy()
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.dropna(subset=["Close"])

        return data

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=120)
def get_market_news(ticker):
    try:
        product = yf.Ticker(ticker)
        articles = product.news

        if not articles:
            return []

        clean_articles = []

        for article in articles[:15]:
            content = article.get("content", article)

            title = content.get(
                "title",
                article.get("title", "Geen titel beschikbaar")
            )

            provider_data = content.get("provider", {})
            publisher = provider_data.get(
                "displayName",
                article.get("publisher", "Onbekende bron")
            )

            canonical_url = content.get("canonicalUrl", {})
            link = canonical_url.get(
                "url",
                article.get("link", "")
            )

            summary = content.get(
                "summary",
                content.get("description", "")
            )

            published = content.get(
                "pubDate",
                article.get("providerPublishTime", "")
            )

            clean_articles.append(
                {
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "summary": summary,
                    "published": str(published)
                }
            )

        return clean_articles

    except Exception:
        return []


# ==================================================
# 6. TECHNISCHE INDICATOREN
# ==================================================


def calculate_rsi(series, period=14):
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    average_loss = losses.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    relative_strength = (
        average_gain /
        average_loss.replace(0, np.nan)
    )

    rsi = 100 - (100 / (1 + relative_strength))
    return rsi.fillna(50)


def calculate_indicators(data):
    df = data.copy()

    df["EMA9"] = df["Close"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["EMA21"] = df["Close"].ewm(
        span=21,
        adjust=False
    ).mean()

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    df["RSI"] = calculate_rsi(df["Close"], 14)

    ema12 = df["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = df["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    df["MACD"] = ema12 - ema26

    df["MACD_SIGNAL"] = df["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["MACD_HISTOGRAM"] = (
        df["MACD"] - df["MACD_SIGNAL"]
    )

    rolling_std = df["Close"].rolling(20).std()

    df["BOLLINGER_UPPER"] = (
        df["SMA20"] + 2 * rolling_std
    )

    df["BOLLINGER_LOWER"] = (
        df["SMA20"] - 2 * rolling_std
    )

    previous_close = df["Close"].shift(1)

    true_range = pd.concat(
        [
            df["High"] - df["Low"],
            abs(df["High"] - previous_close),
            abs(df["Low"] - previous_close)
        ],
        axis=1
    ).max(axis=1)

    df["ATR"] = true_range.rolling(14).mean()

    df["VOLUME_AVERAGE"] = (
        df["Volume"].rolling(20).mean()
    )

    df["VOLUME_RATIO"] = (
        df["Volume"] /
        df["VOLUME_AVERAGE"].replace(0, np.nan)
    )

    df["RETURN"] = df["Close"].pct_change()

    df["VOLATILITY"] = (
        df["RETURN"].rolling(20).std()
        * np.sqrt(252)
        * 100
    )

    df["RUNNING_MAX"] = df["Close"].cummax()

    df["DRAWDOWN"] = (
        (df["Close"] / df["RUNNING_MAX"]) - 1
    ) * 100

    return df


# ==================================================
# 7. NIEUWSSENTIMENT
# ==================================================


POSITIVE_WORDS = [
    "growth",
    "profit",
    "beat",
    "record",
    "approval",
    "partnership",
    "upgrade",
    "increase",
    "surge",
    "gain",
    "positive",
    "bullish",
    "buyback",
    "dividend",
    "strong",
    "outperform",
    "expansion"
]

NEGATIVE_WORDS = [
    "loss",
    "warning",
    "miss",
    "downgrade",
    "lawsuit",
    "investigation",
    "decline",
    "fall",
    "negative",
    "bearish",
    "hack",
    "bankruptcy",
    "layoffs",
    "recession",
    "weak",
    "underperform",
    "risk"
]


def analyze_news_sentiment(news):
    if not news:
        return 50, "NEUTRAAL", []

    scored_articles = []

    for article in news:
        combined_text = (
            f"{article.get('title', '')} "
            f"{article.get('summary', '')}"
        ).lower()

        positive_count = sum(
            1 for word in POSITIVE_WORDS
            if word in combined_text
        )

        negative_count = sum(
            1 for word in NEGATIVE_WORDS
            if word in combined_text
        )

        score = positive_count - negative_count

        scored_articles.append(
            {
                **article,
                "sentiment_points": score
            }
        )

    total_score = sum(
        article["sentiment_points"]
        for article in scored_articles
    )

    normalized_score = 50 + (total_score * 5)
    normalized_score = max(0, min(100, normalized_score))

    if normalized_score >= 60:
        label = "POSITIEF"
    elif normalized_score <= 40:
        label = "NEGATIEF"
    else:
        label = "NEUTRAAL"

    return normalized_score, label, scored_articles


# ==================================================
# 8. HISTORISCHE ANALYSE
# ==================================================


def calculate_historical_statistics(data):
    if data.empty or len(data) < 30:
        return {}

    close = data["Close"].dropna()
    returns = close.pct_change().dropna()

    if returns.empty:
        return {}

    rolling_max = close.cummax()
    drawdown = ((close / rolling_max) - 1) * 100

    statistics = {
        "days": len(close),
        "return_7d": (
            (close.iloc[-1] / close.iloc[-8]) - 1
        ) * 100 if len(close) >= 8 else 0,
        "return_30d": (
            (close.iloc[-1] / close.iloc[-31]) - 1
        ) * 100 if len(close) >= 31 else 0,
        "return_90d": (
            (close.iloc[-1] / close.iloc[-91]) - 1
        ) * 100 if len(close) >= 91 else 0,
        "total_return": (
            (close.iloc[-1] / close.iloc[0]) - 1
        ) * 100,
        "annual_volatility": (
            returns.std() * np.sqrt(252) * 100
        ),
        "max_drawdown": drawdown.min(),
        "positive_days": (
            (returns > 0).mean() * 100
        ),
        "highest_price": close.max(),
        "lowest_price": close.min(),
        "average_daily_return": returns.mean() * 100
    }

    return statistics


# ==================================================
# 9. ANALYSE ENGINE
# ==================================================


def generate_analysis(data, news):
    if data.empty or len(data) < 30:
        return {
            "score": 50,
            "signal": "ONVOLDOENDE DATA",
            "reasons_for": [],
            "reasons_against": [],
            "news_score": 50,
            "news_label": "NEUTRAAL",
            "confidence": 0,
            "stop_loss": 0,
            "target_1": 0,
            "target_2": 0,
            "summary": "Onvoldoende gegevens beschikbaar."
        }

    df = calculate_indicators(data)
    latest = df.iloc[-1]

    price = safe_float(latest["Close"])
    ema9 = safe_float(latest["EMA9"], price)
    ema21 = safe_float(latest["EMA21"], price)
    sma50 = safe_float(latest["SMA50"], price)
    sma200 = safe_float(latest["SMA200"], price)
    rsi = safe_float(latest["RSI"], 50)
    macd = safe_float(latest["MACD"])
    macd_signal = safe_float(latest["MACD_SIGNAL"])
    volume_ratio = safe_float(
        latest["VOLUME_RATIO"],
        1
    )
    atr = safe_float(
        latest["ATR"],
        price * 0.02
    )

    technical_score = 50
    reasons_for = []
    reasons_against = []

    if ema9 > ema21:
        technical_score += 12
        reasons_for.append(
            "EMA9 ligt boven EMA21, wat op positief kortetermijnmomentum wijst."
        )
    else:
        technical_score -= 12
        reasons_against.append(
            "EMA9 ligt onder EMA21, wat op zwak kortetermijnmomentum wijst."
        )

    if sma50 > sma200:
        technical_score += 12
        reasons_for.append(
            "SMA50 ligt boven SMA200, wat de langere opwaartse trend ondersteunt."
        )
    else:
        technical_score -= 8
        reasons_against.append(
            "SMA50 ligt niet boven SMA200."
        )

    if 45 <= rsi <= 65:
        technical_score += 7
        reasons_for.append(
            f"RSI is {rsi:.1f} en bevindt zich in een gezonde momentumzone."
        )
    elif rsi > 70:
        technical_score -= 8
        reasons_against.append(
            f"RSI is {rsi:.1f}. De asset kan technisch oververhit zijn."
        )
    elif rsi < 30:
        technical_score += 3
        reasons_for.append(
            f"RSI is {rsi:.1f}. De asset bevindt zich in een relatief lage zone."
        )

    if macd > macd_signal:
        technical_score += 10
        reasons_for.append(
            "MACD ligt boven de signaallijn."
        )
    else:
        technical_score -= 10
        reasons_against.append(
            "MACD ligt onder de signaallijn."
        )

    if volume_ratio > 1.2:
        technical_score += 5
        reasons_for.append(
            "Het volume ligt boven het twintigdaagse gemiddelde."
        )

    news_score, news_label, scored_news = (
        analyze_news_sentiment(news)
    )

    combined_score = (
        technical_score * 0.75 +
        news_score * 0.25
    )

    combined_score = max(0, min(100, combined_score))

    if combined_score >= 75:
        signal = "STERK BULLISH"
    elif combined_score >= 60:
        signal = "BULLISH"
    elif combined_score >= 40:
        signal = "NEUTRAAL"
    elif combined_score >= 25:
        signal = "BEARISH"
    else:
        signal = "STERK BEARISH"

    confidence = min(
        90,
        40
        + len(reasons_for) * 8
        + min(len(news), 5) * 3
    )

    stop_loss = max(
        0.01,
        price - (2 * atr)
    )

    target_1 = price + (2 * atr)
    target_2 = price + (3 * atr)

    if combined_score >= 60:
        summary = (
            "De combinatie van technische indicatoren en "
            "beschikbaar nieuwssentiment is relatief positief. "
            "Wacht bij paper trading op prijsbevestiging, "
            "voldoende volume en een geldige stop-loss."
        )
    elif combined_score <= 40:
        summary = (
            "De huidige combinatie van technische indicatoren "
            "en nieuwssentiment is relatief zwak. Een nieuwe "
            "paperpositie vereist extra bevestiging."
        )
    else:
        summary = (
            "De beschikbare gegevens geven geen duidelijke richting. "
            "Wachten op bevestiging is het meest voorzichtige scenario."
        )

    return {
        "score": combined_score,
        "signal": signal,
        "reasons_for": reasons_for,
        "reasons_against": reasons_against,
        "news_score": news_score,
        "news_label": news_label,
        "scored_news": scored_news,
        "confidence": confidence,
        "stop_loss": stop_loss,
        "target_1": target_1,
        "target_2": target_2,
        "summary": summary,
        "rsi": rsi,
        "ema9": ema9,
        "ema21": ema21,
        "atr": atr
    }


# ==================================================
# 10. WATCHLIST
# ==================================================


def get_watchlist(user_id):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT ticker
        FROM watchlists
        WHERE user_id = ?
        ORDER BY ticker
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return [row["ticker"] for row in rows]


def add_watchlist_item(user_id, ticker):
    ticker = ticker.upper().strip()

    if not ticker:
        return False

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR IGNORE INTO watchlists (
                user_id,
                ticker,
                added_at
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                ticker,
                datetime.now().isoformat()
            )
        )

        connection.commit()
        return True

    finally:
        connection.close()


def remove_watchlist_item(user_id, ticker):
    connection = get_connection()

    connection.execute(
        """
        DELETE FROM watchlists
        WHERE user_id = ? AND ticker = ?
        """,
        (user_id, ticker)
    )

    connection.commit()
    connection.close()


# ==================================================
# 11. PAPER TRADING
# ==================================================


def open_position(
    user_id,
    account_id,
    ticker,
    quantity,
    entry_price,
    stop_loss,
    take_profit,
    strategy
):
    connection = get_connection()
    cursor = connection.cursor()

    account = cursor.execute(
        """
        SELECT *
        FROM paper_accounts
        WHERE id = ? AND user_id = ?
        """,
        (account_id, user_id)
    ).fetchone()

    if account is None:
        connection.close()
        return False, "Paper-account niet gevonden."

    order_value = quantity * entry_price

    if order_value > account["cash_balance"]:
        connection.close()
        return False, "Onvoldoende virtueel saldo."

    cursor.execute(
        """
        UPDATE paper_accounts
        SET cash_balance = cash_balance - ?
        WHERE id = ?
        """,
        (order_value, account_id)
    )

    cursor.execute(
        """
        INSERT INTO positions (
            user_id,
            account_id,
            ticker,
            direction,
            quantity,
            entry_price,
            stop_loss,
            take_profit,
            strategy,
            opened_at,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            account_id,
            ticker,
            "LONG",
            quantity,
            entry_price,
            stop_loss,
            take_profit,
            strategy,
            datetime.now().isoformat(),
            "OPEN"
        )
    )

    connection.commit()
    connection.close()

    return True, "Virtuele positie succesvol geopend."


def get_open_positions(user_id, account_id):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM positions
        WHERE user_id = ?
        AND account_id = ?
        AND status = 'OPEN'
        ORDER BY opened_at DESC
        """,
        (user_id, account_id)
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def close_position(
    user_id,
    account_id,
    position_id,
    exit_price,
    close_reason
):
    connection = get_connection()
    cursor = connection.cursor()

    position = cursor.execute(
        """
        SELECT *
        FROM positions
        WHERE id = ?
        AND user_id = ?
        AND account_id = ?
        AND status = 'OPEN'
        """,
        (position_id, user_id, account_id)
    ).fetchone()

    if position is None:
        connection.close()
        return False, "Positie niet gevonden."

    quantity = position["quantity"]
    entry_price = position["entry_price"]

    proceeds = quantity * exit_price
    pnl = (exit_price - entry_price) * quantity

    pnl_percentage = (
        ((exit_price / entry_price) - 1) * 100
        if entry_price > 0
        else 0
    )

    cursor.execute(
        """
        UPDATE paper_accounts
        SET
            cash_balance = cash_balance + ?,
            realized_pnl = realized_pnl + ?
        WHERE id = ?
        """,
        (proceeds, pnl, account_id)
    )

    cursor.execute(
        """
        UPDATE positions
        SET status = 'CLOSED'
        WHERE id = ?
        """,
        (position_id,)
    )

    cursor.execute(
        """
        INSERT INTO trades (
            user_id,
            account_id,
            ticker,
            direction,
            quantity,
            entry_price,
            exit_price,
            stop_loss,
            take_profit,
            pnl,
            pnl_percentage,
            strategy,
            close_reason,
            opened_at,
            closed_at,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            account_id,
            position["ticker"],
            position["direction"],
            quantity,
            entry_price,
            exit_price,
            position["stop_loss"],
            position["take_profit"],
            pnl,
            pnl_percentage,
            position["strategy"],
            close_reason,
            position["opened_at"],
            datetime.now().isoformat(),
            ""
        )
    )

    connection.commit()
    connection.close()

    return True, "Positie succesvol gesloten."


def get_trade_history(user_id, account_id):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM trades
        WHERE user_id = ?
        AND account_id = ?
        ORDER BY closed_at DESC
        """,
        (user_id, account_id)
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ==================================================
# 12. AUTHENTICATIEPAGINA
# ==================================================


def show_authentication():
    st.title("🌐 GLOBAL TRADING INTELLIGENCE")

    st.caption(
        "Professional Paper Trading, Historical Analysis "
        "and Market Intelligence"
    )

    st.warning(
        "Dit platform is uitsluitend bedoeld voor educatie "
        "en paper trading met fictief geld."
    )

    login_tab, register_tab = st.tabs(
        ["🔐 Inloggen", "📝 Account aanmaken"]
    )

    with login_tab:
        st.subheader("Inloggen")

        email = st.text_input(
            "E-mailadres",
            key="login_email"
        )

        password = st.text_input(
            "Wachtwoord",
            type="password",
            key="login_password"
        )

        if st.button(
            "Inloggen",
            use_container_width=True,
            type="primary"
        ):
            user = login_user(email, password)

            if user:
                st.session_state.user_id = user["id"]
                st.success("Succesvol ingelogd.")
                st.rerun()
            else:
                st.error(
                    "Onjuist e-mailadres of wachtwoord."
                )

    with register_tab:
        st.subheader("Account aanmaken")

        column_1, column_2 = st.columns(2)

        with column_1:
            first_name = st.text_input(
                "Voornaam",
                key="register_first_name"
            )

            last_name = st.text_input(
                "Achternaam",
                key="register_last_name"
            )

            register_email = st.text_input(
                "E-mailadres",
                key="register_email"
            )

            register_password = st.text_input(
                "Wachtwoord",
                type="password",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Wachtwoord bevestigen",
                type="password",
                key="confirm_password"
            )

        with column_2:
            country = st.selectbox(
                "Land",
                [
                    "Nederland",
                    "België",
                    "Duitsland",
                    "Verenigd Koninkrijk",
                    "Verenigde Staten",
                    "Anders"
                ]
            )

            experience = st.selectbox(
                "Ervaringsniveau",
                [
                    "Volledig beginner",
                    "Beginner",
                    "Gemiddeld",
                    "Ervaren"
                ]
            )

            trading_style = st.selectbox(
                "Tradingstijl",
                [
                    "Swingtrading",
                    "Daytrading",
                    "Position trading",
                    "Lange termijn analyse"
                ]
            )

            starting_balance = st.selectbox(
                "Virtueel startkapitaal",
                [
                    1000.0,
                    2500.0,
                    5000.0,
                    10000.0,
                    25000.0,
                    50000.0,
                    100000.0
                ],
                index=3,
                format_func=lambda value: format_money(value)
            )

        accept_conditions = st.checkbox(
            "Ik ga akkoord met de algemene voorwaarden en privacyvoorwaarden."
        )

        accept_paper = st.checkbox(
            "Ik begrijp dat alle transacties fictief zijn."
        )

        accept_advice = st.checkbox(
            "Ik begrijp dat analyses geen persoonlijk financieel advies zijn."
        )

        if st.button(
            "Account registreren",
            use_container_width=True,
            type="primary"
        ):
            errors = []

            if not first_name.strip():
                errors.append("Vul je voornaam in.")

            if not valid_email(register_email):
                errors.append(
                    "Vul een geldig e-mailadres in."
                )

            if len(register_password) < 8:
                errors.append(
                    "Het wachtwoord moet minimaal acht tekens bevatten."
                )

            if register_password != confirm_password:
                errors.append(
                    "De wachtwoorden komen niet overeen."
                )

            if not (
                accept_conditions
                and accept_paper
                and accept_advice
            ):
                errors.append(
                    "Accepteer alle voorwaarden."
                )

            if errors:
                for error in errors:
                    st.error(error)
            else:
                success, message = create_user(
                    first_name,
                    last_name,
                    register_email,
                    register_password,
                    country,
                    experience,
                    trading_style,
                    starting_balance
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)


# ==================================================
# 13. SESSION STATE
# ==================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    show_authentication()
    st.stop()

current_user = get_user(st.session_state.user_id)
current_account = get_account(st.session_state.user_id)

if current_user is None or current_account is None:
    st.session_state.user_id = None
    st.error("De accountsessie is niet meer geldig.")
    st.stop()

# ==================================================
# 14. SIDEBAR EN NAVIGATIE
# ==================================================

st.sidebar.title("📈 GLOBAL TRADING")

st.sidebar.caption(
    f"Ingelogd als {current_user['first_name']} "
    f"{current_user['last_name']}"
)

page = st.sidebar.radio(
    "Navigatie",
    [
        "🏠 Dashboard",
        "📊 Assetanalyse",
        "📰 Nieuws",
        "🎮 Paper Trading",
        "💼 Open Posities",
        "📓 Trading Journal",
        "📈 Prestaties",
        "⭐ Watchlist",
        "🎓 Trading Academy",
        "👤 Mijn Account"
    ]
)

st.sidebar.divider()
st.sidebar.subheader("⭐ Watchlist")

watchlist = get_watchlist(st.session_state.user_id)

new_ticker = st.sidebar.text_input(
    "Nieuwe ticker",
    placeholder="Bijvoorbeeld ASML.AS of BTC-USD"
).upper().strip()

if st.sidebar.button(
    "Ticker toevoegen",
    use_container_width=True
):
    if new_ticker:
        test_data = get_market_data(
            new_ticker,
            "5d",
            "1d"
        )

        if test_data.empty:
            st.sidebar.error(
                "Ticker niet gevonden of geen data beschikbaar."
            )
        else:
            add_watchlist_item(
                st.session_state.user_id,
                new_ticker
            )
            st.sidebar.success("Ticker toegevoegd.")
            st.rerun()

if not watchlist:
    add_watchlist_item(
        st.session_state.user_id,
        "ASML.AS"
    )
    watchlist = ["ASML.AS"]

selected_ticker = st.sidebar.selectbox(
    "Geselecteerde asset",
    watchlist
)

if st.sidebar.button(
    "Geselecteerde ticker verwijderen",
    use_container_width=True
):
    if len(watchlist) <= 1:
        st.sidebar.warning(
            "De watchlist moet minimaal één ticker bevatten."
        )
    else:
        remove_watchlist_item(
            st.session_state.user_id,
            selected_ticker
        )
        st.rerun()

st.sidebar.divider()

if st.sidebar.button(
    "🔐 Veilig uitloggen",
    use_container_width=True
):
    st.session_state.user_id = None
    st.rerun()

# ==================================================
# 15. ACTUELE DATA EN ANALYSE
# ==================================================

market_data = get_market_data(
    selected_ticker,
    "1y",
    "1d"
)

market_news = get_market_news(selected_ticker)

if market_data.empty:
    st.error(
        "Er is momenteel geen marktdata beschikbaar voor "
        f"{selected_ticker}."
    )
    st.stop()

indicator_data = calculate_indicators(market_data)
current_price = safe_float(
    indicator_data["Close"].iloc[-1]
)

analysis = generate_analysis(
    market_data,
    market_news
)

historical_statistics = (
    calculate_historical_statistics(market_data)
)

# ==================================================
# 16. AUTOMATISCHE STOP-LOSS EN TAKE-PROFIT
# ==================================================

positions = get_open_positions(
    st.session_state.user_id,
    current_account["id"]
)

for position in positions:
    if position["ticker"] != selected_ticker:
        continue

    stop_loss = safe_float(
        position["stop_loss"],
        0
    )

    take_profit = safe_float(
        position["take_profit"],
        0
    )

    if (
        stop_loss > 0
        and current_price <= stop_loss
    ):
        close_position(
            st.session_state.user_id,
            current_account["id"],
            position["id"],
            current_price,
            "STOP_LOSS"
        )
        st.warning(
            f"De virtuele stop-loss voor "
            f"{position['ticker']} is uitgevoerd."
        )
        st.rerun()

    if (
        take_profit > 0
        and current_price >= take_profit
    ):
        close_position(
            st.session_state.user_id,
            current_account["id"],
            position["id"],
            current_price,
            "TAKE_PROFIT"
        )
        st.success(
            f"De virtuele take-profit voor "
            f"{position['ticker']} is uitgevoerd."
        )
        st.rerun()

# ==================================================
# 17. PORTFOLIOBEREKENING
# ==================================================

positions = get_open_positions(
    st.session_state.user_id,
    current_account["id"]
)

invested_value = 0.0
open_pnl = 0.0

for position in positions:
    position_data = get_market_data(
        position["ticker"],
        "5d",
        "1d"
    )

    if position_data.empty:
        position_price = position["entry_price"]
    else:
        position_price = safe_float(
            position_data["Close"].iloc[-1],
            position["entry_price"]
        )

    position_value = (
        position_price * position["quantity"]
    )

    position_pnl = (
        (position_price - position["entry_price"])
        * position["quantity"]
    )

    invested_value += position_value
    open_pnl += position_pnl

account_value = (
    current_account["cash_balance"]
    + invested_value
)

# ==================================================
# 18. HEADER
# ==================================================

st.title("🌐 GLOBAL TRADING INTELLIGENCE")

st.caption(
    f"Paper Trading & Market Intelligence | "
    f"Laatste update: "
    f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)

metric_1.metric(
    "Virtueel cash",
    format_money(current_account["cash_balance"])
)

metric_2.metric(
    "Belegde waarde",
    format_money(invested_value)
)

metric_3.metric(
    "Open P&L",
    format_money(open_pnl)
)

metric_4.metric(
    "Totale accountwaarde",
    format_money(account_value)
)

st.divider()

# ==================================================
# 19. DASHBOARD
# ==================================================

if page == "🏠 Dashboard":
    st.header(
        f"Goedemiddag, {current_user['first_name']} 👋"
    )

    left_column, right_column = st.columns(
        [1.7, 1]
    )

    with left_column:
        st.subheader(
            f"📊 {selected_ticker}"
        )

        price_1, price_2, price_3 = st.columns(3)

        price_1.metric(
            "Laatste koers",
            f"{current_price:,.4f}"
        )

        price_2.metric(
            "Technische score",
            f"{analysis['score']:.0f}/100"
        )

        price_3.metric(
            "Nieuwsstatus",
            analysis["news_label"]
        )

        chart_columns = [
            "Close",
            "EMA9",
            "EMA21",
            "SMA50"
        ]

        available_columns = [
            column
            for column in chart_columns
            if column in indicator_data.columns
        ]

        st.line_chart(
            indicator_data[
                available_columns
            ].tail(180),
            use_container_width=True
        )

    with right_column:
        st.subheader("🤖 Marktanalyse")

        if analysis["score"] >= 60:
            st.success(analysis["signal"])
        elif analysis["score"] <= 40:
            st.error(analysis["signal"])
        else:
            st.warning(analysis["signal"])

        st.metric(
            "Analysezekerheid",
            f"{analysis['confidence']:.0f}%"
        )

        st.write(analysis["summary"])

        st.caption(
            "Dit is een educatieve, regelgebaseerde analyse."
        )

    st.subheader("Argumenten vóór")

    if analysis["reasons_for"]:
        for reason in analysis["reasons_for"]:
            st.success(reason)
    else:
        st.info("Geen sterke positieve bevestigingen.")

    st.subheader("Risico's en tegenargumenten")

    if analysis["reasons_against"]:
        for reason in analysis["reasons_against"]:
            st.error(reason)
    else:
        st.info("Geen sterke technische tegenargumenten gevonden.")

    st.subheader("Historische kenmerken")

    if historical_statistics:
        h1, h2, h3, h4 = st.columns(4)

        h1.metric(
            "Rendement 30 dagen",
            format_percentage(
                historical_statistics["return_30d"]
            )
        )

        h2.metric(
            "Rendement 90 dagen",
            format_percentage(
                historical_statistics["return_90d"]
            )
        )

        h3.metric(
            "Maximale drawdown",
            format_percentage(
                historical_statistics["max_drawdown"]
            )
        )

        h4.metric(
            "Positieve dagen",
            format_percentage(
                historical_statistics["positive_days"]
            )
        )

# ==================================================
# 20. ASSETANALYSE
# ==================================================

elif page == "📊 Assetanalyse":
    st.header(
        f"📊 Uitgebreide analyse van {selected_ticker}"
    )

    tab_technical, tab_historical, tab_scenarios = st.tabs(
        [
            "Technische analyse",
            "Historische analyse",
            "Scenario's"
        ]
    )

    with tab_technical:
        a1, a2, a3, a4 = st.columns(4)

        a1.metric(
            "RSI",
            f"{analysis.get('rsi', 50):.1f}"
        )

        a2.metric(
            "EMA9",
            f"{analysis.get('ema9', current_price):.4f}"
        )

        a3.metric(
            "EMA21",
            f"{analysis.get('ema21', current_price):.4f}"
        )

        a4.metric(
            "ATR",
            f"{analysis.get('atr', 0):.4f}"
        )

        st.line_chart(
            indicator_data[
                [
                    "Close",
                    "EMA9",
                    "EMA21",
                    "SMA20",
                    "SMA50"
                ]
            ].dropna().tail(250),
            use_container_width=True
        )

    with tab_historical:
        if historical_statistics:
            statistics_frame = pd.DataFrame(
                {
                    "Kenmerk": [
                        "Aantal koersdagen",
                        "Rendement 7 dagen",
                        "Rendement 30 dagen",
                        "Rendement 90 dagen",
                        "Totaal rendement",
                        "Jaarvolatiliteit",
                        "Maximale drawdown",
                        "Positieve dagen",
                        "Hoogste koers",
                        "Laagste koers"
                    ],
                    "Waarde": [
                        historical_statistics["days"],
                        format_percentage(
                            historical_statistics["return_7d"]
                        ),
                        format_percentage(
                            historical_statistics["return_30d"]
                        ),
                        format_percentage(
                            historical_statistics["return_90d"]
                        ),
                        format_percentage(
                            historical_statistics["total_return"]
                        ),
                        format_percentage(
                            historical_statistics["annual_volatility"]
                        ),
                        format_percentage(
                            historical_statistics["max_drawdown"]
                        ),
                        format_percentage(
                            historical_statistics["positive_days"]
                        ),
                        f"{historical_statistics['highest_price']:.4f}",
                        f"{historical_statistics['lowest_price']:.4f}"
                    ]
                }
            )

            st.dataframe(
                statistics_frame,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(
                "Onvoldoende historische data beschikbaar."
            )

    with tab_scenarios:
        st.success(
            f"Bullish scenario: een bevestigde beweging boven "
            f"{analysis['target_1']:.4f} met voldoende volume "
            f"kan het positieve scenario ondersteunen."
        )

        st.warning(
            f"Neutraal scenario: zolang de koers tussen "
            f"{analysis['stop_loss']:.4f} en "
            f"{analysis['target_1']:.4f} beweegt, "
            f"is er geen duidelijke doorbraak."
        )

        st.error(
            f"Bearish scenario: een daling onder "
            f"{analysis['stop_loss']:.4f} maakt het huidige "
            f"positieve scenario ongeldig."
        )

# ==================================================
# 21. NIEUWSPAGINA
# ==================================================

elif page == "📰 Nieuws":
    st.header(
        f"📰 Nieuws Intelligence voor {selected_ticker}"
    )

    n1, n2 = st.columns(2)

    n1.metric(
        "Nieuwsscore",
        f"{analysis['news_score']:.0f}/100"
    )

    n2.metric(
        "Sentiment",
        analysis["news_label"]
    )

    if analysis.get("scored_news"):
        for article in analysis["scored_news"]:
            with st.container(border=True):
                st.subheader(article["title"])

                st.caption(
                    f"Bron: {article['publisher']} | "
                    f"Sentimentpunten: "
                    f"{article['sentiment_points']}"
                )

                if article.get("summary"):
                    st.write(article["summary"])

                if article.get("link"):
                    st.link_button(
                        "Open origineel artikel",
                        article["link"]
                    )
    else:
        st.info(
            "Geen gecontroleerd nieuws beschikbaar voor deze asset."
        )

# ==================================================
# 22. PAPER TRADING
# ==================================================

elif page == "🎮 Paper Trading":
    st.header("🎮 Paper Trading Order Ticket")

    st.info(
        "Deze order gebruikt uitsluitend fictief geld. "
        "Er wordt geen echte brokerorder geplaatst."
    )

    risk_percentage = st.slider(
        "Maximaal risico per trade",
        min_value=0.1,
        max_value=5.0,
        value=float(current_account["risk_percentage"]),
        step=0.1,
        format="%.1f%%"
    )

    entry_price = st.number_input(
        "Virtuele instapprijs",
        min_value=0.0001,
        value=float(current_price),
        format="%.4f"
    )

    stop_loss = st.number_input(
        "Stop-loss",
        min_value=0.0001,
        value=float(analysis["stop_loss"]),
        format="%.4f"
    )

    take_profit = st.number_input(
        "Take-profit",
        min_value=0.0001,
        value=float(analysis["target_1"]),
        format="%.4f"
    )

    max_risk_euro = (
        account_value * risk_percentage / 100
    )

    risk_per_unit = abs(
        entry_price - stop_loss
    )

    units_by_risk = (
        math.floor(
            max_risk_euro / risk_per_unit
        )
        if risk_per_unit > 0
        else 0
    )

    units_by_cash = (
        math.floor(
            current_account["cash_balance"]
            / entry_price
        )
        if entry_price > 0
        else 0
    )

    max_allocation_value = account_value * 0.25

    units_by_allocation = (
        math.floor(
            max_allocation_value / entry_price
        )
        if entry_price > 0
        else 0
    )

    recommended_units = max(
        0,
        min(
            units_by_risk,
            units_by_cash,
            units_by_allocation
        )
    )

    target_distance = abs(
        take_profit - entry_price
    )

    risk_reward = (
        target_distance / risk_per_unit
        if risk_per_unit > 0
        else 0
    )

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Maximaal risico",
        format_money(max_risk_euro)
    )

    r2.metric(
        "Risico per stuk",
        format_money(risk_per_unit)
    )

    r3.metric(
        "Aanbevolen aantal",
        recommended_units
    )

    r4.metric(
        "Risk/reward",
        f"{risk_reward:.2f}"
    )

    default_quantity = max(
        1,
        recommended_units
    )

    quantity = st.number_input(
        "Aantal eenheden",
        min_value=1,
        value=default_quantity,
        step=1
    )

    order_value = quantity * entry_price

    actual_risk = quantity * risk_per_unit

    st.write(
        f"Virtuele orderwaarde: "
        f"**{format_money(order_value)}**"
    )

    st.write(
        f"Risico wanneer de stop-loss wordt geraakt: "
        f"**{format_money(actual_risk)}**"
    )

    strategy = st.selectbox(
        "Strategie",
        [
            "Technische analyse",
            "EMA crossover",
            "Support bounce",
            "Resistance breakout",
            "Nieuwsbevestiging",
            "Eigen strategie"
        ]
    )

    validation_errors = []

    if stop_loss >= entry_price:
        validation_errors.append(
            "Voor een longpositie moet de stop-loss "
            "onder de instapprijs liggen."
        )

    if take_profit <= entry_price:
        validation_errors.append(
            "Voor een longpositie moet de take-profit "
            "boven de instapprijs liggen."
        )

    if order_value > current_account["cash_balance"]:
        validation_errors.append(
            "Onvoldoende virtueel saldo."
        )

    if actual_risk > max_risk_euro:
        validation_errors.append(
            "De order overschrijdt het ingestelde maximale risico."
        )

    if risk_reward < 1.5:
        validation_errors.append(
            "De risk/reward-verhouding is lager dan 1,5."
        )

    if analysis["score"] < 60:
        st.warning(
            "De analyse geeft momenteel geen overtuigend "
            "bullish paper-tradingsignaal."
        )

    for error in validation_errors:
        st.error(error)

    if st.button(
        "🟢 Virtuele kooporder plaatsen",
        use_container_width=True,
        type="primary",
        disabled=bool(validation_errors)
    ):
        success, message = open_position(
            st.session_state.user_id,
            current_account["id"],
            selected_ticker,
            quantity,
            entry_price,
            stop_loss,
            take_profit,
            strategy
        )

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

# ==================================================
# 23. OPEN POSITIES
# ==================================================

elif page == "💼 Open Posities":
    st.header("💼 Open paperposities")

    if not positions:
        st.info("Je hebt momenteel geen open posities.")

    for position in positions:
        position_data = get_market_data(
            position["ticker"],
            "5d",
            "1d"
        )

        if position_data.empty:
            position_price = position["entry_price"]
            data_status = "Geen actuele data"
        else:
            position_price = safe_float(
                position_data["Close"].iloc[-1],
                position["entry_price"]
            )
            data_status = "Laatst beschikbare koers"

        position_value = (
            position_price * position["quantity"]
        )

        position_pnl = (
            (position_price - position["entry_price"])
            * position["quantity"]
        )

        position_pnl_percentage = (
            (
                position_price
                / position["entry_price"]
            ) - 1
        ) * 100

        with st.container(border=True):
            p1, p2, p3, p4 = st.columns(4)

            p1.metric(
                position["ticker"],
                f"{position['quantity']} eenheden"
            )

            p2.metric(
                "Instapprijs",
                f"{position['entry_price']:.4f}"
            )

            p3.metric(
                "Huidige prijs",
                f"{position_price:.4f}"
            )

            p4.metric(
                "Open P&L",
                format_money(position_pnl),
                format_percentage(
                    position_pnl_percentage
                )
            )

            st.caption(
                f"{data_status} | "
                f"Stop-loss: {position['stop_loss']:.4f} | "
                f"Take-profit: {position['take_profit']:.4f} | "
                f"Strategie: {position['strategy']}"
            )

            if st.button(
                f"🔴 Sluit {position['ticker']}",
                key=f"close_position_{position['id']}"
            ):
                success, message = close_position(
                    st.session_state.user_id,
                    current_account["id"],
                    position["id"],
                    position_price,
                    "MANUAL_CLOSE"
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

# ==================================================
# 24. TRADING JOURNAL
# ==================================================

elif page == "📓 Trading Journal":
    st.header("📓 Trading Journal")

    trade_history = get_trade_history(
        st.session_state.user_id,
        current_account["id"]
    )

    if not trade_history:
        st.info(
            "Je hebt nog geen gesloten paper trades."
        )
    else:
        journal_data = pd.DataFrame(trade_history)

        display_columns = [
            "closed_at",
            "ticker",
            "quantity",
            "entry_price",
            "exit_price",
            "pnl",
            "pnl_percentage",
            "strategy",
            "close_reason"
        ]

        available_display_columns = [
            column
            for column in display_columns
            if column in journal_data.columns
        ]

        st.dataframe(
            journal_data[available_display_columns],
            use_container_width=True,
            hide_index=True
        )

        csv_data = journal_data.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download journal als CSV",
            data=csv_data,
            file_name="trading_journal.csv",
            mime="text/csv"
        )

# ==================================================
# 25. PRESTATIES
# ==================================================

elif page == "📈 Prestaties":
    st.header("📈 Paper Trading Prestaties")

    trade_history = get_trade_history(
        st.session_state.user_id,
        current_account["id"]
    )

    if not trade_history:
        st.info(
            "Er zijn nog onvoldoende gesloten trades "
            "voor een prestatieanalyse."
        )
    else:
        pnl_values = [
            safe_float(trade["pnl"])
            for trade in trade_history
        ]

        winners = [
            value
            for value in pnl_values
            if value > 0
        ]

        losers = [
            value
            for value in pnl_values
            if value < 0
        ]

        total_trades = len(pnl_values)

        winrate = (
            len(winners) / total_trades * 100
            if total_trades > 0
            else 0
        )

        total_pnl = sum(pnl_values)

        gross_profit = sum(winners)

        gross_loss = abs(sum(losers))

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else gross_profit
        )

        average_win = (
            np.mean(winners)
            if winners
            else 0
        )

        average_loss = (
            np.mean(losers)
            if losers
            else 0
        )

        s1, s2, s3, s4 = st.columns(4)

        s1.metric(
            "Gesloten trades",
            total_trades
        )

        s2.metric(
            "Winrate",
            format_percentage(winrate)
        )

        s3.metric(
            "Profit factor",
            f"{profit_factor:.2f}"
        )

        s4.metric(
            "Totaal resultaat",
            format_money(total_pnl)
        )

        s5, s6 = st.columns(2)

        s5.metric(
            "Gemiddelde winst",
            format_money(average_win)
        )

        s6.metric(
            "Gemiddeld verlies",
            format_money(average_loss)
        )

        pnl_frame = pd.DataFrame(
            {
                "Trade": list(
                    range(1, total_trades + 1)
                ),
                "P&L": list(reversed(pnl_values))
            }
        )

        pnl_frame["Cumulatief P&L"] = (
            pnl_frame["P&L"].cumsum()
        )

        st.subheader("Cumulatief resultaat")

        st.line_chart(
            pnl_frame.set_index("Trade")[
                ["Cumulatief P&L"]
            ]
        )

        if total_trades < 20:
            st.warning(
                "Er zijn minder dan 20 gesloten trades. "
                "Persoonlijke patroonanalyse is nog onvoldoende betrouwbaar."
            )
        else:
            st.success(
                "Er zijn voldoende trades voor een eerste "
                "voorzichtige patroonanalyse."
            )

# ==================================================
# 26. WATCHLISTPAGINA
# ==================================================

elif page == "⭐ Watchlist":
    st.header("⭐ Mijn Watchlist")

    watchlist_rows = []

    for ticker in watchlist:
        ticker_data = get_market_data(
            ticker,
            "1mo",
            "1d"
        )

        if ticker_data.empty:
            watchlist_rows.append(
                {
                    "Ticker": ticker,
                    "Koers": "Niet beschikbaar",
                    "30 dagen": "Niet beschikbaar"
                }
            )
            continue

        ticker_price = safe_float(
            ticker_data["Close"].iloc[-1]
        )

        monthly_return = (
            (
                ticker_data["Close"].iloc[-1]
                / ticker_data["Close"].iloc[0]
            ) - 1
        ) * 100

        watchlist_rows.append(
            {
                "Ticker": ticker,
                "Koers": f"{ticker_price:.4f}",
                "30 dagen": format_percentage(
                    monthly_return
                )
            }
        )

    st.dataframe(
        pd.DataFrame(watchlist_rows),
        use_container_width=True,
        hide_index=True
    )

# ==================================================
# 27. TRADING ACADEMY
# ==================================================

elif page == "🎓 Trading Academy":
    st.header("🎓 Trading Academy")

    with st.expander(
        "1. Wat is een candlestick?"
    ):
        st.write(
            "Een candlestick toont de openingsprijs, "
            "sluitingsprijs, hoogste prijs en laagste prijs "
            "binnen een bepaalde periode."
        )

    with st.expander(
        "2. Wat is een limitorder?"
    ):
        st.write(
            "Een limitorder wordt alleen uitgevoerd tegen "
            "de ingestelde prijs of een gunstigere prijs."
        )

    with st.expander(
        "3. Wat is een stop-loss?"
    ):
        st.write(
            "Een stop-loss is een vooraf ingesteld niveau "
            "waarop een positie wordt gesloten wanneer de "
            "koers tegen de verwachting in beweegt."
        )

    with st.expander(
        "4. Hoe werkt de 1%-regel?"
    ):
        st.write(
            "Bij de 1%-regel mag het verlies wanneer de "
            "stop-loss wordt geraakt maximaal 1% van de "
            "totale accountwaarde bedragen."
        )

        st.code(
            "Maximaal risico = accountwaarde × 1%\n"
            "Aantal = maximaal risico / risico per stuk"
        )

    with st.expander(
        "5. Wat is risk/reward?"
    ):
        st.write(
            "Risk/reward vergelijkt het mogelijke winstdoel "
            "met het mogelijke verlies tot de stop-loss. "
            "Een verhouding van 2 betekent dat het potentiële "
            "winstdoel twee keer zo groot is als het risico."
        )

# ==================================================
# 28. MIJN ACCOUNT
# ==================================================

elif page == "👤 Mijn Account":
    st.header("👤 Mijn Account")

    profile_1, profile_2 = st.columns(2)

    with profile_1:
        st.write(
            f"**Naam:** "
            f"{current_user['first_name']} "
            f"{current_user['last_name']}"
        )

        st.write(
            f"**E-mailadres:** {current_user['email']}"
        )

        st.write(
            f"**Land:** {current_user['country']}"
        )

        st.write(
            f"**Ervaring:** {current_user['experience']}"
        )

    with profile_2:
        st.write(
            f"**Tradingstijl:** "
            f"{current_user['trading_style']}"
        )

        st.write(
            f"**Account aangemaakt:** "
            f"{current_user['created_at']}"
        )

        st.write(
            f"**Virtueel startkapitaal:** "
            f"{format_money(current_account['initial_balance'])}"
        )

        st.write(
            f"**Gerealiseerde P&L:** "
            f"{format_money(current_account['realized_pnl'])}"
        )

    st.warning(
        "De huidige versie gebruikt SQLite. Op Streamlit "
        "Community Cloud kan het databasebestand verdwijnen "
        "wanneer de app opnieuw wordt opgebouwd. Gebruik voor "
        "volledig permanente online accounts later Supabase."
    )

# ==================================================
# 29. DISCLAIMER
# ==================================================

st.divider()

st.markdown(
    """
    <div class="disclaimer">
    <strong>Belangrijke waarschuwing</strong><br>
    Global Trading Intelligence is uitsluitend bedoeld voor educatie,
    historische marktanalyse en paper trading. De technische analyses,
    nieuwsscores en scenario's vormen geen persoonlijk financieel advies
    en bieden geen garantie op rendement. Historische resultaten
    voorspellen geen toekomstige resultaten. Er worden geen echte
    brokerorders geplaatst.
    </div>
    """,
    unsafe_allow_html=True
)
