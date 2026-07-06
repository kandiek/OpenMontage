"""Small Eurostat JSON-stat fetcher with dimension validation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
import json

import requests

EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
DEFAULT_DATASET = "prc_ppp_ind"
DEFAULT_UNIT = "PLI_EU27_2020"
DEFAULT_PPP_CAT = "E011"
COUNTRY_TO_GEO = {
    "SWE": "SE",
    "DNK": "DK",
    "DEU": "DE",
    "POL": "PL",
    "ROU": "RO",
}


class EurostatError(RuntimeError):
    """Raised when Eurostat live data cannot be fetched."""


@dataclass(frozen=True)
class EurostatQuery:
    dataset: str = DEFAULT_DATASET
    unit: str = DEFAULT_UNIT
    ppp_cat: str = DEFAULT_PPP_CAT
    geo: str = "SE"
    time: str | None = None


def country_to_geo(country: str) -> str:
    """Convert supported ISO-3 country inputs to Eurostat ISO-2 geo codes."""
    value = country.strip().upper()
    return COUNTRY_TO_GEO.get(value, value)


def build_url(dataset: str, params: dict[str, Any]) -> str:
    query = urlencode([(k, v) for k, v in params.items() if v is not None])
    return f"{EUROSTAT_BASE_URL}/{dataset}?{query}"


def _request_json(session: requests.Session, url: str) -> dict[str, Any]:
    try:
        response = session.get(url, timeout=30)
    except requests.RequestException as exc:
        raise EurostatError(f"Eurostat request failed: {url} ({exc})") from exc
    if response.status_code >= 400:
        raise EurostatError(f"Eurostat request failed with HTTP {response.status_code}: {url}")
    return response.json()


def _dimension_values(payload: dict[str, Any], dimension: str) -> set[str]:
    category = payload.get("dimension", {}).get(dimension, {}).get("category", {})
    index = category.get("index", {})
    if isinstance(index, dict):
        return set(index.keys())
    return set()


def fetch_metadata(
    dataset: str,
    session: requests.Session | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fetch a compact JSON-stat response used for dimension validation."""
    session = session or requests.Session()
    params = {"lang": "en", "lastTimePeriod": 1}
    if filters:
        params.update(filters)
    url = build_url(dataset, params)
    return _request_json(session, url)


def validate_dimensions(query: EurostatQuery, metadata: dict[str, Any]) -> None:
    dataset_ids = metadata.get("id", [])
    missing_dims = [dim for dim in ("unit", "ppp_cat", "geo") if dim not in dataset_ids]
    if missing_dims:
        raise EurostatError(
            f"Dataset {query.dataset!r} is missing expected dimension(s): {', '.join(missing_dims)}"
        )

    invalid: list[str] = []
    for dim, value in (("unit", query.unit), ("ppp_cat", query.ppp_cat), ("geo", query.geo)):
        valid_values = _dimension_values(metadata, dim)
        if valid_values and value not in valid_values:
            preview = ", ".join(sorted(valid_values)[:20])
            invalid.append(f"{dim}={value!r} (valid examples: {preview})")

    if query.time is not None:
        valid_times = _dimension_values(metadata, "time") or _dimension_values(metadata, "TIME_PERIOD")
        if valid_times and query.time not in valid_times:
            invalid.append(f"time={query.time!r} (valid latest values: {', '.join(sorted(valid_times)[-10:])})")

    if invalid:
        raise EurostatError(f"Invalid Eurostat dimension value(s) for {query.dataset}: " + "; ".join(invalid))


def _extract_first_value(payload: dict[str, Any]) -> float | int | None:
    values = payload.get("value")
    if isinstance(values, dict):
        for _, value in sorted(values.items(), key=lambda item: int(item[0])):
            return value
    if isinstance(values, list):
        for value in values:
            if value is not None:
                return value
    return None


def fetch_live(query: EurostatQuery, session: requests.Session | None = None) -> dict[str, Any]:
    """Validate metadata, fetch one live Eurostat datapoint, and return normalized output."""
    session = session or requests.Session()
    try:
        metadata = fetch_metadata(query.dataset, session=session)
        validate_dimensions(EurostatQuery(query.dataset, query.unit, query.ppp_cat, query.geo, None), metadata)
        if query.time is not None:
            time_metadata = fetch_metadata(
                query.dataset,
                session=session,
                filters={
                    "unit": query.unit,
                    "ppp_cat": query.ppp_cat,
                    "geo": query.geo,
                    "lastTimePeriod": None,
                },
            )
            validate_dimensions(query, time_metadata)
    except EurostatError as exc:
        failed_url = build_url(query.dataset, {"lang": "en", "lastTimePeriod": 1})
        raise EurostatError(
            f"{exc}\nFailed URL: {failed_url}\nDataset: {query.dataset}\nDimensions: "
            f"unit={query.unit}, ppp_cat={query.ppp_cat}, geo={query.geo}, time={query.time or 'lastTimePeriod=1'}"
        ) from exc

    params = {
        "lang": "en",
        "unit": query.unit,
        "ppp_cat": query.ppp_cat,
        "geo": query.geo,
        "time": query.time,
        "lastTimePeriod": None if query.time else 1,
    }
    url = build_url(query.dataset, params)
    try:
        payload = _request_json(session, url)
    except EurostatError as exc:
        raise EurostatError(
            f"{exc}\nFailed URL: {url}\nDataset: {query.dataset}\nDimensions: "
            f"unit={query.unit}, ppp_cat={query.ppp_cat}, geo={query.geo}, time={query.time or 'lastTimePeriod=1'}"
        ) from exc

    value = _extract_first_value(payload)
    if value is None:
        raise EurostatError(
            f"Eurostat returned no value.\nFailed URL: {url}\nDataset: {query.dataset}\nDimensions: "
            f"unit={query.unit}, ppp_cat={query.ppp_cat}, geo={query.geo}, time={query.time or 'lastTimePeriod=1'}"
        )

    time_values = sorted(_dimension_values(payload, "time") or _dimension_values(payload, "TIME_PERIOD"))
    return {
        "is_sample": False,
        "source": "Eurostat live API",
        "dataset": query.dataset,
        "dimensions": {
            "unit": query.unit,
            "ppp_cat": query.ppp_cat,
            "geo": query.geo,
            "time": query.time or (time_values[-1] if time_values else None),
        },
        "request_url": url,
        "value": value,
        "raw": payload,
    }


def sample_data(query: EurostatQuery) -> dict[str, Any]:
    return {
        "is_sample": True,
        "source": "OpenMontage demo sample",
        "dataset": query.dataset,
        "dimensions": {"unit": query.unit, "ppp_cat": query.ppp_cat, "geo": query.geo, "time": query.time},
        "request_url": None,
        "value": 123.4,
    }


def save_output(data: dict[str, Any], output_dir: str | Path = "data/ready/eurostat") -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    geo = data.get("dimensions", {}).get("geo", "unknown")
    dataset = data.get("dataset", DEFAULT_DATASET)
    path = out_dir / f"{dataset}_{geo}.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path
