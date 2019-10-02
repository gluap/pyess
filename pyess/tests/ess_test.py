#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import json
import re
import os

from uuid import UUID


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_to_test


from pyess.ess import find_ess, find_all_esses, get_ess_pw, autodetect_ess, login

password = json.load(open(os.path.dirname(__file__) + "/credentials.json"))["password"]


@pytest.fixture()
def password():
    return json.load(open(os.path.dirname(__file__) + "/credentials.json"))["password"]


@pytest.fixture()
def test_ess(cache=[]):
    if not cache:
        ip, name = autodetect_ess()
        cache.append(ip)
        cache.append(name)
    return cache


def test_find_ess():
    name = find_all_esses()[0]
    name = re.sub(r"LGE_ESS-(.+)\._pmsctrl\._tcp\.local\.", "\g<1>", name)
    find_ess(name)


def test_get_password(test_ess):
    # assuming we are not on ess' wifi
    with pytest.raises(Exception):
        pw = get_ess_pw(test_ess[0])


def test_login(password, test_ess):
    auth_key = login(test_ess[0], password)
