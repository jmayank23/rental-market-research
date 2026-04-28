#!/bin/bash
# Run fetch + train + process for each POI in the list.
# Logs per-POI status to scripts/run_log.txt; final summary to scripts/run_summary.txt.

set -uo pipefail

SLUGS=(
  birmingham-al
  huntsville-al
  montgomery-al
  memphis-tn
  chattanooga-tn
  knoxville-tn
  jackson-ms
  little-rock-ar
  louisville-ky
  lexington-ky
)

LOG=scripts/run_log.txt
mkdir -p scripts
: > "$LOG"

echo "=== Cash-flow POI sweep ===" | tee -a "$LOG"
date -u | tee -a "$LOG"

for slug in "${SLUGS[@]}"; do
  echo | tee -a "$LOG"
  echo ">>> $slug" | tee -a "$LOG"

  if [ -f "outputs/$slug/sale_listings.json" ]; then
    echo "  fetch: cached" | tee -a "$LOG"
  else
    echo "  fetch..." | tee -a "$LOG"
    uv run python fetch_listings.py --poi "$slug" >> "$LOG" 2>&1 || { echo "  FETCH FAILED" | tee -a "$LOG"; continue; }
    echo "  fetch ok" | tee -a "$LOG"
  fi

  if [ -f "outputs/$slug/rent_model.joblib" ]; then
    echo "  train: cached" | tee -a "$LOG"
  else
    echo "  train (lgbm)..." | tee -a "$LOG"
    uv run python rent_model.py --poi "$slug" --model lgbm >> "$LOG" 2>&1 || { echo "  TRAIN FAILED" | tee -a "$LOG"; continue; }
    echo "  train ok" | tee -a "$LOG"
  fi

  echo "  process..." | tee -a "$LOG"
  uv run python process_listings.py --poi "$slug" >> "$LOG" 2>&1 || { echo "  PROCESS FAILED" | tee -a "$LOG"; continue; }
  echo "  process ok" | tee -a "$LOG"

  # Summary line per POI
  python3 - "$slug" >> "$LOG" 2>&1 << 'PY'
import csv, json, sys
slug = sys.argv[1]
m = json.load(open(f"outputs/{slug}/rent_model_metrics.json"))
rows = list(csv.DictReader(open(f"outputs/{slug}/selected_properties.csv")))
ratios = sorted((float(r["mortgageCoverageRatio"]) for r in rows), reverse=True)
above_1 = sum(1 for r in ratios if r > 1.0)
top = ratios[:3] if ratios else []
print(f"  metrics: MAE=${m['val_metrics']['mae']:.0f}  R2={m['val_metrics']['r2']:.2f}")
print(f"  selected: {len(rows)}  above 1.0: {above_1}  top3 ratios: {[round(r,3) for r in top]}")
PY

done

echo | tee -a "$LOG"
echo "Done." | tee -a "$LOG"
