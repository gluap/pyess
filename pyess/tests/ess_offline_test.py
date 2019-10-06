#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import pytest
import json
import os

from pyess.constants import GRAPH_DEVICES, GRAPH_TIMESPANS, STATE_URLS

from pyess.ess import get_ess_pw, ESS


@pytest.fixture()
def password():
    return "ba5511008000"


@pytest.fixture()
def test_ess(cache=[]):
    if not cache:
        ip, name = "192.168.1.253", "THE_ESS_NAME"
        cache.append(ip)
        cache.append(name)
    return cache


@pytest.fixture()
def ess(test_ess, password):
    def uip(self):
        return "192.168.1.253", "THE_ESS_NAME"

    ESS.update_ip = uip
    return ESS(test_ess[1], password)


@pytest.mark.vcr(match_on=['method', 'scheme', 'host', 'port', 'path', 'query'])
def test_offline_init(password, test_ess):
    def uip(self):
        return "192.168.1.253", "bla"

    ESS.update_ip = uip
    ess = ESS(test_ess[1], password)


@pytest.mark.vcr(match_on=['method', 'scheme', 'host', 'port', 'path', 'query', 'body'])
def test_offline_get_password(test_ess):
    # assuming we are not on ess' wifi
    with pytest.raises(Exception):
        pw = get_ess_pw(test_ess[0])


# def test_get_state/

@pytest.mark.vcr(match_on=['method', 'scheme', 'host', 'port', 'path', 'query'])
@pytest.mark.parametrize('dev,timespan', [(d, t) for d in GRAPH_DEVICES for t in GRAPH_TIMESPANS])
def test_offline_get_graph(ess, dev, timespan):
    res = ess.get_graph(dev, timespan, datetime.datetime.now())
    example = json.load(open(os.path.dirname(__file__) + "/examples/" + dev + "_" + timespan + ".json", "r"))
    for key in example.keys():
        assert key in res
    for key in [k for k in example.keys() if isinstance(example[k], dict) and not key == "loginfo"]:
        for k in example[key].keys():
            assert k in res[key]


@pytest.mark.vcr(match_on=['method', 'scheme', 'host', 'port', 'path', 'query'])
@pytest.mark.parametrize("state", [(k) for k in STATE_URLS.keys()])
def test_offline_get_state(ess, state):
    res = ess.get_state(state)
    example = json.load(open(os.path.dirname(__file__) + "/examples/" + state + ".json", "r"))
    for key in example.keys():
        assert key in res
    for key in [k for k in example.keys() if isinstance(example[k], dict)]:
        for k in example[key].keys():
            assert k in res[key]

@pytest.mark.vcr()
def test_offline_auto_reconnect(ess):
    ess.auth_key = "asdf"
    res = ess.get_state("common")
    assert res != {'auth': 'auth_key failed'}
    pass
