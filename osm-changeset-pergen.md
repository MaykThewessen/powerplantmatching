# OSM changeset draft — PerGen (NEW, from osm-powerplants rejection list)

**OSM object:** way/920978717 (PerGen, Air Liquide Pernis, Rotterdam) — found via
osm-powerplants global rejection list 2026-06-12, reason: **"Missing source tag"**.

**Current live tags:** `power=plant`, `name=PerGen`, `operator=Air Liquide`,
`plant:output:electricity=300 MW`, `plant:output:steam=yes` — no `plant:source`,
no `plant:method`, so osm-powerplants rejects it entirely (invisible to PPM's OSM source).

**Tag changes to apply:**
- Add `plant:source=gas` (natural-gas-fired industrial CHP supplying process steam
  to the Pernis refinery/chemical cluster)
- Add `plant:method=combustion`

This single edit moves PerGen from the rejection list into `osm_global.csv.gz`
(monthly CI), i.e. into every downstream powerplantmatching build.

Capacity note: leave 300 MW as-is. ENTSO-E registers 308 MW; our model carries
270 MW. Within nameplate-vs-registered spread — don't churn it without an
operator source.

## Changeset comment

> PerGen (Air Liquide Pernis): add plant:source=gas + plant:method=combustion. Gas-fired industrial CHP; tags were missing, blocking data consumers. Source: ENTSO-E Transparency unit registration + Air Liquide operator info.

## Source tag

- `source:plant:source` = `ENTSO-E Transparency Platform (gas-fired production unit, Pergen); Air Liquide Pernis cogeneration`
