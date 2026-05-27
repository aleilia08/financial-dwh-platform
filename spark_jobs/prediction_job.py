from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("FinancialPredictionJob")
    .getOrCreate()
)

data = [
    ("AAPL", 300.1),
    ("AAPL", 302.5),
    ("AAPL", 305.7),
    ("AAPL", 308.3)
]

df = spark.createDataFrame(data, ["asset_id", "close"])

latest_close = (
    df.collect()[-1]["close"]
)

predicted_close = latest_close * 1.01

print("\n=== Prediction Result ===")
print(f"Latest close: {latest_close}")
print(f"Predicted next close: {predicted_close}")

spark.stop()