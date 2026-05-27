from app.dal.mongo_connection import db
from datetime import datetime


class PredictionRepository:

    def __init__(self):
        self.collection = db["prediction_results"]

    def save_prediction(self, prediction_data):
        prediction_data["created_at"] = datetime.utcnow()

        result = self.collection.insert_one(prediction_data)

        return str(result.inserted_id)

    def get_predictions_by_asset(self, asset_id):

        return list(
            self.collection.find(
                {"asset_id": asset_id},
                {"_id": 0}
            )
        )