# SPDX-FileCopyrightText: Contributors to powerplantmatching <https://github.com/pypsa/powerplantmatching>
#
# SPDX-License-Identifier: MIT

import pandas as pd
import pytest

import powerplantmatching as pm
from powerplantmatching import data
from powerplantmatching.utils import get_name

config = pm.get_config()
sources = [s if isinstance(s, str) else list(s)[0] for s in config["matching_sources"]]

if not config["entsoe_token"] and "ENTSOE" in sources:
    sources.remove("ENTSOE")


@pytest.mark.parametrize("source", sources)
def test_data_request_raw(source):
    func = getattr(data, source)
    df = func(update=True, raw=True)
    if source == "OPSD":
        assert len(df["DE"])
        assert len(df["EU"])
    elif source == "GEO":
        assert len(df["Units"])
        assert len(df["Plants"])
    else:
        assert len(df)


@pytest.mark.parametrize("source", sources)
def test_data_request_processed(source):
    func = getattr(data, source)
    df = func()
    assert len(df)
    assert df.columns.to_list() == config["target_columns"]


def test_OPSD_VRE():
    df = pm.data.OPSD_VRE()
    assert not df.empty
    assert df.Capacity.sum() > 0


def test_OPSD_VRE_country():
    df = pm.data.OPSD_VRE_country("DE")
    assert not df.empty
    assert df.Capacity.sum() > 0


def test_IRENASTAT():
    df = pm.data.IRENASTAT()
    assert not df.empty
    assert df.Capacity.sum() > 0


@pytest.mark.github_actions
def test_url_retrieval():
    pm.powerplants(from_url=True)


def test_reduced_retrieval():
    config = pm.get_config()
    config["matching_sources"] = ["GEO", "GPD"]
    config["fully_included_sources"] = []
    pm.powerplants(reduced=False, config=config)


def test_gem_keeps_source_name(monkeypatch):
    for tracker in ("GBPT", "GGPT", "GCPT", "GGTPT", "GNPT", "GSPT", "GWPT", "GHPT"):
        frame = pd.DataFrame({"Capacity": [1.0]})
        frame.columns.name = tracker
        monkeypatch.setattr(data, tracker, lambda frame=frame, **kwargs: frame)
    assert get_name(data.GEM()) == "GEM"
