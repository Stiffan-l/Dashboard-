import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# ==================================================
# 1. INITIALISATIE & DATABASE GEHEUGEN (PERSISTENT PER SESSIE)
# ==================================================
if 'gebruikers_db' not in st.session_state:
    st.session_state.gebruikers_db = {}
if 'actieve_user' not in st.session_state:
    st.session_state.actieve_user = None

# ==================================================
# 2. MEERTALIGHEID MATRIX (NEDERLANDS & ENGELS)
# ==================================================
VERTALINGEN = {
    'NL': {
        'title': "GLOBAL TRADING INTELLIGENCE",
        'subtitle': "V1 Professional Paper Trading & AI Market Intelligence Platform",
        'cash': "Virtueel Cash",
        'invested': "Belegde Waarde",
        'open_pnl': "Open P&L",
        'total_acc': "Totaal Account",
        'winrate': "Winrate",
        'risk_engine': "Risicomanagement Engine",
        'order_ticket': "Broker Order Ticket",
        'ai_intel': "AI Markt Intelligence & Scenario Matrix",
        'journal': "Persistent Trading Journal & Prestaties",
        'watchlist': "Mijn Watchlists",
        'logout': "Veilig Uitloggen",
        'login': "Inloggen op je Account",
        'register': "Nieuw Account Registreren",
        'profile_page': "Mijn Persoonlijk Profiel",
        'economic_cal': "Macro-Economische Kalender",
        'market_floor': "Wereldwijde Handelsvloer"
    },
    'EN': {
        'title': "GLOBAL TRADING INTELLIGENCE",
        'subtitle': "V1 Professional Paper Trading & AI Market Intelligence Platform",
        'cash': "Virtual Cash",
        'invested': "Invested Value",
        'open_pnl': "Open P&L",
        'total_acc': "Total Account",
        'winrate': "Win Rate",
        'risk_engine': "Risk Management Engine",
        'order_ticket': "Broker Order Ticket",
        'ai_intel': "AI Market Intelligence & Scenario Matrix",
        'journal': "Persistent Trading Journal & Analytics",
        'watchlist': "My Watchlists",
        'logout': "Secure Logout",
        'login': "Account Login",
        'register': "Register New Account",
        'profile_page': "My Personal Profile",
        'economic_cal': "Macro-Economic Calendar",
        'market_floor': "Global Trading Floor"
    }
}

# PAGINA INSTELLINGEN
st.set_page_config(page_title="GLOBAL TRADING INTELLIGENCE v1.0", layout="wide")

# Autorefresh trigger per run
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0
st.session_state.refresh_counter += 1

# ==================================================
# 3. ABSTRACTE PROVIDER-LAAG (MARKET, NEWS, AI)
# ==================================================
class MarketDataProvider:
    @staticmethod
    def haal_koers_en_nieuws(ticker):
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1d", interval="1m")
            return df, t.news if t.news else []
        except:
            return pd.DataFrame(), []

class AIProvider:
    @staticmethod
    def genereer_markt_analyse(ticker, huidige_prijs, trend, history_data):
        bullish = huidige_prijs * 1.045
        bearish = huidige_prijs * 0.952
        fout_tekst = "Je sluit winstgevende trades gemiddeld 12% te vroeg uit angst voor omdraaiingen. Houd strakker vast aan je take-profit targets."
        if len(history_data) > 2:
            verliezen = [t for t in history_data if t['pnl'] < 0]
            if len(verliezen) > 1:
                fout_tekst = "AI Analyse waarschuwing: Je hebt meerdere verliezen achter elkaar geleden door 'wraaktraden'. Neem rust na een verliesgevende trade."
        return {
            "scenario": f"AI Analyse voor {ticker}: De markt vertoont momenteel een {trend} momentum.",
            "bullish": f"{bullish:.4f}. Structuur toont institutionele kooporders op support.",
            "bearish": f"{bearish:.4f}. Risico op liquidatie bij breken van de daggrafiek support.",
            "fouten_analyse": fout_tekst
        }

# ==================================================
# 4. REGISTRATIE & ACCOUNT INLOGSYSTEEM
# ==================================================
def toon_auth_scherm():
    st.title("🌐 GLOBAL TRADING INTELLIGENCE")2
    st.caption("V1 Professional Paper Trading & AI Market Intelligence Platform")
    
    tab1, tab2 = st.tabs(["🔐 Inloggen", "📝 Registreren"])
    
    with tab1:
        st.subheader("Veilig Inloggen")
        login_email = st.text_input("E-mailadres", key="auth_email")
        login_pass = st.text_input("Wachtwoord", type="password", key="auth_pass")
        
        if st.button("Inloggen", use_container_width=True):
            if login_email in st.session_state.gebruikers_db and st.session_state.gebruikers_db[login_email]['password'] == login_pass:
                st.session_state.actieve_user = login_email
                st.success("Sessie succesvol geverifieerd! Je dashboard wordt geladen...")
                st.rerun()
            else:
                st.error("Transactie geweigerd: Onjuist e-mailadres of wachtwoord.")
                
    with tab2:
        st.subheader("Account Aanmaken")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            v_naam = st.text_input("Voornaam")
            a_naam = st.text_input("Achternaam")
            reg_email = st.text_input("E-mailadres")
            reg_pass = st.text_input("Wachtwoord", type="password")
            reg_pass_conf = st.text_input("Wachtwoord Bevestigen", type="password")
        with col_r2:
            land = st.selectbox("Land", ["Nederland", "België", "Duitsland", "Verenigde Staten"])
            tijdzone = st.selectbox("Tijdzone", ["Europe/Amsterdam", "Europe/London", "America/New_York"])
            taal = st.selectbox("Voorkeurstaal", ["NL", "EN"])
            valuta = st.selectbox("Standaardvaluta", ["EUR (€)", "USD ($)"])
            ervaring = st.selectbox("Ervaringsniveau", ["Volledig beginner", "Beginner", "Gemiddeld", "Ervaren"])
            stijl = st.selectbox("Tradingstijl", ["Scalping", "Daytrading", "Swingtrading", "Position trading", "Lange termijn analyse"])
            
        startkapitaal_keuze = st.selectbox("Kies Virtueel Startkapitaal", ["1000", "2500", "5000", "10000", "25000", "50000", "100000"])
        
        c1 = st.checkbox("Ik ga akkoord met de Algemene voorwaarden en Privacyvoorwaarden")
        c2 = st.checkbox("Ik begrijp dat dit platform GEEN financieel advies geeft")
        c3 = st.checkbox("Ik begrijp dat paper trading fictief geld gebruikt")
        
        if st.button("Account Registreren", use_container_width=True):
            if reg_pass != reg_pass_conf:
                st.error("Wachtwoorden komen niet overeen.")
            elif not (c1 and c2 and c3):
                st.error("Je dient akkoord te gaan met alle voorwaarden.")
            elif reg_email in st.session_state.gebruikers_db:
                st.error("Dit e-mailadres is al geregistreerd.")
            elif reg_email and reg_pass:
                st.session_state.gebruikers_db[reg_email] = {
                    "password": reg_pass,
                    "profile": {
                        "first_name": v_naam, "last_name": a_naam, "country": land, 
                        "timezone": tijdzone, "lang": taal, "currency": valuta, 
                        "experience": ervaring, "style": stijl, "created_at": datetime.now().strftime("%Y-%m-%d")
                    },
                    "account": {
                        "cash": float(startkapitaal_keuze), "invested": 0.0, "initial": float(startkapitaal_keuze)
                    },
                    "open_positions": [],
                    "trade_history": [],
                    "watchlist": ["ASML.AS", "BTC-USD", "AAPL", "EURUSD=X"]
                }
                st.success("Registratie voltooid! Log nu in via het linker tabblad.")
            else:
                st.error("Vul alle verplichte velden in.")

if st.session_state.actieve_user is None:
    toon_auth_scherm()
    st.stop()

# ==================================================
# 5. DATA MANAGEMENT & SESSIE-VERWERKING
# ==================================================
user_data = st.session_state.gebruikers_db[st.session_state.actieve_user]
lang = user_data['profile']['lang']
t = VERTALINGEN[lang]

# Top Navigatiebalk van het Platform
st.title(f"🌐 {t['title']} — v1.0 Pro")
col_header1, col_header2 = st.columns()
with col_header1:
    st.caption(f"{t['subtitle']}  |  Sessie: {st.session_state.actieve_user}  |  Systeem Tijd: {datetime.now().strftime('%H:%M:%S')}")
with col_header2:
    if st.button(t['logout'], use_container_width=True):
        st.session_state.actieve_user = None
        st.rerun()

st.markdown("---")

# ==================================================
# 6. SIDEBAR: WATCHLIST MANAGEMENT & SCANNERS
# ==================================================
st.sidebar.header(t['watchlist'])
nieuwe_asset = st.sidebar.text_input("Voeg Ticker toe (bijv. TSLA, NVDA)", value="").upper()
if st.sidebar.button("Toevoegen") and nieuwe_asset:
    if nieuwe_asset not in user_data['watchlist']:
        user_data['watchlist'].append(nieuwe_asset)
        st.rerun()

ticker_keuze = st.sidebar.radio("Selecteer Actief Product", user_data['watchlist'])

if st.sidebar.button("Verwijder Ticker uit Watchlist"):
    if ticker_keuze in user_data['watchlist']:
        user_data['watchlist'].remove(ticker_keuze)
        st.rerun()

# Haal live marktdata op via de abstracte provider
market_data, live_news = MarketDataProvider.haal_koers_en_nieuws(ticker_keuze)

if market_data.empty:
    st.error("Wachten op live marktdata-stream... Kies buiten beurstijden een Crypto-asset (zoals BTC-USD) om de tickers live te zien bewegen.")
    st.stop()

huidige_prijs = market_data['Close'].iloc[-1]
open_prijs = market_data['Open'].iloc[0]
procent_verschil = ((huidige_prijs - open_prijs) / open_prijs) * 100

