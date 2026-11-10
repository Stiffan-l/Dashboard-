import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Realtime timer: Update de pagina automatisch ELKE SECONDE
st_autorefresh(interval=1000, limit=10000, key="trading_dashboard_refresh")

st.set_page_config(page_title="🚀 REALTIME Trading Engine + Paper Trading", layout="wide")

# ==========================================
# RECHTEN & LIVE SESSIONS (NEP GELD PORTFOLIO)
# ==========================================
# We maken een virtuele bankrekening aan in het geheugen van de website
if 'nep_geld_balans' not in st.session_state:
    st.session_state.nep_geld_balans = 10000.0  # Je start met € 10.000,- nep geld
if 'actieve_trades' not in st.session_state:
    st.session_state.actieve_trades = []  # Lijst met open posities
if 'gesloten_trades' not in st.session_state:
    st.session_state.gesloten_trades = []  # Geschiedenis voor je logboek

# Bovenbalk Dashboard
st.title("🚀 Realtime Engine & Paper Trading Simulator")
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    st.metric("💰 Virtueel Saldo (Nep Geld)", f"€ {st.session_state.nep_geld_balans:.2f}")
with col_b2:
    st.info(f"🕒 Systeem Tijd: {datetime.now().strftime('%H:%M:%S')}")
with col_b3:
    st.success(f"📈 Open Posities: {len(st.session_state.actieve_trades)}")

st.markdown("---")

# ==========================================
# SIDEBAR: INSTELLINGEN & ASSET SELECTIE
# ==========================================
st.sidebar.header("⚙️ Simulator Instellingen")
risico_percentage = st.sidebar.slider("Risico per trade voor berekening (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
max_risico_euro = st.session_state.nep_geld_balans * (risico_percentage / 100.0)

st.sidebar.markdown("---")
markt_keuze = st.sidebar.selectbox("Kies Handelsvloer", ["AEX Aandelen (Europa)", "US Tech (VS)", "Crypto Markten"])
markten = {
    "AEX Aandelen (Europa)": ["ASML.AS", "SHELL.AS", "INGA.AS"],
    "US Tech (VS)": ["AAPL", "MSFT", "NVDA"],
    "Crypto Markten": ["BTC-USD", "ETH-USD"]
}
ticker_keuze = st.sidebar.selectbox("Selecteer Asset", markten[markt_keuze])

# Reset knop voor het nep geld
if st.sidebar.button("🔄 Reset Simulator naar € 10.000"):
    st.session_state.nep_geld_balans = 10000.0
    st.session_state.actieve_trades = []
    st.session_state.gesloten_trades = []
    st.rerun()

# ==========================================
# ENGINE: LIVE DATA OPHALEN
# ==========================================
@st.cache_data(ttl=1)
def haal_data(ticker):
    return yf.Ticker(ticker).history(period="1d", interval="1m")

data = haal_data(ticker_keuze)

if data.empty:
    st.error("Wachten op live marktdata... Kies buiten beurstijden een Crypto-asset.")
    st.stop()

huidige_prijs = data['Close'].iloc[-1]

# Berekening simpele indicatoren voor robot advies
data['MA10'] = data['Close'].rolling(window=10).mean()
data['STD'] = data['Close'].rolling(window=10).std()
live_lower = data['MA10'].iloc[-1] - (data['STD'].iloc[-1] * 1.5) if not data['STD'].empty else huidige_prijs

# Automatische stop-loss berekening voor de trade simulator
voorgestelde_stoploss = live_lower if live_lower < huidige_prijs else huidige_prijs * 0.99
verlies_per_stuk = huidige_prijs - voorgestelde_stoploss
aantal_stuks_advies = int(max_risico_euro / verlies_per_stuk) if verlies_per_stuk > 0 else 1

# ==========================================
# INTERFACE: LIVE TRADING VLOER
# ==========================================
col_grafiek, col_actie = st.columns([1.5, 1])

with col_grafiek:
    st.header(f"📊 Live Koers: {ticker_keuze}")
    valuta = "$" if "USD" in ticker_keuze or markt_keuze == "US Tech (VS)" else "€"
    st.metric("Actuele Prijs", f"{valuta} {huidige_prijs:.2f}")
    st.line_chart(data['Close'].tail(30))

with col_actie:
    st.header("🎮 Test met Nep Geld (Paper Trade)")
    st.write(f"Koop virtueel **{ticker_keuze}** op de huidige live prijs.")
    
    aantal_stuks_inzet = st.number_input("Aantal stuks om te testen", min_value=1, value=max(1, aantal_stuks_advies))
    totale_kosten = aantal_stuks_inzet * huidige_prijs
    
    st.write(f"Totale virtuele inzet: {valuta} {totale_kosten:.2f}")
    
    # KOOP KNOP (Virtueel instappen)
    if st.button("🟢 PLAATS VIRTUELE KOOP ORDER", use_container_width=True):
        if totale_kosten > st.session_state.nep_geld_balans:
            st.error("Onvoldoende nep geld saldo voor deze order!")
        else:
            # Sla de actieve trade op
            nieuwe_trade = {
                "ticker": ticker_keuze,
                "instapprijs": huidige_prijs,
                "aantal": aantal_stuks_inzet,
                "tijd": datetime.now().strftime("%H:%M:%S"),
                "valuta": valuta
            }
            st.session_state.actieve_trades.append(nieuwe_trade)
            st.session_state.nep_geld_balans -= totale_kosten
            st.success(f"Succesvol gekocht: {aantal_stuks_inzet}x {ticker_keuze} op {valuta}{huidige_prijs:.2f}!")
            st.rerun()

# ==========================================
# ONDERKANT: OPEN POSITIES BIJHOUDEN
# ==========================================
st.markdown("---")
st.header("💼 Jouw Open Test-Trades (Realtime P&L)")

if len(st.session_state.actieve_trades) == 0:
    st.caption("Je hebt momenteel geen open test-trades lopen. Klik hierboven op de koop-knop om te testen.")
else:
    # We tonen elke open trade en berekenen ELKE SECONDE de live winst of het verlies
    for i, trade in enumerate(st.session_state.actieve_trades):
        v = trade['valuta']
        actuele_waarde = aantal_stuks_inzet * huidige_prijs if trade['ticker'] == ticker_keuze else trade['aantal'] * trade['instapprijs'] # Simpele live check
        
        # Als we naar de actuele ticker kijken, berekenen we de échte live winst/verlies
        if trade['ticker'] == ticker_keuze:
            winst_verlies = (huidige_prijs - trade['instapprijs']) * trade['aantal']
        else:
            winst_verlies = 0.0  # Standby voor andere tickers tot je ze selecteert
            
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.write(f"**{trade['ticker']}** ({trade['aantal']} stuks)")
        with col_t2:
            st.write(f"Inkoop: {v}{trade['instapprijs']:.2f}")
        with col_t3:
            if winst_verlies >= 0:
                st.write(f"📈 Live Resultaat: :green[+{v}{winst_verlies:.2f}]")
            else:
                st.write(f"📉 Live Resultaat: :red[-{v}{abs(winst_verlies):.2f}]")
        with col_t4:
            # VERKOOP KNOP (Virtueel winst of verlies nemen)
            if st.button(f"🔴 Sluit Trade #{i+1}", key=f"sluit_{i}"):
                opbrengst = trade['aantal'] * huidige_prijs if trade['ticker'] == ticker_keuze else trade['aantal'] * trade['instapprijs']
                st.session_state.nep_geld_balans += opbrengst
                
                # Opslaan in geschiedenis
                trade['uitstapprijs'] = huidige_prijs if trade['ticker'] == ticker_keuze else trade['instapprijs']
                trade['resultaat'] = winst_verlies
                st.session_state.gesloten_trades.append(trade)
                
                st.session_state.actieve_trades.pop(i)
                st.success("Trade succesvol gesloten!")
                st.rerun()

# Geschiedenis tonen (Jouw ingebouwde Excel/Logboek op het scherm)
if st.session_state.gesloten_trades:
    st.subheader("📜 Gesloten Test-Trades (Geschiedenis)")
    st.write(pd.DataFrame(st.session_state.gesloten_trades))
