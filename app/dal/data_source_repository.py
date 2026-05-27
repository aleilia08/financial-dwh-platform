from app.dal.mongo_connection import db
from datetime import datetime


class DataSourceRepository:

    def __init__(self):
        self.collection = db["data_sources"]

    def create_data_source(self, source_data):
        existing_source = self.collection.find_one(
            {
                "source_id": source_data["source_id"]
            }
        )

        if existing_source:
            return None

        source_data["system_date"] = datetime.utcnow()

        result = self.collection.insert_one(source_data)

        return str(result.inserted_id)

    def get_all_data_sources(self):
        return list(
            self.collection.find({}, {"_id": 0})
        )

    def get_data_source_by_id(self, source_id):
        return self.collection.find_one(
            {"source_id": source_id},
            {"_id": 0}
        )