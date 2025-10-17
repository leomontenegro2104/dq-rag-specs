import pandera as pa
from pandera import Column, DataFrameSchema, Check

DimProductSchema = DataFrameSchema({
    "product_id": Column(pa.Int64, nullable=False),
    "sku": Column(pa.String, nullable=False),
    "model": Column(pa.String, nullable=False),
    "category": Column(pa.String, nullable=False),
    "weight_g": Column(pa.Int64, Check.gt(0), nullable=False),
    "length_mm": Column(pa.Int64, Check.gt(0), nullable=False),
    "width_mm": Column(pa.Int64, Check.gt(0), nullable=False),
    "height_mm": Column(pa.Int64, Check.gt(0), nullable=False),
    "vendor_code": Column(pa.String, nullable=False),
    "launch_date": Column(pa.DateTime, nullable=True),
    "msrp_usd": Column(pa.Float, Check.ge(0), nullable=False),
})

DimVendorSchema = DataFrameSchema({
    "vendor_code": Column(pa.String, nullable=False),
    "vendor_name": Column(pa.String, nullable=False),
    "country": Column(pa.String, nullable=False),
    "support_email": Column(pa.String, pa.Check.str_matches(r".+@.+\..+"), nullable=False),
})

FactInventorySchema = DataFrameSchema({
    "product_id": Column(pa.Int64, nullable=False),
    "warehouse": Column(pa.String, nullable=False),
    "on_hand": Column(pa.Int64, Check.ge(0), nullable=False),
    "min_stock": Column(pa.Int64, Check.ge(0), nullable=False),
    "last_counted_at": Column(pa.DateTime, nullable=False),
}, coerce=True)