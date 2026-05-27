from app.dal.asset_repository import AssetRepository

repo = AssetRepository()

sample_asset = {
    "asset_id": "AAPL",
    "name": "Apple Inc.",
    "type": "stock",
    "region": "US",
    "currency": "USD"
}

inserted_id = repo.create_asset(sample_asset)

print("Inserted asset id:", inserted_id)

assets = repo.get_all_assets(10, 0)

print("\nAll assets:")
print(assets)

asset = repo.get_asset_by_id("AAPL")

print("\nAsset by id:")
print(asset)