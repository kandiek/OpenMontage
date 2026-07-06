"""Small Eurostat fetcher for posting-first cost-of-living videos.

Codex writes this code; humans run it in Codespaces and commit the saved JSON.
Tests should mock HTTP and must not hit Eurostat live.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
DEFAULT_DATASET = "prc_ppp_ind"
DEFAULT_INDICATOR = "PLI_EU27_2020"
DEFAULT_COICOP = "CP00"
COUNTRY_NAMES = {
    "AUT": "Austria", "BEL": "Belgium", "BGR": "Bulgaria", "HRV": "Croatia",
    "CYP": "Cyprus", "CZE": "Czechia", "DNK": "Denmark", "EST": "Estonia",
    "FIN": "Finland", "FRA": "France", "DEU": "Germany", "GRC": "Greece",
    "HUN": "Hungary", "IRL": "Ireland", "ITA": "Italy", "LVA": "Latvia",
    "LTU": "Lithuania", "LUX": "Luxembourg", "MLT": "Malta", "NLD": "Netherlands",
    "POL": "Poland", "PRT": "Portugal", "ROU": "Romania", "SVK": "Slovakia",
    "SVN": "Slovenia", "ESP": "Spain", "SWE": "Sweden",
}

SAMPLE_VALUES = {"SWE": 115.0, "DNK": 143.0, "DEU": 110.0, "POL": 72.0, "ROU": 58.0}


@dataclass(frozen=True)
class FetchResult:
    raw_path: Path
    ready_path: Path
    used_fallback: bool


def parse_countries(countries: str | list[str]) -> list[str]:
    if isinstance(countries, str):
        values = countries.split(",")
    else:
        values = countries
    parsed = [value.strip().upper() for value in values if value.strip()]
    if not parsed:
        raise ValueError("At least one country code is required.")
    return parsed


def eurostat_url(dataset: str = DEFAULT_DATASET) -> str:
    return f"{EUROSTAT_BASE_URL}/{dataset}"


def fetch_cost_of_living(
    *,
    topic: str,
    countries: list[str],
    year: str | int = "latest",
    raw_dir: str | Path = "data/raw/eurostat",
    ready_dir: str | Path = "data/ready/eurostat",
    timeout: int = 30,
) -> FetchResult:
    """Fetch Eurostat price-level index data and save raw + chart-ready JSON.

    Falls back to clearly marked sample data if the public request fails or the
    mocked/live response cannot be converted into chart rows.
    """
    countries = parse_countries(countries)
    raw_dir = Path(raw_dir)
    ready_dir = Path(ready_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    ready_dir.mkdir(parents=True, exist_ok=True)

    params = {
        "format": "JSON",
        "lang": "en",
        "ppp_cat": DEFAULT_INDICATOR,
        "coicop": DEFAULT_COICOP,
        "geo": countries,
    }
    if str(year).lower() != "latest":
        params["time"] = str(year)

    raw_path = raw_dir / f"{topic}-{int(time.time())}.raw.json"
    ready_path = ready_dir / f"{topic}.json"

    try:
        response = requests.get(eurostat_url(), params=params, timeout=timeout)
        response.raise_for_status()
        raw_payload = response.json()
        raw_path.write_text(json.dumps(raw_payload, indent=2, sort_keys=True), encoding="utf-8")
        ready_payload = build_chart_ready(topic=topic, countries=countries, requested_year=year, raw=raw_payload)
        used_fallback = False
    except Exception as exc:  # noqa: BLE001 - fallback is intentional for manual Codespaces runs.
        raw_payload = {"error": str(exc), "sample_fallback_used": True, "request": {"url": eurostat_url(), "params": params}}
        raw_path.write_text(json.dumps(raw_payload, indent=2, sort_keys=True), encoding="utf-8")
        ready_payload = sample_chart_ready(topic=topic, countries=countries, requested_year=year, reason=str(exc))
        used_fallback = True

    ready_path.write_text(json.dumps(ready_payload, indent=2, sort_keys=True), encoding="utf-8")
    return FetchResult(raw_path=raw_path, ready_path=ready_path, used_fallback=used_fallback)


def build_chart_ready(*, topic: str, countries: list[str], requested_year: str | int, raw: dict[str, Any]) -> dict[str, Any]:
    dimensions = raw.get("dimension", {})
    values = raw.get("value", {})
    geo_index = dimensions.get("geo", {}).get("category", {}).get("index", {})
    time_index = dimensions.get("time", {}).get("category", {}).get("index", {})
    if not geo_index or not time_index or not values:
        raise ValueError("Eurostat response did not contain geo/time/value dimensions.")

    selected_year = _select_year(time_index, requested_year)
    time_count = len(time_index)
    rows = []
    for country in countries:
        geo_pos = geo_index.get(country)
        if geo_pos is None:
            continue
        flat_index = str((geo_pos * time_count) + time_index[selected_year])
        if flat_index in values:
            rows.append({
                "country": country,
                "country_name": COUNTRY_NAMES.get(country, country),
                "value": values[flat_index],
                "unit": "EU27_2020=100",
            })
    if not rows:
        raise ValueError("Eurostat response had no values for the requested countries/year.")
    rows.sort(key=lambda row: row["value"], reverse=True)
    return {
        "topic": topic,
        "source": "Eurostat public API",
        "dataset": DEFAULT_DATASET,
        "indicator": DEFAULT_INDICATOR,
        "coicop": DEFAULT_COICOP,
        "year": selected_year,
        "is_sample": False,
        "chart": {"type": "bar_chart", "title": "Price level index for household consumption", "rows": rows},
    }


def sample_chart_ready(*, topic: str, countries: list[str], requested_year: str | int, reason: str) -> dict[str, Any]:
    rows = [{"country": c, "country_name": COUNTRY_NAMES.get(c, c), "value": SAMPLE_VALUES.get(c, 100.0), "unit": "SAMPLE_EU27_2020=100"} for c in countries]
    rows.sort(key=lambda row: row["value"], reverse=True)
    return {
        "topic": topic,
        "source": "SAMPLE FALLBACK DATA - not live Eurostat data",
        "dataset": DEFAULT_DATASET,
        "indicator": DEFAULT_INDICATOR,
        "coicop": DEFAULT_COICOP,
        "year": "sample-latest" if str(requested_year).lower() == "latest" else str(requested_year),
        "is_sample": True,
        "sample_reason": reason,
        "chart": {"type": "bar_chart", "title": "Sample price level index for household consumption", "rows": rows},
    }


def _select_year(time_index: dict[str, int], requested_year: str | int) -> str:
    if str(requested_year).lower() == "latest":
        return max(time_index, key=lambda year: int(year))
    year = str(requested_year)
    if year not in time_index:
        raise ValueError(f"Year {year} not found in Eurostat response.")
    return year
