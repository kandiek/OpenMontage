#!/usr/bin/env python3
"""Fetch Eurostat purchasing power data for OpenMontage."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.data_fetchers.eurostat import (
    DEFAULT_DATASET,
    DEFAULT_PPP_CAT,
    DEFAULT_UNIT,
    EurostatError,
    EurostatQuery,
    country_to_geo,
    fetch_live,
    sample_data,
    save_output,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Eurostat cost-of-living data.")
    parser.add_argument("--country", default="SWE", help="ISO-3 country code or Eurostat geo code, e.g. SWE or SE")
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--unit", default=DEFAULT_UNIT)
    parser.add_argument("--ppp-cat", default=DEFAULT_PPP_CAT)
    parser.add_argument("--year", dest="time", default=None, help="Optional Eurostat time/year value")
    parser.add_argument("--output-dir", default="data/ready/eurostat")
    parser.add_argument("--allow-sample", action="store_true", help="Allow demo sample fallback when live fetch fails")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    query = EurostatQuery(
        dataset=args.dataset,
        unit=args.unit,
        ppp_cat=args.ppp_cat,
        geo=country_to_geo(args.country),
        time=str(args.time) if args.time else None,
    )

    try:
        data = fetch_live(query)
    except EurostatError as exc:
        if not args.allow_sample:
            print("Eurostat live fetch failed and sample fallback is disabled.", file=sys.stderr)
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Eurostat live fetch failed; using demo sample because --allow-sample was passed: {exc}", file=sys.stderr)
        data = sample_data(query)

    path = save_output(data, args.output_dir)
    label = "sample" if data.get("is_sample") else "live"
    print(f"Saved {label} Eurostat data to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
