from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.dal.mongo_connection import db
from app.dal.analytics_repository import AnalyticsRepository
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

analytics_repo = AnalyticsRepository()
aggregation_results = result.collect()

print("\n=== Aggregation Results ===")
result.show()

for row in aggregation_results:
    analytics_repo.save_analytics_result(
        {
            "asset_id": row["asset_id"],
            "analysis_type": "spark_aggregation",
            "source_id": "spark_job",
            "statistics": {
                "avg_close": float(row["avg_close"]),
                "min_close": float(row["min_close"]),
                "max_close": float(row["max_close"]),
                "record_count": int(row["record_count"])
            }
        }
    )

spark.stop()