# powerplantmatching - upstream issue & PR proposals

Draft proposals for **PyPSA/powerplantmatching**, based on work done on this fork
(Jun 2026). Each item is ready to file as an issue or PR. Checked against open
issues; no duplicates except where noted (relate to #242-244, #273, #286, #287).

---

## PR 1 - open-mastr bulk-export compatibility for the MASTR source

**Type**: PR (bug fixes, we have the patch)
**Files**: `powerplantmatching/data.py`, `powerplantmatching/utils.py`

The MASTR loader assumes the Zenodo CSV dump layout. Zenodo's last dump is frozen
at **2025-02-09** (record 14783581, `is_last:true`); the live registry is months
newer. Driving the loader off a locally built dump from the **open-mastr bulk
export** (current to the day) surfaced three bugs:

1. **Hardcoded dated path for storage_units.** `MASTR()` reads
   `bnetza_open_mastr_2025-02-09/bnetza_mastr_storage_units_raw.csv` by literal
   string, so any other-dated dump raises. Fixed by matching on the filename
   suffix like the other tables.
2. **`ThermischeNutzleistung` assumed present.** It exists in the Zenodo CSV but
   **not** in the open-mastr bulk export, so CHP detection raises `KeyError`.
   Fixed by guarding the column (CHP falls back to `KwkMastrNummer` alone).
3. **`update=True` regresses a glob `fn` to the frozen URL.** With a glob filename
   (auto-selecting the newest local dump), `get_raw_file(update=True)` skipped the
   local match and re-downloaded the frozen 2025 Zenodo zip - silently using stale
   data on a forced refresh. Fixed by preferring the newest local match (the URL
   is only a seed and can never be newer than a dated local build).

Also includes a small helper script to build the ppm-format zip from an
open-mastr SQLite DB (`scripts/build_mastr_zip_from_open_mastr.py`), so users can
refresh MASTR without waiting for a Zenodo re-release.

---

## Issue 2 - open-mastr bulk download silently drops the combustion table

**Type**: Issue (root cause is upstream open-mastr; ppm users are the victims)
**Severity**: high - **0 German conventional plants** (gas/coal/oil) if unnoticed

A fresh `open_mastr.Mastr().download()` aborts `combustion_extended`
(EinheitenVerbrennung) with
`could not convert string to float: '2442, 2442'` and leaves it at **0 rows** -
logged as ERROR only, so `download()` still exits 0. Every other technology
parses fine, so it is easy to ship a German fleet missing all conventional
thermal capacity (~93.6k units / ~101 GW).

Root cause: open-mastr's `replace_mastr_katalogeintraege`
(`xml_download/utils_cleansing_bulk.py`) casts catalog columns with
`.astype("float")`; `WeitereBrennstoffe` can hold comma-separated catalog codes
(e.g. `"2442, 2442"`), which crashes the cast. Workaround: re-drive the casts
through `pd.to_numeric(errors="coerce")` (the unparseable multi-code value is
unused downstream).

Ask: (a) file upstream at OpenEnergyPlatform/open-MaStR; (b) ppm should at least
validate non-empty per-technology row counts after a MASTR build and warn loudly.

---

## Issue 3 - distributed NL greenhouse CHP (glastuinbouw WKK) entirely missing

**Type**: Issue (data coverage gap), with proposed data + method
**Severity**: medium - material for any NL-resolved model

`powerplants()` has **35 NL CHP units, all >= 20 MW** (transmission-connected:
Sloe, Rijnmond, Diemen, ...). The Dutch **greenhouse CHP fleet** -
**~7,000 gas engines, ~3-3.5 GWe, mostly 10-20 kV DSO-connected** (Westland,
Aalsmeer, Venlo) - is **completely absent** (NL gas CHP < 20 MW = **0**). These
are below transmission level, so ENTSO-E / OPSD / GEM / GPD / GEO all miss them.
This is a real chunk of NL dispatchable gas, mis-attributed to utility CCGT.

Authoritative sources for the aggregate:
- **LEI Wageningen Energiemonitor Glastuinbouw**: ~2,300 MWe (2024), ~3,200 MWe
  peak (2010), ~4,000 gasmotor units.
- **CBS Energiebalans Regionaal**: per-gemeente self-generation (Westland ~2.5 TWh/y).

Proposal: ppm cannot enumerate 7,000 DSO units, but could ship an **aggregated
NL greenhouse-CHP source** (cluster rows per region/substation, ~16 rows,
`Set=CHP`, `Fueltype=Natural Gas`), behind a config flag, with the LEI/CBS
provenance. A working 2,800 MW / 16-cluster table already exists on our side and
can be contributed. At minimum, document the limitation so users do not assume NL
CHP is complete.

---

## Issue 4 - OSM source is pinned to a frozen commit and off by default

**Type**: Issue (+ small PR), relates to #242, #243, #244
**Files**: `powerplantmatching/package_data/config.yaml`

Two coupled problems with the OSM source (added in #272):

1. **Pinned to a fixed commit.** `url` points at
   `open-energy-transition/osm-powerplants` commit `13bb6a3`. Manual OSM
   corrections (e.g. fixing NL plant capacities) never propagate to ppm unless
   the pin is bumped. There is no documented refresh path.
2. **Not in `matching_sources` or `fully_included_sources`.** OSM is loadable via
   `pm.data.OSM()` but is **excluded from the combined `powerplants()` output**.
   Many users will not realise their build contains no OSM data.

Proposal: (a) document the pin-bump / repoint workflow; (b) offer an opt-in to
include OSM in the default lists with sensible capacity filters and the same
German-VRE exclusions the other sources use (MASTR owns German wind/solar). OSM
loads clean here (12,917 plants, 35 countries, 570 GW, zero NaN coords) and is a
good cross-check, especially where a region's contributor has curated it.

---

## Already mapped to open issues (our fork has fixes)

- **#286** OPSD backup URL drops efficiency column / biomass co-firing unused -
  fork branch `fix/opsd-efficiency-and-biomass`.
- **#287** Use EIC codes as deterministic matching key before Duke -
  fork branch `feature/eic-deterministic-matching`.
- **#273** Duplicating generation assets - relevant to the OSM/MASTR dedup behaviour
  and the source-precedence (`reliability_score`) reduction.

## Cross-cutting: pandas 3 compatibility

Bulk runs on pandas 3.0.x surface `Pandas4Warning` (deprecated `copy=` keyword)
and Copy-on-Write behaviour in the cleaning/duke/aggregate paths. Largely
addressed on this fork; worth a compatibility PR + a CI matrix entry for pandas 3.
