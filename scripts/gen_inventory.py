import pandas as pd

df = pd.DataFrame([
    {"product_id":1001,"warehouse":"WH-A","on_hand":10,"min_stock":5,"last_counted_at":"2024-11-01T10:00:00"},
    {"product_id":1002,"warehouse":"WH-A","on_hand":-2,"min_stock":5,"last_counted_at":"2024-11-01T10:00:00"},
    {"product_id":1003,"warehouse":"WH-B","on_hand":50,"min_stock":10,"last_counted_at":"2024-11-02T12:00:00"},
    {"product_id":1004,"warehouse":"WH-C","on_hand":3,"min_stock":5,"last_counted_at":"2024-11-03T09:00:00"},
    {"product_id":9999,"warehouse":"WH-A","on_hand":7,"min_stock":5,"last_counted_at":"2024-11-04T08:00:00"},
    {"product_id":1234,"warehouse":"WH-Z","on_hand":1,"min_stock":2,"last_counted_at":"2024-11-04T08:00:00"},
])

df["last_counted_at"] = pd.to_datetime(df["last_counted_at"])
df.to_parquet("raw/inventory.parquet", index=False)