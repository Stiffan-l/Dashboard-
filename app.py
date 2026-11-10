BOUW EEN VOLLEDIG PROFESSIONEEL ONLINE TRADINGPLATFORM

Naam:
GLOBAL TRADING INTELLIGENCE

Versie:
V1 Professional Paper Trading & AI Market Intelligence Platform

TAAL
De volledige gebruikersinterface moet standaard Nederlands zijn.
Maak Engels als tweede taal beschikbaar.

==================================================
1. HOOFDDOEL
==================================================

Bouw een zeer uitgebreid persoonlijk tradingplatform waarmee een gebruiker:

- Een eigen account kan aanmaken
- Veilig kan inloggen en uitloggen
- Een persoonlijk profiel heeft
- Instellingen permanent kan opslaan
- Een eigen virtueel handelsaccount heeft
- Met nepgeld kan oefenen
- Paper trades permanent kan bewaren
- Na opnieuw inloggen exact verdergaat waar hij gebleven was
- Wereldwijde financiële markten kan volgen
- Aandelen kan analyseren
- Crypto kan analyseren
- Forex kan analyseren
- ETF's, indexen en grondstoffen kan volgen
- Watchlists kan maken
- Live of vertraagde koersen kan bekijken
- Financieel nieuws kan bekijken
- Een economische kalender kan volgen
- Technische analyses kan uitvoeren
- AI-marktanalyses kan laten genereren
- Bullish, neutrale en bearish scenario's kan bekijken
- Risico kan laten berekenen
- Virtuele stop-loss en take-profitorders kan instellen
- Een uitgebreid tradingjournal kan bijhouden
- Zijn persoonlijke prestaties kan analyseren
- Kan leren van eerdere trades
- AI kan laten analyseren welke fouten hij vaak maakt

BELANGRIJK:

Het programma moet NIET werken als een tijdelijke sessie.

Alle belangrijke gebruikersgegevens moeten permanent in een database worden opgeslagen.

Wanneer een gebruiker vandaag €10.000 virtueel startkapitaal heeft, 3 paper trades uitvoert, vervolgens uitlogt en een week later opnieuw inlogt, moeten:

- zijn actuele saldo;
- open posities;
- eerdere trades;
- orderhistorie;
- watchlists;
- instellingen;
- journal;
- alerts;
- statistieken;
- AI-analyses;

nog gewoon aanwezig zijn.

==================================================
2. TECHNISCHE ARCHITECTUUR
==================================================

Gebruik een professionele moderne architectuur.

Frontend:
- Next.js
- TypeScript
- Tailwind CSS

Backend:
- Next.js server actions/API-routes of FastAPI

Database:
- Supabase PostgreSQL

Authenticatie:
- Supabase Auth

Grafieken:
- TradingView Lightweight Charts

Hosting:
- Vercel

Database hosting:
- Supabase

Marktdata:
Bouw een abstracte MarketDataProvider zodat later verschillende API-providers kunnen worden gekoppeld.

Nieuws:
Bouw een NewsProvider-architectuur zodat meerdere nieuws-API's tegelijk kunnen worden gebruikt.

AI:
Bouw een AIProvider-laag zodat een taalmodel-API kan worden aangesloten.

Caching:
Gebruik server-side caching waar noodzakelijk.

Alle API-keys moeten in environment variables staan.

NOOIT API-keys in frontendcode opslaan.

==================================================
3. ACCOUNT AANMAKEN
==================================================

Bouw een volledige registratiepagina.

Nieuwe gebruiker vult in:

- Voornaam
- Achternaam
- E-mailadres
- Wachtwoord
- Wachtwoord bevestigen
- Land
- Tijdzone
- Voorkeurstaal
- Standaardvaluta
- Ervaringsniveau

Ervaringsniveau:

- Volledig beginner
- Beginner
- Gemiddeld
- Ervaren

Laat de gebruiker akkoord gaan met:

[ ] Algemene voorwaarden
[ ] Privacyvoorwaarden
[ ] Ik begrijp dat dit platform geen financieel advies geeft
[ ] Ik begrijp dat paper trading fictief geld gebruikt

Voeg e-mailverificatie toe.

==================================================
4. INLOGSYSTEEM
==================================================

Bouw:

- Inloggen
- Uitloggen
- Wachtwoord vergeten
- Wachtwoord opnieuw instellen
- E-mailadres verifiëren
- Account verwijderen
- Sessiebeheer

Optioneel voorbereid op:

- Google login
- Microsoft login
- Apple login
- Passkeys
- MFA / tweestapsverificatie

==================================================
5. PERSOONLIJK PROFIEL
==================================================

Iedere gebruiker krijgt een profielpagina.

Toon:

ACCOUNT
- Naam
- E-mailadres
- Account aangemaakt op
- Laatste login
- Tijdzone
- Valuta
- Taal

TRADINGPROFIEL
- Ervaringsniveau
- Voorkeursmarkt
- Voorkeursstrategie
- Risico per trade
- Virtueel startkapitaal
- Huidige virtuele accountwaarde

VOORKEURSMARKTEN
Gebruiker kan kiezen:

- Aandelen
- ETF
- Crypto
- Forex
- Indexen
- Grondstoffen

TRADINGSTIJL

- Scalping
- Daytrading
- Swingtrading
- Position trading
- Lange termijn analyse

==================================================
6. DATABASEGEHEUGEN
==================================================

DIT ONDERDEEL IS ZEER BELANGRIJK.

Het programma moet permanent gebruikersinformatie onthouden.

Gebruik PostgreSQL.

Maak minimaal databases voor:

USERS
PROFILES
USER_SETTINGS
PAPER_ACCOUNTS
PAPER_POSITIONS
PAPER_ORDERS
TRADE_HISTORY
TRADE_JOURNAL
WATCHLISTS
WATCHLIST_ITEMS
PRICE_ALERTS
NEWS_ALERTS
AI_ANALYSES
AI_CONVERSATIONS
AI_MESSAGES
STRATEGIES
STRATEGY_RESULTS
USER_LEARNING_PROGRESS
NOTIFICATIONS
ECONOMIC_EVENTS
PORTFOLIO_SNAPSHOTS

Iedere tabel moet gekoppeld worden aan:

user_id

Hierdoor ziet elke gebruiker uitsluitend zijn eigen informatie.

Gebruik Supabase Row Level Security.

Een gebruiker mag NOOIT trades, saldo, profielgegevens, watchlists of journalinformatie van een andere gebruiker kunnen bekijken.

==================================================
7. PERSISTENT PAPER TRADING
==================================================

Nieuwe gebruikers ontvangen standaard:

€10.000 virtueel handelskapitaal.

Maar laat tijdens onboarding kiezen:

€1.000
€2.500
€5.000
€10.000
€25.000
€50.000
€100.000

Of:

Eigen bedrag.

Alle bedragen zijn fictief.

==================================================
8. PAPER TRADING ACCOUNT
==================================================

Toon bovenaan permanent:

VIRTUEEL ACCOUNT

Cash:
€7.842

Belegde waarde:
€2.391

Open P&L:
+€143

Totaal account:
€10.233

Vandaag:
+€82 / +0,81%

Totaal:
+€233 / +2,33%

Open posities:
3

Winrate:
56%

Alle informatie komt uit de database.

==================================================
9. ORDERSYSTEEM
==================================================

Ondersteun virtueel:

MARKET BUY
LIMIT BUY
STOP BUY

MARKET SELL
LIMIT SELL
STOP SELL

STOP-LOSS
TAKE-PROFIT

TRAILING STOP

GEDEELTELIJK VERKOPEN

VOLLEDIG VERKOPEN

Laat iedere paper order permanent opslaan.

Per order:

- ID
- User ID
- Asset
- Ticker
- Beurs
- Ordertype
- Buy/Sell
- Aantal
- Orderprijs
- Uitvoeringsprijs
- Datum
- Tijd
- Stop-loss
- Take-profit
- Commissie
- Spread
- Slippage
- Status

Statusmogelijkheden:

PENDING
EXECUTED
CANCELLED
REJECTED

==================================================
10. PERSISTENTE OPEN POSITIES
==================================================

Open posities mogen NIET verdwijnen na:

- Browser sluiten
- Pagina vernieuwen
- Uitloggen
- Computer opnieuw opstarten
- Nieuwe telefoon gebruiken

Wanneer dezelfde gebruiker opnieuw inlogt:

haal open posities uit PostgreSQL.

Bereken opnieuw:

huidige marktwaarde
ongerealiseerde winst/verlies
percentage winst/verlies
afstand tot stop-loss
afstand tot take-profit.

==================================================
11. AUTOMATISCHE STOP-LOSS SIMULATIE
==================================================

Wanneer een virtuele positie een ingestelde stop-loss bereikt:

sluit automatisch de paper positie.

Registreer:

- Uitstapprijs
- Tijd
- Resultaat
- Reden: STOP LOSS

Hetzelfde geldt voor:

TAKE PROFIT.

Registreer:

Reden: TAKE PROFIT

LET OP:

Gebruik uitsluitend beschikbare marktdata.

Simuleer geen koers die niet via een databron is ontvangen.

==================================================
12. RISICOMANAGEMENT ENGINE
==================================================

Gebruiker kiest bijvoorbeeld:

Account:
€10.000

Maximaal risico:
1%

Bereken:

€10.000 × 1% = €100 maximaal toegestaan risico.

Voorbeeld:

ASML

Instap:
€900

Stop-loss:
€880

Risico per aandeel:
€20

Maximaal risico:
€100

Maximale positiegrootte op basis van risico:

€100 / €20 = 5 aandelen.

Controleer vervolgens ook of de gebruiker voldoende virtueel cashsaldo heeft.

Gebruik dus:

maximum_position =
minimum(
risk_based_position,
cash_based_position,
portfolio_allocation_limit
)

==================================================
13. MARKTDASHBOARD
==================================================

Maak een professioneel dashboard met:

BELANGRIJKSTE INDEXEN

AEX
AMX
DAX
CAC 40
FTSE 100
S&P 500
NASDAQ 100
Dow Jones
Nikkei 225
Hang Seng

CRYPTO

Bitcoin
Ethereum
Solana

FOREX

EUR/USD
EUR/GBP
EUR/JPY
GBP/USD
USD/JPY

GRONDSTOFFEN

Goud
Zilver
Olie
Natural Gas

Toon:

- prijs
- verandering
- procentuele verandering
- marktstatus
- volume
- high
- low
- laatste update
- databron

==================================================
14. LIVE MARKTSTATUS
==================================================

Toon:

AMSTERDAM
OPEN / GESLOTEN

NEW YORK
OPEN / GESLOTEN

LONDON
OPEN / GESLOTEN

TOKYO
OPEN / GESLOTEN

HONG KONG
OPEN / GESLOTEN

CRYPTO
24/7

Houd rekening met:

- lokale tijd
- zomertijd
- feestdagen
- openingstijden

==================================================
15. PROFESSIONELE GRAFIEKEN
==================================================

Gebruik candlestickgrafieken.

Tijdsintervallen:

1 minuut
5 minuten
15 minuten
30 minuten
1 uur
4 uur
1 dag
1 week
1 maand

Indicatoren:

EMA 9
EMA 21
EMA 50
EMA 200

SMA 20
SMA 50
SMA 200

RSI 14
MACD
Bollinger Bands
ATR
VWAP
Volume

Markeer automatisch:

Support
Resistance
Trend
Breakouts

==================================================
16. TECHNISCHE ANALYSE ENGINE
==================================================

Bereken een technische score.

Gebruik bijvoorbeeld:

Trend
0-20 punten

Momentum
0-20

Volume
0-15

RSI
0-10

MACD
0-10

Support/resistance
0-10

Volatiliteit
0-10

Datakwaliteit
0-5

Totaal:
0-100.

Toon bijvoorbeeld:

82 / 100

STERK BULLISH

Maar vermeld altijd:

“Technische score, geen garantie op toekomstige koersbeweging.”

==================================================
17. AI MARKET INTELLIGENCE ENGINE
==================================================

Bouw een professionele AI-analysepagina.

De AI ontvangt:

- koersdata
- historische koersdata
- volume
- technische indicatoren
- support
- resistance
- trend
- volatiliteit
- recent financieel nieuws
- economische gebeurtenissen
- beschikbare bedrijfsfundamentals

Daarna produceert AI:

MARKTSAMENVATTING

TECHNISCHE ANALYSE

FUNDAMENTELE CONTEXT

NIEUWSANALYSE

RISICOANALYSE

MARKTSENTIMENT

BELANGRIJKE PRIJSNIVEAUS

SCENARIOANALYSE

CONCLUSIE

==================================================
18. AI TOEKOMSTSCENARIO'S
==================================================

AI mag GEEN gegarandeerde voorspelling geven.

Gebruik drie scenario's.

BULLISH SCENARIO

Voorbeeld:

Als koers boven €X uitbreekt met bovengemiddeld volume:

mogelijke volgende weerstand:
€Y

Vereiste bevestigingen:
- volume
- RSI
- trend
- nieuws

NEUTRAAL SCENARIO

Waarschijnlijke consolidatiezone:

€X - €Y

BEARISH SCENARIO

Als support €X breekt:

volgende relevante support:
€Y

Toon per scenario:

- voorwaarden
- kansinschatting uitsluitend wanneer het model daarvoor een onderbouwde methodiek heeft
- onzekerheid
- nieuwsrisico
- belangrijke niveaus
- ongeldigverklaring van scenario

==================================================
19. AI ADVIESKAART
==================================================

Maak een visuele kaart:

AI MARKET VIEW

ASML

Technisch:
BULLISH

Nieuws:
NEUTRAAL

Momentum:
POSITIEF

Risico:
MIDDEL

Volatiliteit:
MIDDEL

Risk/reward:
2.4

Data confidence:
HIGH

Conclusie:

“De huidige technische omstandigheden zijn positief, maar de koers bevindt zich dicht bij weerstand. Een bevestigde uitbraak biedt technisch een sterker scenario dan direct instappen.”

Daaronder:

POTENTIËLE ENTRY ZONE

STOP-LOSS ZONE

TARGET 1

TARGET 2

RISK/REWARD

POSITIEGROOTTE

Dit is uitsluitend informatief en voor paper trading.

==================================================
20. WERELDWIJD NIEUWS
==================================================

Bouw een centrale:

GLOBAL FINANCIAL NEWS HUB

Ondersteun verschillende API's via adapters.

Nieuws moet kunnen worden opgehaald over:

Aandelen
Crypto
Forex
Macro-economie
Centrale banken
Bedrijfscijfers
Politiek nieuws met financiële relevantie
Geopolitiek
Energie
AI
Technologie
Chips
Banken
Farmacie
Grondstoffen

==================================================
21. NIEUWSANALYSE
==================================================

Per artikel sla op:

- titel
- bron
- URL
- publicatietijd
- categorie
- land
- relevante aandelen
- relevante markten

Laat AI vervolgens analyseren:

SENTIMENT

POSITIEF
NEUTRAAL
NEGATIEF

MARKTIMPACT

LAAG
MIDDEL
HOOG
ZEER HOOG

TIJDSHORIZON

UREN
DAGEN
WEKEN
MAANDEN

AI SAMENVATTING

MOGELIJK EFFECT OP MARKT

==================================================
22. NEWS IMPACT ENGINE
==================================================

Maak een score:

NEWS IMPACT

0-100.

Baseer dit bijvoorbeeld op:

- betrouwbaarheid bron
- relevantie asset
- actualiteit
- historisch effect vergelijkbare gebeurtenissen
- omvang gebeurtenis
- marktreactie

Toon:

92/100 CRITICAL MARKET NEWS

of:

28/100 LOW IMPACT

==================================================
23. ALERTCENTRUM
==================================================

Gebruiker kan meldingen krijgen bij:

prijs boven X
prijs onder X
dagbeweging > X%
volume > X
RSI > 70
RSI < 30
EMA crossover
support break
resistance breakout
nieuw artikel
kritiek nieuws
kwartaalcijfers
ECB
FED
inflatie
werkgelegenheid
stop-loss bereikt
take-profit bereikt
AI-signaal gewijzigd.

Bewaar notificaties in database.

Maak:

NOTIFICATIECENTRUM

met:

ALLE
ONGELEZEN
PRICE
NEWS
AI
PORTFOLIO
ECONOMIC

==================================================
24. ECONOMISCHE KALENDER
==================================================

Toon:

FED
ECB
Bank of England
CPI
PPI
Werkgelegenheid
BBP
PMI
Retail Sales
Bedrijfsresultaten

Per gebeurtenis:

Tijd
Land
Impact
Vorige waarde
Verwachting
Werkelijke waarde

Impact:

LOW
MEDIUM
HIGH
CRITICAL

==================================================
25. PERSOONLIJKE WATCHLISTS
==================================================

Gebruiker kan meerdere watchlists maken:

Bijvoorbeeld:

Mijn AEX
US Tech
AI aandelen
Crypto
Swing kansen

Elke watchlist wordt permanent opgeslagen.

Per asset:

- huidige koers
- verandering
- AI-score
- nieuwsstatus
- alert
- persoonlijke notitie

==================================================
26. FAVORIETEN
==================================================

Gebruiker kan:

ASML
NVIDIA
Microsoft
Bitcoin

favoriet maken.

Bij opnieuw inloggen blijven favorieten bestaan.

==================================================
27. TRADING JOURNAL
==================================================

Iedere gesloten trade moet automatisch worden toegevoegd aan:

TRADING JOURNAL.

Per trade:

Datum
Ticker
Strategie
Instap
Stop-loss
Take-profit
Exit
Aantal
Risico
Resultaat €
Resultaat %
Risk/reward
Duur
Nieuws
AI-analyse

Gebruiker kan toevoegen:

Waarom nam ik deze trade?

Wat verwachtte ik?

Hoe voelde ik mij?

Heb ik mijn plan gevolgd?

Wat ging goed?

Wat ging fout?

Wat heb ik geleerd?

==================================================
28. AI TRADE REVIEW
==================================================

Na iedere gesloten paper trade kan AI een review maken.

Voorbeeld:

AI TRADE REVIEW

Trade:
ASML

Resultaat:
-€82

POSITIEF:

✓ Stop-loss gebruikt
✓ Positiegrootte correct
✓ Risico onder 1%

MOGELIJKE FOUT:

Trade geopend vlak onder resistance.

VERBETERPUNT:

Wacht een volgende keer op bevestiging boven resistance.

BELANGRIJK:

AI beoordeelt alleen de paper-trades en processen en mag niet garanderen dat een andere handelskeuze winst zou hebben opgeleverd.

==================================================
29. PERSOONLIJK AI-GEHEUGEN
==================================================

Bouw een persoonlijk handelsprofiel op uit de historische PAPER TRADING data.

Niet uitsluitend tijdelijk chatgeheugen.

Sla relevante statistieken en gebruikersinstellingen permanent op.

AI moet bijvoorbeeld kunnen herkennen:

- Gebruiker handelt vooral US Tech
- Gebruiker gebruikt vaak EMA-strategieën
- Gemiddeld risico per trade
- Gemiddelde risk/reward
- Welke paper-strategieën historisch beter/slechter presteerden
- Hoe vaak gebruiker eigen trade-regels overtreedt
- Welke soorten paper trades verliesgevend waren

AI moet kunnen antwoorden:

“Hoe ging het deze maand?”

“Welke fouten maakte ik vaak?”

“Welke paper-trading strategie heb ik het meest gebruikt?”

“Hoeveel risico nam ik gemiddeld?”

“Laat mijn laatste 10 trades zien.”

“Hoe was mijn resultaat op ASML?”

“Welke trades heb ik rondom nieuws geopend?”

Alle antwoorden moeten uit de database worden gegenereerd.

Verzin nooit ontbrekende historische informatie.

==================================================
30. PERSOONLIJK DASHBOARD
==================================================

Wanneer gebruiker inlogt:

GOEDEMORGEN, [VOORNAAM]

Toon direct:

Portfolio waarde

Dagresultaat

Open posities

Paper trading saldo

Marktstatus

Belangrijkste alerts

Favorieten

Belangrijkste nieuws

Economische gebeurtenissen vandaag

AI market watch

Persoonlijke tradingstatistieken

==================================================
31. PRESTATIE DASHBOARD
==================================================

Bereken permanent:

TOTAL RETURN

WINRATE

LOSING RATE

PROFIT FACTOR

EXPECTANCY

GEMIDDELDE WINST

GEMIDDELD VERLIES

GEMIDDELDE RISK/REWARD

MAX DRAWDOWN

BEST TRADE

WORST TRADE

LONGEST WIN STREAK

LONGEST LOSS STREAK

RESULTAAT PER:

Dag
Week
Maand
Jaar

Strategie
Asset
Markt
Dag van week
Tijdstip

==================================================
32. EQUITY CURVE
==================================================

Maak automatisch een grafiek van de virtuele accountwaarde.

Bijvoorbeeld:

Start:
€10.000

Week 1:
€10.180

Week 2:
€9.940

Week 3:
€10.450

Week 4:
€10.720

Gegevens uit:

PORTFOLIO_SNAPSHOTS.

==================================================
33. LEEROMGEVING
==================================================

Maak een aparte:

TRADING ACADEMY.

Modules:

01 Marktprincipes

02 Candlesticks

03 Trends

04 Support/resistance

05 Orders

06 Stop-loss

07 Risk management

08 Position sizing

09 RSI

10 MACD

11 Moving averages

12 Volume

13 Price action

14 Fundamentele analyse

15 Nieuws

16 Economische kalender

17 Tradingpsychologie

18 Trading plan

19 Paper trading

20 Trading journal

==================================================
34. LEERVOORTGANG
==================================================

Sla per account permanent op:

Voltooide lessen

Voortgang

Quizscores

Modules

Datum voltooid

Laat dashboard zeggen:

Trading Academy

14 van 20 modules voltooid

70%

==================================================
35. BEGINNERSMODUS
==================================================

Omdat deze applicatie ook geschikt moet zijn voor beginners:

Maak een schakelaar:

BEGINNERSMODUS:
AAN / UIT

Wanneer AAN:

Toon naast moeilijke begrippen:

?

Bijvoorbeeld:

RSI ?

Klik:

“RSI meet momentum op een schaal van 0 tot 100. Waarden boven 70 worden vaak als relatief hoog beschouwd en onder 30 als relatief laag. Dat betekent niet automatisch kopen of verkopen.”

==================================================
36. AI ASSISTENT
==================================================

Maak rechtsonder een permanente AI-assistent.

Naam:

Trading Intelligence Assistant

Voorbeeldvragen:

“Wat gebeurt er vandaag?”

“Waarom daalt ASML?”

“Wat betekent deze candle?”

“Analyseer NVIDIA.”

“Wat zegt het nieuws?”

“Leg RSI eenvoudig uit.”

“Hoeveel zou ik volgens mijn paper-riskregels kunnen inzetten?”

“Hoe presteerde ik deze maand?”

“Welke fouten maak ik?”

“Wat heb ik gisteren gehandeld?”

AI krijgt uitsluitend toegang tot toegestane gebruikersdata en beschikbare marktinformatie.

==================================================
37. AI MAG GEEN DATA VERZINNEN
==================================================

ZEER BELANGRIJK.

Als informatie ontbreekt:

zeg:

“Onvoldoende gegevens beschikbaar.”

NIET:

een fictieve waarde genereren.

Dit geldt voor:

koersen
nieuws
trades
fundamentals
indicatoren
resultaten
voorspellingen
economische cijfers.

==================================================
38. AI BRONNEN
==================================================

Elke AI-marktanalyse moet laten zien:

BRONNEN

Market data:
[provider]

Nieuws:
[source]

Bedrijfsinformatie:
[source]

Laatste update:
[timestamp]

==================================================
39. DATA FRESHNESS
==================================================

Toon bij koersinformatie:

REALTIME

DELAYED

END OF DAY

UNKNOWN

Bijvoorbeeld:

NASDAQ

Last update:
15:34:21

Data:
15 MIN DELAYED

Provider:
[naam provider]

Noem data nooit realtime wanneer de API vertraagde data teruggeeft.

==================================================
40. ERROR HANDLING
==================================================

Wanneer API uitvalt:

toon NIET:

$0

of fake data.

Toon:

DATA MOMENTEEL NIET BESCHIKBAAR

Laatste succesvolle update:
12:41:06

Hiermee wordt voorkomen dat foutieve informatie als echte koers verschijnt.

==================================================
41. PROFESSIONELE UITSTRALING
==================================================

Look:

Bloomberg Terminal
TradingView
Interactive Brokers
moderne fintech SaaS

Maar maak een volledig eigen ontwerp.

Donkere achtergrond.

Kleuren:

#0B0F19
#111827
#1F2937

Bullish:
#22C55E

Bearish:
#EF4444

Neutraal:
#F59E0B

Accent:
#3B82F6

Maak gebruik van:

glass panels
subtiele gradients
micro animations
responsive cards
tooltips
modals
dropdowns
professionele iconen

==================================================
42. PROFESSIONELE AFBEELDINGEN
==================================================

Gebruik per belangrijke pagina unieke gegenereerde hero-afbeeldingen.

Pagina's:

Login
Registratie
Trading Academy
AI Intelligence
Market Overview

Visuele stijl:

institutionele fintech
donkere handelsomgeving
moderne wereldwijde financiële netwerken
subtiele grafieken
serieuze uitstraling
geen tekst in afbeelding
geen logo's van echte bedrijven
geen “snel rijk worden”-uitstraling.

==================================================
43. MOBIEL
==================================================

Website moet perfect werken op:

Desktop
Laptop
Tablet
iPhone
Android

Gebruik responsive design.

Op mobiel:

bottom navigation:

Home
Markets
Trade
News
Portfolio

==================================================
44. NAVIGATIE
==================================================

SIDEBAR:

HOME

Dashboard

MARKETS
Market Overview
Stocks
ETF
Crypto
Forex
Indices
Commodities

INTELLIGENCE
AI Market Analysis
AI News Analysis
Economic Calendar
Scanner

TRADING
Paper Trading
Orders
Positions
Portfolio
Journal

PERSONAL
Watchlists
Alerts
Performance
Trading Academy

ACCOUNT
Profile
Settings
Security

==================================================
45. ONBOARDING
==================================================

Na registratie:

STAP 1

Welkom.

STAP 2

Hoeveel ervaring heb je?

STAP 3

Welke markten interesseren je?

STAP 4

Welke stijl interesseert je?

STAP 5

Kies virtueel startkapitaal.

STAP 6

Kies maximaal risico per paper trade.

Standaard:
1%

STAP 7

Maak eerste watchlist.

STAP 8

Dashboard openen.

==================================================
46. RESET PAPER ACCOUNT
==================================================

Gebruiker kan paper-account resetten.

Maar:

vraag bevestiging.

Bijvoorbeeld:

“Je huidige paper-account bevat 47 trades en €10.842 accountwaarde. Weet je zeker dat je opnieuw wilt beginnen?”

Daarna:

archiveer oude accountdata.

Verwijder historische gegevens NIET direct.

Start nieuw paper-account.

Hierdoor kan gebruiker oude periodes later nog vergelijken.

==================================================
47. MEERDERE PAPER ACCOUNTS
==================================================

Geavanceerde functie:

Gebruiker kan meerdere virtuele accounts maken.

Bijvoorbeeld:

BEGINNER ACCOUNT
€10.000

SWING STRATEGY
€25.000

US TECH TEST
€15.000

CRYPTO TEST
€5.000

Zo kunnen strategieën onafhankelijk worden getest.

==================================================
48. STRATEGY LAB
==================================================

Maak:

STRATEGY LAB.

Gebruiker kan virtuele strategie definiëren.

Voorbeeld:

EMA CROSSOVER

Markt:
NASDAQ

Entry:
EMA 9 kruist EMA 21 omhoog.

Extra voorwaarde:
RSI < 70.

Stop:
1 ATR.

Target:
2 ATR.

Laat strategie vervolgens backtesten wanneer voldoende historische data beschikbaar is.

==================================================
49. BACKTESTING
==================================================

Resultaten:

Aantal signalen

Winrate

Profit factor

Average return

Max drawdown

Average risk/reward

Equity curve

Laat duidelijk zien:

HISTORISCHE RESULTATEN GARANDEREN GEEN TOEKOMSTIGE RESULTATEN.

==================================================
50. SECURITY
==================================================

Implementeer:

Supabase Auth

Row Level Security

Secure session handling

Server-side secrets

Environment variables

Rate limiting

Input validation

CSRF-bescherming waar relevant

XSS-bescherming

Database constraints

Audit logs

Login history

Optionele MFA

API-keys NOOIT naar browser sturen.

==================================================
51. PRIVACY
==================================================

Een gebruiker kan:

accountdata downloaden

tradingdata downloaden

journal exporteren

AI-history verwijderen

account verwijderen.

Voor definitieve verwijdering:

vraag expliciete bevestiging.

==================================================
52. EXPORT
==================================================

Exporteer:

Trading journal -> Excel

Trade history -> CSV

Maandrapport -> PDF

Performance -> Excel

Portfolio -> CSV

==================================================
53. DAGELIJKS AI MARKTRAPPORT
==================================================

Maak dagelijks automatisch voor iedere gebruiker een persoonlijk rapport.

Voorbeeld:

DAILY MARKET BRIEF

Goedemorgen Stiffan.

MARKTEN

AEX futures:
...

S&P 500:
...

NASDAQ:
...

BELANGRIJK VANDAAG

ECB
Inflatie
Bedrijfscijfers

JOUW WATCHLIST

ASML:
...

NVIDIA:
...

Microsoft:
...

BITCOIN:
...

OPEN PAPER POSITIONS

...

RISICO'S VANDAAG

...

De inhoud moet gebaseerd zijn op beschikbare actuele databronnen.

Geen data = geen verzonnen waarde.

==================================================
54. PERSOONLIJKE AI WEEKREVIEW
==================================================

Iedere week genereert het systeem:

WEEKLY TRADING REVIEW

Trades:
12

Wins:
7

Losses:
5

Resultaat:
+2,4%

Regels gevolgd:
83%

Grootste fout:
Trades geopend vlak voor belangrijk nieuws.

Sterkste punt:
Goed stop-lossgebruik.

Focus volgende week:
Wachten op bevestiging van setups.

Deze analyse MOET uitsluitend worden opgebouwd uit de echte paper-tradinghistorie van de gebruiker.

==================================================
55. DATABASE BACKUPLOGICA
==================================================

Omdat gebruikersinformatie belangrijk is:

gebruik database timestamps.

Maak audit trails voor cruciale paper-transacties.

Gebruik geen browser session_state als primaire opslag.

Gebruik database als primaire bron.

De frontend is slechts de weergave.

==================================================
56. GEEN ECHTE TRADING IN VERSIE 1
==================================================

ZEER BELANGRIJK:

Versie 1 voert uitsluitend PAPER TRADING uit.

GEEN:

echte brokerorders
echte automatische kooporders
echte automatische verkooporders
echte portefeuillewijzigingen bij een broker.

De software mag wel bij educatieve analyse tonen:

potential entry
potential stop
potential target
risk/reward
paper position size.

==================================================
57. DISCLAIMERS
==================================================

Toon onderaan relevante pagina's:

“Global Trading Intelligence is bedoeld voor educatie, marktanalyse en paper trading. AI-analyses, technische signalen en scenario's vormen geen persoonlijk financieel advies en bieden geen garantie op rendement. Controleer belangrijke informatie altijd bij betrouwbare en gereguleerde bronnen.”

==================================================
58. PROGRAMMA MOET PRODUCTIEWAARDIG ZIJN
==================================================

Ik wil GEEN simpele demo met één Pythonbestand.

Ik wil een professionele basis waarop het programma verder kan worden ontwikkeld.

Dus:

modulaire architectuur

herbruikbare componenten

duidelijke mappenstructuur

database migrations

authentication

error handling

tests

logging

API abstraction

security

responsive design

type safety

configuration management.

==================================================
59. PROJECTSTRUCTUUR
==================================================

Gebruik ongeveer:

/app
  /(auth)
  /dashboard
  /markets
  /analysis
  /news
  /paper-trading
  /portfolio
  /journal
  /watchlists
  /academy
  /performance
  /settings

/components

/components/charts
/components/trading
/components/news
/components/ai
/components/portfolio
/components/ui

/lib

/lib/market-data
/lib/news
/lib/ai
/lib/risk
/lib/trading
/lib/database

/services

/types

/hooks

/supabase

/tests

/public

==================================================
60. TESTS
==================================================

Maak tests voor:

registratie

login

database permissions

paper buy order

paper sell order

limit order

stop-loss

take-profit

positiegrootte

1%-regel

onvoldoende saldo

portfolio calculation

P&L

journal

watchlist

API failure

delayed data

AI hallucination protection.

==================================================
61. SEED DATA
==================================================

Maak testgebruikers en seeddata uitsluitend voor development.

Label deze data duidelijk:

DEMO DATA

Nooit demo-informatie presenteren als live marktinformatie.

==================================================
62. README
==================================================

Maak een zeer uitgebreide README.md.

Leg aan een beginner stap voor stap uit:

1. Welke programma's geïnstalleerd moeten worden
2. Hoe GitHub wordt gebruikt
3. Hoe Supabase wordt aangemaakt
4. Hoe database wordt ingericht
5. Hoe environment variables worden ingesteld
6. Hoe API-keys worden toegevoegd
7. Hoe lokaal wordt gestart
8. Hoe Vercel wordt ingesteld
9. Hoe online deployment werkt
10. Hoe latere updates worden uitgevoerd

Gebruik duidelijke commando's die direct gekopieerd kunnen worden.

==================================================
63. ENVIRONMENT CONFIGURATION
==================================================

Maak:

.env.example

Met bijvoorbeeld:

NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

MARKET_DATA_API_KEY=
NEWS_API_KEY=
AI_API_KEY=

Plaats nooit echte sleutels in repository.

==================================================
64. BOUWVOLGORDE
==================================================

Werk gefaseerd.

FASE 1
Projectstructuur
UI
Accounts
Login
Supabase
Database
Persoonlijke profielen

FASE 2
Paper trading
Persistent saldo
Orders
Posities
Portfolio
Stop-loss
Take-profit

FASE 3
Marktdata
Grafieken
Indicatoren
Market overview
Watchlists

FASE 4
Nieuws
Economische kalender
Alerts

FASE 5
AI Intelligence
AI News Analysis
Scenario Analysis
Persoonlijke AI-assistent

FASE 6
Journal
Performance
AI Trade Review
Persoonlijk handelsgeheugen

FASE 7
Academy
Learning progress
Strategy Lab
Backtesting

FASE 8
Security
Testing
Performance optimization
Deployment.

==================================================
65. WAT JE NU MOET GENEREREN
==================================================

Begin NIET meteen met duizenden regels willekeurige code.

Genereer eerst:

1. Complete systeemarchitectuur
2. Complete projectmappen
3. Database ERD
4. Database tabellen
5. Relaties tussen tabellen
6. Supabase RLS-policies
7. Authentication flow
8. Paper-trading flow
9. Marktdataflow
10. Nieuwsdataflow
11. AI-dataflow
12. Technische stack
13. Benodigde API's
14. .env.example
15. package.json
16. SQL migrations
17. Installatiecommando's

Controleer daarna zelf:

- Is accountdata permanent?
- Blijft virtueel saldo behouden?
- Blijven paper trades behouden?
- Zijn open posities na opnieuw inloggen aanwezig?
- Zijn gebruikersdata gescheiden?
- Is RLS actief?
- Zijn API-keys veilig?
- Wordt demo-data nergens als live data weergegeven?
- Kan AI ontbrekende data herkennen?
- Kan AI geen echte trades uitvoeren?
- Werkt het programma ook op mobiel?

Pas eventuele problemen aan.

Bouw daarna pas iedere module volledig uit.

Lever per bestand volledige werkende code.

Gebruik geen pseudocode als daadwerkelijke implementatie nodig is.

Als een externe API-key niet aanwezig is:

laat de module veilig overschakelen naar DEMO MODE of DATA UNAVAILABLE.

Verzin NOOIT actuele financiële informatie.

EINDDOEL:

Een professioneel persoonlijk financieel intelligence-platform waarin een gebruiker jarenlang zijn paper-tradinghistorie, tradingjournal, leerontwikkeling, watchlists, analyses en persoonlijke instellingen kan opbouwen, zodat het platform steeds meer historische context over de eigen paper-tradingprestaties kan tonen.

De applicatie moet veel meer zijn dan een koersdashboard.

Het moet functioneren als combinatie van:

MARKTTERMINAL
+
PAPER TRADING PLATFORM
+
AI MARKTASSISTENT
+
TRADING JOURNAL
+
RISICOMANAGER
+
FINANCIEEL NIEUWCENTRUM
+
TRADING ACADEMY
+
PERSOONLIJK PERFORMANCE DASHBOARD.
