#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import logging
import re
import socket
import time

import requests

from zeroconf import Zeroconf

from pyess.constants import PREFIX, LOGIN_URL, TIMESYNC_URL, GRAPH_TIMESPANS, GRAPH_DEVICES, GRAPH_PARAMS, \
    GRAPH_TFORMATS

logger = logging.getLogger(__name__)


def get_ess_pw(ip="192.168.23.1"):
    """this method only works on the wifi provided by the box."""
    res = requests.post(f"https://{ip}/v1/user/setting/read/password", json={"key": "lgepmsuser!@#"},
                        headers={"Charset": "UTF-8", "Content-Type": "application/json"}, verify=False,
                        timeout=1).json()
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


def login(ip, password):
    url = LOGIN_URL.format(ip)
    r = requests.put(url, json={"password": password}, verify=False, headers={"Content-Type": "application/json"})
    auth_key = r.json()["auth_key"]
    timesync_info = {
        "auth_key": auth_key,
        "by": "phone",
        "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    rt = requests.put(TIMESYNC_URL.format(ip), json=timesync_info, verify=False,
                      headers={"Content-Type": "application/json"})
    assert rt.json()['status'] == 'success', rt.__dict__
    return auth_key


def get_graph(device, timespan, date):
    assert device in GRAPH_DEVICES
    assert timespan in GRAPH_TIMESPANS
    jsondata = {"auth_key": auth_key, GRAPH_PARAMS[timespan]: date.strftime(GRAPH_TFORMATS[GRAPH_PARAMS[timespan]])}
    print(jsondata)
    url = f"{PREFIX}v1/user/graph/{device}/{timespan}"
    print(url)
    r = requests.post(url, json=jsondata, verify=False, headers={"Content-Type": "application/json"})
    return r.json()


def get_json_with_auth(url, auth_key):
    r = requests.post(url, json={"auth_key": auth_key}, verify=False, headers={"Content-Type": "application/json"})
    return r.json()


def switch_on(auth_key):
    r = requests.put(f"{PREFIX}/v1/user/operation/status", json={"auth_key": auth_key, "operation": "start"},
                     verify=False, headers={"Content-Type": "application/json"})


def switch_off(auth_key):
    return requests.put(f"{PREFIX}/v1/user/operation/status", json={"auth_key": auth_key, "operation": "stop"},
                        verify=False, headers={"Content-Type": "application/json"})


# results = {}
# for (name, url) in simple_urls.items():
#    results[name] = get_json_with_auth(url, auth_key)
# print(results)


def find_all_esses():
    from zeroconf import ServiceBrowser, Zeroconf
    esses = []

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
