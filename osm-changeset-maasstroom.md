# OSM changeset draft — Maasstroom (Rijnmond 2)

**OSM object:** way/164715508 (Maasstroom Energie, Rotterdam Pernis) — verified live 2026-06-12 via Overpass.

**Current live tags:** `plant:output:electricity=420 MW`, `plant:source=gas`,
`plant:method=combustion`, plus a stray `generator:method=thermal`.

**Tag changes to apply:**
- `plant:output:electricity` → `426 MW` (was 420 in OSM; 426 = ENTSO-E registered
  unit capacity, EIC 49W0000000001225)
- Remove stray `generator:method=thermal` — `generator:*` keys belong on
  `power=generator` objects, not on the `power=plant` site (plant:method=combustion
  already present and correct)

## Decision (resolved)

Option (b) from the original draft: bundle with the Amer capacity fix in one
NL-thermal-capacities changeset, all values sourced from ENTSO-E TP. A 6 MW solo
edit invites a "noise" revert; a sourced multi-plant changeset does not.

## Changeset comment

> Maasstroom Energie: electric capacity 420→426 MW per ENTSO-E Transparency registered unit capacity (EIC 49W0000000001225); drop stray generator:method tag from plant object.

## Source tag

- `source:plant:output:electricity` = `ENTSO-E Transparency Platform, production unit 49W0000000001225`
