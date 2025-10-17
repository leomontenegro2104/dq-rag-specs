import pandas as pd
from src.etl.transform import build_dim_product, build_dim_vendor, build_fact_inventory

def test_vendor_dedup():
    import pandas as pd
    v = pd.DataFrame([
        {"vendor_code":"V-77","name":"Vectortron","country":"DE","support_email":"support@vectortron.com"},
        {"vendor_code":"V-77","name":"Vectortron GmbH","country":"DE","support_email":"care@vectortron.com"},
    ])
    dim, _ = build_dim_vendor(v)
    assert len(dim) == 1
    assert dim.iloc[0]["vendor_code"] == "V-77"

def test_dimensions_quarantine():
    p = pd.DataFrame([{
        "product_id":1004,"sku":"ZZ-001","model":"OmegaCam","category":"Camera",
        "weight_grams":650,"dimensions_mm":"90x60x","vendor_code":"V-77","launch_date":"2021-02-29","msrp_usd":"249.00"
    }])
    dim, q = build_dim_product(p, {})
    assert len(dim) == 0
    assert not q.empty
    assert "dimensions_incomplete" in q["reason"].unique()

def test_inventory_fk_quarantine():
    import pandas as pd
    dim = pd.DataFrame([{"product_id": 1001, "sku":"AB-001","model":"M","category":"Router","weight_g":900,"length_mm":10,"width_mm":10,"height_mm":10,"vendor_code":"V-77","launch_date":None,"msrp_usd":1.0}])
    inv = pd.DataFrame([{"product_id":9999,"warehouse":"WH-A","on_hand":1,"min_stock":0,"last_counted_at":"2024-01-01"}])
    fact, q = build_fact_inventory(inv, dim)
    assert len(fact) == 0
    assert not q.empty