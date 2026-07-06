from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.data_fetchers.eurostat import fetch_cost_of_living, parse_countries


class MockResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self.payload


def eurostat_payload():
    return {
        "dimension": {
            "geo": {"category": {"index": {"SWE": 0, "DNK": 1, "DEU": 2}}},
            "time": {"category": {"index": {"2022": 0, "2023": 1}}},
        },
        "value": {
            "0": 111,
            "1": 115,
            "2": 140,
            "3": 143,
            "4": 108,
            "5": 110,
        },
    }


def test_parse_countries():
    assert parse_countries("swe, DNK, deu") == ["SWE", "DNK", "DEU"]


def test_fetch_saves_raw_and_ready_with_mocked_http(monkeypatch, tmp_path):
    calls = []

    def mock_get(url, params, timeout):
        calls.append({"url": url, "params": params, "timeout": timeout})
        return MockResponse(eurostat_payload())

    monkeypatch.setattr("lib.data_fetchers.eurostat.requests.get", mock_get)
    result = fetch_cost_of_living(
        topic="sweden-vs-denmark-germany",
        countries=["SWE", "DNK", "DEU"],
        year="latest",
        raw_dir=tmp_path / "raw",
        ready_dir=tmp_path / "ready",
    )

    assert result.used_fallback is False
    assert result.raw_path.exists()
    assert result.ready_path.exists()
    assert calls[0]["params"]["geo"] == ["SWE", "DNK", "DEU"]

    ready = json.loads(result.ready_path.read_text())
    assert ready["is_sample"] is False
    assert ready["year"] == "2023"
    assert [row["country"] for row in ready["chart"]["rows"]] == ["DNK", "SWE", "DEU"]


def test_fetch_writes_marked_sample_fallback_on_http_failure(monkeypatch, tmp_path):
    def mock_get(url, params, timeout):
        raise RuntimeError("network unavailable in test")

    monkeypatch.setattr("lib.data_fetchers.eurostat.requests.get", mock_get)
    result = fetch_cost_of_living(
        topic="is-sweden-expensive-compared-with-europe",
        countries=["SWE", "POL"],
        year="latest",
        raw_dir=tmp_path / "raw",
        ready_dir=tmp_path / "ready",
    )

    ready = json.loads(result.ready_path.read_text())
    raw = json.loads(result.raw_path.read_text())
    assert result.used_fallback is True
    assert ready["is_sample"] is True
    assert "SAMPLE FALLBACK DATA" in ready["source"]
    assert raw["sample_fallback_used"] is True
