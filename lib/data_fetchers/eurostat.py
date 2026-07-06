"""Small Eurostat fetcher for posting-first cost-of-living charts.

Codex writes this code; Codespaces runs it and commits saved JSON; Remotion reads
``data/ready/eurostat/*.json`` without needing live internet access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable

import requests

EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
DEFAULT_DATASET = "prc_ppp_ind"
DEFAULT_UNIT = "PLI_EU27_2020"
DEFAULT_PPP_CAT = "E011"  # Household final consumption expenditure price level index.

COUNTRY_ALPHA3_TO_EUROSTAT = {
    "AUT": "AT", "BEL": "BE", "BGR": "BG", "HRV": "HR", "CYP": "CY",
    "CZE": "CZ", "DNK": "DK", "EST": "EE", "FIN": "FI", "FRA": "FR",
    "DEU": "DE", "GRC": "EL", "HUN": "HU", "IRL": "IE", "ITA": "IT",
    "LVA": "LV", "LTU": "LT", "LUX": "LU", "MLT": "MT", "NLD": "NL",
    "POL": "PL", "PRT": "PT", "ROU": "RO", "SVK": "SK", "SVN": "SI",
    "ESP": "ES", "SWE": "SE", "NOR": "NO", "ISL": "IS", "CHE": "CH",
}
EUROSTAT_TO_ALPHA3 = {v: k for k, v in COUNTRY_ALPHA3_TO_EUROSTAT.items()}


class EurostatFetchError(RuntimeError):
    """Raised when Eurostat data cannot be fetched or parsed."""


@dataclass(frozen=True)
class EurostatCostFetcher:
    """Fetch Eurostat price-level-index data and save raw + chart-ready JSON."""

    raw_dir: Path = Path("data/raw/eurostat")
    ready_dir: Path = Path("data/ready/eurostat")
    base_url: str = EUROSTAT_BASE_URL
    timeout: int = 30
    session: Any = requests

    def fetch_topic(
        self,
        *,
        topic: str,
        countries: Iterable[str],
        year: str | int = "latest",
    ) -> dict[str, Any]:
        """Fetch a topic and return the chart-ready payload that was written."""

        country_list = [country.strip().upper() for country in countries if country.strip()]
        if not country_list:
            raise ValueError("At least one country is required")

        raw_payloads = []
        rows = []
        for country in country_list:
            geo = normalize_country(country)
            payload = self._get_country_payload(geo=geo, year=year)
            raw_payloads.append({"country": country, "geo": geo, "response": payload})
            rows.append(parse_price_level(payload, requested_country=country, geo=geo, requested_year=year))

        rows.sort(key=lambda row: row["value"], reverse=True)
        for index, row in enumerate(rows, start=1):
            row["rank_in_result"] = index

        fetched_at = datetime.now(timezone.utc).isoformat()
        ready = {
            "topic": topic,
            "source": "Eurostat",
            "dataset": DEFAULT_DATASET,
            "indicator": "Price level index for household final consumption expenditure",
            "unit": DEFAULT_UNIT,
            "ppp_cat": DEFAULT_PPP_CAT,
            "requested_year": str(year),
            "is_sample": False,
            "fetched_at": fetched_at,
            "countries": rows,
        }

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.ready_dir.mkdir(parents=True, exist_ok=True)
        raw_path = self.raw_dir / f"{topic}.raw.json"
        ready_path = self.ready_dir / f"{topic}.json"
        write_json(raw_path, {"topic": topic, "fetched_at": fetched_at, "responses": raw_payloads})
        write_json(ready_path, ready)
        return ready

    def _get_country_payload(self, *, geo: str, year: str | int) -> dict[str, Any]:
        params: dict[str, str] = {
            "format": "JSON",
            "lang": "en",
            "unit": DEFAULT_UNIT,
            "ppp_cat": DEFAULT_PPP_CAT,
            "geo": geo,
        }
        if str(year).lower() != "latest":
            params["time"] = str(year)

        response = self.session.get(
            f"{self.base_url}/{DEFAULT_DATASET}", params=params, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


def normalize_country(country: str) -> str:
    code = country.strip().upper()
    if len(code) == 2:
        return "EL" if code == "GR" else code
    if code in COUNTRY_ALPHA3_TO_EUROSTAT:
        return COUNTRY_ALPHA3_TO_EUROSTAT[code]
    raise ValueError(f"Unsupported country code: {country}")


def parse_price_level(
    payload: dict[str, Any], *, requested_country: str, geo: str, requested_year: str | int
) -> dict[str, Any]:
    """Parse a Eurostat JSON-stat response for one country into a chart row."""

    values = payload.get("value") or {}
    if not values:
        raise EurostatFetchError(f"Eurostat returned no values for {requested_country}")

    dimensions = payload.get("dimension", {})
    time_categories = dimensions.get("time", {}).get("category", {}).get("index", {})
    if not time_categories:
        raise EurostatFetchError(f"Eurostat returned no time dimension for {requested_country}")

    index_to_year = {str(index): year for year, index in time_categories.items()}
    value_key = max(values, key=lambda key: int(key) if str(key).isdigit() else -1)
    year = index_to_year.get(str(value_key), str(requested_year))
    value = values[value_key]
    if value is None:
        raise EurostatFetchError(f"Eurostat returned a null value for {requested_country}")

    return {
        "country": requested_country,
        "geo": geo,
        "alpha3": EUROSTAT_TO_ALPHA3.get(geo, requested_country),
        "year": str(year),
        "value": float(value),
        "label": f"{float(value):.1f}",
    }


def sample_ready_payload(*, topic: str, countries: Iterable[str], year: str | int) -> dict[str, Any]:
    """Build clearly marked fallback data for offline demos only."""

    sample_values = {"SWE": 124.0, "DNK": 143.0, "DEU": 109.0, "POL": 72.0, "ROU": 61.0}
    rows = []
    for code in [c.strip().upper() for c in countries if c.strip()]:
        geo = normalize_country(code)
        value = sample_values.get(code, 100.0)
        rows.append({
            "country": code,
            "geo": geo,
            "alpha3": EUROSTAT_TO_ALPHA3.get(geo, code),
            "year": "2023" if str(year).lower() == "latest" else str(year),
            "value": value,
            "label": f"{value:.1f}",
        })
    rows.sort(key=lambda row: row["value"], reverse=True)
    for index, row in enumerate(rows, start=1):
        row["rank_in_result"] = index
    return {
        "topic": topic,
        "source": "SAMPLE FALLBACK - not live Eurostat data",
        "dataset": DEFAULT_DATASET,
        "indicator": "Price level index for household final consumption expenditure",
        "unit": DEFAULT_UNIT,
        "ppp_cat": DEFAULT_PPP_CAT,
        "requested_year": str(year),
        "is_sample": True,
        "sample_note": "Generated only because live fetching failed. Do not present as live data.",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "countries": rows,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
