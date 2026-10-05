<!-- SPDX-FileCopyrightText: Contributors to powerplantmatching <https://github.com/pypsa/powerplantmatching> -->
<!-- SPDX-License-Identifier: MIT -->

# UK REPD loader research

Checked on 2026-10-05. This prepares [issue #257](https://github.com/PyPSA/powerplantmatching/issues/257) for implementation. Source recommendations below are proposed choices, not upstream policy.

## Official extract and reuse

The current official extract is July 2026, quarter 2, published on 3 August 2026. The former monthly URL redirects to the quarterly publication. Coverage is UK renewable electricity projects above 150 kW; the threshold was 1 MW before 2021. Small older installations can therefore be absent. The publication footer states Open Government Licence v3.0 except where otherwise stated. No additional reuse restriction was identified during this check. Retain DESNZ attribution and the source URL. [Official publication](https://www.gov.uk/government/publications/renewable-energy-planning-database-quarterly-extract), [GOV.UK reuse terms](https://www.gov.uk/help/terms-conditions).

- [Official CSV](https://assets.publishing.service.gov.uk/media/6a6cbdc00c36759b5ccaa305/REPD_Publication_Q2_2026.csv)
- [Official Excel with definitions](https://assets.publishing.service.gov.uk/media/6a6cbdd2862aaf18d9c62b02/REPD_Publication_Q2_2026.xlsx)

The workbook was downloaded to `/private/tmp/repd-q2-2026.xlsx`. Its sheets are `Definition Sheet` and `REPD`. Inspection found 14,657 records, 53 columns, unique `Ref ID`, and 3,132 operational records. Fifty operational records have unknown electrical capacity. These are source observations, not model validation results. [Workbook](https://assets.publishing.service.gov.uk/media/6a6cbdd2862aaf18d9c62b02/REPD_Publication_Q2_2026.xlsx).

## Mapping contract

| Input | Proposed output or handling |
|---|---|
| Ref ID | Stable projectID `REPD-<integer>` |
| Site Name | Name |
| Installed Capacity (MWelec) | Capacity in MW; numeric coercion, preserve unknown |
| Country | Strip whitespace; map constituent nations to United Kingdom |
| X-coordinate, Y-coordinate | British National Grid, transform to longitude and latitude |
| Operational | DateIn year from actual operation date |
| CHP Enabled | CHP when Yes, otherwise PP unless storage |
| Technology Type | Explicit fuel and technology mapping |
| Development Status (short) | Configurable filter, proposed default Operational |
| Storage Co-location REPD Ref ID | Relationship metadata, never sum into generation |

The definitions specify British National Grid for XY. Use that system for Northern Ireland too, rather than automatically choosing Irish Grid. `Storage Type` has inconsistent case and whitespace. Strip column labels and string fields. `Old Ref ID` and reapplication references identify relationships, not equivalent IDs to merge blindly. [Workbook definitions and inspected fields](https://assets.publishing.service.gov.uk/media/6a6cbdd2862aaf18d9c62b02/REPD_Publication_Q2_2026.xlsx).

Use `pyproj.Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)` on arrays. The result order is longitude, latitude. Validate both coordinates together and preserve missing points. Project `pyproject.toml` currently does not declare pyproj, and it is absent from the active Pixi environment. Add it through Pixi and declare the runtime dependency. Do not implement a custom coordinate formula. Transformation accuracy depends on installed PROJ grids; do not claim survey accuracy. [Official pyproj API](https://pyproj4.github.io/pyproj/stable/api/transformer.html).

## Proposed technology and status policy

Suggested mappings are Solar Photovoltaics to Solar/PV, Wind Onshore and Wind Offshore to Wind with the corresponding technology, digestion and landfill gas to Biogas, dedicated biomass to Solid Biomass, and EfW Incineration to Waste. Small and Large Hydro should remain Hydro with unknown subtype unless another field proves reservoir or run-of-river. Pumped Storage Hydroelectricity maps to Hydro/Pumped Storage with Set Store. Battery maps to Battery with Set Store. CHP is a separate flag.

Co-firing biomass is not the entire thermal plant rating. Avoid adding it as fully included capacity. Advanced Conversion Technologies, Hydrogen, Air Source Heat Pumps and Unknown require explicit treatment; default to omission with a warning rather than guessing an electrical generation category. Fuel Cell Hydrogen and storage technologies require their own mappings if included.

Keep REPD opt-in initially. Normalize only Operational by default; raw=True returns all stages unchanged. Permit a configured status list for future scenario studies. Never infer DateIn from application dates or permission expiry. The latter is not DateOut. Revised applications should be excluded from the operational default and should not be counted alongside their replacements.

## Existing source overlap

`data.py` already contains `OPSD_VRE_country`, and config `OPSD_VRE_GB` points to the 2020-08-25 UK renewable extract. This creates potential overlap in UK wind, solar and other renewable assets. Current GEM, GPD and GEO loaders can also contain UK assets. Actual duplicate counts have not been measured. Use the existing matching pipeline for selected overlapping generation sources; adding REPD to fully_included_sources would require a capacity/deduplication study first. Local code inspected: `powerplantmatching/data.py` lines 1598 onward and `powerplantmatching/package_data/config.yaml` OPSD_VRE_GB.

## Implementation and acceptance checks

1. Add typed REPD loader in data.py and an opt-in version-pinned config source using the normal get_raw_file cache path. Prefer CSV for the published source; workbook defines its schema. Confirm CSV encoding and dates against the downloaded workbook before finalizing parsing.
2. Use explicit mapping constants, vectorized numeric conversion, UTC-aware date parsing, paired coordinate validation and source provenance. Preserve unknown capacities.
3. Tests should cover raw preservation, operational default versus configured pipeline statuses, stable IDs, UK country normalization, Northern Ireland coordinates, invalid coordinate pairs, storage/generation co-location separation, unknown technologies and missing capacities.
4. Run the real extract and report excluded statuses, mapping exclusions, unknown capacities and valid coordinates. Then evaluate duplicate candidates against existing UK renewable sources before enabling default matching or fully included behavior.

The exact CSV encoding remains unverified. This research changes no production code and does not certify the source as a complete UK operational inventory.

## Measured overlap before inclusion

Ran the current `linkage.match` on the operational REPD subset against the cached configured inventory, restricted to United Kingdom. This measures matching candidates, not independently confirmed identities. The inventory combines source statuses, including planned and retired assets; a candidate can refer to such a record. Its completion timestamp is `2026-10-04T19:43:35.751587+00:00`, with 180,064 global records and 2,976 UK records. Source vintages differ, so this is not a controlled coverage or recall experiment.

REPD input SHA256 is `624a0a9712c58a7a93716e51f2bf054eec8b1af7170f6f9516cc10cd248e2657` for `/private/tmp/repd-q2-2026.xlsx`. Comparison inventory is `/private/tmp/ppm-pr-review/full-build/validated-powerplant-inventory.parquet`, SHA256 `713ca9c71f92199dbf43791cc2f3b42b6169ee81f5b158e971532a1b527b1958`. Matcher source was inspected at repository HEAD `fdc8208763141983912c754cbb176594ea35ad38`.

The measured subset contains 3,095 operational records in the proposed mapping, including 48 unknown capacities. Excluded operational technologies total 37: Advanced Conversion Technologies 20, Tidal Stream 5, Hydrogen 3, Biomass co-firing 2, Shoreline Wave 2, Geothermal 2, and one each liquid-air storage, flywheels and compressed-air storage. These exclusions define this experiment, not final permanent mappings.

At inherited threshold 0.85, the matcher returned 4,760 candidate pairs involving 2,281 distinct REPD records. Its maximum-weight one-to-one selection retained 2,178 pairs. The remaining 917 mapped REPD records are unselected, which does not establish that they are absent from the inventory.

| Technology | Operational mapped REPD | Selected candidate pairs |
|---|---:|---:|
| Solar Photovoltaics | 1,407 | 1,213 |
| Wind Onshore | 785 | 708 |
| Wind Offshore | 49 | 39 |
| Battery | 178 | 103 |
| Anaerobic Digestion | 151 | 1 |
| Landfill Gas | 270 | 4 |
| Sewage Sludge Digestion | 12 | 0 |
| Dedicated biomass | 81 | 24 |
| EfW Incineration | 61 | 42 |
| Large Hydro | 25 | 15 |
| Small Hydro | 72 | 25 |
| Pumped hydro | 4 | 4 |

For wind and solar together, 1,960 of 2,241 records have selected candidates. Selected inventory records carry these source memberships: GEM 1,943, GPD 1,596, OSM 742, ENTSOE 99, EESI 96, OPSD 57, GHR 32, JRC 20, GEO 2 and BEYONDCOAL 1. Membership counts overlap because an inventory record can contain IDs from several sources. OPSD here is the configured inventory source, not a separate direct comparison against OPSD_VRE_GB.

Coordinates were transformed with global Pixi main's pyproj 3.8.0 without modifying project dependencies. EPSG:27700 to EPSG:4326 used always_xy=True; the selected operation reports expected accuracy 2 metres, not verified site-position accuracy. Invalid transformed pairs were replaced with paired NaN before matching. Unknown capacities stayed unknown. The resulting candidate counts remained unchanged after that correction.

Analysis outputs are preserved in `outputs/2026-oct-05-uk-repd-overlap/repd-overlap-summary.json` and `outputs/2026-oct-05-uk-repd-overlap/repd-overlap-selected-candidates.parquet`; the exploratory runner is `/private/tmp/repd-overlap-analysis.py`. The measured overlap supports keeping REPD opt-in and avoiding blanket fully included behavior. Especially for solar and wind, raw appending would add many plausible duplicates. The very low digestion and landfill-gas matches warrant reviewing source coverage, fuel categorization and names before calling those records new capacity. Implement the loader next, then inspect candidate samples and residuals before considering default inclusion.
