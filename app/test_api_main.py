from fastapi.testclient import TestClient

from app.api import main as api_main


class FakeAssetRepository:
    def __init__(self, assets=None, fail=False):
        self.assets = assets or []
        self.fail = fail

    def get_all_assets(self, limit, offset):
        if self.fail:
            raise RuntimeError("database failure")
        return self.assets

    def get_asset_by_id(self, asset_id):
        if self.fail:
            raise RuntimeError("database failure")
        for asset in self.assets:
            if asset["asset_id"] == asset_id:
                return asset
        return None

    def soft_delete_asset(self, asset_id):
        if self.fail:
            raise RuntimeError("database failure")
        return "delete-marker-id"


class FakeSourceRepository:
    def __init__(self, sources=None, fail=False):
        self.sources = sources or []
        self.fail = fail

    def get_all_data_sources(self):
        if self.fail:
            raise RuntimeError("database failure")
        return self.sources

    def get_data_source_by_id(self, source_id):
        if self.fail:
            raise RuntimeError("database failure")
        for source in self.sources:
            if source["source_id"] == source_id:
                return source
        return None


class FakeTimeSeriesRepository:
    def __init__(self, records=None, fail=False):
        self.records = records or []
        self.fail = fail

    def get_time_series(self, asset_id, limit, offset, as_of=None):
        if self.fail:
            raise RuntimeError("database failure")
        return self.records


class FakeAnalyticsService:
    def __init__(self, compare_result=None, analyze_result=None, fail=False):
        self.compare_result = compare_result
        self.analyze_result = analyze_result
        self.fail = fail

    def compare_assets(self, asset1, asset2):
        if self.fail:
            raise RuntimeError("service failure")
        return self.compare_result

    def analyze_asset(self, asset_id):
        if self.fail:
            raise RuntimeError("service failure")
        return self.analyze_result


def _client_with(monkeypatch, *, asset_repo=None, source_repo=None, time_series_repo=None, analytics_service=None):
    if asset_repo is not None:
        monkeypatch.setattr(api_main, "asset_repo", asset_repo)
        monkeypatch.setattr(api_main, "asset_repository", asset_repo)
    if source_repo is not None:
        monkeypatch.setattr(api_main, "source_repo", source_repo)
    if time_series_repo is not None:
        monkeypatch.setattr(api_main, "time_series_repo", time_series_repo)
        monkeypatch.setattr(api_main, "time_series_repository", time_series_repo)
    if analytics_service is not None:
        monkeypatch.setattr(api_main, "analytics_service", analytics_service)

    return TestClient(api_main.app)


def test_get_asset_returns_404_for_missing_asset(monkeypatch):
    client = _client_with(monkeypatch, asset_repo=FakeAssetRepository([]))

    response = client.get("/assets/UNKNOWN")

    assert response.status_code == 404
    assert response.json()["detail"] == "Asset 'UNKNOWN' not found"


def test_get_sources_returns_500_on_repository_failure(monkeypatch):
    client = _client_with(monkeypatch, source_repo=FakeSourceRepository(fail=True))

    response = client.get("/sources")

    assert response.status_code == 500
    assert response.json()["detail"] == "Unable to fetch sources"


def test_analyze_asset_returns_404_when_no_data(monkeypatch):
    client = _client_with(monkeypatch, analytics_service=FakeAnalyticsService(analyze_result=None))

    response = client.get("/analytics/AAPL")

    assert response.status_code == 404
    assert response.json()["detail"] == "Asset 'AAPL' not found"