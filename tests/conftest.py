#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import random
import subprocess
import time

import pytest


@pytest.fixture()
def password():  # pragma: no cover
    if "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true":
        return json.load(open(os.path.dirname(__file__) + "/credentials.json"))["password"]
    else:
        return "ba5511008000"


@pytest.fixture()
def hbmqtt(tmpdir):
    port = random.randint(30000, 60000)
    conf = tmpdir.join(f"hbmqtt_{port}.conf")
    open(conf, "w").write(
        HBMQTT_CONF.format(port=port, passwd=os.path.join(os.path.dirname(__file__), "data/hbmqtt_passwd")))

    hbmqtt = subprocess.Popen(["amqtt", "-c", str(conf)])

    time.sleep(0.5)

    yield port

    hbmqtt.kill()


HBMQTT_CONF = """
listeners:
    default:
        type: tcp
        bind: 0.0.0.0:{port}
sys_interval: 20
auth:
    allow-anonymous: false
    password-file: {passwd}
plugins:
    - auth_file
topic-check:
    enabled: False
"""
