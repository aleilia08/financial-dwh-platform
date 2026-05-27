from app.dal.asset_repository import AssetRepository
from app.dal.data_source_repository import DataSourceRepository
from app.dal.time_series_repository import TimeSeriesRepository
from app.analytics.analytics_service import AnalyticsService


asset_repo = AssetRepository()
source_repo = DataSourceRepository()
time_series_repo = TimeSeriesRepository()
analytics_service = AnalyticsService()


def list_assets():
    return asset_repo.get_all_assets(limit=100, offset=0)


def get_asset_details(asset_id: str):
    return asset_repo.get_asset_by_id(asset_id)


def list_data_sources():
    return source_repo.get_all_data_sources()


def get_time_series_data(
    asset_id: str,
    limit: int = 20,
    offset: int = 0,
    as_of: str | None = None
):
    return time_series_repo.get_time_series(
        asset_id=asset_id,
        limit=limit,
        offset=offset,
        as_of=as_of
    )


def summarize_trend(asset_id: str):
    return analytics_service.analyze_asset(asset_id)


def compare_assets(asset1: str, asset2: str):
    return analytics_service.compare_assets(asset1, asset2)


def explain_change(asset_id: str):

    analytics = analytics_service.analyze_asset(asset_id)

    stats = analytics["statistics"]

    trend = stats["trend_percentage"]
    volatility = stats["volatility"]

    if trend > 20:
        trend_text = "strong upward trend"
    elif trend > 0:
        trend_text = "moderate upward trend"
    else:
        trend_text = "downward trend"

    explanation = {
        "asset_id": asset_id,
        "explanation":
            f"{asset_id} shows a {trend_text} "
            f"with a trend percentage of {trend:.2f}% "
            f"and volatility of {volatility:.2f}."
    }

    return explanation