#!/opt/homebrew/bin/python3.11
"""
Generate remaining Shay carousels that haven't been produced yet.
Skips any carousel that already has a _carousel.json in the output folder.
"""
import os
import sys
import json
import time
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv
load_dotenv(BASE / ".env")

# Import everything from the batch script
from execution.shay_30day_batch import CAROUSELS, generate_carousel, OUTPUT

already_done = {p.stem.replace("_carousel", "") for p in OUTPUT.glob("*_carousel.json")}

remaining = [c for c in CAROUSELS if c["id"] not in already_done]

print(f"Already generated: {len(already_done)}")
print(f"Remaining to generate: {len(remaining)}")
print(f"IDs: {[c['id'] for c in remaining]}\n")

total = len(remaining)
for i, carousel in enumerate(remaining):
    generate_carousel(carousel, i, total)
    if i < total - 1:
        print("  Cooling down 5s...")
        time.sleep(5)

print("\nDone. All remaining Shay carousels generated.")
