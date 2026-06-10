# 03 — Cronoprogramma operativo (10 giugno → 31 dicembre 2026)

Ogni azione ha: data, condizione di attivazione, operazione esatta, fallback. Le date post-agosto dipendono dalla data della prima trimestrale (sarà annunciata da SpaceX: aggiornare questo file appena nota).

---

## FASE 0 — Preparazione (mar 10 giugno → gio 11 giugno)

**Obiettivo: essere operativi PRIMA del debutto, senza fare alcun trade.**

- [ ] Aprire/verificare conto IBKR. Richiedere permessi trading opzioni (livello "option spreads"; questionario MiFID: serve esperienza dichiarata su derivati).
- [ ] Bonificare €2.000. Tempo accredito SEPA: 1-2 giorni lavorativi → farlo SUBITO.
- [ ] Convertire €1.150 in USD (per tranche A): ordine FX EUR.USD, costo min $2. Tenere il resto in EUR.
- [ ] Creare watchlist: SPCX, GOOGL. Configurare alert prezzo: SPCX a $120, $135, $150, $175.
- [ ] 11 giu sera: leggere il pricing definitivo (conferma $135 o revisione). Se il prezzo sale sopra $150 in pricing → la sopravvalutazione peggiora, tesi short rafforzata; nessuna azione.
- [ ] **Vietato**: qualsiasi ordine su SPCX in questa fase.

## FASE 1 — Debutto: solo osservazione (ven 12 giugno → ven 26 giugno)

**Obiettivo: raccogliere dati. Il day-1 è il giorno in cui il retail perde di più. Tu non operi su SPCX.**

- [ ] 12 giu: annotare nel registro (file 06): prezzo apertura, massimo, chiusura day-1, volume. Confrontare con Polymarket (99% sopra $1T ≈ sopra ~$77/azione: quasi certo; interessa DI QUANTO sopra).
- [ ] 12-13 giu (facoltativo, consigliato): eseguire tranche A — acquisto GOOGL ~€1.110-1.200, ordine limit a prezzo ≤ ultimo close, validità GTC 3 giorni. GOOGL non dipende dal timing di SPCX: nessuna fretta, nessun inseguimento. Se il limit non viene eseguito in 3 giorni, rialzare il limit dello 0,5% una sola volta.
- [ ] ~19-24 giu: **verifica quotazione opzioni SPCX** (tipicamente 4-7 giorni di borsa dopo l'IPO). Quando quotano, annotare ogni giorno: IV ATM scadenza settembre, prezzo spot.
- [ ] Calcolare ogni venerdì: IV percentile rispetto ai giorni osservati. Soglia operativa: **IV ATM < 55%**.
- [ ] **Vietato**: comprare opzioni in questa fase (IV 75-90%, ogni acquisto è regalato al market maker).

## FASE 2 — Inclusione indici e IV crush (lun 29 giugno → ven 17 luglio)

**Obiettivo: lasciare che i flussi passivi gonfino il prezzo (meglio per lo spread) e che l'IV si sgonfi (meglio per il costo).**

- [ ] ~3 lug: inclusione Nasdaq-100 attesa (15 giorni di trading dal 12 giu). Flussi passivi ~$30B → possibile spinta rialzista. NON interpretarla come "la tesi è sbagliata": è meccanica, non fondamentale.
- [ ] **Finestra di ingresso strategia B: 6-17 luglio**, alla PRIMA occorrenza di TUTTE queste condizioni:
  - IV ATM settembre < 55%
  - SPCX spot > $140 (lo spread 140/135 deve essere OTM: se lo spot è già sotto, l'edge è consumato → vedi fallback)
  - debito spread 140/135 settembre ≤ $2,30
- [ ] Esecuzione: ordine combo "bear put spread" (mai le due leg separate — rischio di leg risk), limit al mid-price, pazienza fino a 3 giorni.
- [ ] Annotare nel registro: debito pagato, IV all'ingresso, spot, greeks (delta, theta dello spread).
- [ ] **Fallback 1**: se IV non scende sotto 55% entro il 17 lug → rimandare al 24 lug con soglia rilassata a 60%. Se ancora no → **annullare la strategia B**, il costo non giustifica l'edge. Il cash resta cash.
- [ ] **Fallback 2**: se SPCX è già sotto $135 prima dell'ingresso → il mercato ha anticipato la tesi; NON inseguire con strike più bassi (comprare ribasso già avvenuto = pagare l'edge degli altri). Strategia B annullata.
- [ ] **Fallback 3**: se la data della trimestrale annunciata cade dopo il 18 set → spostare la scadenza dello spread a ottobre; ricalcolare budget (le ottobre costeranno ~15-20% in più; se debito > $2,60 ridurre larghezza a $140/$136,25 o annullare).

## FASE 3 — Attesa disciplinata (20 luglio → trimestrale)

**Obiettivo: non toccare niente. Il theta dello spread debit lavora contro lentamente finché lo spot resta sopra 140; è il costo pianificato dell'attesa.**

- [ ] Check settimanale (15 minuti, venerdì): spot, valore spread, news su data trimestrale. Annotare nel registro.
- [ ] Se SPCX sale +30% sopra $135 (cioè > $175,50) per 5 sedute su 10: si sblocca il 10% insider aggiuntivo. Valutare roll dello strike long da 140 a 150 SOLO se: costo del roll ≤ €60 E siamo prima del 1 agosto. Altrimenti tenere.
- [ ] Se lo spread perde il 50% del valore prima della trimestrale senza che la tesi sia falsificata (solo theta/rialzo): TENERE. Il payoff è binario sull'evento di agosto; vendere prima dell'evento butta via la parte di premio che paga l'evento stesso.
- [ ] **Vietato**: aggiungere contratti, "mediare", aprire B2 in aggiunta a B.

## FASE 4 — L'evento: trimestrale + sblocco insider (~agosto, date da confermare)

**Obiettivo: eseguire le regole scritte a luglio, non le emozioni di agosto.**

Giorno T = pubblicazione prima trimestrale. T+2 = primo giorno di vendita insider (20% delle quote).

- [ ] T: leggere i numeri. Tre dati decidono tutto: burn xAI trimestrale (atteso ~$2,5B), crescita abbonati Starlink, guidance. Annotare.
- [ ] T+2 → T+7: finestra critica. Monitoraggio giornaliero (apertura + chiusura).
- [ ] **Take profit**: se il valore dello spread raggiunge $3,90+ (= 70% del max gain): chiudere con ordine combo limit. Incasso ~€360, profit ~+€155 netto commissioni.
- [ ] **Regola d'uscita da event study** (notebook 00, sez. 6 — UBER/RIVN/META/SNAP): il calo da lockup è da ANTICIPAZIONE (-37 punti medi T-30→T0) e T0 è spesso minimo locale (+19 punti T0→T+20). Quindi: chiudere lo spread ENTRO T+5 dallo sblocco, qualunque sia il P&L — non aspettare una continuazione del calo che storicamente non arriva.
- [ ] **Falsificazione**: se a T+7 SPCX non è scesa sotto il prezzo di T (gli insider non vendono o il mercato assorbe): chiudere lo spread recuperando il valore residuo (stima 30-50% del debito ≈ €60-100). Perdita contenuta ~€105-145 invece di €205. Annotare la lezione.
- [ ] **Scenario crollo violento** (SPCX < $120 in pochi giorni): lo spread va vicino al massimo. Chiudere a $4,50+ senza aspettare $5 (la liquidità sugli spread ITM peggiora).
- [ ] Decisione tranche C: SOLO dopo T+7.
  - SPCX scesa sotto ~$85 (≈ fair value Morningstar +10%): valutare acquisto 4-5 azioni SPCX (~€350) come posizione long di lungo periodo. Condizione aggiuntiva: burn xAI in calo trimestre su trimestre.
  - Tesi confermata con momentum (titolo in calo, altri sblocchi al giorno 135 in arrivo): valutare secondo spread ottobre/novembre, stesse regole di sizing della B.
  - Nessuna delle due: il cash resta cash. Esito valido.

## FASE 5 — Coda del lockup (settembre → ~25 ottobre, giorno 135)

- [ ] 18 set: scadenza spread (se ancora aperto, decidere entro il 16: mai portare uno spread a scadenza con lo spot fra gli strike — rischio assegnazione sulla leg corta).
- [ ] Tranche del 7% si sbloccano a intervalli regolari fino al giorno ~135 (~25 ott): pressione di vendita ricorrente. Se hai aperto posizioni con la tranche C, questo è il vento che hai a favore (short) o contro (long anticipato).
- [ ] Fine ottobre: revisione completa del piano. Il prezzo post-lockup completo è il primo prezzo "vero" di SPCX.

## FASE 6 — Chiusura anno e fisco (novembre → dicembre)

- [ ] Scaricare da IBKR il report annuale (Activity Statement completo).
- [ ] Calcolare plusvalenze/minusvalenze realizzate (vedi file 05): le minus realizzate nel 2026 sono compensabili fino al 2030.
- [ ] Se la strategia B ha chiuso in perdita e GOOGL è in forte gain: valutare (solo se sensato per altri motivi) realizzare parte del gain GOOGL entro il 31 dic per compensare la minus → risparmio fiscale 26% della minus (~€53 se persi €205).
- [ ] Promemoria dichiarazione 2027: quadro RW (conto estero IBKR), quadro RT (redditi diversi), IVAFE €4.
- [ ] Retrospettiva scritta nel registro: cosa ha funzionato, cosa no, EV ex-ante vs risultato ex-post.

---

## Tabella riassuntiva delle date

| Data | Evento | Azione |
|---|---|---|
| 10-11 giu | Pre-IPO | Setup conto, bonifico, FX, alert. Zero trade |
| 11 giu sera | Pricing | Solo lettura |
| 12 giu | Debutto SPCX | Osservare. Eventuale acquisto GOOGL (limit) |
| ~19-24 giu | Quotazione opzioni | Inizio tracking IV giornaliero |
| ~3 lug | Nasdaq-100 | Nessuna azione (è meccanica, non tesi) |
| 6-17 lug | Finestra ingresso B | Spread SOLO se IV<55% + spot>$140 + debito≤$2,30 |
| ~ago (T) | Prima trimestrale | Leggere burn xAI |
| T+2 | Sblocco 20% insider | Monitoraggio giornaliero |
| T+2→T+7 | Finestra critica | Take profit ≥$3,90 / falsificazione → chiusura |
| post T+7 | Decisione tranche C | Long sotto $85 / secondo spread / niente |
| 16-18 set | Scadenza spread | Mai a scadenza con spot fra gli strike |
| ~25 ott | Giorno 135, fine lockup | Revisione totale |
| dic | Fisco | Compensazioni, report, retrospettiva |
