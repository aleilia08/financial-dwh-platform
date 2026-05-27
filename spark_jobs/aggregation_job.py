from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, min, max, count

spark = (
    SparkSession.builder
    .appName("FinancialAggregationJob")
    .getOrCreate()
)

data = [
    ("AAPL", 308.3),
    ("AAPL", 304.9),
    ("AAPL", 302.1),
    ("MSFT", 512.1),
    ("MSFT", 510.2),
    ("BTC-USD", 109000.0)
]

df = spark.createDataFrame(data, ["asset_id", "close"])

result = (
    df.groupBy("asset_id")
    .agg(
        avg("close").alias("avg_close"),
        min("close").alias("min_close"),
        max("close").alias("max_close"),
        count("*").alias("record_count")
    )
)

print("\n=== Aggregation Results ===")
result.show()

spark.stop()