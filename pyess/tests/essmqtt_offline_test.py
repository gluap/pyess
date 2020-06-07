#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os
import subprocess
import time
import asyncio

from pyess.essmqtt import main, _main


def using_network():
    return "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true"


@pytest.mark.skipif(using_network(), reason="only when not using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.asyncio()
async def test_offline_log_against_mqtt(password, hbmqtt,mocker):
    mocker.patch('pyess.ess.autodetect_ess', return_value=["192.168.1.253", "THE_ESS_NAME"])
    mocker.patch('pyess.essmqtt.autodetect_ess', return_value=["192.168.1.253", "THE_ESS_NAME"])

    mocker.patch('pyess.ess.get_ess_ip', return_value="192.168.1.253")

    await asyncio.sleep(1)

    await _main(["--mqtt_server", "localhost",
          "--mqtt_user", "test",
          "--mqtt_port", str(hbmqtt),
          "--mqtt_password", "test",
          "--ess_password", password,
          "--once", "true"])


@pytest.mark.skipif(using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
@pytest.mark.asyncio()
async def test_offline_log_against_mqtt_with_autopublish(password, hbmqtt, mocker):
    mocker.patch('pyess.ess.autodetect_ess', return_value=["192.168.1.253", "THE_ESS_NAME"])
    mocker.patch('pyess.essmqtt.autodetect_ess', return_value=["192.168.1.253", "THE_ESS_NAME"])

    mocker.patch('pyess.ess.get_ess_ip', return_value="192.168.1.253")
    await asyncio.sleep(1)

    await _main(["--mqtt_server", "localhost",
          "--mqtt_user", "test",
          "--mqtt_port", str(hbmqtt),
          "--mqtt_password", "test",
          "--ess_password", password,
          "--once", "true",
          "--hass_autoconfig_sensors", "/bla/blech/blu/bloch" ])