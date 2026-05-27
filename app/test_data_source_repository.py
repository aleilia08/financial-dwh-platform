from app.dal.data_source_repository import DataSourceRepository

repo = DataSourceRepository()

sample_source = {
    "source_id": "yfinance",
    "name": "Yahoo Finance",
    "provider_type": "financial_market_api",
    "description": "Historical financial market data provider",
    "attributes": ["open", "high", "low", "close", "volume"]
}

inserted_id = repo.create_data_source(sample_source)

print("Inserted data source id:", inserted_id)

sources = repo.get_all_data_sources()

print("\nAll data sources:")
print(sources)

source = repo.get_data_source_by_id("yfinance")

print("\nData source by id:")
print(source)