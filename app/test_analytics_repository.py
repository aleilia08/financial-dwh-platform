from app.dal.analytics_repository import AnalyticsRepository

repo = AnalyticsRepository()

sample_result = {
    "asset_id": "AAPL",

    "analysis_type": "trend_summary",

    "results": {
        "avg_close": 210.3,
        "max_close": 230.1,
        "trend_percent": 7.2
    }
}

inserted_id = repo.save_analytics_result(sample_result)

print("Inserted analytics result id:", inserted_id)

results = repo.get_analytics_by_asset("AAPL")

print("\nAnalytics results:")
print(results)