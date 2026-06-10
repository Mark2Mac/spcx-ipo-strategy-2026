# 04 — Risk management

Il documento più importante del repo. Le regole qui scritte prevalgono su qualsiasi convinzione futura. Se una regola sembra sbagliata durante l'operatività, si chiude la posizione PRIMA e si riscrive la regola POI, mai il contrario.

## 1. Hard cap di perdita (struttura del piano)

| Posizione | Perdita massima | Tipo di cap |
|---|---|---|
| A — GOOGL €1.200 | -€180 (stop tesi a -15%) | Soft (richiede disciplina) |
| B — Put spread €205 | -€205 | **Hard (matematico: non puoi perdere di più del debito)** |
| C — Cash €400 | €0 | Hard |
| Attrito/fisco | -€25 | Fisso |
| **Piano intero** | **~-€410 (20,5%)** | |

Nessuna combinazione di eventi può azzerare il conto. Questo è il requisito "sicurezza > rendimento" tradotto in struttura: il 60% del capitale non tocca mai SPCX, il 20% è cash, e l'unica posizione sul titolo ha perdita massima scolpita nel contratto.

## 2. Position sizing — perché questi numeri

- Regola classica: 1-2% di rischio per trade. Su €2.000 = €20-40 → **incompatibile con le opzioni** (taglio minimo spread ≈ €200).
- Adattamento dichiarato: si accetta UN trade a rischio definito al 10% del capitale, compensato da: (a) hard cap matematico, (b) 80% del capitale fuori dal trade, (c) divieto di aggiungere contratti.
- Formula di controllo prima di ogni ordine: `rischio_massimo_ordine / capitale_totale ≤ 0,105` → se falso, l'ordine non parte.
- Kelly check (per onestà intellettuale): con P=0,50, odds 1,27 → f* = (0,50×1,27-0,50)/1,27 ≈ 0,11 → il 10% è già full-Kelly, cioè AGGRESSIVO. Mezzo Kelly sarebbe €100, sotto il taglio minimo. Conclusione: il trade B è al limite superiore del sizing razionale; per questo è uno solo e irripetibile prima dell'evento.

## 3. Regole comportamentali (le perdite vere nascono qui)

1. **Mai ordini market** su SPCX o sue opzioni: solo limit. Gli spread bid/ask su un titolo neo-quotato possono superare l'1%.
2. **Mai operare nelle prime e ultime 0,5h di sessione USA** salvo take-profit pianificati.
3. **Mai aumentare una posizione in perdita** ("mediare" uno spread = raddoppiare un errore al doppio del costo psicologico).
4. **Mai più di 1 posizione in derivati aperta** contemporaneamente.
5. Ogni ordine richiede una riga PRIMA nel registro (file 06) con: tesi, invalidazione, perdita massima. Nessuna riga → nessun ordine.
6. **Regola delle 24 ore**: ogni deviazione dal piano scritto richiede 24h di attesa tra idea ed esecuzione. L'urgenza percepita è il segnale più affidabile che stai per fare un errore.
7. FOMO check del day-1: se il 12 giugno SPCX apre a +40% e "senti" di dover entrare — rileggere la riga Rivian/Uber nel file 01. Il pop iniziale è IL meccanismo con cui il retail compra dagli istituzionali.

## 4. Condizioni di invalidazione della tesi (scritte ORA, a mente fredda)

La tesi short-agosto è MORTA (chiudere B, non aprire altro short) se si verifica una qualsiasi:
- Trimestrale: burn xAI < $1,5B (in forte calo) E crescita Starlink > 15% QoQ.
- T+7 dallo sblocco: prezzo ≥ prezzo di T (il mercato assorbe le vendite insider).
- SpaceX annuncia spin-off di xAI (rimuove il driver delle perdite dal perimetro).
- SPCX scende sotto $135 PRIMA dell'ingresso nello spread (edge consumato dal mercato).

La tesi long-proxy (GOOGL) è MORTA se:
- Alphabet vende/svaluta la quota SpaceX, o emergono problemi propri di GOOGL che ne cambiano i fondamentali (a quel punto è una decisione su GOOGL, non su SpaceX).

## 5. Rischi non di mercato (spesso ignorati, spesso fatali)

| Rischio | Mitigazione |
|---|---|
| Rischio cambio EUR/USD | Tranche A esposta (~€1.200): un -5% EUR/USD = -€60. Accettato (orizzonte lungo). Tranche C tenuta in EUR fino all'uso |
| Rischio assegnazione (leg corta spread) | Mai tenere lo spread a scadenza con spot fra gli strike (regola in Fase 5). L'assegnazione comporterebbe acquisto di 100 azioni = $13.500 di notional su un conto da €2.000 → margin call |
| Rischio liquidità opzioni | Su un titolo neo-quotato gli strike "fini" possono avere book vuoti: usare solo strike a $5 tondi, ordini combo, mai inseguire il mid di più di $0,10 |
| Rischio broker/operativo | 2FA su IBKR; nessuna API key di trading su macchine condivise; controllare le conferme d'ordine prima dell'invio (un contratto = 100x il prezzo visualizzato) |
| Rischio informativo | Le date di trimestrale/sblocco vanno verificate sui filing SEC (sec.gov, CIK SpaceX), non su Reddit |
| Rischio fiscale | Accantonare mentalmente il 26% di ogni gain realizzato: il P&L vero è il netto |

## 6. Metriche di controllo settimanali (venerdì, 15 minuti)

- Valore totale conto in EUR vs €2.000 iniziale.
- Drawdown corrente vs massimo accettato (-20,5%).
- Per lo spread: valore mark-to-market, theta residuo, giorni all'evento.
- Una riga nel registro anche se non è successo niente ("nessuna azione" è un dato).

## 7. Il rischio più sottovalutato: te stesso

Con €2.000 nessuna strategia cambia la tua vita in positivo; una cattiva abitudine presa adesso (mediare, vendicarsi del mercato, togliere gli stop) scala con il capitale futuro e quella sì può cambiartela in negativo. Questo piano va giudicato al 90% sul processo (regole rispettate?) e al 10% sull'esito (P&L). Un +€240 ottenuto violando le regole è un risultato PEGGIORE di un -€205 ottenuto rispettandole.
