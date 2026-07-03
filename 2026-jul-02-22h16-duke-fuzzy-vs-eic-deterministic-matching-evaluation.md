# Duke fuzzy matching vs EIC deterministic ground truth: evaluation

**Date:** 2026-07-02 22h16
**Question:** How well does ppm's current Duke fuzzy matcher (static `Comparison.xml`, no learning) perform on the OPSD-ENTSOE pair, measured against the 371 unambiguous EIC-confirmed matches from PR [#289](https://github.com/PyPSA/powerplantmatching/pull/289)? Is learning (tuned weights/threshold) worth pursuing?

## Setup

- Worktree on `feature/eic-deterministic-matching` (`a3adb84`), plus master's pandas-3 `duke.py` geoposition fix (branch predates merged #294).
- Env: `.pixi/envs/default` (python 3.12, pandas 3.0.3), zulu OpenJDK 25 via `~/.pixi/bin`.
- Data loaded exactly as `collection.collect` does: `matching_sources` config queries applied, then `aggregate_units`. Frames: **OPSD 3325 / ENTSOE 1521 rows**, matching the PR #289 assessment baseline exactly (477 cross-source EIC edges, 410 connected components: 371 clean 1-to-1, 39 ambiguous).
- **Ground truth:** the 371 degree-1-both-ends EIC pairs from `_match_by_eic`.
- **Fuzzy under test:** pure Duke record linkage on the *full* frames (pre-#289 production behavior): country-wise, `singlematch=True`, then best-match reduction per ENTSOE entry. 18 countries ran (the rest lack rows in one frame); 571 raw links, **531 final pairs**, of which 376 have EIC codes on both sides (evaluable against ground truth).

## Results

| Metric | Value |
|---|---|
| Recall on 371 EIC ground-truth pairs | **85.2%** (316 recovered) |
| Missed pairs | 55 (48 fully unmatched, 7 matched to the wrong plant), **34.6 GW** |
| Precision on labeled subset (both rows carry EIC) | **89.1%** (335 of 376 EIC-consistent) |
| EIC-inconsistent Duke pairs | 41 = 5 actively contradicted (~4.2 GW) + 36 weak (disjoint codes, includes label noise) |
| Duke pairs resolving ambiguous EIC clusters consistently | 19 |

### Where fuzzy matching fails

**Misses are dominated by the UK (30 of 55)** because ENTSOE UK plant names are 4-6 letter codes that defeat string similarity: West Burton = "Wbups", Connahs Quay = "Cnqps", Peterhead = "Pehe", Heysham 2 = "Heym2". Other big misses: Oskarshamn, PSW Vianden, Amercentrale.

**Actively contradicted matches** (a row's EIC provably links it elsewhere), all high-scoring:

| Duke matched | EIC says | Score |
|---|---|---|
| Fiddler Ferry (1961 MW) ↔ "Ferr" | Fiddler Ferry = "Fidl" | 0.994 |
| South Humber Bank (1365 MW) ↔ "Humr" | "Humr" = VPI Immingham (co-located on the Humber) | 0.986 |
| Gud (695 MW) ↔ Gud Ludwigshafen Mitte | different GuD units | 0.998 |
| Linz Sa Fernheizkraftwerk ↔ Voestalpine Linz | co-located Linz plants | 0.970 |
| Fiddler Ferry Gt (35 MW) ↔ "Ferr" | | 0.993 |

These are exactly the co-located/similar-name failure mode PR #289 targets (the Eemshaven example generalizes: Immingham/South Humber Bank is the UK equivalent).

Of the 36 weak inconsistencies, several are almost certainly *true* matches with inconsistently registered EICs (e.g. Bexbach: identical name, identical 726 MW on both sides; sources registered different code levels). So 89.1% is a lower bound on labeled precision; the hard floor of confirmed errors is the 5 active contradictions plus the 7 mismatches among ground-truth rows.

### Duke scores carry no confidence signal

| Group | n | median score | min | max |
|---|---|---|---|---|
| EIC-consistent pairs | 335 | 0.9987 | 0.9656 | 0.9987 |
| EIC-contradicted pairs | 41 | 0.9971 | 0.9703 | 0.9987 |

The distributions overlap almost completely and saturate at ~0.9987 (the Bayes-composition ceiling of the current comparator weights). **No score threshold can separate correct from incorrect matches.** A wrong match (Gud, 0.998) outscores hundreds of correct ones.

## Implications

1. **Strong quantitative case for #289.** Deterministic EIC matching recovers all 371 pairs with certainty where fuzzy matching gets 85.2%, rescues 34.6 GW of missed links (UK code-names above all), and removes multi-GW wrong matches (Fiddler's Ferry, South Humber Bank) that no threshold tuning can catch.
2. **Learning the threshold is pointless.** Scores are saturated and uninformative at the top; there is nothing for a learned cutoff to exploit.
3. **Learning comparator weights (Duke's genetic trainer) has limited headroom.** The dominant failure modes are (a) identifier-style names with no string overlap and (b) co-located plants with near-identical attributes: both are information problems, not weight problems. The 371 EIC pairs now provide labeled training/eval data for free, so a weight-tuning experiment is *possible*, but the expected gain is concentrated in the ~55 misses outside the identifier problem, i.e. small. Deterministic identifier matchers (EIC now; name+country canonicalization or other registries later, via the `DirectMatcher` list) are the higher-leverage path.
4. **Housekeeping:** branch `feature/eic-deterministic-matching` crashes under pandas 3 (`best_matches` groupby-apply, `duke.py` geoposition join) because it predates #294, which is now **merged** and already fixes both on master. Rebase #289 onto master before further work.

## Reproduction

Artifacts (summary.json, duke_matches.parquet, gt_pairs.parquet, missed_gt.csv, contradictions.csv) were produced by the script below, run from a worktree of the PR branch:

```bash
git worktree add /tmp/eic-eval-wt fork/feature/eic-deterministic-matching --detach
cd /tmp/eic-eval-wt && git checkout master -- powerplantmatching/duke.py  # pandas-3 fix
PATH="$HOME/.pixi/bin:$PATH" PYTHONPATH="$PWD" \
  /Users/mayk/powerplantmatching/.pixi/envs/default/bin/python eval_duke_vs_eic.py
```

<details>
<summary>eval_duke_vs_eic.py (full script)</summary>

```python
"""Evaluate ppm's Duke fuzzy matcher against EIC-deterministic ground truth.

Ground truth: the 371 unambiguous 1-to-1 EIC pairs between OPSD and ENTSOE
(degree-1 both ends), as produced by _match_by_eic on branch
feature/eic-deterministic-matching (PR #289).

Fuzzy under test: pure Duke record linkage on the FULL aggregated frames
(country-wise, singlematch=True, then best_matches) - i.e. the pre-#289
production behavior of compare_two_datasets.
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

OUT_DIR = Path(__file__).parent / "eval-results"
OUT_DIR.mkdir(exist_ok=True)

import powerplantmatching as pm
from powerplantmatching.cleaning import aggregate_units
from powerplantmatching.data import ENTSOE, OPSD
from powerplantmatching.duke import duke
from powerplantmatching.matching import _match_by_eic

config = pm.get_config()
L0, L1 = "OPSD", "ENTSOE"


def log(msg: str) -> None:
    print(f"[eval] {msg}", flush=True)


# 1. Load + aggregate (mirrors collection.collect.df_by_name)
def load(name: str, get_df) -> pd.DataFrame:
    log(f"loading {name} ...")
    df = get_df(config=config)
    for source in config["matching_sources"]:
        if isinstance(source, dict) and next(iter(source)) == name:
            df = df.query(source[name])
    return aggregate_units(df, dataset_name=name, config=config)


opsd = load(L0, OPSD)
entsoe = load(L1, ENTSOE)
log(f"frames post-aggregate_units: OPSD={len(opsd)} ENTSOE={len(entsoe)}")

# 2. EIC ground truth
gt = _match_by_eic(opsd, entsoe, L0, L1)
log(f"EIC 1-to-1 ground-truth pairs: {len(gt)}")

e0 = opsd["EIC"].explode().dropna().rename("code").rename_axis("i0").reset_index()
e1 = entsoe["EIC"].explode().dropna().rename("code").rename_axis("i1").reset_index()
edges = e0.merge(e1, on="code")[["i0", "i1"]].drop_duplicates()
log(f"cross-source EIC edges: {len(edges)}")

n0map = {v: k for k, v in enumerate(edges.i0.unique())}
n1map = {v: k + len(n0map) for k, v in enumerate(edges.i1.unique())}
row = edges.i0.map(n0map).to_numpy()
col = edges.i1.map(n1map).to_numpy()
n = len(n0map) + len(n1map)
adj = coo_matrix((np.ones(len(edges)), (row, col)), shape=(n, n))
ncomp, labels_arr = connected_components(adj, directed=False)
comp0 = pd.Series({i: labels_arr[p] for i, p in n0map.items()}, name="comp")
comp1 = pd.Series({i: labels_arr[p] for i, p in n1map.items()}, name="comp")
comp_sizes = pd.Series(labels_arr).value_counts()
clean_comps = set(comp_sizes[comp_sizes == 2].index)
log(f"components: {ncomp} total, {len(clean_comps)} clean size-2, "
    f"{ncomp - len(clean_comps)} ambiguous")

has_eic0 = opsd.index.isin(e0.i0)
has_eic1 = entsoe.index.isin(e1.i1)

# 3. Pure Duke fuzzy linkage (pre-#289 behavior)
dfs = [opsd, entsoe]
links_all = []
t0 = time.time()
countries = config["target_countries"]
for k, c in enumerate(countries, 1):
    sel = [df["Country"] == c for df in dfs]
    if not all(s.any() for s in sel):
        continue
    lk = duke([df[s] for df, s in zip(dfs, sel)], labels=[L0, L1],
              singlematch=True)
    log(f"  duke {c} ({k}/{len(countries)}): {len(lk)} links")
    if not lk.empty:
        links_all.append(lk)
links = pd.concat(links_all, ignore_index=True)
log(f"duke done in {time.time() - t0:.0f}s, raw links: {len(links)}")

# equivalent of matching.best_matches (highest score per second-dataset
# entry); the branch's groupby(...).apply form crashes on pandas 3 - fixed
# on master by #294's idxmax rewrite, semantics identical.
links["scores"] = links["scores"].astype(float)
duke_matches = (
    links.sort_values("scores", ascending=False, kind="stable")
    .drop_duplicates(subset=[L1])[[L0, L1]]
    .reset_index(drop=True)
)
duke_matches[[L0, L1]] = duke_matches[[L0, L1]].astype(opsd.index.dtype)
log(f"duke matches after best_matches: {len(duke_matches)}")

links[[L0, L1]] = links[[L0, L1]].astype(opsd.index.dtype)
duke_matches = duke_matches.merge(
    links.groupby([L0, L1], as_index=False)["scores"].max(), on=[L0, L1],
    how="left",
)

# 4. Metrics
gt_keys = set(zip(gt[L0], gt[L1]))
dk_keys = set(zip(duke_matches[L0], duke_matches[L1]))
recovered = gt_keys & dk_keys
missed = gt_keys - recovered
recall = len(recovered) / len(gt_keys)

dk_by0 = duke_matches.set_index(L0)[L1]
dk_by1 = duke_matches.set_index(L1)[L0]
missed_df = pd.DataFrame(sorted(missed), columns=["i0", "i1"])
alt1 = missed_df.i0.map(dk_by0)
alt0 = missed_df.i1.map(dk_by1)
missed_df = missed_df.assign(
    kind=np.where(alt1.notna() | alt0.notna(), "mismatched", "unmatched"),
    opsd_name=opsd["Name"].reindex(missed_df.i0).to_numpy(),
    entsoe_name=entsoe["Name"].reindex(missed_df.i1).to_numpy(),
    opsd_cap=opsd["Capacity"].reindex(missed_df.i0).to_numpy(),
    entsoe_cap=entsoe["Capacity"].reindex(missed_df.i1).to_numpy(),
    country=opsd["Country"].reindex(missed_df.i0).to_numpy(),
    duke_alt_entsoe_name=alt1.map(entsoe["Name"]).fillna("").to_numpy(),
    duke_alt_opsd_name=alt0.map(opsd["Name"]).fillna("").to_numpy(),
).sort_values("opsd_cap", ascending=False)

dm = duke_matches.copy()
dm["both_eic"] = dm[L0].isin(opsd.index[has_eic0]) & dm[L1].isin(entsoe.index[has_eic1])
edge_keys = set(zip(edges.i0, edges.i1))
dm["eic_agree"] = [(a, b) in edge_keys for a, b in zip(dm[L0], dm[L1])]
evaluable = dm[dm.both_eic]
agree = evaluable[evaluable.eic_agree]
contradict = evaluable[~evaluable.eic_agree]
precision_labeled = len(agree) / len(evaluable) if len(evaluable) else float("nan")

contra_df = pd.DataFrame({
    "i0": contradict[L0].to_numpy(), "i1": contradict[L1].to_numpy(),
    "score": contradict["scores"].to_numpy(),
    "opsd_name": opsd["Name"].reindex(contradict[L0]).to_numpy(),
    "entsoe_name": entsoe["Name"].reindex(contradict[L1]).to_numpy(),
    "opsd_cap": opsd["Capacity"].reindex(contradict[L0]).to_numpy(),
    "entsoe_cap": entsoe["Capacity"].reindex(contradict[L1]).to_numpy(),
    "opsd_fuel": opsd["Fueltype"].reindex(contradict[L0]).to_numpy(),
    "entsoe_fuel": entsoe["Fueltype"].reindex(contradict[L1]).to_numpy(),
    "country": opsd["Country"].reindex(contradict[L0]).to_numpy(),
    "opsd_comp": contradict[L0].map(comp0).fillna(-1).to_numpy(),
    "entsoe_comp": contradict[L1].map(comp1).fillna(-1).to_numpy(),
}).sort_values("opsd_cap", ascending=False)

amb_pairs = dm[dm.eic_agree & ~dm[L0].map(comp0).isin(clean_comps)]

score_stats = {
    grp: dm.loc[m, "scores"].describe().round(4).to_dict()
    for grp, m in {
        "eic_agree": dm.both_eic & dm.eic_agree,
        "eic_contradict": dm.both_eic & ~dm.eic_agree,
        "unlabeled": ~dm.both_eic,
    }.items()
}

summary = {
    "frames": {"OPSD": len(opsd), "ENTSOE": len(entsoe)},
    "eic_edges": len(edges),
    "eic_components": {"total": int(ncomp), "clean_1to1": len(clean_comps),
                        "ambiguous": int(ncomp - len(clean_comps))},
    "gt_pairs": len(gt_keys),
    "duke_pairs_total": len(dk_keys),
    "duke_pairs_both_eic": int(dm.both_eic.sum()),
    "recall_on_gt": round(recall, 4),
    "gt_recovered": len(recovered),
    "gt_missed": len(missed),
    "gt_missed_mismatched": int((missed_df.kind == "mismatched").sum()),
    "gt_missed_unmatched": int((missed_df.kind == "unmatched").sum()),
    "precision_on_labeled": round(precision_labeled, 4),
    "labeled_agree": len(agree),
    "labeled_contradict": len(contradict),
    "duke_pairs_in_ambiguous_clusters_eic_consistent": len(amb_pairs),
    "score_stats": score_stats,
}

duke_matches.to_parquet(OUT_DIR / "duke_matches.parquet")
gt.to_parquet(OUT_DIR / "gt_pairs.parquet")
missed_df.to_csv(OUT_DIR / "missed_gt.csv", index=False)
contra_df.to_csv(OUT_DIR / "contradictions.csv", index=False)
(OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

log("SUMMARY:\n" + json.dumps(summary, indent=2, default=str))
```

</details>

## Appendix: all 55 missed ground-truth pairs (top 20 by capacity)

| OPSD | ENTSOE | MW | Country | Kind |
|---|---|---|---|---|
| Oskarshamn G1 | Oskarshamn 3 | 2511 | Sweden | unmatched |
| West Burton | Wbups | 2000 | UK | unmatched |
| Fiddler Ferry | Fidl | 1961 | UK | mismatched (→ "Ferr") |
| Connahs Quay | Cnqps | 1380 | UK | unmatched |
| South Humber Bank | Shba | 1365 | UK | mismatched (→ "Humr") |
| West Burton Ccgt | Wburb | 1332 | UK | unmatched |
| Psw Vianden | Vianden | 1291 | Luxembourg | unmatched |
| Amercentrale | Amer | 1285 | Netherlands | unmatched |
| Heysham 2 | Heym2 | 1254 | UK | unmatched |
| Vpi Immingham | Humr | 1252 | UK | mismatched |
| Peterhead | Pehe | 1180 | UK | unmatched |

(Full lists in the eval artifacts: `missed_gt.csv`, `contradictions.csv`.)
