"""
Download and extract the Paderborn Bearing DataCenter dataset.

Official source : https://mb.uni-paderborn.de/en/kat/research/bearing-datacenter/data-sets-and-download
Direct files at : http://groups.uni-paderborn.de/kat/BearingDataCenter/<CODE>.rar
Mirror (fallback): https://zenodo.org/records/15845309  (same 32 files, same md5s)

License: CC BY-NC 4.0 — non-commercial academic use only; cite Lessmeier et al. 2016.

The 32 codes below = 6 healthy + 26 damaged (12 artificial + 3 KB + 11 KI),
matching the "32 bearing states" figure the Phase 0 test criteria check against.

Usage:
    python scripts/download_paderborn.py
    python scripts/download_paderborn.py --dest data/raw/paderborn --mirror zenodo
Requires: `unrar` or `unar` on PATH (for the `patool`/`rarfile` extraction step).
"""
import argparse
import sys
from pathlib import Path

import requests
from tqdm import tqdm

BEARING_CODES = [
    # healthy (6)
    "K001", "K002", "K003", "K004", "K005", "K006",
    # artificially damaged (12)
    "KA01", "KA03", "KA04", "KA05", "KA06", "KA07", "KA08", "KA09",
    "KA15", "KA16", "KA22", "KA30",
    # real-damage, accelerated lifetime test (14 -> KB* + KI*)
    "KB23", "KB24", "KB27",
    "KI01", "KI03", "KI04", "KI05", "KI07", "KI08",
    "KI14", "KI16", "KI17", "KI18", "KI21",
]
assert len(BEARING_CODES) == 32, "code list drifted from the verified 32-state figure"

OFFICIAL_BASE = "http://groups.uni-paderborn.de/kat/BearingDataCenter/"
ZENODO_RECORD = "15845309"  # https://zenodo.org/records/15845309


def download_file(url: str, dest: Path, timeout: int = 60) -> bool:
    try:
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with open(dest, "wb") as f, tqdm(
                total=total, unit="B", unit_scale=True, desc=dest.name, leave=False
            ) as bar:
                for chunk in r.iter_content(chunk_size=1 << 16):
                    f.write(chunk)
                    bar.update(len(chunk))
        return True
    except requests.RequestException as e:
        print(f"  ! failed: {url} ({e})")
        return False


def zenodo_file_url(code: str) -> str:
    # Zenodo record file URLs follow /records/<id>/files/<filename>
    return f"https://zenodo.org/records/{ZENODO_RECORD}/files/{code}.rar"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default="data/raw/paderborn")
    ap.add_argument("--mirror", choices=["official", "zenodo"], default="official")
    ap.add_argument("--extract", action="store_true", default=True)
    ap.add_argument("--no-extract", dest="extract", action="store_false")
    args = ap.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    base = OFFICIAL_BASE
    print(f"Downloading {len(BEARING_CODES)} bearing codes from {args.mirror} source into {dest}/")

    failures = []
    for code in BEARING_CODES:
        rar_path = dest / f"{code}.rar"
        if rar_path.exists():
            print(f"  {code}.rar already present, skipping")
            continue
        url = zenodo_file_url(code) if args.mirror == "zenodo" else f"{base}{code}.rar"
        ok = download_file(url, rar_path)
        if not ok and args.mirror == "official":
            print(f"  retrying {code} via Zenodo mirror...")
            ok = download_file(zenodo_file_url(code), rar_path)
        if not ok:
            failures.append(code)

    if failures:
        print(f"\n{len(failures)} files failed both sources: {failures}")
        print("Retry those manually from the official page, or check network access.")

    if args.extract:
        try:
            import patoolib
        except ImportError:
            print("\npatool not installed — run `pip install patool` then re-run with --extract only.")
            sys.exit(1)
        for code in BEARING_CODES:
            rar_path = dest / f"{code}.rar"
            out_dir = dest / code
            if rar_path.exists() and not out_dir.exists():
                out_dir.mkdir(exist_ok=True)
                print(f"  extracting {code}.rar ...")
                patoolib.extract_archive(str(rar_path), outdir=str(out_dir))

    n_ok = len(BEARING_CODES) - len(failures)
    print(f"\nDone: {n_ok}/{len(BEARING_CODES)} bearing codes downloaded to {dest}/")


if __name__ == "__main__":
    main()
