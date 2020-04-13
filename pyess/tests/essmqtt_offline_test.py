#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os
import subprocess
import time

from pyess.essmqtt import main


def using_network():
    return "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true"


@pytest.mark.skipif(using_network(), reason="only when not using network")
@pytest.mark.vcr(mode="all")
def test_offline_log_against_mqtt(password, hbmqtt):
    time.sleep(5)

    main(["--mqtt_server", "localhost",
          "--mqtt_user", "test",
          "--mqtt_port", str(hbmqtt),
          "--mqtt_password", "test",
          "--ess_password", password,
          "--once", "true"])

