#!/bin/bash
# Build the report: run the lopos-brand generator from the repo root, then render preview PNGs.
# Portable (resolves the repo root relative to this script). Stable command -> easy to allow-list.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 make_w2w_report.py
rm -f /tmp/rep-*.png
pdftoppm -png -r 110 "$ROOT/lopos_w2w_report.pdf" /tmp/rep
ls /tmp/rep-*.png
