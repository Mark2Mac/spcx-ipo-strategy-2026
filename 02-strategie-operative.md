# 02 — Strategie operative con calcoli completi

Capitale: **€2.000,00**. Cambio assunto EUR/USD = 1,08 (aggiornare a ogni calcolo reale). Broker: IBKR, regime dichiarativo. Priorità dichiarata: **sicurezza > rendimento**.

## Vincoli normativi (verificati, non negoziabili)

- **PRIIPs/KID**: XOVR, NASA ETF, DXYZ e ogni veicolo USA senza KID sono **bloccati** per retail UE. Niente proxy ETF.
- **Opzioni su azioni USA**: accessibili (esenti dall'obbligo KID).
- **Polymarket**: non licenziato ADM → escluso (rischio legale + fiscalità indefinita + controparte).
- **Short diretto SPCX**: tecnicamente possibile, escluso (borrow cost stimato 20-100%+ annuo le prime settimane, perdita illimitata, squeeze risk con domanda 4x).

## Attrito di base (costo del "giocare")

| Voce | Costo | Frequenza |
|---|---|---|
| Conversione EUR→USD | min $2 (~€1,85) | 1-2 volte |
| Ordine azioni IBKR | ~$1-2 | per ordine |
| Opzione IBKR | ~$1/contratto/leg | 2 leg per spread, x2 (apertura+chiusura) = ~$4-8 |
| IVAFE | 0,2%/anno = €4 su €2.000 | annuale |
| Quadro RW | tempo proprio o commercialista €100-200 | annuale |
| **Totale attrito anno** | **~€15-25 (0,8-1,2% del capitale)** | |

Conseguenza matematica: ogni strategia deve rendere >1% solo per pareggiare. Con €2.000 il nemico numero uno sono i costi fissi, non il mercato.

---

## STRATEGIA A — Proxy long difensiva: GOOGL (€1.200, 60%)

### Edge
Alphabet detiene ~5% di SpaceX (≈$90B al prezzo IPO) su una market cap di ~$3.5T: catalizzatore parzialmente non prezzato (~2,5% del valore di GOOGL). Sotto: business dominante, cassa, buyback. È l'unico modo a basso rischio di essere "long SpaceX" da retail UE.

### Esecuzione
- Acquisto: ~5-6 azioni GOOGL (prezzo ipotetico ~$200; ricalcolare) ≈ €1.110-1.200.
- Ordine: **limit**, mai market. Orario: 16:00-17:30 CET (overlap liquido).
- Nessuna leva. Nessuna opzione su questa tranche.

### Calcoli scenario (tranche €1.200)
| Scenario SpaceX | Effetto su stake | Effetto su GOOGL | P&L tranche |
|---|---|---|---|
| SPCX +50% | +$45B | +~1,3% | **+€16** |
| SPCX invariata | 0 | 0 | €0 |
| SPCX -50% | -$45B | -~1,3% | **-€16** |
| GOOGL business +10% (driver propri) | — | +10% | **+€120** |
| Mercato -15% (beta ~1,05) | — | -~16% | **-€190** |

**Lettura onesta**: il rischio/rendimento di questa tranche è dominato da Alphabet stessa, non da SpaceX. Funzione nel piano: parcheggiare il 60% del capitale in qualità invece che nel circo, mantenendo un'esposizione simbolica al tema. Questa È la strategia "più sicurezza, meno rendimento" richiesta.

### Risk management tranche A
- Stop loss mentale (non in macchina, per evitare stop-hunt): **-15%** → -€180. Rivalutazione, non vendita automatica.
- Orizzonte: 12+ mesi (anche per efficienza fiscale: nessun evento tassabile finché non vendi).
- Dividendo ~0,4%/anno ≈ €4,80 lordi → €3 netti (vedi fiscalità).

---

## STRATEGIA B — Short su catalizzatore datato: put spread SPCX (max €400, 20%)

### Edge (dichiarato e falsificabile)
Il mercato prezza bene il pop del debutto (Polymarket 99% sopra $1T) ma sottoprezza la finestra agosto: prima trimestrale (burn xAI ~$2,5B/trimestre visibile a tutti) + sblocco 20% insider 2 giorni dopo. Precedenti storici: RIVN -20% in un giorno, UBER -40% a scadenza lockup. Fair value Morningstar -55% dal prezzo IPO.

**La tesi è falsificata se**: ad agosto gli insider non vendono in massa, o la trimestrale mostra burn xAI in netto calo, o il titolo ha già perso >30% prima della finestra (edge consumato).

### Struttura: bear put spread (debit spread verticale)
Numeri **illustrativi** con SPCX a $150 post-pop e IV 75% → ricalcolare sui prezzi reali di fine giugno/luglio.

```
COMPRA 1 put SPCX scadenza 18 set 2026, strike $140
VENDE  1 put SPCX scadenza 18 set 2026, strike $135
Larghezza spread: $5
Debito stimato: $2,20/azione → costo totale $220 ≈ €205
```

### Tutti i calcoli
| Grandezza | Formula | Valore |
|---|---|---|
| Rischio massimo | debito pagato | $220 ≈ **€205** (10,2% del capitale) |
| Guadagno massimo | (larghezza - debito) × 100 | (5-2,20)×100 = $280 ≈ **€260** |
| Breakeven a scadenza | strike long - debito | 140 - 2,20 = **$137,80** |
| Rapporto rischio/rendimento | max gain / max loss | **1 : 1,27** |
| P(profit) minima per EV=0 | debito / larghezza | 2,20/5 = **44%** |
| Commissioni totali | 2 leg × 2 (in+out) × $1 | ~$4-8 (≈2-4% del premio: incidenza alta, conteggiata) |

### Expected Value — tabella di sensitività
EV = P(sotto $135) × (+€260) + P(tra 135 e 137,80) × (parziale, ~€0 medio) + P(sopra 137,80) × (-€205). Semplificando a due esiti:

| P(SPCX ≤ $135 al 18 set) | EV dello spread |
|---|---|
| 30% | 0,30×260 - 0,70×205 = **-€65** |
| 40% | 0,40×260 - 0,60×205 = **-€19** |
| 44% | **€0** (breakeven probabilistico) |
| 50% | 0,50×260 - 0,50×205 = **+€28** |
| 55% | 0,55×260 - 0,45×205 = **+€51** |
| 60% | 0,60×260 - 0,40×205 = **+€74** |

**Onestà**: l'operazione ha EV positivo SOLO se assegni alla tesi lockup una probabilità >44%. Polymarket e la domanda 4x suggeriscono che il mercato la prezza sotto. Il tuo edge presunto: il mercato guarda il day-1, tu guardi agosto. Se non credi a P≥50%, NON eseguire la strategia B e lascia il 20% in cash.

### Regole di esecuzione (vincolanti)
1. **MAI comprare lo spread nei primi 10-15 giorni di trading**: IV post-IPO al massimo (~75-90%). L'IV crush tipico è di 20-30 punti nelle prime 3-4 settimane → lo stesso spread costerà ~$1,50-1,80 invece di $2,20 (-20/30% sul costo).
2. Finestra di ingresso: **6-17 luglio 2026** (vedi cronoprogramma), SOLO se IV scesa sotto ~55% e SPCX sopra $140.
3. La scadenza DEVE contenere la trimestrale e i 2 giorni successivi: settembre minimo, ottobre se i prezzi lo permettono a parità di budget.
4. Massimo **1 contratto**. Il secondo contratto porterebbe il rischio della tranche al 20%+ del capitale: vietato.
5. **Take profit: +70% del guadagno massimo** (≈ +€180): chiudere senza aspettare la scadenza. Motivo: gli ultimi 30% di guadagno richiedono di tenere lo spread fino a scadenza, dove gamma e pin risk lavorano contro.
6. **Stop alla tesi, non al prezzo**: se la trimestrale esce e il titolo NON scende entro 5 sedute dallo sblocco insider, la tesi è falsificata → chiudere per recuperare valore temporale residuo (~30-50% del premio), non aspettare l'azzeramento.
7. Trappola del +30%: se SPCX sale +30% per 5/10 sedute, si sblocca un ulteriore 10% insider — tesi rafforzata ma strike lontano. Valutare roll up dello strike SOLO se costo aggiuntivo ≤ €60 e prima del 1 agosto.

### Variante B2 — se la view diventa "stallo" invece che "calo": bear call spread (credit)
```
VENDE  1 call SPCX scadenza set, strike ~$165 (sopra resistenza)
COMPRA 1 call SPCX scadenza set, strike ~$170
Credito stimato: $1,80 → incasso $180 ≈ €167
Rischio massimo: (5-1,80)×100 = $320 ≈ €296
Breakeven: 165+1,80 = $166,80
P(profit) per EV=0: 320/500 = 64% → serve P(SPCX < $165) ≥ 64%
```
Vantaggio: monetizza l'IV alta invece di pagarla; guadagna anche se SPCX sale poco, stalla o scende. Svantaggio: rischio massimo maggiore del guadagno (1,78:1). Scegliere B oppure B2, **mai entrambe** (somma rischi oltre il cap di tranche).

### Variante B3 — esplicitamente esclusa: iron condor
Con €2.000, un condor (4 leg) genera ~$8 di commissioni round-trip e richiede gestione attiva su un titolo senza storia di prezzo. Rapporto complessità/beneficio insensato a questa scala. Rivalutare solo a capitale ≥ €10k.

---

## STRATEGIA C — Riserva di opzionalità: cash (€400, 20%)

### Perché il cash è una posizione
Dopo la trimestrale di agosto esisterà informazione che oggi non esiste: burn xAI reale, comportamento effettivo degli insider, reazione del prezzo. Chi ha cash a quel punto può:
1. **Comprare SPCX dopo un calo del 35-45%** verso il fair value Morningstar ($780B ≈ $60-77/azione equivalente): a quel prezzo il rischio/rendimento long si inverte.
2. **Raddoppiare la strategia B** (un secondo spread su scadenza ottobre/novembre) se la tesi si conferma con momentum.
3. **Non fare nulla** se nessuna condizione si verifica — esito perfettamente accettabile.

### Parcheggio
- Tenere in EUR sul conto IBKR (nessun rischio cambio) oppure convertire in USD solo al momento dell'uso.
- Non investirlo "nel frattempo" in altro: la sua funzione è essere disponibile in 24h.

---

## Riepilogo portafoglio — scenari a 6 mesi (al netto di ~€20 di attrito)

| Scenario | Prob. soggettiva | A (GOOGL) | B (spread) | C (cash) | **Totale** |
|---|---|---|---|---|---|
| SPCX -30%+ ad agosto, mercato regge | 30% | ~€0 | +€260 | 0 | **+€240** |
| SPCX stalla (±10%), mercato regge | 30% | ~€0 | -€100/-€205 | 0 | **-€120/-€225** |
| SPCX vola (+40%+), mercato sale | 25% | +€60 | -€205 | 0 | **-€145** |
| Mercato generale -15% | 15% | -€190 | +€150 | 0 | **-€60** |

**EV ponderato ≈ -€25/+€25 — statisticamente zero.** Il piano non è una macchina da soldi: è un'esposizione a perdita massima nota (~€385-425, 19-21%) con guadagno massimo ~€300 e apprendimento del ciclo IPO-lockup. Se l'EV zero non è accettabile, l'alternativa razionale è: 100% strategia A oppure 100% fuori.
