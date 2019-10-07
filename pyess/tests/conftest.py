#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
import pytest


@pytest.fixture()
def password():
    if "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true":
        return json.load(open(os.path.dirname(__file__) + "/credentials.json"))["password"]
    else:
        return "ba5511008000"