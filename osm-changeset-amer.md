# OSM changeset draft — Amer power plant

**OSM object:** way/6318872 (Amercentrale, Geertruidenberg, NL) — verified live 2026-06-12 via Overpass.

**Current live tags (already correct, do NOT re-edit):**
- `plant:source=biomass` ✓ (community fixed since this draft was written)
- `plant:method=combustion` ✓
- `operator=RWE` ✓

**Remaining tag change to apply:**
- `plant:output:electricity` → `631 MW` (currently **1245 MW** — stale sum of Amer-8 + Amer-9; Amer-8 closed 2015 and was demolished. Only Amer-9 operates: 631 MWe.)
- Leave `plant:output:hot_water=600 MW` untouched (unverified; RWE cites ~350 MWth district heat but no authoritative public figure — do not change without source).

## Changeset comment

> Amercentrale: correct electric capacity 1245→631 MW. Amer-8 (645 MW) closed 2015; only Amer-9 (631 MW, biomass) operates. Source: ENTSO-E Transparency installed capacity per unit (EIC 49W000000000070Z) + RWE operator page.

## Source tags

- `source:plant:output:electricity` = `ENTSO-E Transparency Platform, production unit 49W000000000070Z (631 MW); https://www.rwe.com/en/the-group/countries-and-locations/amer-power-plant/`

## Notes for reviewer

Prior 1245 MW = historical two-unit site total. ENTSO-E registered unit capacity and RWE both state 631 MW for the single remaining unit (Amer-9). plant:source=biomass already correct in OSM.
