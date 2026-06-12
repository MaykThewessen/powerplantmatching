# OSM changeset draft — Hemweg — RESOLVED, no lifecycle edit needed

**Verified live 2026-06-12 via Overpass:** way/292125850 (Centrale Hemweg, Amsterdam).

The coal-unit retirement this draft planned is **already done in OSM**: no coal
object remains in the Westpoort bbox. The surviving plant object is:

- `power=plant`, `plant:source=gas`, `plant:method=combustion`
- `plant:output:electricity=435 MW`, `operator=Vattenfall`, `start_date=1953`

The original decision point (disused vs demolished prefix for Hemweg 8) is moot —
the community removed/retagged the coal unit after the 2024 demolition.

## Optional remaining micro-fix

- `plant:output:electricity` 435 → `440 MW` (Hemweg 9 CCGT registered capacity,
  ENTSO-E EIC 49W000000000045Y). 5 MW delta — borderline noise; only worth it
  bundled into a changeset with the Amer fix.
- `start_date=1953` refers to the site, not the current CCGT (2012). Could move to
  `start_date=2012` on the plant with site history in `note`, but this is
  opinionated — skip unless a reviewer asks.

## Changeset comment (if bundling the 440 MW fix)

> Centrale Hemweg: electric capacity 435→440 MW per ENTSO-E Transparency registered unit capacity (EIC 49W000000000045Y).

## Source tag

- `source:plant:output:electricity` = `ENTSO-E Transparency Platform, production unit 49W000000000045Y`
