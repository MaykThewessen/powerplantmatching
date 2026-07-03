# OSM changeset draft — NL waste-to-energy (AVI) batch — APPLIED

**UPLOADED 2026-07-03 as changeset
[185023244](https://www.openstreetmap.org/changeset/185023244)** (7 ways), on top of
Mayk's manual iD edits of 2026-07-02 ~13:00 UTC which had already applied most Tier 1
items (Moerdijk 123 MW + method, Wijster 54 MW, REC method, PreZero polish).

Deviations from the draft below:
- **EEW Delfzijl: left at Mayk's 50 MW** (own research in the `description` tag:
  "ca. 36 MW tot 50 MW"; operator set to group GmbH) — draft's 36 MW (PBL) NOT applied.
- **Westpoort: 64 MW → 150 MW** (64 was nl-wiki average AEC production, not nameplate).
- **Twence: Option B site total 73 MW** + `plant:source=waste;biomass` (biomass plant
  not separately mapped, confirmed via Overpass 2026-07-03).
- **Alkmaar: Option A 71.2 MW**; BEC (22 MW, 2006) is NOT mapped in OSM — open
  follow-up: map it as its own `power=plant` (needs geometry, do in iD).
- Wijster: replaced malformed `generator:output:heat=steam` with `plant:output:steam=yes`.

End state: all 11 NL AVIs carry numeric capacity + `plant:method` + `start_date`
(773.6 MW honest total) → all pass every osm-powerplants gate at the next upstream
rebuild.

---

Original draft below (kept for the sourcing rationale).

**Verified live 2026-07-02 via main OSM API** (`/api/0.6/ways`). Do NOT re-verify via
overpass.kumi.systems: it served ~7-months-stale data on 2026-07-02 (missing our own
June 12 edits); overpass-api.de and overpass.private.coffee were timing out.

Why this batch matters downstream: osm-powerplants silently drops way-plants without
`start_date` (see `2026-jul-02-22h14-upstream-osm-powerplants-issue-drafts.md`), so
the `start_date` fills below are what get Wijster, Twence, Rozenburg, Dordrecht and
Westpoort into `osm_global.csv.gz` at all. Capacity corrections fix ~340 MW of
overstatement (243→123 Moerdijk, 185→36 EEW, 92→54 Wijster).

Reference of record for capacities: PBL/TNO MIDDEN 2022 waste-incineration report,
Table 2.5 (2018 installed MWth/MWe for all 12 NL AVIs):
<https://www.pbl.nl/uploads/default/downloads/pbl-2022-decarbonisation-options-for-the-dutch-waste-incineration-industry-4916.pdf>
(stale for Moerdijk: predates the 2017 turbine).

---

## Tier 1 — pure gap fills (safe, upload as-is)

### way/813659494 — Afvalenergiecentrale Westpoort (AEB Amsterdam)

- `plant:output:electricity` = `yes` → **`150 MW`**
  (AEC 2×39 MWe turbines 1993 + HRC 72 MWe turbine 2007; GEM GBPT units
  G100000200240/G100001052295/G100000200241; City-zen D5.16 p.15, report written
  with AEB. PBL lists 154 MWe. HRC net design is 57 MW at 30%+ net efficiency,
  NAWTEC16-1929 — gross nameplate is the OSM convention.)
- add **`start_date=1993`** (AEB history page "in 1993 voltooid en in gebruik
  genomen"; Rijkswaterstaat Tabel C-2: in gebruikname 1-1-1993)
- add `source:plant:output:electricity` =
  `Global Energy Monitor GBPT (AEC 2x39 MW 1993, HRC 72 MW 2007); City-zen D5.16`
- Do **not** change `operator=Afval Energie Bedrijf`: the AVR takeover was blocked
  by ACM (2021), and Amsterdam decided 2025-02-11 to keep AEB for ≥10 years.
- NOTE: the nl.wikipedia "64 MW" is the AEC's *average annual production*
  (525 GWh/yr ≈ 60–64 MW continuous), not installed capacity. Ignore.

### way/404999017 — Attero Afvalenergiecentrale Moerdijk

- add **`plant:method=combustion`** (grate incinerator)
- `plant:output:electricity` = `243 MW` → **`123 MW`**
  (new steam-turbine generator in service Nov 2017: "de nieuwe turbine 123 MW"
  energienieuws.info/2015/01/nieuwe-attero-turbine.html; "ruim 120 MW"
  cordeel.nl/nl/projecten/attero-stoomturbine-moerdijk; from 2018 all power to the
  150 kV grid, steam to Shell, afvalonline.nl/bericht/25470. Origin of 243 unknown,
  plausibly thermal. PBL's 16.2 MWe is pre-2018 and also stale.)
- keep `plant:output:steam=yes` (450 t/h to Shell Moerdijk)
- add `source:plant:output:electricity` =
  `Attero STG 2017, 123 MW (energienieuws.info; cordeel.nl project page)`

### way/302051658 — Reststoffen Energie Centrale (Omrin, Harlingen)

- add **`plant:method=combustion`** (only edit; 20 MW / 2008 left untouched)

### way/684877116 — EEW Energy from Waste (Delfzijl)

- add **`operator=EEW Energy from Waste Delfzijl B.V.`**
  (eew-energyfromwaste.com/en/our-sites/delfzijl; PBL lists "EEW Delfzijl B.V.")
- `plant:output:electricity` = `185 MW` → **`36 MW`**
  (PBL Table 2.5: 180 MWth / 36 MWe. The OSM 185 ≈ PBL's 180 MWth mislabeled as
  electric. EEW's own 2022 figures: 156 GWh electricity, 949 GWh steam per year —
  consistent with 36 MWe, impossible for 185 MWe.)
- `plant:output:steam` = `463 MW` → **`yes`** (463 unsupported anywhere; real steam
  ≈ 108 MW average from 949 GWh/yr, but no nameplate source — don't invent)
- add `source:plant:output:electricity` = `PBL/TNO MIDDEN 2022 Table 2.5 (36 MWe)`
- operator:wikidata: SKIP for now. Group items exist (Q902021, newer Q131891245)
  but operator names the Dutch B.V., which has no own item. Decide later.

### way/27402460 — Attero (Wijster, GAVI)

- add **`start_date=1996`** (GAVI in gebruik 9 sep 1996: historiebeilen.nl,
  wijster.info, Attero's own historische tijdlijn. GEM's 1992 cites a dead link;
  nl-wiki's 1992 is unsourced — 1996 is the defensible year.)
- `plant:output:electricity` = `92 MW` → **`54 MW`**
  (Attero's own CEWEP 2012 paper: "Turbine generator: 54 MWe gross (installed
  capacity), (48 MWe at design load)" —
  cewep.eu/wp-content/uploads/2017/11/996_6_d_spanjaard_improving_r1_attero_wijster.pdf)
- add `source:plant:output:electricity` =
  `Attero CEWEP 2012 paper: 54 MWe gross installed (48 MWe design load)`

### way/1431035765 — Afvalenergiecentrale Dordrecht (HVC)

- add **`start_date=1973`** (Rijkswaterstaat Tabel C-2: in gebruikname 1-6-1973,
  ex-Gevudo; GEM also 1973). Current energy line (5th, 32 MWe) in service
  2009/2010 — optionally `note=Huidige 5e lijn met 32 MWe turbine sinds 2009`.
- capacity 32 MW stands (PBL 32.5 MWe; 32 MW turbine nameplate) — no change.

---

## Tier 2 — decision points (pick before upload)

### way/51089306 — HVC Alkmaar: 93 MW conflates AVI + separate BEC

The way is `building=industrial` (the AVI building). GEM's "at least 93 MW" =
71.2 MW AVI (unit 1) + 22 MW bio-energiecentrale BEC (unit 2, 2006) — but the BEC
is a separate facility/building.

- **Option A (recommended):** `plant:output:electricity` 93 → **`71.2 MW`**
  (PBL Table 2.5: 243 MWth / 71.2 MWe) and update
  `source:plant:output:electricity` to `PBL/TNO MIDDEN 2022 Table 2.5 (AVI only;
  BEC 22 MW is a separate installation)`. Check in the editor whether the BEC is
  mapped; if not, map it as its own `power=plant` (22 MW, 2006).
  (Overpass was down 2026-07-02; separate-BEC check still outstanding.)
- **Option B:** keep 93 as site total — only defensible if the polygon is enlarged
  to the whole site including the BEC.

### way/700898274 — Twence: 75 MW conflates AVI + biomass plant

Way is the `landuse=industrial` site polygon, so a site total is geometrically
defensible, but 75 matches no source exactly: AVI = 2×25 MWel (District Energy
Award summary, archived) or 56 MWe (PBL); separate wood-fired unit 23 MWel.

- **Option A (recommended):** keep the site polygon, set **`56 MW`** on the AVI
  basis (PBL) only if the biomass plant gets its own object; otherwise
- **Option B:** retag as site total `73 MW` (50 AVI + 23 bio, District Energy
  Award) with a source tag saying so.
- add **`start_date=1997`** either way (Tabel C-2: in gebruikname 1-7-1997;
  line 3 added 2009).

### way/1237376864 — AVR Rozenburg: 122 MW unverifiable

`plant:source=waste;biomass` already reflects the two units. Best-sourced:
108 MW waste (Modern Power Systems) + 22 MW wood unit 2008 (GEM) = 130 MW;
PBL says 140 MWe site-wide. The current 122 has no findable source.

- **Option A (recommended):** `plant:output:electricity` 122 → **`130 MW`**,
  `source:plant:output:electricity` = `GEM: 108 MW waste (1973) + 22 MW wood
  (2008); PBL 2022 site total 140 MWe`
- **Option B:** leave 122, only add start_date.
- add **`start_date=1972`** either way (first ovens mid-1972: RDM archief; MPS
  "entered operation in 1972". Tabel C-2 formal date 1-1-1973 — acceptable
  alternative; GEM uses 1973.)

---

## No edit needed

- **way/47962126 AVR Duiven** — complete (31.4 MW, combustion, 1984, wikidata).
- **way/277240530 PreZero Energy** — complete since our 2026-06-12 edit; 39 MWe
  independently confirmed (PBL: 124 MWth / 39 MWe).
- `name:en` stays empty everywhere: no established English names exist.

## Changeset comment

> NL afvalenergiecentrales: add missing start_date / operator / plant:method;
> correct plant:output:electricity to sourced installed capacity (PBL/TNO MIDDEN
> 2022 Table 2.5, Global Energy Monitor GBPT, operator publications). Source per
> value in source:plant:output:electricity.

## After upload

1. osm-powerplants rebuilds six-monthly (cron `0 0 1 */6 *`) or via maintainer
   `workflow_dispatch` — request a rebuild when filing the start_date issue.
2. Bump the ppm pin (`config.yaml` OSM url) — already worthwhile today to
   `fdc852389a` (2026-07-01 build: brings in Alkmaar + PreZero).
3. Expected end state: all 11 NL AVIs in OSM source at ~715 MW honest total
   (today: 4 plants / 479 MW, of which ~428 MW carries wrong values).
