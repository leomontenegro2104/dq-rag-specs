import argparse
from .utils import read_raw_frames, write_outputs
from .validators import validate_raw_products, validate_raw_vendors, validate_raw_inventory
from .transform import build_dim_product, build_dim_vendor, build_fact_inventory


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default="raw")
    ap.add_argument("--out-dir", default="data")
    args = ap.parse_args()

    dfs = read_raw_frames(args.raw_dir)
    p = validate_raw_products(dfs["products"])
    v = validate_raw_vendors(dfs["vendors"])
    i = validate_raw_inventory(dfs["inventory"])

    dim_vendor, vendor_map = build_dim_vendor(v)
    dim_product, q_prod = build_dim_product(p, vendor_map)
    fact_inventory, q_inv = build_fact_inventory(i, dim_product)

    write_outputs(args.out_dir, dim_vendor, dim_product, fact_inventory, q_prod, q_inv)


if __name__ == "__main__":
    main()
