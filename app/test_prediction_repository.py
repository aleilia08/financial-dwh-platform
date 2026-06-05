from datetime import datetime

from app.dal import prediction_repository as prediction_repository_module
from app.dal.prediction_repository import PredictionRepository
from tests_support import FakeCollection, FakeDatabase


def test_save_prediction_adds_timestamp_and_returns_id(monkeypatch):
    collection = FakeCollection(inserted_id="prediction-1")
    monkeypatch.setattr(
        prediction_repository_module,
        "db",
        FakeDatabase({"prediction_results": collection})
    )

    repo = PredictionRepository()
    payload = {"asset_id": "AAPL", "predicted_close": 218.4}

    inserted_id = repo.save_prediction(payload)

    assert inserted_id == "prediction-1"
    assert len(collection.inserted_documents) == 1
    assert collection.inserted_documents[0]["asset_id"] == "AAPL"
    assert isinstance(collection.inserted_documents[0]["created_at"], datetime)


def test_get_predictions_by_asset_returns_documents(monkeypatch):
    collection = FakeCollection(
        find_result=[
            {"asset_id": "AAPL", "predicted_close": 218.4},
            {"asset_id": "AAPL", "predicted_close": 219.2}
        ]
    )
    monkeypatch.setattr(
        prediction_repository_module,
        "db",
        FakeDatabase({"prediction_results": collection})
    )

    repo = PredictionRepository()

    assert repo.get_predictions_by_asset("AAPL") == [
        {"asset_id": "AAPL", "predicted_close": 218.4},
        {"asset_id": "AAPL", "predicted_close": 219.2}
    ]