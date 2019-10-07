#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
import pytest


@pytest.fixture()
def password():
    return json.load(open(os.path.dirname(__file__) + "/credentials.json"))["password"]