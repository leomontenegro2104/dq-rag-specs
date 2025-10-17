import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

def read_raw_frames(raw_dir: str):
    raw = Path(raw_dir)
    products = pd.read_csv(raw / "products.csv")
    vendors = pd.read_json(raw / "vendors.jsonl", lines=True)
    inventory = pd.read_parquet(raw / "inventory.parquet")
    return {"products": products, "vendors": vendors, "inventory": inventory}

def write_parquet(df: pd.DataFrame, out_path: Path, partition_cols=None):
    out_path.mkdir(parents=True, exist_ok=True)
    if partition_cols:
        import pyarrow as pa
        import pyarrow.parquet as pq
        table = pa.Table.from_pandas(df)
        pq.write_to_dataset(
            table,
            root_path=str(out_path),
            partition_cols=partition_cols,
            use_dictionary=True
        )
    else:
        df.to_parquet(out_path / "data.parquet", index=False)

def write_outputs(
    base_out: str,
    dim_vendor: pd.DataFrame,
    dim_product: pd.DataFrame,
    fact_inventory: pd.DataFrame,
    q_prod: pd.DataFrame,
    q_inv: pd.DataFrame,
):
    base = Path(base_out)
    write_parquet(dim_vendor, base / "dim_vendor")
    write_parquet(dim_product, base / "dim_product", partition_cols=["vendor_code"])
    write_parquet(fact_inventory, base / "fact_inventory", partition_cols=["warehouse"])

    silver = base / "silver" / "_quarantine"
    silver.mkdir(parents=True, exist_ok=True)
    if not q_prod.empty:
        q_prod.to_parquet(silver / "products.parquet", index=False)
    if not q_inv.empty:
        q_inv.to_parquet(silver / "inventory.parquet", index=False)