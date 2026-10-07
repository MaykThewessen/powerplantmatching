# Powerplantmatching contribution tasks

Assessed against upstream issues and open pull requests on 2026-10-04.

## Implementation queue

- [x] [#237: GEM matching error](https://github.com/PyPSA/powerplantmatching/issues/237). Local fix and validation complete. Assign the processed combined GEM source name in the loader. Upstream PR preparation remains open below.
- [ ] [#257: UK Renewable Energy Planning Database](https://github.com/PyPSA/powerplantmatching/issues/257). Inspect the current official extract and licence, map technologies, capacities, locations and status, and measure overlap with existing sources before choosing inclusion defaults.
- [ ] [#303: Attribute-level data quality](https://github.com/PyPSA/powerplantmatching/issues/303). Propose a companion provenance and reliability table. Resolve treatment of aggregated dates and identifiers before implementation. Reliability scores express source preference, not measured accuracy.
- [ ] [#270: DUKES UK generators](https://github.com/PyPSA/powerplantmatching/issues/270). Inspect the latest table and location completeness, design location conversion, and quantify additional coverage. Keep missing locations explicit.
- [ ] [#289: EIC linkage through JRC IDs](https://github.com/PyPSA/powerplantmatching/pull/289). Use `JRC_OPEN_LINKAGES.csv` (EIC to GPD and GEO IDs) for deterministic pre-matching, as fneum suggested on #306. No JRC capacities or coordinates. Measure gained and lost ENTSO-E capacity against master before updating the PR. In progress in a separate session.
- [ ] [#273: Duplicate generation assets](https://github.com/PyPSA/powerplantmatching/issues/273). Reproduce the Colombia example on current upstream, trace failed matching and fully included sources, then choose a fix based on evidence.

## Existing work and overlaps

- [#287](https://github.com/PyPSA/powerplantmatching/issues/287) already has our [PR #289](https://github.com/PyPSA/powerplantmatching/pull/289).
- The classification portion of [#286](https://github.com/PyPSA/powerplantmatching/issues/286) already has our [PR #288](https://github.com/PyPSA/powerplantmatching/pull/288). Efficiency enrichment remains a separate problem.
- [#306: JRC-PPDB-OPEN](https://github.com/PyPSA/powerplantmatching/pull/306) will not be merged (fneum, 2026-10-07). Its EIC aggregation fix is already on master as [#312](https://github.com/PyPSA/powerplantmatching/pull/312). As a matching source JRC double counts about 57 GW; as an ENTSO-E coordinate source it loses about 9 GW of correct matches. Our JRC coordinate enrichment is opt-in since `a22d636`.
- Matching-engine replacement is already in [PR #301](https://github.com/PyPSA/powerplantmatching/pull/301). Coordinate matching and performance work with that change.
- [#249: UK hydro classification](https://github.com/PyPSA/powerplantmatching/issues/249) is related to #257. Audit affected records during UK source integration; do not infer storage technology from component type alone.

## First contribution acceptance criteria

- [x] Regression fails on the unchanged loader because its source name is missing.
- [x] Processed GEM data has a stable source name and preserves all tracker records.
- [x] Raw GEM output remains an unmodified concatenation of raw tracker data.
- [x] Focused tests and relevant matching checks pass.
- [ ] Changes are isolated and ready for upstream review.

## Validation of #237

- Before the fix: processed-data regression failed with source name `None`; raw-data case passed.
- After the fix: 12 focused data, matching and cleaning tests passed; 25 download-related tests were deselected. Full live-source rebuild was not run.
- Real Java smoke check exercised `GEM()`, `aggregate_units()` and `combine_multiple_datasets()` with eight synthetic plants. All eight matched; both source labels survived.
- Ruff lint, test formatting and whitespace checks passed.
- Existing pytest warning: unregistered `github_actions` marker in `test/test_data.py`.
- Existing local checkout is `master`, 25 commits ahead of its recorded `origin/master`. Extract only this loader fix and regression into a clean upstream branch before PR submission. No commit or push performed.
