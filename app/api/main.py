from fastapi import FastAPI, Query

from app.analytics.analytics_service import AnalyticsService
from app.dal.asset_repository import AssetRepository
from app.dal.data_source_repository import DataSourceRepository
from app.dal.time_series_repository import TimeSeriesRepository


app = FastAPI(
    title="Financial DWH Platform",
    version="1.0.0"
)

asset_repo = AssetRepository()
source_repo = DataSourceRepository()
time_series_repo = TimeSeriesRepository()
analytics_service = AnalyticsService()

asset_repository = asset_repo
time_series_repository = time_series_repo


@app.get("/")
def root():
    return {
        "message": "Financial DWH Platform API"
    }


@app.get("/assets")
def get_assets(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    return asset_repository.get_all_assets(limit, offset)


@app.get("/assets/{asset_id}")
def get_asset(asset_id: str):

    return asset_repo.get_asset_by_id(asset_id)


@app.delete("/assets/{asset_id}")
def delete_asset(asset_id: str):
    result = asset_repository.soft_delete_asset(asset_id)

    return {
        "message": f"Asset {asset_id} marked as deleted",
        "delete_marker_id": result
    }


@app.get("/sources")
def get_sources():

    return source_repo.get_all_data_sources()


@app.get("/sources/{source_id}")
def get_source(source_id: str):

    return source_repo.get_data_source_by_id(source_id)


@app.get("/timeseries")
def get_time_series(
    asset_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    as_of: str | None = None
):
    return time_series_repository.get_time_series(
        asset_id,
        limit,
        offset,
        as_of
    )


@app.get("/analytics/compare")
def compare_assets(asset1: str, asset2: str):

    result = analytics_service.compare_assets(
        asset1,
        asset2
    )

    return result


@app.get("/analytics/{asset_id}")
def analyze_asset(asset_id: str):

    return analytics_service.analyze_asset(asset_id)