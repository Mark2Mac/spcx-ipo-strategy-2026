# Checkpoint index

One frozen snapshot per milestone. Never modified after creation — git history is the witness.

| Checkpoint | Git HEAD | Contents | Milestone note |
|---|---|---|---|
| 2026-06-10-baseline | 1ec4524e | 9 artifacts | T-2 state: everything the predictions were based on |
| 2026-06-11-T-1-pricing | b2e88482 | 10 artifacts | T-1: final pre-debut odds + benchmark closes |
| 2026-06-11-auto | c74fb448 | 11 artifacts | Evening (UTC) snapshot. An earlier same-day auto run (HEAD d0bec3b5) was overwritten in place before the tag-collision fix; its frozen data survives in git at commit 6faf899. |
| 2026-06-13-ci-verify | 416d6ba2 | 13 artifacts | |
| 2026-06-15-day1-score | 86dd7d7b | 13 artifacts | |
| 2026-06-15-day1-rescore | f43d4a26 | 13 artifacts | |
| 2026-06-15-ci-node24-verify | 880dd244 | 13 artifacts | |
| 2026-06-15-harden-verify | eace4f09 | 13 artifacts | |
| 2026-06-15-2314-auto | f741f9c0 | 13 artifacts | |
| 2026-06-18-2314-auto | 397174b3 | 13 artifacts | |
| 2026-06-22-2259-auto | 9d4609b7 | 13 artifacts | |
| 2026-06-25-2253-auto | ea43b509 | 13 artifacts | |
| 2026-06-29-2234-auto | 83bbc9f5 | 13 artifacts | |
| 2026-07-02-2233-auto | c7556f1d | 13 artifacts | |
| 2026-07-06-entry-window | 301817a2 | 14 artifacts | Strategy-B entry window (Jul 6-17). SPCX identity resolved (SpaceX live, `identity_suspect:false`); Aug ATM IV ~87% archived as `derived_atm_iv` term structure + full `spcx_ohlcv.parquet`. `montecarlo.json` is the frozen baseline MC (like every snapshot); the realized-param re-run and stand-down decision live in `notebooks/07_entry_decision`. IV > 55% gate → **no entry, stand-down**. |
