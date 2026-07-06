import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.data_fetchers.eurostat import EurostatCostFetcher, normalize_country, sample_ready_payload


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        geo = params["geo"]
        values = {"SE": 124.2, "DK": 143.7, "DE": 109.1}[geo]
        return FakeResponse({
            "value": {"0": values},
            "dimension": {"time": {"category": {"index": {"2023": 0}}}},
        })


def test_normalize_country_accepts_alpha3_and_eurostat_codes():
    assert normalize_country("SWE") == "SE"
    assert normalize_country("DNK") == "DK"
    assert normalize_country("DE") == "DE"


def test_fetch_topic_writes_raw_and_ready_json(tmp_path):
    session = FakeSession()
    fetcher = EurostatCostFetcher(
        raw_dir=tmp_path / "raw",
        ready_dir=tmp_path / "ready",
        session=session,
    )

    ready = fetcher.fetch_topic(
        topic="sweden-vs-denmark-germany",
        countries=["SWE", "DNK", "DEU"],
        year="latest",
    )

    assert len(session.calls) == 3
    assert all("time" not in call["params"] for call in session.calls)
    assert ready["is_sample"] is False
    assert ready["countries"][0]["country"] == "DNK"
    assert (tmp_path / "raw" / "sweden-vs-denmark-germany.raw.json").exists()
    assert (tmp_path / "ready" / "sweden-vs-denmark-germany.json").exists()


def test_fetch_topic_passes_specific_year(tmp_path):
    session = FakeSession()
    fetcher = EurostatCostFetcher(raw_dir=tmp_path / "raw", ready_dir=tmp_path / "ready", session=session)

    fetcher.fetch_topic(topic="example", countries=["SWE"], year="2023")

    assert session.calls[0]["params"]["time"] == "2023"


def test_sample_payload_is_clearly_marked():
    sample = sample_ready_payload(topic="example", countries=["SWE", "DEU"], year="latest")

    assert sample["is_sample"] is True
    assert "SAMPLE FALLBACK" in sample["source"]
    assert "Do not present as live data" in sample["sample_note"]
