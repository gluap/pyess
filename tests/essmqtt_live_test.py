#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os
import asyncio

from pyess.essmqtt import _main


def using_network():
    return "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true"


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.asyncio()
async def test_online_log_against_mqtt(password, hbmqtt):
    await asyncio.sleep(1)

    await _main(["--mqtt_server", "localhost",
          "--mqtt_user", "test",
          "--mqtt_port", str(hbmqtt),
          "--mqtt_password", "test",
          "--ess_password", password,
          "--once", "true"])


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.asyncio()
async def test_online_log_against_mqtt_with_autopublish(password, hbmqtt):
    await asyncio.sleep(1)

    await _main(["--mqtt_server", "localhost",
          "--mqtt_user", "test",
          "--mqtt_port", str(hbmqtt),
          "--mqtt_password", "test",
          "--ess_password", password,
          "--once", "true",
          "--hass_autoconfig_sensors", "/bla/blech/blu/bloch" ])


