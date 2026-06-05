from datetime import datetime

from app.dal import analytics_repository as analytics_repository_module
from app.dal.analytics_repository import AnalyticsRepository
from tests_support import FakeCollection, FakeDatabase


def test_save_analytics_result_adds_timestamp_and_returns_id(monkeypatch):
    collection = FakeCollection(inserted_id="analytics-1")
    monkeypatch.setattr(
        analytics_repository_module,
        "db",
        FakeDatabase({"analytics_results": collection})
    )

    repo = AnalyticsRepository()
    payload = {"asset_id": "AAPL", "analysis_type": "trend_summary"}

    inserted_id = repo.save_analytics_result(payload)

    assert inserted_id == "analytics-1"
    assert len(collection.inserted_documents) == 1
    assert collection.inserted_documents[0]["asset_id"] == "AAPL"
    assert isinstance(collection.inserted_documents[0]["created_at"], datetime)


def test_get_analytics_by_asset_returns_documents(monkeypatch):
    collection = FakeCollection(
        find_result=[
            {"asset_id": "AAPL", "avg_close": 210.3},
            {"asset_id": "AAPL", "avg_close": 211.7}
        ]
    )
    monkeypatch.setattr(
        analytics_repository_module,
        "db",
        FakeDatabase({"analytics_results": collection})
    )

    repo = AnalyticsRepository()

    assert repo.get_analytics_by_asset("AAPL") == [
        {"asset_id": "AAPL", "avg_close": 210.3},
        {"asset_id": "AAPL", "avg_close": 211.7}
    ]