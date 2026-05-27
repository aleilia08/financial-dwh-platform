from datetime import datetime

from app.dal.mongo_connection import db


class AssetRepository:

    def __init__(self):
        self.collection = db["assets"]

    def create_asset(self, asset_data):
        existing_asset = self.collection.find_one(
            {
                "asset_id": asset_data["asset_id"]
            }
        )

        if existing_asset:
            return None

        asset_data["system_date"] = datetime.utcnow()

        result = self.collection.insert_one(asset_data)

        return str(result.inserted_id)

    def get_all_assets(self, limit: int, offset: int):
        cursor = (
            self.collection
            .find({"is_deleted": {"$ne": True}})
            .skip(offset)
            .limit(limit)
        )

        assets = []

        for asset in cursor:
            asset["_id"] = str(asset["_id"])
            assets.append(asset)

        return assets

    def get_asset_by_id(self, asset_id):
        return self.collection.find_one(
            {"asset_id": asset_id},
            {"_id": 0}
        )

    def soft_delete_asset(self, asset_id: str):
        delete_marker = {
            "asset_id": asset_id,
            "is_deleted": True,
            "valid_from": datetime.utcnow().date().isoformat(),
            "system_date": datetime.utcnow().isoformat()
        }

        result = self.collection.insert_one(delete_marker)

        return str(result.inserted_id)