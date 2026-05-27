from app.analytics.analytics_service import AnalyticsService


service = AnalyticsService()

result = service.analyze_asset("AAPL")

print(result)