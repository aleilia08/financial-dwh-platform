from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.dal.mongo_connection import db
from app.dal.prediction_repository import PredictionRepository
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

latest_record = records[0]

predicted_close = latest_close * 1.01

prediction_repo = PredictionRepository()
prediction_repo.save_prediction(
    {
        "asset_id": latest_record["asset_id"],
        "model": "spark_simple_growth",
        "prediction_date": latest_record["business_date"],
        "predicted_close": float(predicted_close)
    }
)

print("\n=== Prediction Result ===")
print(f"Latest close: {latest_close}")
print(f"Predicted next close: {predicted_close}")

spark.stop()