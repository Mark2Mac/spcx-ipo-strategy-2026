# SPCX IPO Strategy 2026 — Piano operativo €2.000

> **Disclaimer**: documento educativo/personale. Non è consulenza finanziaria. Tutti i prezzi delle opzioni sono **stime illustrative** da ricalcolare con le quotazioni reali (le opzioni SPCX quoteranno ~fine giugno 2026). Capitale a rischio: solo denaro la cui perdita totale non cambia la tua vita.

## Contesto in una riga

SpaceX debutta al Nasdaq il **12 giugno 2026** (ticker **SPCX**, $135/azione, valutazione $1.75T, raccolta $75B — la più grande IPO della storia). Tesi: valutazione estrema (94x ricavi), lockup insider anomalo ad agosto, fair value Morningstar $780B (-55%). Strategia: **non inseguire il debutto**, posizionarsi su catalizzatori datati con rischio definito e priorità alla protezione del capitale.

## Struttura del repo

| File | Contenuto |
|---|---|
| [01-contesto-e-tesi.md](01-contesto-e-tesi.md) | Dati IPO, fondamentali S-1, tesi rialzista/ribassista, fonti |
| [02-strategie-operative.md](02-strategie-operative.md) | Le 3 strategie con tutti i calcoli: struttura, breakeven, EV, sensitività |
| [03-cronoprogramma.md](03-cronoprogramma.md) | Timeline operativa giorno per giorno, 10 giu → 31 dic 2026 |
| [04-risk-management.md](04-risk-management.md) | Regole hard, position sizing, stop conditions, scenari di invalidazione |
| [05-fiscalita-italia.md](05-fiscalita-italia.md) | 26%, minusvalenze, IVAFE, quadro RW, trappola ETF, calcoli netti |
| [06-registro-operazioni.md](06-registro-operazioni.md) | Trade journal: template da compilare a ogni operazione |
| `notebooks/01_data_pipeline.ipynb` | Pipeline dati testata: yfinance+Stooq fallback, SEC EDGAR, Polymarket, FRED, quality report |
| `notebooks/02_correlation_risk.ipynb` | Correlazioni Pearson vs EWMA, beta, drawdown, rolling corr, risk ledger |
| `notebooks/03_montecarlo.ipynb` | 10k path Student-t + jump evento, VaR/ES, payoff, sensitività al jump |
| `src/` | Connectors (market_data, edgar, polymarket, fred) e moduli risk (metrics, montecarlo), tutti con smoke test in `__main__` |

## Setup quant

```bash
python3 -m venv ~/.venvs/quant && ~/.venvs/quant/bin/pip install -r requirements.txt
# test pipeline:
~/.venvs/quant/bin/python src/connectors/market_data.py
# rigenerare + rieseguire i notebook:
~/.venvs/quant/bin/python tools/build_notebooks.py
```

Post-IPO (dal ~22 giu): aggiornare in `03_montecarlo` i parametri `spcx_s0`, `spcx_vol` (dalla IV reale delle opzioni) e `debit`; da agosto `src/connectors/edgar.py form4_watch()` mostra le vendite insider reali entro 2 giorni dal fatto.

## Allocazione master

| Tranche | Importo | Strumento | Ruolo | Perdita max |
|---|---|---|---|---|
| A | €1.200 (60%) | GOOGL | Proxy long difensiva | Beta mercato (no hard cap, stop -15%) |
| B | €400 (20%) | Put spread SPCX | Short su catalizzatore lockup | €205 (hard cap, rischio definito) |
| C | €400 (20%) | Cash USD/EUR | Opzionalità post-trimestrale | €0 |

**Perdita massima teorica del piano: ~€385-425 (19-21% del capitale). Nessuno scenario azzera il conto.**

## Principio guida

> Su un evento così mediatico l'edge retail è sottile e l'EV complessivo è vicino a zero. Il valore del piano non è "arricchirsi" ma: (1) perdita massima nota in anticipo, (2) esposizione al ciclo IPO-lockup con struttura professionale, (3) processo replicabile per le prossime occasioni. Priorità dichiarata dall'investitore: **sicurezza > rendimento**.
