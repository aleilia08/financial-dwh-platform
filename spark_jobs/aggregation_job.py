from app.dal.mongo_connection import db
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, min, max, count

spark = (
    SparkSession.builder
    .appName("FinancialAggregationJob")
    .getOrCreate()
)

records = list(db.time_series.find())

data = [
    {
        "asset_id": record["asset_id"],
        "close": record["values"]["close"]
    }
    for record in records
    if record.get("asset_id") and record.get("values", {}).get("close") is not None
]

df = spark.createDataFrame(data)

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