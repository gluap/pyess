#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import pytest
import json
import os

from pyess.constants import GRAPH_DEVICES, GRAPH_TIMESPANS, STATE_URLS

from pyess.ess import get_ess_pw, autodetect_ess, ESS


def using_network():
    return "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true"





@pytest.fixture()
def test_online_ess(cache=[]):
    if not cache:
        ip, name = autodetect_ess()
        cache.append(ip)
        cache.append(name)
    return cache


@pytest.fixture()
def ess(test_online_ess, password):
    return ESS(test_online_ess[1], password)


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
def test_online_init(password, test_online_ess):
    ess = ESS(test_online_ess[1], password)


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
def test_online_get_password(test_online_ess):
    # assuming we are not on ess' wifi
    with pytest.raises(Exception):
        pw = get_ess_pw(test_online_ess[0])


# def test_online_get_state/
@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.parametrize('dev,timespan', [(d, t) for d in GRAPH_DEVICES for t in GRAPH_TIMESPANS])
def test_online_get_graph(ess, dev, timespan):
    res = ess.get_graph(dev, timespan, datetime.datetime.now())
    example = json.load(open(os.path.dirname(__file__) + "/examples/" + dev + "_" + timespan + ".json", "r"))
    for key in example.keys():
        assert key in res
    for key in [k for k in example.keys() if isinstance(example[k], dict) and not key == "loginfo"]:
        for k in example[key].keys():
            assert k in res[key]


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.parametrize("state", [(k) for k in STATE_URLS.keys()])
def test_online_get_state(ess, state):
    res = ess.get_state(state)
    example = json.load(open(os.path.dirname(__file__) + "/examples/" + state + ".json", "r"))
    for key in example.keys():
        assert key in res
    for key in [k for k in example.keys() if isinstance(example[k], dict)]:
        for k in example[key].keys():
            assert k in res[key]


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
def test_online_auto_reconnect(ess):
    ess.auth_key = "asdf"
    res = ess.get_state("common")
    assert res != {'auth': 'auth_key failed'}
    pass
