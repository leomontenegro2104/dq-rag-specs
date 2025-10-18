import pandera as pa
from pandera import Column, DataFrameSchema, Check

ProductsRawSchema = DataFrameSchema(
    {
        "product_id": Column(pa.Float, nullable=True),
        "sku": Column(pa.String, nullable=False),
        "model": Column(pa.String, nullable=True),
        "category": Column(pa.String, nullable=True),
        "weight_grams": Column(pa.Int, nullable=True),
        "dimensions_mm": Column(pa.String, nullable=True),
        "vendor_code": Column(pa.String, nullable=True),
        "launch_date": Column(pa.String, nullable=True),
        "msrp_usd": Column(pa.Float, nullable=True),
    }
)

VendorsRawSchema = DataFrameSchema(
    {
        "vendor_code": Column(pa.String, nullable=False),
        "name": Column(pa.String, nullable=False),
        "country": Column(pa.String, nullable=False),
        "support_email": Column(pa.String, nullable=False),
    }
)

InventoryRawSchema = DataFrameSchema(
    {
        "product_id": Column(pa.Int64, nullable=False),
        "warehouse": Column(pa.String, nullable=False),
        "on_hand": Column(pa.Int64, nullable=False),
        "min_stock": Column(pa.Int64, Check.ge(0), nullable=False),
        "last_counted_at": Column(pa.DateTime, nullable=False),
    },
    coerce=True,
)
