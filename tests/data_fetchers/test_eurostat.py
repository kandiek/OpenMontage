import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.data_fetchers import eurostat
from lib.data_fetchers.eurostat import EurostatError, EurostatQuery, country_to_geo, fetch_live, sample_data


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.urls = []

    def get(self, url, timeout=30):
        self.urls.append(url)
        return self.responses.pop(0)


def metadata(times=("2023",)):
    return {
        "id": ["unit", "ppp_cat", "geo", "time"],
        "dimension": {
            "unit": {"category": {"index": {"PLI_EU27_2020": 0}}},
            "ppp_cat": {"category": {"index": {"E011": 0}}},
            "geo": {"category": {"index": {"SE": 0, "DK": 1, "DE": 2, "PL": 3, "RO": 4}}},
            "time": {"category": {"index": {time: i for i, time in enumerate(times)}}},
        },
    }


def live_payload():
    payload = metadata(("2023",))
    payload["value"] = {"0": 101.2}
    return payload


def test_valid_country_conversion():
    assert country_to_geo("SWE") == "SE"
    assert country_to_geo("DNK") == "DK"
    assert country_to_geo("DEU") == "DE"
    assert country_to_geo("POL") == "PL"
    assert country_to_geo("ROU") == "RO"
    assert country_to_geo("SE") == "SE"


def test_failed_live_fetch_without_allow_sample_raises_with_url_and_dimensions():
    session = FakeSession([
        FakeResponse(200, metadata()),
        FakeResponse(200, metadata()),
        FakeResponse(400, {"error": "bad request"}),
    ])

    with pytest.raises(EurostatError) as exc:
        fetch_live(EurostatQuery(geo="SE", time="2023"), session=session)

    message = str(exc.value)
    assert "Failed URL:" in message
    assert "Dataset: prc_ppp_ind" in message
    assert "unit=PLI_EU27_2020" in message
    assert "ppp_cat=E011" in message
    assert "geo=SE" in message
    assert "time=2023" in message


def test_script_uses_sample_only_with_allow_sample(monkeypatch, tmp_path, capsys):
    def fail_live(query):
        raise EurostatError("boom")

    monkeypatch.setattr(eurostat, "fetch_live", fail_live)
    monkeypatch.setattr("scripts.fetch_eurostat_cost.fetch_live", fail_live)
    monkeypatch.setattr(
        "sys.argv",
        ["fetch_eurostat_cost.py", "--country", "SWE", "--output-dir", str(tmp_path)],
    )
    from scripts.fetch_eurostat_cost import main

    assert main() == 1
    assert not list(tmp_path.glob("*.json"))

    monkeypatch.setattr(
        "sys.argv",
        ["fetch_eurostat_cost.py", "--country", "SWE", "--output-dir", str(tmp_path), "--allow-sample"],
    )
    assert main() == 0
    assert (tmp_path / "prc_ppp_ind_SE.json").exists()
    assert "using demo sample" in capsys.readouterr().err


def test_output_metadata_marks_sample_vs_live():
    session = FakeSession([
        FakeResponse(200, metadata()),
        FakeResponse(200, metadata()),
        FakeResponse(200, live_payload()),
    ])
    live = fetch_live(EurostatQuery(geo="SE", time="2023"), session=session)
    sample = sample_data(EurostatQuery(geo="SE", time="2023"))

    assert live["is_sample"] is False
    assert live["source"] == "Eurostat live API"
    assert live["dimensions"]["geo"] == "SE"
    assert sample["is_sample"] is True
