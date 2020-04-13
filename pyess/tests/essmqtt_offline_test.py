#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os
import subprocess

from pyess.essmqtt import main


def using_network():
    return "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true"


@pytest.mark.skipif(using_network(), reason="only when not using network")
@pytest.mark.vcr(mode="all")
def test_online_log_against_mqtt(password):
    hbmqtt = subprocess.Popen(["hbmqtt","-c","data/hbmqtt.conf"])


    main(["--mqtt_server", "localhost",
          "--mqtt_user", "test",
          "--mqtt_password", "test",
          "--ess_password", password,
          "--once", "true"])

    hbmqtt.kill()

