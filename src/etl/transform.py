import pandas as pd
import re
import hashlib
from datetime import datetime
from schemas.trusted_schemas import DimProductSchema, DimVendorSchema, FactInventorySchema

DECIMAL_COMMA = re.compile(r"(\d+),(\d+)")
DIMENSIONS_RE = re.compile(r"^\s*(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*$")


def _fix_decimal_str(s: str) -> str:
    if pd.isna(s):
        return s
    return DECIMAL_COMMA.sub(r"\1.\2", str(s)).strip()


def _parse_float(s):
    if pd.isna(s) or s == "":
        return None
    try:
        return float(_fix_decimal_str(str(s)))
    except Exception:
        return None


def _parse_date(s):
    if pd.isna(s) or str(s).strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y/%d/%m"):
        try:
            return pd.to_datetime(datetime.strptime(str(s).strip(), fmt))
        except Exception:
            continue
    return None


def _parse_dimensions(s):
    if pd.isna(s):
        return None
    m = DIMENSIONS_RE.match(str(s))
    if not m:
        return None
    L, W, H = map(int, m.groups())
    return L, W, H


def _gen_product_id_from_sku(sku: str) -> int:
    h = hashlib.sha1(sku.encode()).hexdigest()
    return int(h[:12], 16)


def build_dim_vendor(vendors: pd.DataFrame):
    def choose_name(group):
        return group.loc[group["name"].str.len().idxmax(), "name"]

    def choose_email(group):
        preferred = group["support_email"].iloc[0]
        return preferred

    agg = (
        vendors.groupby("vendor_code", as_index=False)
        .apply(
            lambda g: pd.Series(
                {
                    "vendor_name": choose_name(g),
                    "country": g["country"].iloc[0],
                    "support_email": choose_email(g),
                }
            )
        )
        .reset_index(drop=True)
    )

    dim_vendor = DimVendorSchema.validate(agg, lazy=True)
    vendor_map = dim_vendor.set_index("vendor_code").to_dict(orient="index")
    return dim_vendor, vendor_map


def build_dim_product(products: pd.DataFrame, vendor_map: dict):
    rows = []
    quarantine = []
    for _, r in products.iterrows():
        pid = r.get("product_id")
        sku = str(r.get("sku") or "").strip()
        model = str(r.get("model") or "").strip()
        category = str(r.get("category") or "").strip()
        weight = _parse_float(r.get("weight_grams"))
        msrp = _parse_float(r.get("msrp_usd"))
        dims = _parse_dimensions(r.get("dimensions_mm"))
        vcode = str(r.get("vendor_code") or "").strip()
        ldate = _parse_date(r.get("launch_date"))

        if not sku:
            quarantine.append({**r.to_dict(), "reason": "sku_missing"})
            continue

        if pd.isna(pid):
            pid = _gen_product_id_from_sku(sku)

        if dims is None:
            quarantine.append({**r.to_dict(), "reason": "dimensions_incomplete"})
            continue

        if weight is None or weight <= 0:
            quarantine.append({**r.to_dict(), "reason": "invalid_weight"})
            continue

        if msrp is None or msrp < 0:
            quarantine.append({**r.to_dict(), "reason": "invalid_msrp"})
            continue

        L, W, H = dims
        if not vcode:
            quarantine.append({**r.to_dict(), "reason": "vendor_code_missing"})
            continue

        rows.append(
            {
                "product_id": int(pid),
                "sku": sku,
                "model": model if model else "UNKNOWN",
                "category": category if category else "UNKNOWN",
                "weight_g": int(weight),
                "length_mm": L,
                "width_mm": W,
                "height_mm": H,
                "vendor_code": vcode,
                "launch_date": ldate,
                "msrp_usd": float(msrp),
            }
        )

    dim_product = pd.DataFrame(rows)
    q_prod = pd.DataFrame(quarantine)
    if not dim_product.empty:
        dim_product = DimProductSchema.validate(dim_product, lazy=True)
    return dim_product, q_prod


def build_fact_inventory(inventory: pd.DataFrame, dim_product: pd.DataFrame):
    quarantine = []
    valid = []
    valid_ids = set(dim_product["product_id"].tolist())

    for _, r in inventory.iterrows():
        if r["on_hand"] < 0:
            quarantine.append({**r.to_dict(), "reason": "negative_on_hand"})
            continue
        if int(r["product_id"]) not in valid_ids:
            quarantine.append({**r.to_dict(), "reason": "fk_product_missing"})
            continue
        valid.append(r.to_dict())

    fact = pd.DataFrame(valid)
    q = pd.DataFrame(quarantine)
    if not fact.empty:
        fact = FactInventorySchema.validate(fact, lazy=True)
    return fact, q
