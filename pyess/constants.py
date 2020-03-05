#!/usr/bin/python
# -*- coding: utf-8 -*-
PREFIX = "https://{}/"
LOGIN_URL = f"{PREFIX}v1/user/setting/login"
TIMESYNC_URL = f"{PREFIX}v1/user/setting/timesync"
STATE_URLS = {
    "network": f"{PREFIX}v1/user/setting/network",
    "systeminfo": f"{PREFIX}v1/user/setting/systeminfo",
    "batt": f"{PREFIX}v1/user/setting/batt",
    "home": f"{PREFIX}v1/user/essinfo/home",
    "common": f"{PREFIX}v1/user/essinfo/common",
}
GRAPH_TIMESPANS = {"day", "week", "month", "year"}
GRAPH_DEVICES = {"batt", "load", "pv"}
GRAPH_PARAMS = {"day": "year_month_day",  # "20190929"
                "week": "year_month_day",  # "20190929"
                "month": "year_month",  # "201909"
                "year": "year"}
GRAPH_TFORMATS = {
    "year_month_day": "%Y%m%d",
    "year": "%Y",
    "year_month": "%Y%m"
}
GRAPH_DATA_URL = {
    f"{PREFIX}v1/user/graph/{dev}/{ts}" for ts in GRAPH_TIMESPANS for dev in GRAPH_DEVICES
}

RETRIES=3

SWITCH_URL = f"{PREFIX}/v1/user/operation/status"

BATT_URL = f"{PREFIX}/v1/user/setting/batt"
