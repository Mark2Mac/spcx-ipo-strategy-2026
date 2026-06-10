# 06 — Registro operazioni (trade journal)

Regola: **una riga PRIMA di ogni ordine** (sezione 2), aggiornamento settimanale (sezione 3), retrospettiva a chiusura (sezione 4). Nessuna riga → nessun ordine (regola 5 del file 04).

## 1. Stato del conto

| Data | Valore totale (€) | vs iniziale | Drawdown | Note |
|---|---|---|---|---|
| 2026-06-10 | 2.000,00 | 0% | 0% | Piano creato. Nessuna posizione |

## 2. Ordini (compilare PRIMA dell'invio)

### Template
```
ID:               #001
Data/ora:
Strumento:        (es. GOOGL azioni / SPCX put spread 140-135 set26)
Direzione:        long / short
Tesi (1 frase):
Invalidazione:    (condizione oggettiva che chiude il trade)
Rischio massimo:  € ____ ( ___% del capitale — deve essere ≤10,5%)
Take profit:      (livello e regola)
Ordine:           tipo limit, prezzo, validità
Stato emotivo:    (1 parola onesta: calmo / FOMO / vendetta / noia)
```

> Se "Stato emotivo" ≠ calmo → regola delle 24 ore (file 04, regola 6).

### Ordini effettuati

_(vuoto — popolare in Fase 1)_

## 3. Check settimanali (venerdì, 15 min)

| Data | SPCX spot | IV ATM set | Valore spread | GOOGL | Valore conto | Azione |
|---|---|---|---|---|---|---|
| | | | | | | |

## 4. Trade chiusi — retrospettiva

### Template
```
ID:                #
P&L lordo:         €
P&L netto (26%):   €
Regole rispettate: sì/no (quali violate)
La tesi era giusta? sì/no/parzialmente
Il processo era giusto? sì/no
Lezione (1 frase):
```

## 5. Eventi di mercato annotati

| Data | Evento | Dato | Implicazione per il piano |
|---|---|---|---|
| 2026-06-11 | Pricing IPO | atteso $135 | |
| 2026-06-12 | Day-1: open/high/close/volume | | |
| | Quotazione opzioni SPCX | | inizio tracking IV |
| | Inclusione Nasdaq-100 | | |
| | Data trimestrale annunciata | | aggiornare Fase 4 del cronoprogramma |
| | Trimestrale: burn xAI / sub Starlink / guidance | | conferma o falsificazione tesi |
| | T+2: volumi vendita insider | | |

## 6. Promemoria scadenze

- [ ] ~19-24 giu: verificare quotazione opzioni
- [ ] 6-17 lug: finestra ingresso strategia B (condizioni nel file 03, Fase 2)
- [ ] 16 set: decisione finale spread (MAI portarlo a scadenza fra gli strike)
- [ ] ~25 ott: giorno 135, revisione totale
- [ ] dic: ottimizzazione fiscale di fine anno (file 05)
- [ ] mar 2027: documenti per dichiarazione (RW, RT, RM, IVAFE)
