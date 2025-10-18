import pandas as pd
from schemas.raw_schemas import ProductsRawSchema, VendorsRawSchema, InventoryRawSchema


def validate_raw_products(df: pd.DataFrame) -> pd.DataFrame:
    return ProductsRawSchema.validate(df, lazy=True)


def validate_raw_vendors(df: pd.DataFrame) -> pd.DataFrame:
    return VendorsRawSchema.validate(df, lazy=True)


def validate_raw_inventory(df: pd.DataFrame) -> pd.DataFrame:
    return InventoryRawSchema.validate(df, lazy=True)
