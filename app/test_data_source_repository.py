from datetime import datetime

from app.dal import data_source_repository as data_source_repository_module
from app.dal.data_source_repository import DataSourceRepository
from tests_support import FakeCollection, FakeDatabase


def test_create_data_source_inserts_new_source(monkeypatch):
    collection = FakeCollection(find_one_result=None, inserted_id="source-1")
    monkeypatch.setattr(
        data_source_repository_module,
        "db",
        FakeDatabase({"data_sources": collection})
    )

    repo = DataSourceRepository()
    payload = {
        "source_id": "yfinance",
        "name": "Yahoo Finance",
        "provider_type": "financial_market_api",
        "description": "Historical financial market data provider",
        "attributes": ["open", "high", "low", "close", "volume"]
    }

    inserted_id = repo.create_data_source(payload)

    assert inserted_id == "source-1"
    assert len(collection.inserted_documents) == 1
    assert collection.inserted_documents[0]["source_id"] == "yfinance"
    assert isinstance(collection.inserted_documents[0]["system_date"], datetime)


def test_get_all_data_sources_returns_documents(monkeypatch):
    collection = FakeCollection(
        find_result=[
            {"source_id": "yfinance", "name": "Yahoo Finance"},
            {"source_id": "alpha_vantage", "name": "Alpha Vantage"}
        ]
    )
    monkeypatch.setattr(
        data_source_repository_module,
        "db",
        FakeDatabase({"data_sources": collection})
    )

    repo = DataSourceRepository()

    assert repo.get_all_data_sources() == [
        {"source_id": "yfinance", "name": "Yahoo Finance"},
        {"source_id": "alpha_vantage", "name": "Alpha Vantage"}
    ]


def test_get_data_source_by_id_returns_document(monkeypatch):
    collection = FakeCollection(find_one_result={"source_id": "yfinance", "name": "Yahoo Finance"})
    monkeypatch.setattr(
        data_source_repository_module,
        "db",
        FakeDatabase({"data_sources": collection})
    )

    repo = DataSourceRepository()

    assert repo.get_data_source_by_id("yfinance") == {
        "source_id": "yfinance",
        "name": "Yahoo Finance"
    }