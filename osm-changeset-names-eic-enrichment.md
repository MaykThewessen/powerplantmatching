# OSM changeset drafts: naming + ref:EU:EIC enrichment for power plants

**Status: UPLOADED on 2026-07-03** via the OSM API (OAuth app claude-changesets),
after re-validating every object against live state (guards: power=plant, expected
name, no conflicting existing tags):

- Changeset 1 (6 NL EIC additions): https://www.openstreetmap.org/changeset/185022959
- Changeset 2 (Kelmė + Sysav names): https://www.openstreetmap.org/changeset/185022960

All 8 objects updated (Maasvlakte way v4, Onyx v13, Swentibold v5, RoCa v18,
Den Haag v15, Lage Weide relation v3, Kelmė relation v2, Sysav way v2).

## Motivation

powerplantmatching consumes OpenStreetMap through the pre-built
`osm_global.csv.gz` table from open-energy-transition/osm-powerplants. Its fuzzy
matchers fail whenever a plant's `name` is missing, abbreviated, an operator-only
label, or generic. The far more robust path is deterministic matching on the
ENTSO-E Energy Identification Code (EIC): when an OSM plant carries
`ref:EU:EIC=<code>`, it can be joined 1:1 to the ENTSO-E generation-unit record
(and thus to every dataset keyed on EIC) without any name similarity at all.

The user has an open PR (open-energy-transition/osm-powerplants#14) to extract
`ref:EU:EIC` into a dedicated EIC column, and PyPSA/powerplantmatching#289
adds EIC-first deterministic matching before the Duke fuzzy matcher. This draft targets the two highest-value
enrichments those PRs unlock:

1. **`ref:EU:EIC`** on large, unambiguously-identified plants that today carry a
   good name but no EIC. This is the bulk of the value: it converts a fuzzy match
   into a deterministic one.
2. **Complete naming tags** on plants that are genuinely nameless in live OSM.

Every proposed tag is traceable to a cited source. Live tags were fetched from
the OSM API on **2026-07-02** (per object below). The cached
`osm_global.csv.gz` table is several weeks stale, so many plants that looked
weak in the table already carry good names live; those were rejected (see
"Rejected candidates" at the end). Fewer well-sourced changes beat many
speculative ones.

### EIC source

EIC codes are taken from the cached ENTSO-E Transparency Platform generation-unit
list (`entsoe_transparency_platform_20250820.csv`, NL bidding zone
`10YNL----------L`), cross-checked for name + fuel-type + capacity + location
consistency against the OSM object and independent public sources. Only the
16-character production-unit W-codes (prefix `49W`) are proposed, and only where
the correspondence is unambiguous.

## Summary table

| Plant | Country | MW | OSM object | Change |
|---|---|---|---|---|
| Centrale Maasvlakte (MPP3) | NL | 1070 | way/1275268357 | add ref:EU:EIC=49W000000000102B |
| Onyx Centrale Rotterdam | NL | 731 | way/608602718 | add ref:EU:EIC=49W000000000078J |
| Centrale Swentibold | NL | 209 | way/908909571 | add ref:EU:EIC=49W0000000001217 |
| Centrale RoCa (RoCa3) | NL | 220 | way/54099556 | add ref:EU:EIC=49W0000000001047 |
| Uniper Centrale Den Haag | NL | 112 | way/214775379 | add ref:EU:EIC=49W0000000000342 |
| Centrale Lage Weide | NL | 248 | relation/17222289 | add ref:EU:EIC=49W000000000047U |
| Kelmė wind farm | LT | 314 | relation/19223894 | add name + name:en + start_date |
| Sysav waste-to-energy plant | SE | (waste CHP) | way/1052858580 | add name + name:en |

Six EIC additions (all NL) plus two naming additions (LT, SE). The German 260 MW
solar plant near Bartow was investigated and deliberately left unchanged (a local
mapper set `not:name` for good reason: see "Rejected candidates").

---

# Changeset 1: Netherlands, add ref:EU:EIC to large conventional plants

Suggested single changeset (6 objects, all Netherlands). All six already have a
correct `name`; the only change is adding the deterministic EIC reference. None
of these objects carried `ref:EU:EIC` when fetched on 2026-07-02.

## 1.1 Centrale Maasvlakte (MPP3), Uniper

**OSM object:** way/1275268357
(https://www.openstreetmap.org/way/1275268357)

**Current live tags (fetched 2026-07-02):** `power=plant`,
`name=Centrale Maasvlakte`, `operator=Uniper`, `operator:wikidata=Q19839259`,
`plant:source=coal`, `plant:method=combustion`,
`plant:output:electricity=1070 MW`, `start_date=2016`, `wikidata=Q2552071`,
`wikipedia=nl:Centrale Maasvlakte`. No `ref:EU:EIC`.

**Tag changes to apply:**
- Add `ref:EU:EIC=49W000000000102B`

**Justification:** ENTSO-E generation-unit record "Maasvlakte", NL bidding zone,
Fossil Hard coal, 1070 MW: an exact capacity and fuel-type match to this object,
which is Uniper's Maasvlakte Power Plant 3 (MPP3), hard coal (with biomass
co-firing), 1070 MW, opened 2016. There is no other 1070 MW coal unit in the NL
bidding zone. Confidence: HIGH.
- ENTSO-E generation-unit list (cached `entsoe_transparency_platform_20250820.csv`)
- https://www.uniper.energy/ (Maasvlakte energy hub, MPP3)
- https://www.gem.wiki/Maasvlakte_Power_Station_(Uniper)

## 1.2 Onyx Centrale Rotterdam

**OSM object:** way/608602718
(https://www.openstreetmap.org/way/608602718)

**Current live tags (fetched 2026-07-02):** `power=plant`,
`name=Onyx Centrale Rotterdam`, `operator=Riverstone Holdings`,
`operator:wikidata=Q7338653`, `plant:source=coal`, `plant:method=combustion`,
`plant:output:electricity=736 MW`, `start_date=2013`, `wikidata=Q29414104`,
`wikipedia=nl:Onyx Centrale Rotterdam`. No `ref:EU:EIC`.

**Tag changes to apply:**
- Add `ref:EU:EIC=49W000000000078J`

**Justification:** ENTSO-E generation-unit "NLROTTETH__1", NL bidding zone,
Fossil Hard coal, 731 MW. The coded name reads NL + ROTTerdam + TH (thermal).
S&P Global describes the exact plant as the "731-MW Rotterdam coal plant" and
Global Energy Monitor lists 731 MW; the operator's own site (Onyx Power) gives
net 731 MW hard coal on the Maasvlakte. It is the only 731 MW coal unit in the
NL zone. Confidence: HIGH.

Status note: this plant has been offline since a February 2020 breakdown and the
Dutch government agreed closure compensation in November 2021 (coal use ending,
decommissioning over up to three years). The EIC is still worth adding: it lets
matchers deterministically link the OSM object to the historical ENTSO-E unit
record even after retirement. Do not change the capacity or status tags here
without a dedicated operator source.
- ENTSO-E generation-unit list (cached CSV, unit NLROTTETH__1)
- https://www.spglobal.com/commodity-insights/en/news-research/latest-news/electric-power/120121-dutch-government-agrees-on-closure-compensation-for-731-mw-rotterdam-coal-plant
- https://www.gem.wiki/Maasvlakte_Power_Station_(Riverstone_Holdings)
- https://www.onyx-power.com/en/locations/power-plant-rotterdam/

## 1.3 Centrale Swentibold

**OSM object:** way/908909571
(https://www.openstreetmap.org/way/908909571)

**Current live tags (fetched 2026-07-02):** `power=plant`,
`name=Centrale Swentibold`, `operator=Utility Support Group`,
`plant:source=gas`, `plant:output:electricity=231 MW`, `start_date=1999`,
`wikidata=Q16069901`, `wikipedia=nl:Centrale Swentibold`. No `ref:EU:EIC`.

**Tag changes to apply:**
- Add `ref:EU:EIC=49W0000000001217`

**Justification:** ENTSO-E generation-unit "Swentibold", NL bidding zone, Fossil
Gas, 209 MW: a unique name match (Swentibold is a single named plant on the
Chemelot site in Geleen). The 209 MW (ENTSO-E registered) vs 231 MW (OSM
nameplate) difference is within the normal net-vs-gross spread for a single unit.
Confidence: HIGH.

Optional (not applied here, flagged for the mapper): the generation operator is
RWE Generation NL per RWE's own site; "Utility Support Group" runs site utilities
at Chemelot. Leave `operator` unchanged unless you want to verify and correct it
separately; this draft only adds the EIC.
- ENTSO-E generation-unit list (cached CSV, unit Swentibold)
- https://benelux.rwe.com/en/locations-and-projects/swentibold-power-plant
- https://www.gem.wiki/Swentibold_power_station

## 1.4 Centrale RoCa (RoCa3)

**OSM object:** way/54099556
(https://www.openstreetmap.org/way/54099556)

**Current live tags (fetched 2026-07-02):** `power=plant`, `name=RoCa3`,
`operator=E.ON`, `plant:source=gas`, `plant:output:electricity=220 MW`,
`start_date=1982`, `wikidata=Q15873801`, `wikipedia=nl:Centrale RoCa`. No
`ref:EU:EIC`.

**Tag changes to apply:**
- Add `ref:EU:EIC=49W0000000001047`

**Justification:** ENTSO-E generation-unit "RoCa", NL bidding zone, Fossil Gas,
220 MW: an exact capacity and fuel match, and the name matches the RoCa3 CCGT/CHP
block at Rotterdam-Capelle. Confidence: HIGH.
- ENTSO-E generation-unit list (cached CSV, unit RoCa)
- https://www.gem.wiki/Rotterdam_Capelle_(RoCa)_power_station
- https://www.uniper.energy/ (Rotterdam city plant)

## 1.5 Uniper Centrale Den Haag

**OSM object:** way/214775379
(https://www.openstreetmap.org/way/214775379)

**Current live tags (fetched 2026-07-02):** `power=plant`,
`name=Uniper Centrale Den Haag`, `operator=Uniper`, `plant:source=gas`,
`plant:output:electricity=110 MW`, `start_date=1947`, `wikidata=Q1894489`,
`wikipedia=nl:Energiecentrale Den Haag`. No `ref:EU:EIC`.

**Tag changes to apply:**
- Add `ref:EU:EIC=49W0000000000342`

**Justification:** ENTSO-E generation-unit "Den Haag", NL bidding zone, Fossil
Gas, 112 MW. The ~110-112 MW gas figure matches this Uniper Den Haag gas plant
(the historic Electriciteitsfabriek, retrofitted with two GE gas turbines in
2007), and there is no other ~110 MW gas plant in Den Haag. Confidence: HIGH.

Note (not applied here): the live `start_date=1947` is not corroborated by
sources: the building dates to 1906, the current gas turbines to 2007. This
draft does not touch `start_date` (no single clean commissioning year), only adds
the EIC. Flag for separate follow-up if desired.
- ENTSO-E generation-unit list (cached CSV, unit Den Haag)
- https://nl.wikipedia.org/wiki/Energiecentrale_Den_Haag
- https://www.gem.wiki/Den_Haag_power_station

## 1.6 Centrale Lage Weide

**OSM object:** relation/17222289
(https://www.openstreetmap.org/relation/17222289)

**Current live tags (fetched 2026-07-02):** `power=plant`,
`name=Centrale Lage Weide`, `operator=Eneco`, `plant:source=gas`,
`plant:output:electricity=266 MW`, `start_date=1959`, `wikidata=Q2702611`,
`wikipedia=nl:Centrale Lage Weide`. No `ref:EU:EIC`.

**Tag changes to apply:**
- Add `ref:EU:EIC=49W000000000047U`

**Justification:** ENTSO-E generation-unit "Lage Weide 6", NL bidding zone,
Fossil Gas, 248 MW. The current active unit at Lage Weide is a single CHP block
internally known as "Lage Weide 06" (nl.wikipedia gives 266 MW; ENTSO-E
registers 248 MW for the same single unit), so this is a clean 1:1
plant-to-unit correspondence. The 248 vs 266 MW gap is a nameplate-vs-registered
difference for the same unit. Confidence: HIGH (single active unit).
- ENTSO-E generation-unit list (cached CSV, unit Lage Weide 6)
- https://nl.wikipedia.org/wiki/Centrale_Lage_Weide

## Changeset 1 comment

> NL power plants: add ref:EU:EIC (ENTSO-E generation-unit codes) to 6 large, unambiguously-identified plants (Maasvlakte, Onyx Rotterdam, Swentibold, RoCa, Den Haag, Lage Weide). Enables deterministic matching to ENTSO-E / open datasets. Codes cross-checked on name + fuel + capacity + bidding zone. Source: ENTSO-E Transparency Platform generation-unit list.

---

# Changeset 2: Nameless renewables and waste plants, add names

Two objects in two countries. If your changeset workflow prefers one country per
changeset, split into 2a (Lithuania) and 2b (Sweden).

## 2.1 Kelmė wind farm (Kelmės vėjo elektrinių parkas), Lithuania

**OSM object:** relation/19223894
(https://www.openstreetmap.org/relation/19223894)

**Current live tags (fetched 2026-07-02):** `power=plant`, `type=site`,
`site=wind_farm`, `plant:source=wind`, `plant:output:electricity=314 MW`,
`operator=UAB Vėjas LT;Ignitis renewables`. No `name`, no `start_date`.

**Tag changes to apply:**
- Add `name=Kelmės vėjo elektrinių parkas`
- Add `name:en=Kelmė wind farm`
- Add `start_date=2025`

**Justification:** This is the Kelmė wind farm in western Lithuania, the largest
onshore wind farm in Lithuania and the Baltics: 44 turbines, 314 MW installed
(an exact match to the OSM `plant:output:electricity=314 MW`), developed and
operated by Ignitis Renewables (Ignitis Group), which matches the OSM operator
string. First stage reached commercial operation in April 2025, full
commissioning June 2025 (hence `start_date=2025`). Adding `start_date` also
raises inclusion, since osm-powerplants drops some way/relation plants without a
start_date. Confidence: HIGH.
- https://www.enerdata.net/publications/daily-energy-news/ignitis-renewables-fully-commissions-314-mw-wind-project-lithuania.html
- https://ignitisrenewables.com/the-first-stage-of-kelme-wind-farm-has-reached-commercial-operations-date/
- https://www.eib.org/en/press/all/2025-405-ignitis-group-secures-a-major-financing-deal-tied-to-the-largest-baltic-wind-farm

## 2.2 Sysav waste-to-energy plant, Malmö, Sweden

**OSM object:** way/1052858580
(https://www.openstreetmap.org/way/1052858580)

**Current live tags (fetched 2026-07-02):** `power=plant`, `plant:source=waste`,
`plant:method=combustion`, `operator=SYSAV`,
`plant:output:electricity=196 MW`, `plant:output:steam=174 MW`,
`plant:output:hot_water=60 MW`, `start_date=1973`, `landuse=industrial`,
`fixme=The output numbers may be wrong ...`. No `name`.

**Tag changes to apply:**
- Add `name=Sysav avfallskraftvärmeverk`
- Add `name:en=Sysav waste-to-energy plant`

**Justification:** This is the SYSAV (Sydskånes avfallsaktiebolag) waste-to-energy
combined heat and power plant in the Sjölunda industrial area of Malmö, matching
the OSM operator `SYSAV`, location, and waste fuel. The facility dates to 1973
(consistent with the existing `start_date=1973`), with additional boilers added
in 2003 and 2008. Confidence: HIGH on name/operator/location.

Do NOT change the output figures in this changeset. The plant is
district-heating-dominated (roughly 1.4 TWh heat vs 0.3 TWh electricity per year),
so the `plant:output:electricity=196 MW` value is almost certainly too high, as
the existing `fixme` already flags. Leave the `fixme` in place; correcting the
electrical output is a separate, source-backed edit.
- https://en.wikipedia.org/wiki/SYSAV_waste-to-energy_plant
- https://stateofgreen.com/en/solutions/waste-to-energy-chp-sysav-in-malmoe-sweden/
- https://www.friotherm.com/wp-content/uploads/2017/11/sysave006_uk.pdf

## Changeset 2 comment

> Add missing names to two large power plants confirmed against operator/public sources: Kelmė wind farm (314 MW, Ignitis Renewables, Lithuania) and the Sysav waste-to-energy CHP plant (Malmö, Sweden). Improves dataset matching for plants that were entirely nameless. (Kelmė also gets start_date=2025.)

---

# Rejected candidates (live data already fine or a name would be wrong)

These looked weak in the stale `osm_global.csv.gz` table but were verified against
live OSM on 2026-07-02 and left unchanged:

- **Solarpark near Bartow, Germany (260 MW), way/1274220605**: DO NOT add a name.
  A local mapper deliberately set `not:name=Solarpark Bartow` (moving the string
  to `description`) because the Bartow municipality has several distinct
  "Solarpark Bartow ..." parks (Ost, West, Konversion) and the polygon does not
  correspond 1:1 to any one official plan area. `not:name` means the plausible
  name is confirmed wrong. Respect it: a wrong name is worse than none.
- **Borssele Nuclear Power Station**: the live plant object is now
  relation/20806673 (`Kernenergiecentrale Borssele`) and already carries
  `ref:EU:EIC=49W000000000054X`, `operator=EPZ`, and a correct name. Nothing to do.
  (The stale table's way/87788958 no longer carries any power tags.)
- **Centrale Hemweg, way/292125850**: already carries
  `ref:EU:EIC=49W000000000045Y` and a correct name live. This is the working
  template that proves the pattern.
- **Sloecentrale (way/311472382), Centrale Merwedekanaal (way/903065206),
  Pergen**: well-named live but intentionally NOT given an EIC. Each is a
  multi-unit plant with two (or more) separate ENTSO-E generation-unit W-codes and
  no single plant-level code, so assigning one unit's W-code to the whole-plant
  polygon would be an ambiguous/partial match. Left for a future site-relation
  approach that can attach per-unit EICs.
- **way/287329147 (nameless 164 MW gas at Leiden)**: this is a duplicate polygon
  overlapping relation/18024360 (`Uniper Centrale Leiden`, correctly named). Adding
  a name to a duplicate would create two matchable names for one plant, hurting
  matching. Flagged as a data-quality (duplicate-object) issue instead.
- **way/288454756 (former "IJmond 1")**: live object is now only
  `building=industrial` with no `power=*` tags: no longer a plant object. Skip.
- **NL wind farms that were cryptic in the table but are well-named live**:
  Windplanblauw (rel/12695731, was "RD03"), Windpark Zeewolde (rel/12695366, was
  "RDT-04"), Windpark De Drentse Monden en Oostermoer (rel/12361136, was "RH-1.2"),
  Windpark Maasvlakte 2 (rel/13839170, was "HZ-03"), Windpark Kreekraksluizen
  (rel/12372452, was "#Nl Krs Wp01"), Windpark Eekerpolder (rel/11985860, "N33"),
  Windpark Vermeer Noord (rel/19269842).
- **Rest-of-Europe plants cryptic in the table but well-named live**: Grand-Maison
  (FR, rel/3113489 + 3113488), Centrale de La Bathie (FR, rel/4500049), Whitelee
  Wind Farm (UK, rel/2593160), Øyfjellet vindkraftverk (NO, rel/12629796),
  Voestalpine Kraftwerk Linz (AT, rel/14006374), Windpark Feldheim (DE,
  rel/14887956), Centrale hydroélectrique de Bort (FR, rel/5973967), Tellenes
  vindkraftverk (NO, rel/7885555), Windpark Wangenheim/Hochheim (DE, rel/9382777),
  Windpark Rastenberg (DE, rel/9371251), Sub-parque Eólico do Alto da Coutada
  (PT, rel/14052857), Farr (UK, rel/7872100), Windpark Kirchengel (DE,
  rel/17725708).

---

## Verification checklist before upload

- Re-fetch each object's live tags immediately before editing (this draft's
  fetch date is 2026-07-02; state may have changed).
- For each EIC addition, confirm the object still has no `ref:EU:EIC` and that its
  live `name`, `plant:source`, and `plant:output:electricity` still match the
  ENTSO-E unit cited.
- Use the per-changeset comments above. Keep changesets to one country/theme,
  10 objects or fewer.
- Do not churn `operator`, `capacity`, or `start_date` on the EIC-only edits
  unless separately sourced (the optional notes above call out the specific
  fields that may warrant a follow-up edit).
