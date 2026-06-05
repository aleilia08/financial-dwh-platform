import logging

from fastapi import FastAPI, HTTPException, Query

from app.analytics.analytics_service import AnalyticsService
from app.dal.asset_repository import AssetRepository
from app.dal.data_source_repository import DataSourceRepository
from app.dal.time_series_repository import TimeSeriesRepository


app = FastAPI(
    title="Financial DWH Platform",
    version="1.0.0"
)

logger = logging.getLogger(__name__)

asset_repo = AssetRepository()
source_repo = DataSourceRepository()
time_series_repo = TimeSeriesRepository()
analytics_service = AnalyticsService()

asset_repository = asset_repo
time_series_repository = time_series_repo


def _raise_not_found(resource_type: str, identifier: str):
    raise HTTPException(
        status_code=404,
        detail=f"{resource_type} '{identifier}' not found"
    )


def _raise_internal_error(action: str, exception: Exception):
    logger.exception("Failed to %s", action)
    raise HTTPException(
        status_code=500,
        detail=f"Unable to {action}"
    ) from exception


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
    try:
        return asset_repository.get_all_assets(limit, offset)
    except Exception as exception:
        _raise_internal_error("fetch assets", exception)


@app.get("/assets/{asset_id}")
def get_asset(asset_id: str):
    try:
        asset = asset_repo.get_asset_by_id(asset_id)
    except Exception as exception:
        _raise_internal_error(f"fetch asset {asset_id}", exception)

    if asset is None:
        _raise_not_found("Asset", asset_id)

    return asset


@app.delete("/assets/{asset_id}")
def delete_asset(asset_id: str):
    try:
        existing_asset = asset_repo.get_asset_by_id(asset_id)
    except Exception as exception:
        _raise_internal_error(f"check asset {asset_id}", exception)

    if existing_asset is None:
        _raise_not_found("Asset", asset_id)

    try:
        result = asset_repository.soft_delete_asset(asset_id)
    except Exception as exception:
        _raise_internal_error(f"delete asset {asset_id}", exception)

    return {
        "message": f"Asset {asset_id} marked as deleted",
        "delete_marker_id": result
    }


@app.get("/sources")
def get_sources():
    try:
        return source_repo.get_all_data_sources()
    except Exception as exception:
        _raise_internal_error("fetch sources", exception)


@app.get("/sources/{source_id}")
def get_source(source_id: str):
    try:
        source = source_repo.get_data_source_by_id(source_id)
    except Exception as exception:
        _raise_internal_error(f"fetch source {source_id}", exception)

    if source is None:
        _raise_not_found("Source", source_id)

    return source


@app.get("/timeseries")
def get_time_series(
    asset_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    as_of: str | None = None
):
    try:
        return time_series_repository.get_time_series(
            asset_id,
            limit,
            offset,
            as_of
        )
    except Exception as exception:
        _raise_internal_error(f"fetch time series for {asset_id}", exception)


@app.get("/analytics/compare")
def compare_assets(asset1: str, asset2: str):
    try:
        result = analytics_service.compare_assets(
            asset1,
            asset2
        )
    except Exception as exception:
        _raise_internal_error(f"compare assets {asset1} and {asset2}", exception)

    if not result or result.get("asset_1") is None:
        _raise_not_found("Asset", asset1)

    if result.get("asset_2") is None:
        _raise_not_found("Asset", asset2)

    return result


@app.get("/analytics/{asset_id}")
def analyze_asset(asset_id: str):
    try:
        result = analytics_service.analyze_asset(asset_id)
    except Exception as exception:
        _raise_internal_error(f"analyze asset {asset_id}", exception)

    if result is None:
        _raise_not_found("Asset", asset_id)

    return result