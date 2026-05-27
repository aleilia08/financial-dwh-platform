import pandas as pd
from datetime import datetime

from app.dal.time_series_repository import TimeSeriesRepository
from app.dal.analytics_repository import AnalyticsRepository


class AnalyticsService:

    def __init__(self):

        self.time_series_repo = TimeSeriesRepository()
        self.analytics_repo = AnalyticsRepository()

    def analyze_asset(
        self,
        asset_id,
        source_id="yfinance"
    ):

        records = self.time_series_repo.get_time_series(
            asset_id,
            1000,
            0
        )

        if not records:
            return None

        df = pd.DataFrame(records)

        df = df.sort_values(by="business_date")

        df["close"] = df["values"].apply(
            lambda x: x["close"]
        )

        min_close = df["close"].min()
        max_close = df["close"].max()
        avg_close = df["close"].mean()
        latest_close = df["close"].iloc[-1]
        record_count = len(df)

        trend_percentage = (
            (latest_close - min_close) / min_close
        ) * 100

        volatility = df["close"].std()

        moving_average_7 = (
            df["close"]
            .rolling(window=7)
            .mean()
            .iloc[-1]
        )

        analytics_result = {

            "asset_id": asset_id,
            "source_id": source_id,

            "statistics": {

                "min_close": float(min_close),
                "max_close": float(max_close),
                "avg_close": float(avg_close),
                "latest_close": float(latest_close),
                "record_count": int(record_count),

                "trend_percentage": float(trend_percentage),

                "volatility": float(volatility),

                "moving_average_7": float(moving_average_7)

            },

            "record_count": record_count
        }

        self.analytics_repo.save_analytics_result(
            analytics_result
        )

        created_at = analytics_result.get("created_at")
        if isinstance(created_at, datetime):
            analytics_result["created_at"] = created_at.isoformat()

        analytics_result.pop("_id", None)


        return analytics_result

    def compare_assets(self, asset1: str, asset2: str):

        analytics1 = self.analyze_asset(asset1)
        analytics2 = self.analyze_asset(asset2)

        comparison = {
            "asset_1": analytics1,
            "asset_2": analytics2
        }

        return comparison