#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os

from pyess.cli import main


def using_network():
    return "USE_NETWORK" in os.environ and os.environ["USE_NETWORK"] == "true"


@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
def test_log_against_graphite(password):
    main(["--action", "log_against_graphite", "--graphite", "127.0.0.1", "--password", password, "--once", "true"])

#@pytest.mark.skipif(not using_network(), reason="only when using network")
@pytest.mark.vcr(mode="all")
def test_get_data(password):
    main(["--action", "get_data",  "--password", password])
