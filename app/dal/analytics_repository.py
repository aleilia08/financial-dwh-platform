from app.dal.mongo_connection import db
from datetime import datetime


class AnalyticsRepository:

    def __init__(self):
        self.collection = db["analytics_results"]

    def save_analytics_result(self, analytics_data):
        analytics_data["created_at"] = datetime.utcnow()

        result = self.collection.insert_one(analytics_data)

        return str(result.inserted_id)

    def get_analytics_by_asset(self, asset_id):

        return list(
            self.collection.find(
                {"asset_id": asset_id},
                {"_id": 0}
            )
        )