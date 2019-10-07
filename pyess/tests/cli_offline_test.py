#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os

import pyess.cli
import pyess.ess

def using_network():
    return "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true"


@pytest.mark.vcr(mode="all")
def test_log_against_graphite(password, mocker):
    mocker.patch('pyess.cli.autodetect_ess', return_value=["192.168.1.253", "THE_ESS_NAME"])
    mocker.patch('pyess.ess.get_ess_ip', return_value=["192.168.1.253", "THE_ESS_NAME"])


    pyess.cli.main(["--action", "log_against_graphite", "--graphite", "127.0.0.1", "--password", password, "--once", "true"])


@pytest.mark.vcr(mode="all")
def test_get_data(password,mocker):
    mocker.patch('pyess.cli.autodetect_ess', return_value=["192.168.1.253", "THE_ESS_NAME"])
    mocker.patch('pyess.ess.get_ess_ip', return_value=["192.168.1.253", "THE_ESS_NAME"])

    pyess.cli.main(["--action", "get_data",  "--password", password])