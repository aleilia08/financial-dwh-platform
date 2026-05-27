from datetime import datetime
import yfinance as yf

from app.dal.asset_repository import AssetRepository
from app.dal.data_source_repository import DataSourceRepository
from app.dal.time_series_repository import TimeSeriesRepository


ASSETS = [
    {
        "asset_id": "AAPL",
        "name": "Apple Inc.",
        "type": "stock",
        "region": "US",
        "currency": "USD"
    },
    {
        "asset_id": "MSFT",
        "name": "Microsoft Corporation",
        "type": "stock",
        "region": "US",
        "currency": "USD"
    },
    {
        "asset_id": "BTC-USD",
        "name": "Bitcoin USD",
        "type": "crypto",
        "region": "Global",
        "currency": "USD"
    }
]


def ingest():
    asset_repo = AssetRepository()
    source_repo = DataSourceRepository()
    time_series_repo = TimeSeriesRepository()

    source = {
        "source_id": "yfinance",
        "name": "Yahoo Finance",
        "provider_type": "financial_market_api",
        "description": "Historical financial market data provider",
        "attributes": ["open", "high", "low", "close", "volume"],
        "fetch_time": datetime.utcnow()
    }

    source_repo.create_data_source(source)

    total_records = 0

    for asset in ASSETS:
        asset_repo.create_asset(asset)

        print(f"\nFetching data for {asset['asset_id']}...")

        data = yf.download(
            asset["asset_id"],
            period="2y",
            interval="1d",
            progress=False
        )

        for index, row in data.iterrows():
            record = {
                "asset_id": asset["asset_id"],
                "source_id": "yfinance",
                "business_date": index.strftime("%Y-%m-%d"),
                "values": {
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                }
            }

            time_series_repo.create_time_series_record(record)
            total_records += 1

        print(f"Stored {len(data)} records for {asset['asset_id']}")

    print("\nIngestion completed.")
    print(f"Total stored time-series records: {total_records}")


if __name__ == "__main__":
    ingest()