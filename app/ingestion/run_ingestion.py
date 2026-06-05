from datetime import datetime
import math
import logging
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


REQUIRED_ASSET_FIELDS = ("asset_id", "name", "type", "region", "currency")
REQUIRED_PRICE_FIELDS = ("Open", "High", "Low", "Close", "Volume")

logger = logging.getLogger(__name__)


def _validate_asset(asset):
    if not isinstance(asset, dict):
        raise ValueError("Asset configuration must be a dictionary")

    validated_asset = {}

    for field in REQUIRED_ASSET_FIELDS:
        value = asset.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Invalid asset field: {field}")
        validated_asset[field] = value.strip()

    return validated_asset


def _sanitize_market_row(asset_id, index, row):
    values = {}

    try:
        for field in REQUIRED_PRICE_FIELDS:
            raw_value = row[field]
            if raw_value is None:
                return None

            if field == "Volume":
                numeric_value = float(raw_value)
                if not math.isfinite(numeric_value):
                    return None
                values["volume"] = int(numeric_value)
            else:
                numeric_value = float(raw_value)
                if not math.isfinite(numeric_value):
                    return None
                values[field.lower()] = numeric_value
    except (KeyError, TypeError, ValueError):
        return None

    if not hasattr(index, "strftime"):
        return None

    return {
        "asset_id": asset_id,
        "source_id": "yfinance",
        "business_date": index.strftime("%Y-%m-%d"),
        "values": values,
    }


def ingest():
    asset_repo = AssetRepository()
    source_repo = DataSourceRepository()
    time_series_repo = TimeSeriesRepository()

    validated_assets = [_validate_asset(asset) for asset in ASSETS]

    source = {
        "source_id": "yfinance",
        "name": "Yahoo Finance",
        "provider_type": "financial_market_api",
        "description": "Historical financial market data provider",
        "attributes": ["open", "high", "low", "close", "volume"],
        "fetch_time": datetime.utcnow()
    }

    try:
        source_repo.create_data_source(source)
    except Exception as exception:
        logger.exception("Failed to create data source")
        raise RuntimeError("Unable to register ingestion source") from exception

    total_records = 0

    for asset in validated_assets:
        try:
            asset_repo.create_asset(asset)
        except Exception as exception:
            logger.exception("Failed to create asset %s", asset["asset_id"])
            continue

        print(f"\nFetching data for {asset['asset_id']}...")

        try:
            data = yf.download(
                asset["asset_id"],
                period="2y",
                interval="1d",
                progress=False
            )
        except Exception as exception:
            logger.exception("Failed to download data for %s", asset["asset_id"])
            print(f"Skipping {asset['asset_id']} due to download error")
            continue

        if not hasattr(data, "iterrows"):
            print(f"Skipping {asset['asset_id']} due to invalid data response")
            continue

        for index, row in data.iterrows():
            record = _sanitize_market_row(asset["asset_id"], index, row)
            if record is None:
                continue

            try:
                time_series_repo.create_time_series_record(record)
            except Exception as exception:
                logger.exception(
                    "Failed to store time-series record for %s on %s",
                    asset["asset_id"],
                    record["business_date"]
                )
                continue

            total_records += 1

        print(f"Stored {len(data)} records for {asset['asset_id']}")

    print("\nIngestion completed.")
    print(f"Total stored time-series records: {total_records}")


if __name__ == "__main__":
    ingest()