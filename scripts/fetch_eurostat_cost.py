#!/usr/bin/env python
"""Fetch Eurostat cost-of-living data into raw and ready JSON files."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.data_fetchers.eurostat import fetch_cost_of_living, parse_countries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, help="Post topic slug, e.g. is-sweden-expensive-compared-with-europe")
    parser.add_argument("--countries", required=True, help="Comma-separated ISO-3 country codes, e.g. SWE,DNK,DEU")
    parser.add_argument("--year", default="latest", help="Year such as 2023, or latest")
    args = parser.parse_args()

    result = fetch_cost_of_living(topic=args.topic, countries=parse_countries(args.countries), year=args.year)
    print(f"raw: {result.raw_path}")
    print(f"ready: {result.ready_path}")
    if result.used_fallback:
        print("warning: saved clearly marked SAMPLE fallback data because live fetching failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
