#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import os

import pytest

from pyess.ess import autodetect_ess
from pyess.aio_ess import ESS
from pyess.constants import GRAPH_DEVICES, GRAPH_TIMESPANS, STATE_URLS


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
async def aioess(test_online_ess, password):
    return await ESS.create(test_online_ess[1], password, test_online_ess[0])


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.asyncio
@pytest.mark.vcr(mode=all)
async def test_aio_online_init(password, test_online_ess):
    ip, name = test_online_ess
    ess = await ESS.create(name, password, ip)


# def test_aio_online_get_state/
@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.asyncio
@pytest.mark.parametrize('dev,timespan', [(d, t) for d in GRAPH_DEVICES for t in GRAPH_TIMESPANS])
async def test_aio_online_get_graph(test_online_ess, password, dev, timespan):
    ip, name = test_online_ess
    ess = await ESS.create(name, password, ip)
    res = await ess.get_graph(dev, timespan, datetime.datetime.now())
    example = json.load(open(os.path.dirname(__file__) + "/examples/" + dev + "_" + timespan + ".json", "r"))
    for key in example.keys():
        assert key in res
    for key in [k for k in example.keys() if isinstance(example[k], dict) and not key == "loginfo"]:
        for k in example[key].keys():
            assert k in res[key]


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.parametrize("state", [(k) for k in STATE_URLS.keys()])
@pytest.mark.asyncio
async def test_aio_online_get_state(aioess, state):
    res = await aioess.get_state(state)
    example = json.load(open(os.path.dirname(__file__) + "/examples/" + state + ".json", "r"))
    for key in example.keys():
        assert key in res
    for key in [k for k in example.keys() if isinstance(example[k], dict)]:
        for k in example[key].keys():
            assert k in res[key]


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.asyncio
async def test_aio_online_auto_reconnect(aioess):
    aioess.auth_key = "asdf"
    res = await aioess.get_state("common")
    assert res != {'auth': 'auth_key failed'}
    pass

@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.asyncio
async def test_aio_online_fastcharge_on_off(aioess):
    res = await aioess.fastcharge_off()
    import time
    time.sleep(2)

    res2 = await aioess.get_batt_settings()

    assert res2["alg_setting"] == "off"
    res = await aioess.fastcharge_on()
    res2 = await aioess.get_batt_settings()
    assert res2["alg_setting"] == "on"

    assert res != {'auth': 'auth_key failed'}
    pass


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.asyncio
async def test_aio_online_winter_mode_on_off(aioess):
    res = await aioess.winter_off()
    import time
    time.sleep(2)
    res2 = await aioess.get_batt_settings()

    assert res2["winter_setting"] == "off"
    res = await aioess.winter_on()
    res2 = await aioess.get_batt_settings()
    assert res2["alg_setting"] == "on"

    assert res != {'auth': 'auth_key failed'}
    pass