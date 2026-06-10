#!/usr/bin/env bash
# Smoke-test suite: every module must print TEST OK. Usage: tools/run_tests.sh [python-bin]
set -u
PY="${1:-.venv/bin/python}"
cd "$(dirname "$0")/.."
MODULES="src.connectors.market_data src.connectors.edgar src.connectors.polymarket \
src.connectors.fred src.connectors.hackernews src.connectors.wikipedia \
src.risk.metrics src.risk.montecarlo src.research.lockup_study \
src.research.dist_validation src.research.signal_quality src.viz"
FAIL=0
for m in $MODULES; do
  if "$PY" -m "$m" 2>&1 | grep -q "TEST OK"; then
    echo "PASS $m"
  else
    echo "FAIL $m"
    FAIL=1
  fi
done
[ $FAIL -eq 0 ] && echo "SUITE: 12/12 PASS" || { echo "SUITE: FAILURES"; exit 1; }
