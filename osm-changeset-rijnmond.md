# OSM changeset draft — Rijnmond 1 — HOLD, do not apply

**OSM object:** way/151767943 (Rijnmond Energie, Rotterdam) — verified live 2026-06-12 via Overpass.

**Current live tag:** `plant:output:electricity=820 MW` (wikidata Q2133125,
wikipedia nl:EP NL Rijnmond centrale, url intergen.com).

## Why HOLD

The planned edit (→ 750 MW) conflates two different capacity conventions:

- **820 MW** = nameplate / gross plant capacity (matches NL Wikipedia + operator history)
- **750 MW** = ENTSO-E registered market capacity (EIC 49W0000000001128) — market
  registrations are routinely de-rated below nameplate

OSM `plant:output:electricity` convention is nameplate. Overwriting nameplate with a
market registration is arguably a downgrade and a likely revert. PPM's matched value
(810) and our model both consume ENTSO-E directly anyway — the OSM value isn't the
binding input for the 750 figure.

## If editing anyway

Only with an operator/permit source that explicitly states net capacity < 820 MW.
ENTSO-E TP alone is insufficient justification for this object.

## Source candidates (collect before any edit)

- Operator page (EP NL / formerly InterGen) stating current net MW
- Dutch emissions permit (omgevingsvergunning) capacity figure
