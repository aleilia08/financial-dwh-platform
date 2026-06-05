from datetime import datetime

from app.dal import asset_repository as asset_repository_module
from app.dal.asset_repository import AssetRepository
from tests_support import FakeCollection, FakeDatabase


def test_create_asset_inserts_new_asset(monkeypatch):
    collection = FakeCollection(find_one_result=None, inserted_id="asset-1")
    monkeypatch.setattr(
        asset_repository_module,
        "db",
        FakeDatabase({"assets": collection})
    )

    repo = AssetRepository()
    payload = {"asset_id": "AAPL", "name": "Apple Inc."}

    inserted_id = repo.create_asset(payload)

    assert inserted_id == "asset-1"
    assert len(collection.inserted_documents) == 1
    assert collection.inserted_documents[0]["asset_id"] == "AAPL"
    assert isinstance(collection.inserted_documents[0]["system_date"], datetime)


def test_get_all_assets_skips_deleted_documents(monkeypatch):
    collection = FakeCollection(
        find_result=[
            {"_id": 1, "asset_id": "AAPL"},
            {"_id": 2, "asset_id": "MSFT"}
        ]
    )
    monkeypatch.setattr(
        asset_repository_module,
        "db",
        FakeDatabase({"assets": collection})
    )

    repo = AssetRepository()

    assert repo.get_all_assets(10, 0) == [
        {"_id": "1", "asset_id": "AAPL"},
        {"_id": "2", "asset_id": "MSFT"}
    ]


def test_get_asset_by_id_returns_document(monkeypatch):
    collection = FakeCollection(find_one_result={"asset_id": "AAPL", "name": "Apple Inc."})
    monkeypatch.setattr(
        asset_repository_module,
        "db",
        FakeDatabase({"assets": collection})
    )

    repo = AssetRepository()

    assert repo.get_asset_by_id("AAPL") == {"asset_id": "AAPL", "name": "Apple Inc."}