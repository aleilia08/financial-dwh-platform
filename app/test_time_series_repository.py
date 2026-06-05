from datetime import datetime

from app.dal import time_series_repository as time_series_repository_module
from app.dal.time_series_repository import TimeSeriesRepository
from tests_support import FakeCollection, FakeDatabase


def test_create_time_series_record_inserts_new_record(monkeypatch):
    collection = FakeCollection(find_one_result=None, inserted_id="ts-1")
    monkeypatch.setattr(
        time_series_repository_module,
        "db",
        FakeDatabase({"time_series": collection})
    )

    repo = TimeSeriesRepository()
    payload = {
        "asset_id": "AAPL",
        "source_id": "yfinance",
        "business_date": "2026-05-01",
        "values": {"close": 213.2}
    }

    inserted_id = repo.create_time_series_record(payload)

    assert inserted_id == "ts-1"
    assert len(collection.inserted_documents) == 1
    assert collection.inserted_documents[0]["asset_id"] == "AAPL"
    assert isinstance(collection.inserted_documents[0]["system_date"], datetime)


def test_create_time_series_record_rejects_duplicates(monkeypatch):
    collection = FakeCollection(find_one_result={"asset_id": "AAPL"})
    monkeypatch.setattr(
        time_series_repository_module,
        "db",
        FakeDatabase({"time_series": collection})
    )

    repo = TimeSeriesRepository()

    assert repo.create_time_series_record({
        "asset_id": "AAPL",
        "source_id": "yfinance",
        "business_date": "2026-05-01",
        "values": {"close": 213.2}
    }) is None


def test_get_time_series_sorts_and_limits_results(monkeypatch):
    collection = FakeCollection(
        find_result=[
            {"_id": 1, "asset_id": "AAPL", "business_date": "2026-05-01", "values": {"close": 213.2}},
            {"_id": 2, "asset_id": "AAPL", "business_date": "2026-05-03", "values": {"close": 216.4}},
            {"_id": 3, "asset_id": "AAPL", "business_date": "2026-05-02", "values": {"close": 214.7}},
        ]
    )
    monkeypatch.setattr(
        time_series_repository_module,
        "db",
        FakeDatabase({"time_series": collection})
    )

    repo = TimeSeriesRepository()
    results = repo.get_time_series("AAPL", limit=2, offset=0)

    assert results == [
        {"_id": "2", "asset_id": "AAPL", "business_date": "2026-05-03", "values": {"close": 216.4}},
        {"_id": "3", "asset_id": "AAPL", "business_date": "2026-05-02", "values": {"close": 214.7}},
    ]


def test_get_time_series_applies_as_of_filter(monkeypatch):
    collection = FakeCollection(find_result=[])
    monkeypatch.setattr(
        time_series_repository_module,
        "db",
        FakeDatabase({"time_series": collection})
    )

    repo = TimeSeriesRepository()
    repo.get_time_series("AAPL", limit=10, offset=0, as_of="2026-05-02")

    assert collection.queries[0][1] == {
        "asset_id": "AAPL",
        "business_date": {"$lte": "2026-05-02"}
    }