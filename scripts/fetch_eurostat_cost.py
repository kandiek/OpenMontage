#!/usr/bin/env python3
"""Fetch Eurostat cost-of-living data for a posting topic."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.data_fetchers.eurostat import EurostatCostFetcher, sample_ready_payload, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, help="Post topic slug")
    parser.add_argument("--countries", required=True, help="Comma-separated ISO alpha-3 or Eurostat country codes")
    parser.add_argument("--year", default="latest", help="Year such as 2023, or 'latest'")
    parser.add_argument("--no-sample-fallback", action="store_true", help="Fail instead of writing sample fallback data")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    countries = [country.strip() for country in args.countries.split(",")]
    fetcher = EurostatCostFetcher()
    try:
        fetcher.fetch_topic(topic=args.topic, countries=countries, year=args.year)
    except Exception as exc:
        if args.no_sample_fallback:
            raise
        ready = sample_ready_payload(topic=args.topic, countries=countries, year=args.year)
        write_json(Path("data/ready/eurostat") / f"{args.topic}.json", ready)
        print(f"Live Eurostat fetch failed; wrote clearly marked sample fallback data: {exc}")
    print("data/raw/eurostat/")
    print(f"data/ready/eurostat/{args.topic}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
