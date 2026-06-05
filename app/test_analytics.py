from datetime import datetime
import math

from app.analytics import analytics_service as analytics_service_module
from app.analytics.analytics_service import AnalyticsService


class FakeTimeSeriesRepository:
	def __init__(self, records):
		self.records = records
		self.calls = []

	def get_time_series(self, asset_id, limit, offset, as_of=None):
		self.calls.append((asset_id, limit, offset, as_of))
		return self.records


class FakeAnalyticsRepository:
	def __init__(self):
		self.saved_payloads = []

	def save_analytics_result(self, analytics_data):
		analytics_data["created_at"] = datetime(2026, 6, 5, 12, 0, 0)
		self.saved_payloads.append(analytics_data.copy())
		return "analytics-id"


def test_analyze_asset_computes_expected_statistics(monkeypatch):
	records = [
		{"business_date": "2026-05-03", "values": {"close": 13.0}},
		{"business_date": "2026-05-01", "values": {"close": 11.0}},
		{"business_date": "2026-05-04", "values": {"close": 14.0}},
		{"business_date": "2026-05-02", "values": {"close": 12.0}},
		{"business_date": "2026-05-05", "values": {"close": 15.0}},
		{"business_date": "2026-05-06", "values": {"close": 16.0}},
		{"business_date": "2026-05-07", "values": {"close": 17.0}},
	]
	time_series_repo = FakeTimeSeriesRepository(records)
	analytics_repo = FakeAnalyticsRepository()

	monkeypatch.setattr(analytics_service_module, "TimeSeriesRepository", lambda: time_series_repo)
	monkeypatch.setattr(analytics_service_module, "AnalyticsRepository", lambda: analytics_repo)

	service = AnalyticsService()
	result = service.analyze_asset("AAPL")

	assert time_series_repo.calls == [("AAPL", 1000, 0, None)]
	assert result["asset_id"] == "AAPL"
	assert result["source_id"] == "yfinance"
	assert result["statistics"]["min_close"] == 11.0
	assert result["statistics"]["max_close"] == 17.0
	assert result["statistics"]["avg_close"] == 14.0
	assert result["statistics"]["latest_close"] == 17.0
	assert result["statistics"]["record_count"] == 7
	assert math.isclose(result["statistics"]["trend_percentage"], 54.5454545455, rel_tol=1e-9)
	assert math.isclose(result["statistics"]["volatility"], 2.160246899, rel_tol=1e-9)
	assert result["statistics"]["moving_average_7"] == 14.0
	assert result["record_count"] == 7
	assert result["created_at"] == "2026-06-05T12:00:00"
	assert analytics_repo.saved_payloads[0]["asset_id"] == "AAPL"


def test_compare_assets_returns_both_analyses(monkeypatch):
	monkeypatch.setattr(
		AnalyticsService,
		"analyze_asset",
		lambda self, asset_id: {"asset_id": asset_id}
	)

	service = AnalyticsService()

	assert service.compare_assets("AAPL", "MSFT") == {
		"asset_1": {"asset_id": "AAPL"},
		"asset_2": {"asset_id": "MSFT"}
	}