#!/usr/bin/env python3
"""
Detect changes to the official PEP 8 document and report impacted rules.
Run from backend dir: python scripts/detect_pep8_changes.py [--accept]
Requires: pip install -r requirements.txt (requests, beautifulsoup4)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Run from backend/ so app is importable
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import requests
from bs4 import BeautifulSoup

from app.pep8_map import PEP8_URL, get_section_fragment_to_codes, get_tracked_section_fragments

BASELINE_PATH = BACKEND_ROOT / "data" / "pep8_baseline.json"


def fetch_pep8_html() -> str:
    r = requests.get(PEP8_URL, timeout=30)
    r.raise_for_status()
    return r.text


def extract_section_text(soup: BeautifulSoup, section_id: str) -> str:
    """Get normalized text content of the section with id=section_id."""
    el = soup.find(id=section_id)
    if not el:
        return ""
    # Include following siblings until next heading with id
    parts = [el.get_text(separator=" ", strip=True)]
    for sib in el.find_next_siblings():
        if sib.name in ("h1", "h2", "h3", "h4") and sib.get("id"):
            break
        parts.append(sib.get_text(separator=" ", strip=True))
    text = " ".join(parts)
    return re.sub(r"\s+", " ", text).strip()


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_baseline() -> dict | None:
    if not BASELINE_PATH.exists():
        return None
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_baseline(data: dict) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser(description="Detect PEP 8 spec changes and report impacted rules")
    ap.add_argument("--accept", action="store_true", help="Update baseline to current fetch (after you review)")
    args = ap.parse_args()

    fragments = get_tracked_section_fragments()
    fragment_to_codes = get_section_fragment_to_codes()

    try:
        html = fetch_pep8_html()
    except requests.RequestException as e:
        print(f"Failed to fetch {PEP8_URL}: {e}", file=sys.stderr)
        return 1

    soup = BeautifulSoup(html, "html.parser")
    current = {"revision_date": datetime.utcnow().strftime("%Y-%m-%d"), "sections": {}}
    for frag in fragments:
        text = extract_section_text(soup, frag)
        current["sections"][frag] = hash_text(text) if text else ""

    baseline = load_baseline()
    if not baseline:
        print("No baseline found. Run with --accept to create one.")
        if args.accept:
            save_baseline(current)
            print("Baseline created at data/pep8_baseline.json")
        return 0

    changed = []
    for frag in fragments:
        old_h = baseline.get("sections", {}).get(frag)
        new_h = current["sections"].get(frag)
        if old_h != new_h:
            codes = fragment_to_codes.get(frag, [])
            changed.append((frag, codes))

    if not changed:
        print("No PEP 8 section changes detected.")
        return 0

    print("PEP 8 changes detected (review and update app/pep8_map.py if needed):\n")
    for frag, codes in changed:
        codes_str = ", ".join(sorted(codes)) if codes else "(no mapped rules)"
        print(f"  Section #{frag}")
        print(f"    Impacted rule codes: {codes_str}\n")
    print("Suggested: update PEP8_DATE and PEP8_REVISION in .env to current revision, then restart backend.")
    if args.accept:
        save_baseline(current)
        print("\nBaseline updated (data/pep8_baseline.json).")
    else:
        print("\nRun with --accept to update the baseline after you have updated the rule mapping.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
