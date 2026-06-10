# 05 — Fiscalità italiana (regime dichiarativo, broker estero IBKR)

> Verificare con un commercialista per la dichiarazione effettiva. Aliquote 2026 assunte invariate rispetto al regime vigente: ricontrollare a inizio 2027 (le aliquote sul capital gain sono periodicamente oggetto di proposte di modifica).

## 1. Quadro generale

Con IBKR (broker estero) sei in **regime dichiarativo**: nessun sostituto d'imposta, calcoli e dichiari tu. Conseguenze:
- Vantaggio: tassazione differita all'anno successivo (il 26% lo versi a giugno-novembre 2027 per i gain 2026) → piccolo beneficio finanziario.
- Svantaggio: quadri RW + RT da compilare; errori = sanzioni.

## 2. Le categorie che ti riguardano

| Strumento | Categoria fiscale | Aliquota | Compensabile con minus? |
|---|---|---|---|
| Azioni (GOOGL, SPCX) — plusvalenze | Redditi diversi | 26% | SÌ, genera e assorbe minus |
| Opzioni e spread — P&L | Redditi diversi | 26% | SÌ, genera e assorbe minus |
| Dividendi esteri (GOOGL) | Redditi di capitale | 26% sul netto frontiera | **NO** |
| ETF/fondi — plusvalenze | Redditi di capitale | 26% | **NO** (trappola italiana) |

**La trappola ETF**: le plusvalenze da ETF non possono assorbire minusvalenze pregresse (le minus da ETF invece sono compensabili con gain di azioni/opzioni). Motivo in più, oltre a PRIIPs, per cui questo piano non usa ETF.

## 3. Calcoli sul piano specifico

### Dividendi GOOGL (tranche A, ~€1.200)
- Dividend yield ~0,4% → ~€4,80/anno lordi.
- Ritenuta USA (treaty W-8BEN, da firmare su IBKR): 15% → -€0,72.
- Imposta italiana: 26% sul netto frontiera: 26% × €4,08 = -€1,06.
- **Netto: ~€3,02/anno** (tassazione effettiva ~37,1%).

### Strategia B — caso profitto
- Chiusura a +€155 netto commissioni → imposta 26% = **-€40,30** → netto in tasca **€114,70**.

### Strategia B — caso perdita
- Perdita -€205 = **minusvalenza** riportabile: compensabile con plusvalenze da redditi diversi (azioni, opzioni) realizzate entro il **31/12/2030**.
- Valore fiscale della minus: fino a €53,30 di imposte future risparmiate (26% × 205) — SE genererai gain compensabili in tempo.

### GOOGL — fino a vendita: zero eventi tassabili
- Nessuna imposta su plusvalenze non realizzate. Tenere GOOGL 12+ mesi = pieno controllo del timing fiscale.
- Ottimizzazione di fine anno (vedi cronoprogramma Fase 6): se B chiude in minus e GOOGL è in gain, vendere e ricomprare GOOGL entro il 31/12 realizza il gain che assorbe la minus (attenzione: costi di transazione ~€4 e rischio di prezzo nel reacquisto; farlo solo se la minus altrimenti rischia di scadere o se volevi comunque ribilanciare).

### IVAFE
- 0,2% annuo sul valore dei prodotti finanziari esteri al 31/12 (pro-rata sui giorni di possesso).
- Su ~€2.000: **~€4/anno**. Si versa con la dichiarazione.

## 4. Quadri dichiarativi (dichiarazione 2027 per anno 2026)

| Quadro | Cosa dichiara | Note |
|---|---|---|
| **RW** | Conto IBKR (monitoraggio attività estere) + calcolo IVAFE | Obbligatorio anche con P&L zero. Valore massimo e finale dell'anno |
| **RT** | Plusvalenze/minusvalenze da redditi diversi | Metodo LIFO per i carichi; IBKR fornisce i report ma il calcolo in EUR (cambio BCE del giorno) è a carico tuo |
| **RM** | Dividendi esteri | 26% sul netto frontiera |

Strumenti pratici: l'Activity Statement annuale di IBKR + un foglio di calcolo con cambi BCE giornalieri; oppure servizi tipo commercialista online specializzato (~€100-200, sensato dal secondo anno o con molte operazioni).

## 5. Costo fiscale totale stimato del piano (anno 2026)

| Scenario | Imposte |
|---|---|
| B in profitto (+€155), GOOGL non venduta | €40,30 + IVAFE €4 ≈ **€44** |
| B in perdita (-€205), GOOGL non venduta | IVAFE €4 + minus da riportare (credito fiscale futuro ~€53) |
| Tutto liquidato a fine anno in pari | IVAFE €4 |

## 6. Errori da non fare

1. Dimenticare il quadro RW: sanzione 3-15% degli importi non dichiarati (anche senza redditi!).
2. Non firmare il W-8BEN su IBKR: ritenuta USA sui dividendi al 30% invece che 15%.
3. Pensare al P&L lordo: ogni take-profit va valutato al netto del 26%.
4. Comprare un ETF "per parcheggiare" la tranche C: redditi di capitale, niente compensazione minus.
5. Usare Polymarket "tanto è poco": vincite da piattaforma non autorizzata ADM = trattamento fiscale incerto, potenziale qualificazione come redditi diversi al lordo senza compensazioni, più profili sanzionatori. Fuori dal piano.
