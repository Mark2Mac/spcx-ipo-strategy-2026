<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/SpaceX-Logo.svg/640px-SpaceX-Logo.svg.png" alt="SpaceX" width="380"/>

# Un retail, €2.000 e un'AI contro la più grande IPO della storia

**Esperimento documentato e falsificabile**: può un modello di frontiera (Fable 5, Anthropic)
colmare il gap di informazione e competenza tra un piccolo investitore retail e gli istituzionali?
Banco di prova: l'IPO SpaceX del 12 giugno 2026 — $1.75T di valutazione, 94x i ricavi, il lockup
più anomalo mai visto.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Fable 5](https://img.shields.io/badge/AI-Fable%205%20·%20Anthropic-D4A27F)
![Data](https://img.shields.io/badge/data-SEC%20EDGAR%20·%20Polymarket%20·%20FRED%20·%20yfinance-555)
![Capitale](https://img.shields.io/badge/capitale-€2.000-2C8C3C)
![Status](https://img.shields.io/badge/status-esperimento%20in%20corso-FFBE00)

<img src="assets/mc_paths.gif" alt="Monte Carlo SPCX" width="640"/><br>
<sub><b>2.000 path Monte Carlo</b> — Student-t (fat tails empiriche) + jump sull'evento trimestrale/sblocco insider</sub>

</div>

---

## L'idea, in breve

Il 12 giugno 2026 SpaceX debutta al Nasdaq: la più grande IPO di sempre. Gli analisti la
danno sopravvalutata del 55% (Morningstar), Reddit grida al "furto del secolo", Polymarket
prezza il pop al 60%, e gli insider potranno vendere con uno sblocco accelerato mai visto.

Un piccolo retail normalmente entra qui dentro con FOMO e zero strumenti. In questo repo,
invece, un umano con €2.000 e un'AI hanno costruito quello che fa un desk istituzionale:
ricerca multi-fonte, valutazione, strategia a rischio definito, Monte Carlo validato sui dati,
event study sui precedenti storici, fiscalità, e un **registro di previsioni falsificabili**
scritto PRIMA del debutto.

Tra qualche mese si riapre tutto e si fanno i conti: [**PREDICTIONS.md**](PREDICTIONS.md) è il
contratto con il futuro — fa fede la history git.

## I numeri al 10 giugno 2026 (T-2 dal debutto)

| | |
|---|---|
| Pricing IPO | $135/azione · valutazione $1.75T · raccolta $75B (record storico) |
| Fair value Morningstar | $780B (**-55%** dal prezzo IPO) · 94x ricavi vs 22x di Nvidia |
| Il difetto strutturale | xAI brucia >$6B/anno dentro SpaceX; Starlink (61% dei ricavi) è profittevole |
| L'anomalia | insider liberi di vendere il 20% **2 giorni dopo la prima trimestrale** (vs 180gg standard) |
| Polymarket (soldi veri) | 99% chiusura day-1 sopra $1T · 60,5% sopra $2T |
| Il piano | 60% GOOGL (proxy difensiva) · 20% put spread sul lockup · 20% cash · perdita max hard-capped ~20% |

## Risultati della ricerca quant, a colpo d'occhio

<div align="center">
<table>
<tr>
<td align="center"><img src="assets/chart_mc_pnl.png" width="420"/><br><sub><b>Distribuzione P&L del piano</b> — 10k simulazioni, VaR/ES annotati: coda destra cappata dallo spread, coda sinistra tutta beta GOOGL</sub></td>
<td align="center"><img src="assets/chart_corr.png" width="420"/><br><sub><b>Correlazioni</b> — struttura 2 anni vs regime corrente (EWMA λ=0.94): quanto dell'hedge è illusorio</sub></td>
</tr>
<tr>
<td align="center"><img src="assets/chart_sensitivity.png" width="420"/><br><sub><b>Sensitività</b> — il piano vive o muore sul jump di agosto: EV>0 richiede jump ≤ -5%</sub></td>
<td align="center"><img src="assets/chart_universe.png" width="420"/><br><sub><b>Universe</b> — portafoglio, "pale e picconi" e benchmark: la pala migliore risk-adjusted è VIRT, non HOOD</sub></td>
</tr>
</table>
</div>

**La scoperta che ha corretto la tesi** — l'event study su 4 lockup storici (UBER, RIVN, META,
SNAP) mostra che il calo avviene in *anticipazione* (-37 punti medi nelle 30 sedute prima della
scadenza) e che il giorno dello sblocco è spesso un minimo locale. Si vende il rumor, si compra
la news: regola d'uscita aggiornata di conseguenza (chiusura entro T+5 dallo sblocco).

## Cosa c'è nel repo

```
notebooks/00_master_report.ipynb     ← APRI QUESTO: orchestra tutto, output inclusi
notebooks/01..03                     pipeline dati · correlazioni · Monte Carlo
docs/01..06                          tesi · strategie con tutti i conti · cronoprogramma ·
                                     risk management · fiscalità ITA · trade journal
docs/html/                           gli stessi notebook in HTML (doppio click, zero setup)
src/connectors/                      SEC EDGAR · Polymarket · FRED · yfinance + Stooq fallback
src/risk/ · src/research/            metriche, Monte Carlo, event study, validazione fat-tails
PREDICTIONS.md                       le previsioni falsificabili — il cuore dell'esperimento
```

## Riprodurre tutto

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python tools/build_master.py         # rigenera ed esegue i 4 notebook con dati freschi
.venv/bin/python -m src.research.lockup_study  # ogni modulo ha il suo smoke test
```

Per leggere i notebook senza alcun setup: apri `docs/html/` nel browser, oppure lasciali
renderizzare a GitHub online. In VS Code: estensione Jupyter + kernel della venv creata sopra.

## L'allocazione, per chi vuole solo il punto

| Tranche | Importo | Strumento | Ruolo | Perdita max |
|---|---|---|---|---|
| A | €1.200 (60%) | GOOGL (~5% di SpaceX in pancia) | proxy long difensiva | stop tesi -15% |
| B | €400 (20%) | put spread SPCX 140/135 set | short sul catalizzatore lockup | **€205, hard cap** |
| C | €400 (20%) | cash | opzionalità post-trimestrale | €0 |

EV dichiarato ex-ante: ≈ zero. Perdita massima strutturale: ~20% del capitale, nessuno
scenario azzera il conto. Il piano compra processo e apprendimento, non rendimento atteso.

## Perché esiste questo repo

Non per il P&L — €2.000 con EV≈0 non cambiano la vita di nessuno. Esiste per rispondere,
con dati e a costo di figuracce pubbliche, a una domanda seria: **l'AI può dare a chi ha
duemila euro gli strumenti di chi ne gestisce duemila miliardi?** La risposta onesta
arriverà nella colonna "Esito" di [PREDICTIONS.md](PREDICTIONS.md).

---

<div align="center">
<sub>
Niente in questo repo è consulenza finanziaria. È un esperimento documentato, con capitale che
l'autore può permettersi di perdere e regole scritte prima degli eventi.<br>
Il logo SpaceX appartiene a Space Exploration Technologies Corp. — usato qui a solo scopo identificativo.
</sub>
</div>
