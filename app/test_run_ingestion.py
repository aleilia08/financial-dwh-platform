from datetime import datetime

from app.ingestion import run_ingestion


class FakeDownloadFrame:
    def __init__(self, rows):
        self.rows = rows

    def iterrows(self):
        for index, row in self.rows:
            yield index, row

    def __len__(self):
        return len(self.rows)


class FakeDatetime:
    @staticmethod
    def utcnow():
        return datetime(2026, 6, 5, 12, 0, 0)


class FakeAssetRepository:
    def __init__(self):
        self.created_assets = []

    def create_asset(self, asset_data):
        self.created_assets.append(asset_data.copy())
        return "asset-id"


class FakeDataSourceRepository:
    def __init__(self):
        self.created_sources = []

    def create_data_source(self, source_data):
        self.created_sources.append(source_data.copy())
        return "source-id"


class FakeTimeSeriesRepository:
    def __init__(self):
        self.created_records = []

    def create_time_series_record(self, record_data):
        self.created_records.append(record_data.copy())
        return f"record-{len(self.created_records)}"


def test_ingest_loads_assets_and_time_series(monkeypatch, capsys):
    asset_repo = FakeAssetRepository()
    source_repo = FakeDataSourceRepository()
    time_series_repo = FakeTimeSeriesRepository()

    monkeypatch.setattr(run_ingestion, "AssetRepository", lambda: asset_repo)
    monkeypatch.setattr(run_ingestion, "DataSourceRepository", lambda: source_repo)
    monkeypatch.setattr(run_ingestion, "TimeSeriesRepository", lambda: time_series_repo)
    monkeypatch.setattr(
        run_ingestion.yf,
        "download",
        lambda asset_id, period, interval, progress: {
            "AAPL": FakeDownloadFrame([
                (datetime(2026, 6, 1), {"Open": 100.0, "High": 110.0, "Low": 95.0, "Close": 105.0, "Volume": 1000}),
                (datetime(2026, 6, 2), {"Open": 105.0, "High": 112.0, "Low": 101.0, "Close": 108.0, "Volume": 1200}),
            ]),
            "MSFT": FakeDownloadFrame([
                (datetime(2026, 6, 3), {"Open": 200.0, "High": 210.0, "Low": 198.0, "Close": 207.0, "Volume": 900}),
            ]),
            "BTC-USD": FakeDownloadFrame([]),
        }[asset_id]
    )

    monkeypatch.setattr(
        run_ingestion,
        "ASSETS",
        [
            {
                "asset_id": "AAPL",
                "name": "Apple Inc.",
                "type": "stock",
                "region": "US",
                "currency": "USD",
            },
            {
                "asset_id": "MSFT",
                "name": "Microsoft Corporation",
                "type": "stock",
                "region": "US",
                "currency": "USD",
            },
        ],
    )

    monkeypatch.setattr(run_ingestion, "datetime", FakeDatetime)

    run_ingestion.ingest()

    captured = capsys.readouterr().out

    assert len(source_repo.created_sources) == 1
    assert source_repo.created_sources[0]["source_id"] == "yfinance"
    assert isinstance(source_repo.created_sources[0]["fetch_time"], datetime)

    assert [asset["asset_id"] for asset in asset_repo.created_assets] == ["AAPL", "MSFT"]
    assert [record["asset_id"] for record in time_series_repo.created_records] == ["AAPL", "AAPL", "MSFT"]
    assert all(record["source_id"] == "yfinance" for record in time_series_repo.created_records)
    assert [record["business_date"] for record in time_series_repo.created_records] == [
        "2026-06-01",
        "2026-06-02",
        "2026-06-03",
    ]
    assert "Ingestion completed." in captured
    assert "Total stored time-series records: 3" in captured