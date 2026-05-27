from app.dal.mongo_connection import db
from datetime import datetime


class TimeSeriesRepository:

    def __init__(self):
        self.collection = db["time_series"]

    def create_time_series_record(self, record_data):

        existing_record = self.collection.find_one(
            {
                "asset_id": record_data["asset_id"],
                "source_id": record_data["source_id"],
                "business_date": record_data["business_date"]
            }
        )

        if existing_record:
            return None

        record_data["system_date"] = datetime.utcnow()

        result = self.collection.insert_one(record_data)

        return str(result.inserted_id)

    def get_time_series(
        self,
        asset_id: str,
        limit: int,
        offset: int,
        as_of: str | None = None
    ):
        query = {
            "asset_id": asset_id
        }

        if as_of:
            query["business_date"] = {
                "$lte": as_of
            }

        cursor = (
            self.collection
            .find(query)
            .sort("business_date", -1)
            .skip(offset)
            .limit(limit)
        )

        results = []

        for item in cursor:
            item["_id"] = str(item["_id"])
            results.append(item)

        return results