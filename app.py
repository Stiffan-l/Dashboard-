import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# ==================================================
# 1. PAGINA-INSTELLINGEN
# ==================================================

st.set_page_config(
    page_title="GLOBAL TRADING INTELLIGENCE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2. GEBRUIKERSDATABASE EN ACCOUNTGEHEUGEN
# ==================================================

if "gebruikers_db" not in st.session_state:
    st.session_state.gebruikers_db = {}

if "actieve_user" not in st.session_state:
    st.session_state.actieve_user = None

if "notifications" not in st.session_state:
    st.session_state.notifications = []


# ==================================================
# 3. MARKTDATA PROVIDER
# ==================================================

class MarketDataProvider:

    @staticmethod
    def haal_data(ticker, period="5d", interval="5m"):
        try:
            product = yf.Ticker(ticker)
            data = product.history(period=period, interval=interval)

            if data.empty:
                return pd.DataFrame()

            return data

        except Exception:
            return pd.DataFrame()

    @staticmethod
    def haal_nieuws(ticker):
        try:
            product = yf.Ticker(ticker)
            nieuws = product.news
            return nieuws if nieuws else []
        except Exception:
            return []


# ==================================================
# 4. TECHNISCHE INDICATOREN
# ==================================================

def bereken_indicatoren(data):

    df = data.copy()

    df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    delta = df["Close"].diff()

    winst = delta.clip(lower=0)
    verlies = -delta.clip(upper=0)

    gemiddelde_winst = winst.rolling(14).mean()
    gemiddelde_verlies = verlies.rolling(14).mean()

    rs = gemiddelde_winst / gemiddelde_verlies.replace(0, np.nan)

    df["RSI"] = 100 - (100 / (1 + rs))

    df["MACD"] = (
        df["Close"].ewm(span=12, adjust=False).mean()
        - df["Close"].ewm(span=26, adjust=False).mean()
    )

    df["MACD_SIGNAL"] = df["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["STD20"] = df["Close"].rolling(20).std()

    df["BOLLINGER_UPPER"] = (
        df["SMA20"] + (2 * df["STD20"])
    )

    df["BOLLINGER_LOWER"] = (
        df["SMA20"] - (2 * df["STD20"])
    )

    return df


# ==================================================
# 5. TECHNISCHE ANALYSE ENGINE
# ==================================================

def technische_analyse(data):

    laatste = data.iloc[-1]

    score = 50
    redenen = []

    if laatste["EMA9"] > laatste["EMA21"]:
        score += 15
        redenen.append("EMA9 ligt boven EMA21.")
    else:
        score -= 15
        redenen.append("EMA9 ligt onder EMA21.")

    if pd.notna(laatste["RSI"]):

        if laatste["RSI"] < 30:
            score += 10
            redenen.append("RSI bevindt zich onder 30.")

        elif laatste["RSI"] > 70:
            score -= 10
            redenen.append("RSI bevindt zich boven 70.")

    if laatste["MACD"] > laatste["MACD_SIGNAL"]:
        score += 10
        redenen.append("MACD ligt boven de signaallijn.")
    else:
        score -= 10

    score = max(0, min(100, score))

    if score >= 75:
        status = "STERK BULLISH"

    elif score >= 60:
        status = "BULLISH"

    elif score >= 40:
        status = "NEUTRAAL"

    elif score >= 25:
        status = "BEARISH"

    else:
        status = "STERK BEARISH"

    return score, status, redenen


# ==================================================
# 6. REGISTRATIE EN LOGIN
# ==================================================

def auth_scherm():

    st.title("🌐 GLOBAL TRADING INTELLIGENCE")

    st.caption(
        "Professional Paper Trading & AI Market Intelligence"
    )

    login_tab, register_tab = st.tabs(
        ["🔐 Inloggen", "📝 Account aanmaken"]
    )

    # ---------------- LOGIN ----------------

    with login_tab:

        st.subheader("Inloggen")

        email = st.text_input(
            "E-mailadres",
            key="login_email"
        )

        wachtwoord = st.text_input(
            "Wachtwoord",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Inloggen",
            use_container_width=True
        ):

            gebruiker = st.session_state.gebruikers_db.get(email)

            if gebruiker and gebruiker["password"] == wachtwoord:

                st.session_state.actieve_user = email

                gebruiker["last_login"] = datetime.now()

                st.success("Succesvol ingelogd.")

                st.rerun()

            else:

                st.error(
                    "Onjuist e-mailadres of wachtwoord."
                )

    # ---------------- REGISTRATIE ----------------

    with register_tab:

        st.subheader("Nieuw account")

        col1, col2 = st.columns(2)

        with col1:

            voornaam = st.text_input("Voornaam")

            achternaam = st.text_input("Achternaam")

            reg_email = st.text_input(
                "E-mailadres",
                key="register_email"
            )

            password = st.text_input(
                "Wachtwoord",
                type="password",
                key="register_password"
            )

        with col2:

            land = st.selectbox(
                "Land",
                [
                    "Nederland",
                    "België",
                    "Duitsland",
                    "Verenigde Staten"
                ]
            )

            ervaring = st.selectbox(
                "Ervaring",
                [
                    "Volledig beginner",
                    "Beginner",
                    "Gemiddeld",
                    "Ervaren"
                ]
            )

            stijl = st.selectbox(
                "Tradingstijl",
                [
                    "Daytrading",
                    "Swingtrading",
                    "Position trading"
                ]
            )

            startkapitaal = st.selectbox(
                "Virtueel startkapitaal",
                [
                    1000,
                    2500,
                    5000,
                    10000,
                    25000,
                    50000,
                    100000
                ],
                index=3
            )

        akkoord = st.checkbox(
            "Ik begrijp dat dit uitsluitend paper trading is."
        )

        if st.button(
            "Account aanmaken",
            use_container_width=True
        ):

            if not reg_email or not password:

                st.error(
                    "Vul minimaal e-mailadres en wachtwoord in."
                )

            elif not akkoord:

                st.error(
                    "Accepteer eerst de voorwaarden."
                )

            elif reg_email in st.session_state.gebruikers_db:

                st.error(
                    "Dit account bestaat al."
                )

            else:

                st.session_state.gebruikers_db[reg_email] = {

                    "password": password,

                    "profile": {
                        "first_name": voornaam,
                        "last_name": achternaam,
                        "country": land,
                        "experience": ervaring,
                        "style": stijl,
                        "created": datetime.now()
                    },

                    "account": {
                        "initial": float(startkapitaal),
                        "cash": float(startkapitaal)
                    },

                    "open_positions": [],

                    "trade_history": [],

                    "journal": [],

                    "watchlist": [
                        "ASML.AS",
                        "AAPL",
                        "MSFT",
                        "NVDA",
                        "BTC-USD",
                        "ETH-USD"
                    ],

                    "alerts": [],

                    "ai_history": []
                }

                st.success(
                    "Account aangemaakt. Je kunt nu inloggen."
                )


# ==================================================
# 7. AUTHENTICATIE CONTROLEREN
# ==================================================

if st.session_state.actieve_user is None:

    auth_scherm()

    st.stop()


user = st.session_state.gebruikers_db[
    st.session_state.actieve_user
]


# ==================================================
# 8. NAVIGATIE
# ==================================================

st.sidebar.title("GLOBAL TRADING")

pagina = st.sidebar.radio(
    "Navigatie",
    [
        "🏠 Dashboard",
        "🌍 Markets",
        "📊 Analyse",
        "🤖 AI Intelligence",
        "📰 Nieuws",
        "🎮 Paper Trading",
        "💼 Portfolio",
        "📓 Trading Journal",
        "⭐ Watchlist",
        "📈 Performance",
        "🎓 Trading Academy",
        "👤 Mijn Account"
    ]
)

st.sidebar.divider()

if st.sidebar.button(
    "🔐 Veilig uitloggen",
    use_container_width=True
):

    st.session_state.actieve_user = None

    st.rerun()


# ==================================================
# 9. WATCHLIST
# ==================================================

st.sidebar.subheader("⭐ Watchlist")

nieuwe_ticker = st.sidebar.text_input(
    "Ticker toevoegen"
).upper()

if st.sidebar.button("Ticker toevoegen"):

    if (
        nieuwe_ticker
        and nieuwe_ticker not in user["watchlist"]
    ):

        user["watchlist"].append(nieuwe_ticker)

        st.rerun()


ticker = st.sidebar.selectbox(
    "Actieve asset",
    user["watchlist"]
)


# ==================================================
# 10. MARKTDATA OPHALEN
# ==================================================

data = MarketDataProvider.haal_data(ticker)

nieuws = MarketDataProvider.haal_nieuws(ticker)

if data.empty:

    st.warning(
        "Voor deze asset is momenteel geen marktdata beschikbaar."
    )

    st.stop()


data = bereken_indicatoren(data)

prijs = float(data["Close"].iloc[-1])

score, marktstatus, redenen = technische_analyse(data)


# ==================================================
# 11. DASHBOARD
# ==================================================

if pagina == "🏠 Dashboard":

    naam = user["profile"]["first_name"]

    st.title(
        f"Goedemiddag {naam} 👋"
    )

    st.caption(
        f"Laatste dashboardupdate: "
        f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )

    cash = user["account"]["cash"]

    open_waarde = 0
    open_pnl = 0

    for positie in user["open_positions"]:

        positie_data = MarketDataProvider.haal_data(
            positie["ticker"]
        )

        if not positie_data.empty:

            positie_prijs = float(
                positie_data["Close"].iloc[-1]
            )

            open_waarde += (
                positie_prijs * positie["aantal"]
            )

            open_pnl += (
                (positie_prijs - positie["entry"])
                * positie["aantal"]
            )

    totale_accountwaarde = cash + open_waarde

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "💰 Virtueel Cash",
        f"€ {cash:,.2f}"
    )

    metric2.metric(
        "💼 Belegde waarde",
        f"€ {open_waarde:,.2f}"
    )

    metric3.metric(
        "📈 Open P&L",
        f"€ {open_pnl:,.2f}"
    )

    metric4.metric(
        "🏦 Totale accountwaarde",
        f"€ {totale_accountwaarde:,.2f}"
    )

    st.divider()

    left, right = st.columns([2, 1])

    with left:

        st.subheader(
            f"📊 {ticker}"
        )

        st.metric(
            "Actuele koers",
            f"{prijs:,.2f}"
        )

        chart_data = data[
            ["Close", "EMA9", "EMA21"]
        ].dropna()

        st.line_chart(chart_data)

    with right:

        st.subheader(
            "🤖 Market Intelligence"
        )

        st.metric(
            "Technische score",
            f"{score}/100"
        )

        if score >= 60:

            st.success(marktstatus)

        elif score <= 40:

            st.error(marktstatus)

        else:

            st.warning(marktstatus)

        for reden in redenen:

            st.write("•", reden)


# ==================================================
# 12. PAPER TRADING
# ==================================================

elif pagina == "🎮 Paper Trading":

    st.title("🎮 Paper Trading Terminal")

    st.info(
        "Alle orders op deze pagina gebruiken uitsluitend fictief geld."
    )

    accountwaarde = user["account"]["cash"]

    risico_percentage = st.slider(
        "Maximaal risico per trade (%)",
        0.1,
        5.0,
        1.0,
        0.1
    )

    stop_loss = st.number_input(
        "Stop-loss",
        min_value=0.01,
        value=float(prijs * 0.98)
    )

    take_profit = st.number_input(
        "Take-profit",
        min_value=0.01,
        value=float(prijs * 1.04)
    )

    risico_euro = (
        accountwaarde
        * risico_percentage
        / 100
    )

    risico_per_stuk = abs(
        prijs - stop_loss
    )

    if risico_per_stuk > 0:

        risico_aantal = int(
            risico_euro / risico_per_stuk
        )

    else:

        risico_aantal = 0

    cash_aantal = int(
        user["account"]["cash"] / prijs
    )

    aanbevolen_aantal = min(
        risico_aantal,
        cash_aantal
    )

    st.subheader(
        "🛡️ Risk Engine"
    )

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Maximaal risico",
        f"€ {risico_euro:,.2f}"
    )

    r2.metric(
        "Risico per aandeel",
        f"€ {risico_per_stuk:,.2f}"
    )

    r3.metric(
        "Maximaal aantal",
        aanbevolen_aantal
    )

    aantal = st.number_input(
        "Aantal",
        min_value=1,
        value=max(1, aanbevolen_aantal)
    )

    orderwaarde = aantal * prijs

    st.write(
        f"Orderwaarde: **€ {orderwaarde:,.2f}**"
    )

    if st.button(
        "🟢 VIRTUEEL KOPEN",
        use_container_width=True
    ):

        if orderwaarde > user["account"]["cash"]:

            st.error(
                "Onvoldoende virtueel saldo."
            )

        else:

            user["account"]["cash"] -= orderwaarde

            user["open_positions"].append({
                "ticker": ticker,
                "entry": prijs,
                "aantal": aantal,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "opened": datetime.now()
            })

            st.success(
                f"{aantal}x {ticker} virtueel gekocht."
            )

            st.rerun()


# ==================================================
# 13. PORTFOLIO
# ==================================================

elif pagina == "💼 Portfolio":

    st.title("💼 Mijn Paper Portfolio")

    if not user["open_positions"]:

        st.info(
            "Je hebt momenteel geen open posities."
        )

    for index, positie in enumerate(
        user["open_positions"]
    ):

        positie_data = MarketDataProvider.haal_data(
            positie["ticker"]
        )

        if positie_data.empty:
            continue

        actuele_prijs = float(
            positie_data["Close"].iloc[-1]
        )

        pnl = (
            actuele_prijs - positie["entry"]
        ) * positie["aantal"]

        pnl_pct = (
            (actuele_prijs / positie["entry"]) - 1
        ) * 100

        with st.container(border=True):

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                positie["ticker"],
                positie["aantal"]
            )

            c2.metric(
                "Entry",
                f"{positie['entry']:.2f}"
            )

            c3.metric(
                "Huidige prijs",
                f"{actuele_prijs:.2f}"
            )

            c4.metric(
                "P&L",
                f"€ {pnl:.2f}",
                f"{pnl_pct:.2f}%"
            )

            st.caption(
                f"Stop-loss: {positie['stop_loss']:.2f} | "
                f"Take-profit: {positie['take_profit']:.2f}"
            )

            if st.button(
                f"🔴 Sluit positie {positie['ticker']}",
                key=f"close_{index}"
            ):

                opbrengst = (
                    actuele_prijs
                    * positie["aantal"]
                )

                user["account"]["cash"] += opbrengst

                gesloten_trade = positie.copy()

                gesloten_trade.update({
                    "exit": actuele_prijs,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "closed": datetime.now()
                })

                user["trade_history"].append(
                    gesloten_trade
                )

                user["open_positions"].pop(index)

                st.rerun()


# ==================================================
# 14. AI INTELLIGENCE
# ==================================================

elif pagina == "🤖 AI Intelligence":

    st.title(
        f"🤖 AI Market Intelligence | {ticker}"
    )

    st.warning(
        "Dit is momenteel een regelgebaseerde analyse en geen externe AI-modelanalyse."
    )

    st.metric(
        "Technische score",
        f"{score}/100"
    )

    st.subheader(
        "Bullish scenario"
    )

    st.write(
        f"Wanneer {ticker} technisch boven relevante weerstand "
        f"uitbreekt met bevestigend volume, kan dit het bullish "
        f"scenario versterken."
    )

    st.subheader(
        "Neutraal scenario"
    )

    st.write(
        "Wanneer momentum en volume geen duidelijke richting tonen, "
        "blijft wachten op bevestiging een mogelijk scenario."
    )

    st.subheader(
        "Bearish scenario"
    )

    st.write(
        "Wanneer belangrijke support breekt met toenemend volume, "
        "neemt het technische neerwaartse risico toe."
    )


# ==================================================
# 15. NIEUWS
# ==================================================

elif pagina == "📰 Nieuws":

    st.title(
        f"📰 Financieel nieuws | {ticker}"
    )

    if nieuws:

        for artikel in nieuws[:15]:

            content = artikel.get(
                "content",
                artikel
            )

            titel = content.get(
                "title",
                "Geen titel"
            )

            provider = content.get(
                "provider",
                {}
            )

            publisher = provider.get(
                "displayName",
                "Onbekende bron"
            )

            link_data = content.get(
                "canonicalUrl",
                {}
            )

            link = link_data.get(
                "url",
                ""
            )

            with st.container(
                border=True
            ):

                st.subheader(titel)

                st.caption(
                    f"Bron: {publisher}"
                )

                if link:

                    st.link_button(
                        "Artikel openen",
                        link
                    )

    else:

        st.info(
            "Momenteel geen nieuws beschikbaar."
        )


# ==================================================
# 16. TRADING JOURNAL
# ==================================================

elif pagina == "📓 Trading Journal":

    st.title("📓 Trading Journal")

    if not user["trade_history"]:

        st.info(
            "Je hebt nog geen gesloten paper trades."
        )

    else:

        journal_df = pd.DataFrame(
            user["trade_history"]
        )

        st.dataframe(
            journal_df,
            use_container_width=True
        )


# ==================================================
# 17. PERFORMANCE
# ==================================================

elif pagina == "📈 Performance":

    st.title(
        "📈 Persoonlijke Trading Performance"
    )

    trades = user["trade_history"]

    if not trades:

        st.info(
            "Nog onvoldoende tradinghistorie."
        )

    else:

        winnaars = [
            x for x in trades
            if x.get("pnl", 0) > 0
        ]

        verliezers = [
            x for x in trades
            if x.get("pnl", 0) < 0
        ]

        totaal_pnl = sum(
            x.get("pnl", 0)
            for x in trades
        )

        winrate = (
            len(winnaars)
            / len(trades)
            * 100
        )

        p1, p2, p3, p4 = st.columns(4)

        p1.metric(
            "Trades",
            len(trades)
        )

        p2.metric(
            "Winrate",
            f"{winrate:.1f}%"
        )

        p3.metric(
            "Winnaars",
            len(winnaars)
        )

        p4.metric(
            "Totaal P&L",
            f"€ {totaal_pnl:,.2f}"
        )


# ==================================================
# 18. MARKETS / ANALYSE / WATCHLIST / ACADEMY
# ==================================================

elif pagina in [
    "🌍 Markets",
    "📊 Analyse",
    "⭐ Watchlist",
    "🎓 Trading Academy"
]:

    st.title(pagina)

    st.info(
        "Deze module wordt in de volgende versie verder uitgebreid."
    )


# ==================================================
# 19. ACCOUNT
# ==================================================

elif pagina == "👤 Mijn Account":

    st.title("👤 Mijn Account")

    profiel = user["profile"]

    st.write(
        f"**Naam:** "
        f"{profiel['first_name']} "
        f"{profiel['last_name']}"
    )

    st.write(
        f"**E-mail:** "
        f"{st.session_state.actieve_user}"
    )

    st.write(
        f"**Land:** "
        f"{profiel['country']}"
    )

    st.write(
        f"**Ervaringsniveau:** "
        f"{profiel['experience']}"
    )

    st.write(
        f"**Tradingstijl:** "
        f"{profiel['style']}"
    )

    st.write(
        f"**Account aangemaakt:** "
        f"{profiel['created']}"
    )


# ==================================================
# 20. DISCLAIMER
# ==================================================

st.divider()

st.caption(
    "⚠️ Global Trading Intelligence is bedoeld voor educatie, "
    "marktanalyse en paper trading. Technische signalen en "
    "scenario's vormen geen persoonlijk financieel advies en "
    "bieden geen garantie op rendement."
)
