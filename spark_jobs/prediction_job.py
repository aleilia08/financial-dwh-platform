from app.dal.mongo_connection import db
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("FinancialPredictionJob")
    .getOrCreate()
)

records = list(
    db.time_series.find(
        {"asset_id": "AAPL"}
    ).sort("business_date", -1)
)

data = [
    {
        "asset_id": record["asset_id"],
        "close": record["values"]["close"]
    }
    for record in records
    if record.get("values", {}).get("close") is not None
]

df = spark.createDataFrame(data)

latest_close = (
    df.collect()[0]["close"]
)

predicted_close = latest_close * 1.01

print("\n=== Prediction Result ===")
print(f"Latest close: {latest_close}")
print(f"Predicted next close: {predicted_close}")

spark.stop()