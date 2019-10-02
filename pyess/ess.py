#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import logging
import re
import socket
import time

import requests

from zeroconf import Zeroconf

logger = logging.getLogger(__name__)


def get_ess_pw(ip="192.168.23.1"):
    """this method only works on the wifi provided by the box."""
    res = requests.post(f"https://{ip}/v1/user/setting/read/password", json={"key": "lgepmsuser!@#"},
                        headers={"Charset": "UTF-8", "Content-Type": "application/json"}, verify=False, timeout=1).json()
    if res['status'] == 'success':
        return res['password']
    logger.exception("could not fetch password")
    raise LookupError("could not look up password")

def autodetect_ess():
    name = find_all_esses()[0]
    name = re.sub(r"LGE_ESS-(.+)\._pmsctrl\._tcp\.local\.", "\g<1>", name)
    return find_ess(name)

def find_ess(name: str):
    zeroconf = Zeroconf()
    ess_info = zeroconf.get_service_info("_pmsctrl._tcp.local.", f"LGE_ESS-{name}._pmsctrl._tcp.local.")
    zeroconf.close()
    return [socket.inet_ntoa(ip) for ip in ess_info.addresses][0], ess_info.server

prefix = "https://{}/"
login_url = f"{prefix}v1/user/setting/login"
timesync_url = f"{prefix}v1/user/setting/timesync"


def login(ip, password):
    url=login_url.format(ip)
    r = requests.put(url, json={"password": password}, verify=False, headers={"Content-Type": "application/json"})
    auth_key = r.json()["auth_key"]
    timesync_info = {
        "auth_key": auth_key,
        "by": "phone",
        "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    rt = requests.put(timesync_url.format(ip), json=timesync_info, verify=False, headers={"Content-Type": "application/json"})
    assert rt.json()['status'] == 'success', rt.__dict__
    return auth_key


#auth_key = login()

simple_urls = {
    "network": f"{prefix}v1/user/setting/network",
    "systeminfo": f"{prefix}v1/user/setting/systeminfo",
    "batt": f"{prefix}v1/user/setting/batt",
    "home": f"{prefix}v1/user/essinfo/home",
    "common": f"{prefix}v1/user/essinfo/common",
}
graph_timespans = {"day", "week", "month", "year"}
graph_devices = {"batt", "load", "pv"}
graph_params = {"day": "year_month_day",  # "20190929"
                "week": "year_month_day",  # "20190929"
                "month": "year_month",  # "201909"
                "year": "year"}
graph_tformats = {
    "year_month_day": "%Y%m%d",
    "year": "%Y",
    "year_month": "%Y%m"
}
graph_data = {
    f"{prefix}v1/user/graph/{dev}/{ts}" for ts in graph_timespans for dev in graph_devices
}


def get_graph(device, timespan, date):
    assert device in graph_devices
    assert timespan in graph_timespans
    jsondata = {"auth_key": auth_key, graph_params[timespan]: date.strftime(graph_tformats[graph_params[timespan]])}
    print(jsondata)
    url = f"{prefix}v1/user/graph/{device}/{timespan}"
    print(url)
    r = requests.post(url, json=jsondata, verify=False, headers={"Content-Type": "application/json"})
    return r.json()


def get_json_with_auth(url, auth_key):
    r = requests.post(url, json={"auth_key": auth_key}, verify=False, headers={"Content-Type": "application/json"})
    return r.json()


def switch_on(auth_key):
    r = requests.put(f"{prefix}/v1/user/operation/status", json={"auth_key": auth_key, "operation": "start"},
                     verify=False, headers={"Content-Type": "application/json"})


def switch_off(auth_key):
    return requests.put(f"{prefix}/v1/user/operation/status", json={"auth_key": auth_key, "operation": "stop"},
                        verify=False, headers={"Content-Type": "application/json"})


#results = {}
#for (name, url) in simple_urls.items():
#    results[name] = get_json_with_auth(url, auth_key)
#print(results)


def find_all_esses():
    import zeroconf
    from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
    esses=[]
    class MyListener:

        def remove_service(self, zeroconf, type, name):
            pass
        def add_service(self, zeroconf, type, name):
            info = zeroconf.get_service_info(type, name)
            esses.append(info.name)

    zeroconf = Zeroconf()
    listener = MyListener()
    # browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    browser = ServiceBrowser(zeroconf, "_pmsctrl._tcp.local.", listener)
    time.sleep(3)
    zeroconf.close()
    return esses

def mitm_for_ess(name):
    import socket
    info = ServiceInfo(
        "_pmsctrl._tcp.local.",
        f"LGE_ESS-{name}._pmsctrl._tcp.local.",
        addresses=[socket.inet_aton("192.168.1.24")],
        port=80,
        properties={b'Device': b'LGEESS', b'HWRevison': b'1.5'},
        server="myaddress.local.",
    )

    zeroconf = Zeroconf()
    print("Registration of a service, press Ctrl-C to exit...")
    zeroconf.unregister_service(info)


