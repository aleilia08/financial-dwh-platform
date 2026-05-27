from app.dal.time_series_repository import TimeSeriesRepository

repo = TimeSeriesRepository()

sample_record = {
    "asset_id": "AAPL",
    "source_id": "yfinance",

    "business_date": "2026-05-01",

    "values": {
        "open": 210.4,
        "close": 213.2,
        "high": 214.1,
        "low": 209.8,
        "volume": 1234567
    }
}

inserted_id = repo.create_time_series_record(sample_record)

print("Inserted time series id:", inserted_id)

records = repo.get_time_series(
    "AAPL",
    50,
    0
)

print("\nTime series records:")
print(records)