# Upstream issue drafts for open-energy-transition/osm-powerplants

Verified 2026-07-02 against pinned commit `262b9a550e86` (code + published artifacts)
and the fresh dataset build `fdc852389a` (2026-07-01). Their tracker has nothing on
either topic (14 items total; closest are #13/#14 on EIC extraction).

**FILED 2026-07-03:** Issue 1 = upstream #15, fix PR = #18 (branch
`fix/honor-missing-start-date-allowed` on fork MaykThewessen: gates the
`start_date is None` drop on `missing_start_date_allowed` in both plants.py and
generators.py, +6 tests, suite 68 green). Issue 2 = upstream #16, fix PR = #17
(filed concurrently in another session). Both PRs await maintainer CI approval
(first-time contributor gate, `action_required`).

---

## Issue 1: way/node plants without `start_date` are silently dropped despite `missing_start_date_allowed: true`

**Title:** `way`/`node` plants without `start_date` are silently dropped, contradicting `missing_start_date_allowed: true`

**Body:**

`PlantParser.process_element` unconditionally rejects way- and node-type plants that
lack a `start_date` tag (`src/osm_powerplants/parsing/plants.py:229-230` at
`262b9a5`):

```python
if start_date is None:
    return None
```

The config shipped with the CI build says `missing_start_date_allowed: true`
(`config.yaml:10`), but that flag is only honored in the relation member-aggregation
salvage path (`plants.py:363-364`). Worse, in `parsing/base.py:433-434` the flag
short-circuits *before* `add_rejection`:

```python
if missing_start_date_allowed:
    return None          # no rejection recorded
```

so an affected plant appears in **neither** the accepted CSV **nor**
`*_rejected.csv`. There is no trace that it was ever considered.

**Empirical impact** (published `osm_global.csv.gz` at `262b9a5`): 0 of 16,618
way-type and 0 of 107 node-type plants have missing `DateIn`, while 3,685 of 12,245
relations do. Every way-mapped plant in OSM without `start_date` is invisible in the
output, regardless of how completely it is otherwise tagged.

**Repro** (present in OSM since 2025-09, still absent from the 2026-07-01 build
`fdc852389a`, in both accepted and rejected outputs):
[way/1431035765](https://www.openstreetmap.org/way/1431035765)
"Afvalenergiecentrale Dordrecht" (NL) carries `power=plant`, `plant:source=waste`,
`plant:method=combustion`, `plant:output:electricity=32 MW`, `name`, `operator` —
everything the parser needs except `start_date`.

More NL examples with numeric capacity, all silently dropped:
[way/27402460](https://www.openstreetmap.org/way/27402460) Attero Wijster,
[way/700898274](https://www.openstreetmap.org/way/700898274) Twence,
[way/1237376864](https://www.openstreetmap.org/way/1237376864) AVR Rozenburg.
Together with Dordrecht that is 4 of the 11 Dutch waste-to-energy plants.

**Expected behavior:** when `missing_start_date_allowed: true`, emit way/node plants
with an empty start date (as already happens for relations); when the flag is false,
record a `MISSING_START_DATE` rejection instead of returning early, so the drop is
auditable in `*_rejected.csv`.

Happy to submit a PR for either or both changes.

---

## Issue 2 (separate, smaller): `plant:method=combustion` maps to Technology "Combustion Engine"

> **FILED 2026-07-03** as
> [open-energy-transition/osm-powerplants#16](https://github.com/open-energy-transition/osm-powerplants/issues/16),
> with fix PR [#17](https://github.com/open-energy-transition/osm-powerplants/pull/17)
> (branch `fix/combustion-method-per-source-technology` on fork MaykThewessen/osm-powerplants).
> Root cause found during filing: `combustion` sits in BOTH the Combustion Engine and
> Steam Turbine lists of `technology_mapping`; the loop in
> `parsing/base.py::extract_technology_from_tags` iterates `technology_mapping` in
> declaration order, so Combustion Engine always wins. Fix: iterate
> `source_technology_mapping[source_type]` in order (per-source preference ranking) and
> reorder `Waste` to `[Steam Turbine, Combustion Engine]`. Dataset impact: 241/279 Waste
> (5,980 MW) and 358/489 Solid Biomass (8,975 MW) plants mislabeled; 1 Steam Turbine each.
> Issue 1 (start_date gate) remains NOT filed.

**Title:** `plant:method=combustion` is translated to Technology "Combustion Engine", mislabeling steam-turbine plants

**Body:**

Plants tagged `plant:method=combustion` get `Technology = "Combustion Engine"` in
the output CSV. For waste incinerators and other boiler+steam-turbine plants this is
wrong: `combustion` in OSM describes the heat-generating method, not the prime
mover. Example: [way/47962126](https://www.openstreetmap.org/way/47962126)
AVR Duiven (grate incinerator, steam turbine) appears as
`Waste / Combustion Engine / 31.4 MW`.

Downstream consumers (e.g. powerplantmatching, PyPSA) interpret "Combustion Engine"
as reciprocating engines, with different efficiency/flexibility assumptions than
steam cycles.

**Suggestion:** map `plant:method=combustion` to "Steam Turbine" when
`plant:source` is waste/biomass/coal (or leave Technology empty and only use
`generator:type` when present, which does distinguish `steam_turbine`,
`gas_turbine`, `combustion_engine`, `combined_cycle`).

---

## Filing notes

- Cross-links: PyPSA/powerplantmatching#297 (OSM pin discussion) is related context
  for issue 1; mention it.
- After issue 1 is fixed upstream, the OSM `start_date` fills drafted in
  `osm-changeset-waste-avis.md` stop being a *requirement* for inclusion, but stay
  valuable as data (DateIn).
