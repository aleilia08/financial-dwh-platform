from app.dal.prediction_repository import PredictionRepository

repo = PredictionRepository()

sample_prediction = {
    "asset_id": "AAPL",

    "model": "linear_regression",

    "prediction_date": "2026-06-01",

    "predicted_close": 218.4
}

inserted_id = repo.save_prediction(sample_prediction)

print("Inserted prediction id:", inserted_id)

predictions = repo.get_predictions_by_asset("AAPL")

print("\nPredictions:")
print(predictions)