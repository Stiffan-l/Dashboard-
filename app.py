# ==================================================
# HISTORICAL CHART LEARNING ENGINE
# ==================================================

Bouw een professionele Historical Chart Learning Engine voor minimaal
200 verschillende cryptomunten.

Het systeem moet niet alleen naar de actuele grafiek kijken.

Het systeem moet historische grafiekpatronen terugzoeken, beoordelen hoe
de prijs daarna bewoog en deze resultaten gebruiken als extra onderdeel
van het actuele paper-tradingadvies.

Gebruik hiervoor uitsluitend historische gegevens die daadwerkelijk door
de gekozen marktprovider zijn geleverd.

Verzin nooit historische koersdata.

# ==================================================
# HISTORISCHE DATA PER COIN
# ==================================================

Download per cryptomunt, wanneer beschikbaar:

- maximale dagelijkse historie;
- minimaal vijf jaar dagelijkse candles;
- twee jaar vieruurscandles;
- zestig dagen uurcandles;
- zeven dagen korte intraday candles.

Wanneer een coin nog geen vijf jaar bestaat:

gebruik alle beschikbare historie.

Toon per coin:

- eerste beschikbare koersdatum;
- laatste beschikbare koersdatum;
- aantal candles;
- ontbrekende periodes;
- databron;
- data-interval;
- datakwaliteit;
- mogelijke vertraging.

# ==================================================
# LEER DE GRAFIEK KENNEN
# ==================================================

Analyseer per coin de historische eigenschappen.

Bereken:

- gemiddelde beweging per dag;
- gemiddelde beweging per week;
- gemiddelde beweging per maand;
- gemiddelde positieve dag;
- gemiddelde negatieve dag;
- grootste dagelijkse stijging;
- grootste dagelijkse daling;
- jaarlijkse volatiliteit;
- rolling volatility;
- maximum drawdown;
- gemiddelde drawdown;
- gemiddelde hersteltijd na een drawdown;
- percentage positieve dagen;
- percentage negatieve dagen;
- gemiddelde stijging tijdens een uptrend;
- gemiddelde daling tijdens een downtrend;
- gemiddelde duur van een trend;
- gemiddelde duur van een consolidatie;
- volume tijdens stijgingen;
- volume tijdens dalingen;
- reactie op volume-uitbraken;
- reactie op volatility spikes;
- afstand tot all-time high;
- afstand tot 52-weeks high;
- afstand tot 52-weeks low.

# ==================================================
# HISTORISCHE TRENDCLASSIFICATIE
# ==================================================

Classificeer iedere historische candleperiode als:

STRONG UPTREND
UPTREND
BULLISH CONSOLIDATION
RANGE
BEARISH CONSOLIDATION
DOWNTREND
STRONG DOWNTREND
CAPITULATION
VOLATILITY EXPANSION
VOLATILITY CONTRACTION

Gebruik hiervoor:

- koersstructuur;
- hogere toppen;
- hogere bodems;
- lagere toppen;
- lagere bodems;
- EMA9;
- EMA21;
- EMA50;
- EMA200;
- SMA50;
- SMA200;
- MACD;
- RSI;
- ATR;
- Bollinger Band width;
- volume ratio;
- rolling volatility.

# ==================================================
# HISTORISCHE PATROONBIBLIOTHEEK
# ==================================================

Herken en test minimaal:

- EMA9 kruist EMA21 omhoog;
- EMA9 kruist EMA21 omlaag;
- EMA21 kruist EMA50 omhoog;
- EMA21 kruist EMA50 omlaag;
- SMA50 kruist SMA200 omhoog;
- SMA50 kruist SMA200 omlaag;
- RSI daalt onder 30;
- RSI stijgt boven 70;
- RSI verlaat oversold gebied;
- RSI verlaat overbought gebied;
- bullish MACD crossover;
- bearish MACD crossover;
- Bollinger lower-band touch;
- Bollinger upper-band touch;
- Bollinger squeeze;
- volume breakout;
- resistance breakout;
- support breakdown;
- support bounce;
- resistance rejection;
- trend pullback;
- higher-high breakout;
- lower-low breakdown;
- bullish divergence;
- bearish divergence;
- volatility spike;
- capitulation candle;
- bullish engulfing;
- bearish engulfing;
- hammer;
- shooting star;
- morning star;
- evening star;
- inside bar;
- outside bar;
- double bottom;
- double top;
- ascending triangle;
- descending triangle;
- range breakout.

Geef geen patroon weer wanneer de detectie onvoldoende betrouwbaar is.

# ==================================================
# CONTEXT VAN EEN PATROON
# ==================================================

Behandel hetzelfde patroon niet altijd hetzelfde.

Sla bij ieder historisch patroon ook op:

- marktregime;
- bitcointrend;
- cryptomarkttrend;
- volume ratio;
- voorafgaande trend;
- volatiliteit;
- RSI;
- MACD;
- afstand tot support;
- afstand tot resistance;
- afstand tot EMA200;
- dag van de week;
- maand;
- nieuwsstatus indien beschikbaar.

Een bullish engulfing candle in een sterke downtrend moet anders worden
beoordeeld dan een bullish engulfing candle tijdens een bevestigde uptrend.

# ==================================================
# WAT GEBEURDE ER DAARNA?
# ==================================================

Bereken per historische setup de koersreactie na:

- 1 candle;
- 3 candles;
- 5 candles;
- 10 candles;
- 20 candles;
- 50 candles.

Bereken voor iedere horizon:

- gemiddeld rendement;
- mediaan rendement;
- positief resultaatpercentage;
- negatief resultaatpercentage;
- beste uitkomst;
- slechtste uitkomst;
- standaarddeviatie;
- maximum favorable excursion;
- maximum adverse excursion;
- gemiddelde drawdown na het signaal;
- gemiddelde tijd tot target;
- gemiddelde tijd tot stop-loss.

# ==================================================
# HISTORISCHE VERGELIJKING VAN HUIDIGE SETUP
# ==================================================

Maak een functie:

find_similar_historical_setups()

De functie vergelijkt de huidige grafieksituatie met historische situaties
van dezelfde coin.

Gebruik minimaal:

- trend;
- EMA-verhoudingen;
- SMA-verhoudingen;
- RSI;
- MACD;
- ATR;
- volume ratio;
- volatiliteit;
- supportafstand;
- resistanceafstand;
- recente rendementen;
- candlepatroon.

Bereken een similarity score tussen 0 en 100.

Gebruik alleen historische voorbeelden met:

similarity_score >= 75

Toon:

- aantal vergelijkbare situaties;
- gemiddelde similarity;
- gemiddelde reactie na 1 dag;
- gemiddelde reactie na 3 dagen;
- gemiddelde reactie na 7 dagen;
- gemiddelde reactie na 14 dagen;
- mediaan;
- positief percentage;
- negatief percentage;
- beste uitkomst;
- slechtste uitkomst;
- gemiddelde maximum drawdown.

# ==================================================
# MINIMALE STEEKPROEF
# ==================================================

Gebruik geen hard historisch advies bij minder dan vijf vergelijkbare situaties.

Gebruik classificatie:

0-4 voorbeelden:
ONVOLDOENDE HISTORISCHE DATA

5-9 voorbeelden:
ZEER LAGE HISTORISCHE BETROUWBAARHEID

10-19 voorbeelden:
LAGE HISTORISCHE BETROUWBAARHEID

20-49 voorbeelden:
REDELIJKE HISTORISCHE BETROUWBAARHEID

50 of meer:
HOGERE HISTORISCHE BETROUWBAARHEID

Ook 50 voorbeelden bieden geen garantie.

# ==================================================
# VOORKOM LOOK-AHEAD BIAS
# ==================================================

Zeer belangrijk:

Bij het genereren van een historisch signaal mag het systeem uitsluitend
informatie gebruiken die op dat historische moment beschikbaar was.

Het systeem mag toekomstige candles alleen gebruiken voor het meten van
de latere uitkomst.

Het systeem mag toekomstige data nooit gebruiken bij:

- patroondetectie;
- indicatorberekening;
- support/resistance op het signaalmoment;
- trendclassificatie;
- setupscore;
- nieuwsclassificatie.

# ==================================================
# WALK-FORWARD VALIDATIE
# ==================================================

Verdeel historische data chronologisch.

Gebruik bijvoorbeeld:

60% training
20% validation
20% out-of-sample test

Of rolling walk-forward windows.

Optimaliseer geen regels op de out-of-sample periode.

Toon resultaten afzonderlijk voor:

TRAINING
VALIDATION
OUT-OF-SAMPLE

Wanneer training goed scoort maar out-of-sample slecht:

classificeer de strategie als:

MOGELIJK OVERFIT

Gebruik een mogelijk overfit model niet voor een sterk paper-buyadvies.

# ==================================================
# HISTORISCHE SCORE
# ==================================================

Bereken een Historical Setup Score van 0 tot 100.

Gebruik:

- steekproefgrootte;
- similarity;
- positief resultaatpercentage;
- mediaan rendement;
- gemiddelde adverse excursion;
- maximum drawdown;
- out-of-sample prestatie;
- stabiliteit over verschillende marktregimes;
- recency van vergelijkbare patronen.

De Historical Setup Score vormt maximaal 15% van de totale adviesscore.

Historische resultaten mogen nooit het volledige advies bepalen.

# ==================================================
# CRYPTO-SPECIFIEKE ADVIESENGINE
# ==================================================

Maak voor crypto een afzonderlijke score-engine.

Weging:

Trend Score:
20%

Momentum Score:
15%

Volume/Liquidity Score:
15%

Volatility/Risk Score:
10%

Support/Resistance Score:
10%

Historical Setup Score:
15%

Bitcoin Market Regime:
5%

News Score:
5%

Data Quality:
5%

Totaal:
100%

Gebruik niet hetzelfde scoremodel voor aandelen en crypto.

# ==================================================
# BITCOIN MARKTREGIME
# ==================================================

Veel altcoins bewegen mee met bitcoin.

Bereken daarom voor iedere altcoin:

- correlatie met bitcoin over 30 dagen;
- correlatie over 90 dagen;
- beta ten opzichte van bitcoin;
- relatieve sterkte tegenover bitcoin;
- coin/BTC-trend indien beschikbaar.

Classificeer bitcoin als:

BITCOIN STRONG BULL
BITCOIN BULL
BITCOIN NEUTRAL
BITCOIN BEAR
BITCOIN STRONG BEAR

Een altcoin krijgt geen STRONG PAPER BUY wanneer:

- bitcoin in een sterke beartrend zit;
- altcoinliquiditeit laag is;
- datakwaliteit onvoldoende is;
- risk/reward onvoldoende is.

# ==================================================
# ADVIES PER COIN
# ==================================================

Toon per coin:

ACTUEEL ADVIES

Mogelijke statussen:

STRONG PAPER BUY
PAPER BUY
EARLY BUY WATCH
WAIT FOR CONFIRMATION
HOLD
PROTECT PAPER PROFIT
TAKE PARTIAL PAPER PROFIT
TIGHTEN STOP
REDUCE PAPER POSITION
PAPER SELL
STRONG PAPER SELL
NO TRADE
INSUFFICIENT DATA

Toon vervolgens:

- Total Score;
- Historical Setup Score;
- Trend Score;
- Momentum Score;
- Volume Score;
- Risk Score;
- News Score;
- Bitcoin Regime Score;
- Data Quality;
- Confidence;
- Trade Grade.

# ==================================================
# CONCREET PAPER-TRADEPLAN
# ==================================================

Bij een geldige setup:

- actuele koers;
- ideale entryzone;
- breakout-entry;
- pullback-entry;
- stop-loss;
- trailing-stopafstand;
- take-profit 1;
- take-profit 2;
- take-profit 3;
- risk/reward;
- paper-aantal;
- maximale paper-inzet;
- maximaal verlies;
- setup geldig tot;
- setup ongeldig wanneer.

De knop mag uitsluitend een paper-orderticket vullen.

Voer nooit automatisch een order uit.

# ==================================================
# WAAROM DIT ADVIES?
# ==================================================

Schrijf een begrijpelijke uitleg.

Voorbeeld:

PAPER BUY SETUP

De korte en middellange trend zijn positief. EMA9 ligt boven EMA21 en
EMA21 ligt boven EMA50. MACD ondersteunt de trend en het volume ligt
1,6 keer boven het twintigdaagse gemiddelde.

Het systeem vond 34 historisch vergelijkbare situaties voor deze coin.
In 22 van de 34 gevallen stond de koers na zeven dagen hoger. Het
mediane rendement bedroeg 3,1%, maar de slechtste uitkomst was -11,4%.

De setup wordt ongeldig wanneer de koers onder de aangegeven support en
stop-loss sluit.

# ==================================================
# TEGENARGUMENTEN
# ==================================================

Toon altijd een afzonderlijk blok:

WAAROM NIET INSTAPPEN?

Voorbeelden:

- bitcointrend is zwak;
- volume neemt af;
- koers ligt dicht bij sterke resistance;
- volatiliteit is extreem;
- historische vergelijkingen waren instabiel;
- weinig vergelijkbare voorbeelden;
- nieuwsrisico;
- risk/reward onvoldoende;
- coin heeft beperkte liquiditeit.

Een advies zonder tegenargumenten is niet toegestaan.

# ==================================================
# CHART EDUCATION MODE
# ==================================================

Voeg een knop toe:

LEER DEZE GRAFIEK KENNEN

Wanneer geactiveerd, leg stap voor stap uit:

1. Wat is de huidige trend?
2. Waar zijn hogere toppen en bodems?
3. Waar liggen support en resistance?
4. Wat tonen EMA9, EMA21 en EMA50?
5. Wat toont RSI?
6. Wat toont MACD?
7. Wat doet het volume?
8. Hoe hoog is de volatiliteit?
9. Welk patroon is mogelijk zichtbaar?
10. Wat gebeurde historisch bij vergelijkbare patronen?
11. Welke bevestiging ontbreekt?
12. Wanneer is de analyse ongeldig?

Gebruik eenvoudige Nederlandse taal.

# ==================================================
# CANDLE UITLEG
# ==================================================

Wanneer gebruiker een candle selecteert:

toon:

- openingsprijs;
- hoogste prijs;
- laagste prijs;
- sluitingsprijs;
- procentuele verandering;
- volume;
- body size;
- upper wick;
- lower wick;
- candle-classificatie;
- positie binnen de trend.

Leg uit wat de candle mogelijk betekent, zonder zekerheid te claimen.

# ==================================================
# HISTORISCHE SETUPS VISUALISEREN
# ==================================================

Laat gebruiker historische voorbeelden bekijken.

Toon per voorbeeld:

- datum;
- grafiek rondom het signaal;
- indicatorwaarden;
- similarity score;
- resultaat na 1/3/5/10/20 candles;
- maximum favorable excursion;
- maximum adverse excursion.

Markeer:

ENTRY
STOP
TARGET
OUTCOME

# ==================================================
# ADVIESCONTROLER
# ==================================================

Bouw een onafhankelijke Recommendation Validator.

Deze validator controleert vóór publicatie van ieder advies:

- voldoende historische data;
- geldige actuele koers;
- indicatoren beschikbaar;
- geen NaN;
- geen Infinity;
- redelijke liquiditeit;
- datakwaliteit;
- risk/reward;
- historische steekproef;
- bitcoinregime;
- extreme volatiliteit;
- nieuwsrisico;
- portefeuillelimiet.

Wanneer één kritieke controle faalt:

verlaag het advies naar:

WAIT FOR CONFIRMATION
NO TRADE
INSUFFICIENT DATA

# ==================================================
# ADVIES TERUGCONTROLEREN
# ==================================================

Sla ieder advies permanent op.

Controleer later automatisch wat er gebeurde na:

- 1 dag;
- 3 dagen;
- 7 dagen;
- 14 dagen;
- 30 dagen.

Bereken:

- richting correct of niet;
- rendement;
- maximum drawdown;
- target bereikt;
- stop-loss bereikt;
- tijd tot target;
- tijd tot stop.

Toon op Performance:

HOE GOED WAREN DE ADVIEZEN?

- totaal aantal adviezen;
- aantal buy-signalen;
- aantal sell-signalen;
- richting correct na 7 dagen;
- gemiddelde uitkomst;
- mediaan;
- beste signaal;
- slechtste signaal;
- resultaat per coin;
- resultaat per setup;
- resultaat per marktregime.

# ==================================================
# ZELFLERENDE GEWICHTEN MET GRENZEN
# ==================================================

Laat het systeem de scoregewichten voorzichtig aanpassen op basis van
out-of-sample resultaten.

Gebruik beperkingen:

- geen gewicht lager dan 5%;
- geen dominant gewicht hoger dan 25%;
- alleen aanpassen na minimaal 100 geëvalueerde signalen;
- maximaal 2 procentpunt verandering per evaluatie;
- oude en nieuwe gewichten opslaan;
- mogelijkheid om terug te keren naar standaardgewichten.

Gebruik geen onbeperkt zelflerend model.

# ==================================================
# BELANGRIJKE UITKOMST
# ==================================================

De website moet dus niet zeggen:

“Deze coin stijgt.”

De website moet zeggen:

“De huidige situatie lijkt op 34 eerdere situaties. In 65% van die
gevallen stond de koers na zeven dagen hoger. De spreiding was groot en
de slechtste historische uitkomst bedroeg -11,4%. De huidige setup heeft
een score van 78/100 en wordt uitsluitend als PAPER BUY geclassificeerd.”

# ==================================================
# DISCLAIMER
# ==================================================

Toon permanent:

Historische grafiekpatronen en eerdere koersreacties voorspellen geen
toekomstige resultaten. De analyse is uitsluitend bedoeld voor
educatie en paper trading. Cryptomarkten kunnen zeer snel en sterk
bewegen. Een stop-loss kan bij sterke volatiliteit tegen een minder
gunstige prijs worden uitgevoerd.
