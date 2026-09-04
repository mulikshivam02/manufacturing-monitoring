"""
Phase 0 dataset verification — checks row/image counts against the verified
figures in the implementation plan's Phase 0 test criteria.

Run after downloading each dataset:
    python scripts/verify_datasets.py --dataset loco
    python scripts/verify_datasets.py --dataset tep --tep-format rdata
    python scripts/verify_datasets.py --dataset paderborn
    python scripts/verify_datasets.py --dataset all
"""
import argparse
from pathlib import Path

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".bmp"}


def count_images(root: Path) -> int:
    return sum(1 for p in root.rglob("*") if p.suffix.lower() in IMAGE_EXT)


def verify_loco(root: Path):
    expected_total, expected_categories = 3644, 5
    cats = [d for d in root.iterdir() if d.is_dir()]
    total = count_images(root)
    print(f"MVTec LOCO AD: {total} images across {len(cats)} categories "
          f"(expected {expected_total} / {expected_categories})")
    ok = total == expected_total and len(cats) == expected_categories
    print("  PASS" if ok else "  MISMATCH — check download completeness / extraction path")
    return ok


def verify_mvtec_ad(root: Path):
    expected_total, expected_categories = 5354, 15
    cats = [d for d in root.iterdir() if d.is_dir()]
    total = count_images(root)
    print(f"MVTec AD: {total} images across {len(cats)} categories "
          f"(expected {expected_total} / {expected_categories})")
    ok = total == expected_total and len(cats) == expected_categories
    print("  PASS" if ok else "  MISMATCH")
    return ok


def verify_tep_csv(root: Path):
    """Expects the 4 Rieth-format CSVs (or the RData->CSV conversion) present."""
    import pandas as pd
    expected_cols = 55  # faultNumber, simulationRun, sample + 52 process vars
    expected_faults = 20
    csvs = list(root.glob("*.csv"))
    if not csvs:
        print("TEP: no CSVs found in", root, "— convert RData first, or download the CSV mirror")
        return False
    ok_all = True
    for f in csvs:
        df = pd.read_csv(f, nrows=5000)  # sample rows are enough to check shape/faults
        ncols = df.shape[1]
        faults = sorted(df["faultNumber"].unique()) if "faultNumber" in df.columns else []
        max_fault = max(faults) if faults else 0
        print(f"  {f.name}: {ncols} columns (expected {expected_cols}), "
              f"max faultNumber seen {max_fault} (expected up to {expected_faults})")
        ok_all &= (ncols == expected_cols)
    print("  PASS" if ok_all else "  MISMATCH — check column count")
    return ok_all


def verify_paderborn(root: Path):
    expected_codes = 32
    code_dirs = [d for d in root.iterdir() if d.is_dir()]
    print(f"Paderborn: {len(code_dirs)} bearing-code folders found (expected {expected_codes})")
    healthy = [d for d in code_dirs if d.name.startswith("K0")]
    damaged = [d for d in code_dirs if d.name.startswith(("KA", "KB", "KI"))]
    print(f"  healthy={len(healthy)} (expected 6), damaged={len(damaged)} (expected 26)")
    ok = len(code_dirs) == expected_codes and len(healthy) == 6 and len(damaged) == 26
    print("  PASS" if ok else "  MISMATCH — re-run scripts/download_paderborn.py for missing codes")
    return ok


def verify_swat(root: Path):
    files = list(root.glob("*"))
    print(f"SWaT: {len(files)} file(s) present in {root}.")
    print("  (No fixed count checked here — verify against the file list iTrust emails you;"
          " confirm 41 labeled attack windows are present in the attack-period file.)")
    return len(files) > 0


DATASETS = {
    "loco": ("data/raw/mvtec_loco_ad", verify_loco),
    "mvtec_ad": ("data/raw/mvtec_ad", verify_mvtec_ad),
    "tep": ("data/raw/tep", verify_tep_csv),
    "paderborn": ("data/raw/paderborn", verify_paderborn),
    "swat": ("data/raw/swat", verify_swat),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=list(DATASETS) + ["all"], default="all")
    args = ap.parse_args()

    targets = DATASETS if args.dataset == "all" else {args.dataset: DATASETS[args.dataset]}
    results = {}
    for name, (path, fn) in targets.items():
        root = Path(path)
        print(f"\n--- {name} ---")
        if not root.exists():
            print(f"  {root} does not exist yet — nothing downloaded here.")
            results[name] = False
            continue
        results[name] = fn(root)

    print("\n=== Summary ===")
    for name, ok in results.items():
        print(f"  {name}: {'PASS' if ok else 'INCOMPLETE / MISMATCH'}")


if __name__ == "__main__":
    main()
