# SPDX-FileCopyrightText: Contributors to powerplantmatching <https://github.com/pypsa/powerplantmatching>
#
# SPDX-License-Identifier: MIT

"""
Build a powerplantmatching-compatible MaStR zip from an open-mastr SQLite DB.

open-mastr's bulk download (`Mastr().download()`) writes the Marktstammdatenregister
into ~/.open-MaStR/data/sqlite/open-mastr.db. powerplantmatching's MASTR() loader,
however, reads a zip of `*_raw.csv` files (the layout of the Zenodo open-mastr dump).

This script bridges the two: it exports the technology tables that ppm's loader
consumes into exactly those CSVs and zips them, so a fresh bulk download can refresh
ppm's MaStR source without waiting for the (infrequent) Zenodo re-release.

Usage:
    python scripts/build_mastr_zip_from_open_mastr.py [--db PATH] [--out PATH] [--date YYYY-MM-DD]

Then point config.yaml MASTR.fn at the produced filename (it lands in ppm's data dir).
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

# DB table -> ppm CSV filename suffix (ppm matches by str.endswith).
TABLE_TO_CSV = {
    "biomass_extended": "bnetza_mastr_biomass_raw.csv",
    "combustion_extended": "bnetza_mastr_combustion_raw.csv",
    "nuclear_extended": "bnetza_mastr_nuclear_raw.csv",
    "hydro_extended": "bnetza_mastr_hydro_raw.csv",
    "wind_extended": "bnetza_mastr_wind_raw.csv",
    "solar_extended": "bnetza_mastr_solar_raw.csv",
    "storage_extended": "bnetza_mastr_storage_raw.csv",
    "storage_units": "bnetza_mastr_storage_units_raw.csv",
}

# Columns ppm's MASTR() loader reads from the *_extended tables (see data.py).
# Exporting only these keeps the 6M-row solar CSV to a sane size; ppm intersects
# with what is present, so a missing column in one table is harmless.
EXTENDED_COLUMNS = [
    # target_columns
    "GeplantesInbetriebnahmedatum",
    "ThermischeNutzleistung",
    "KwkMastrNummer",
    "Batterietechnologie",
    "DatumBeginnVoruebergehendeStilllegung",
    "DatumWiederaufnahmeBetrieb",
    "Postleitzahl",
    "Ort",
    "Gemeinde",
    "Landkreis",
    "Lage",
    # PARSE_COLUMNS (Filesuffix is added by ppm, not sourced)
    "ArtDerWasserkraftanlage",
    "Biomasseart",
    "Energietraeger",
    "Hauptbrennstoff",
    "NameStromerzeugungseinheit",
    "NameKraftwerksblock",
    "NameWindpark",
    "Technologie",
    # RENAME_COLUMNS keys
    "EinheitMastrNummer",
    "NameKraftwerk",
    "Land",
    "Nettonennleistung",
    "Inbetriebnahmedatum",
    "DatumEndgueltigeStilllegung",
    "EinheitBetriebsstatus",
    "Laengengrad",
    "Breitengrad",
    "WEIC",
]
STORAGE_UNITS_COLUMNS = ["NutzbareSpeicherkapazitaet", "VerknuepfteEinheit"]

DEFAULT_DB = Path.home() / ".open-MaStR" / "data" / "sqlite" / "open-mastr.db"
DEFAULT_OUT_DIR = (
    Path.home() / ".local" / "share" / "powerplantmatching" / "data" / "in"
)


def _existing_columns(con: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in con.execute(f"PRAGMA table_info({table})")]


def build(db_path: Path, out_path: Path, date_tag: str) -> None:
    con = sqlite3.connect(db_path)
    folder = f"bnetza_open_mastr_{date_tag}"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with (
        tempfile.TemporaryDirectory() as tmp,
        zipfile.ZipFile(
            out_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
        ) as zf,
    ):
        for table, csv_name in TABLE_TO_CSV.items():
            avail = _existing_columns(con, table)
            if not avail:
                print(f"  skip {table}: table missing/empty")
                continue
            wanted = (
                STORAGE_UNITS_COLUMNS if table == "storage_units" else EXTENDED_COLUMNS
            )
            cols = [c for c in wanted if c in avail]
            if not cols:
                print(f"  skip {table}: none of the wanted columns present")
                continue
            df = pd.read_sql(f"SELECT {', '.join(cols)} FROM {table}", con)
            csv_path = Path(tmp) / csv_name
            df.to_csv(csv_path, index=False)
            zf.write(csv_path, arcname=f"{folder}/{csv_name}")
            print(f"  {table:22} -> {csv_name:38} rows={len(df):>9} cols={len(cols)}")
    con.close()
    print(f"\nWrote {out_path}  ({out_path.stat().st_size / 1e6:.0f} MB)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument(
        "--date", default=None, help="date tag for folder/filename, e.g. 2026-06-14"
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    date_tag = args.date or os.environ.get("MASTR_DATE_TAG")
    if not date_tag:
        raise SystemExit("pass --date YYYY-MM-DD (the bulk export date)")

    out_path = args.out or (DEFAULT_OUT_DIR / f"bnetza_open_mastr_{date_tag}.zip")
    print(f"DB:  {args.db}\nOut: {out_path}\n")
    build(args.db, out_path, date_tag)


if __name__ == "__main__":
    main()
