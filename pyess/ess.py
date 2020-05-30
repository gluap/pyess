#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import logging
import re
import socket
import time
from json import JSONDecodeError

import requests
from zeroconf import Zeroconf, ServiceInfo

from pyess.constants import LOGIN_URL, TIMESYNC_URL, GRAPH_TIMESPANS, GRAPH_DEVICES, GRAPH_PARAMS, \
    GRAPH_TFORMATS, SWITCH_URL, STATE_URLS, BATT_URL


class ESSException(Exception):
    pass


logger = logging.getLogger(__name__)


class ESS:
    def __init__(self, name, pw, ip=None):
        self.name = name
        self.pw = pw
        self.ip = self.update_ip()
        self.auth_key = self._login()

    def _login(self, retry=1):
        """
        Login to the ESS device. Called by __init__
        :return:
        """
        url = LOGIN_URL.format(self.ip)
        logger.info("fetching auth key")
        r = requests.put(url, json={"password": self.pw}, verify=False, headers={"Content-Type": "application/json"})
        auth_key = r.json()["auth_key"]
        timesync_info = {
            "auth_key": auth_key,
            "by": "phone",
            "date_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }
        rt = requests.put(TIMESYNC_URL.format(self.ip), json=timesync_info, verify=False,
                          headers={"Content-Type": "application/json"})
        try:
            assert rt.json()['status'] == 'success', rt.__dict__
        except JSONDecodeError:
            time.sleep(retry)
            return self._login(retry=retry*2)
        self.auth_key = auth_key
        return auth_key

    def update_ip(self):
        """
        update IP by running mdns scan, return IP and server name (also update internal state)
        :return:
        """
        ip = get_ess_ip(self.name)
        self.ip = ip
        return self.ip

    def get_graph(self, device: str, timespan: str, date: datetime.datetime):
        """
        Get the time series data about a device
        :param device: the device in question ``["batt", "load", "pv"]``
        :param timespan: the timespan in question ``["day", "week", "month", "year"]``
        :param date: the date specifying the time span. (for week, month and year I guess any date within the timespan
                     of interest will suffice)
        :return:
        """
        assert device in GRAPH_DEVICES
        assert timespan in GRAPH_TIMESPANS
        url = f"https://{self.ip}/v1/user/graph/{device}/{timespan}"
        # r = requests.post(url, json=jsondata, verify=False, headers={"Content-Type": "application/json"})
        return self.post_json_with_auth(url, extra_json_data={
            GRAPH_PARAMS[timespan]: date.strftime(GRAPH_TFORMATS[GRAPH_PARAMS[timespan]])})

    def post_json_with_auth(self, url: str, retries: int = 0, extra_json_data: dict = None):
        """
        wrapper that posts json data after adding auth data. Optionally takes an extra_json_data argument.
        :param url: URL to fetch
        :param retries: internal parameter for recoursive calls
        :param extra_json_data: extra json data to pass
        :return:
        """
        json = {"auth_key": self.auth_key}
        error = False
        if extra_json_data:
            json.update(extra_json_data)
        try:
            r = requests.post(url, json=json, verify=False, headers={"Content-Type": "application/json"}, timeout=(3,3))
        except (requests.ConnectionError, requests.ConnectTimeout):
            error = True
        if not error and (r.status_code == 200 or (r.json() != {'auth': 'auth_key failed'})):
            return r.json()
        logger.info("seems we got logged out, retrying after {} seconds".format(retries))
        time.sleep(retries)
        self._login()
        return self.post_json_with_auth(url, retries=retries + 1, extra_json_data=None)

    def get_network(self):  # pragma: no cover
        return self.get_state("network")

    def get_systeminfo(self):  # pragma: no cover
        return self.get_state("systeminfo")

    def get_batt(self):  # pragma: no cover
        return self.get_state("batt")

    def get_home(self):  # pragma: no cover
        return self.get_state("home")

    def get_common(self):  # pragma: no cover
        return self.get_state("common")

    def get_state(self, state):
        return self.post_json_with_auth(STATE_URLS[state].format(self.ip))

    def switch_on(self):
        """
        switch on operation.
        :return:
        """
        r = requests.put(SWITCH_URL.format(self.ip), json={"auth_key": self.auth_key, "operation": "start"},
                         verify=False, headers={"Content-Type": "application/json"})

    def switch_off(self):
        """
        switch off operation.
        :return:
        """
        r = requests.put(SWITCH_URL.format(self.ip), json={"auth_key": self.auth_key, "operation": "stop"},
                         verify=False, headers={"Content-Type": "application/json"})
        # if not r.json()["status"] == "success":
        #    raise ESSException("switching unsuccessful")

    def get_batt_settings(self):
        """
        fetch current batt settings
        :return: dict with current settings
        """
        return self.post_json_with_auth(BATT_URL.format(self.ip))

    def set_batt_settings(self, command):
        command.update({"auth_key": self.auth_key})
        requests.put(BATT_URL.format(self.ip), json=command, verify=False)

    def winter_off(self):  # pragma: no cover
        """
        switch off winter mode
        :return:
        """
        self.set_batt_settings({"wintermode": "off"})

    def winter_on(self):  # pragma:no cover
        """
        switch off winter mode
        :return:
        """
        self.set_batt_settings({"wintermode": "on"})

    def fastcharge_on(self):  # pragma:no cover
        """
        switch off winter mode
        :return:
        """
        self.set_batt_settings({"alg_setting": "on"})

    def fastcharge_off(self):  # pragma:no cover
        """
        switch off winter mode
        :return:
        """
        self.set_batt_settings({"alg_setting": "off"})


def get_ess_ip(name):
    """
    Resolve the ESS Device name ``Name`` to an IP Address. Makes sense to find the ESS when its IP is dynamic.
    :param name: The ESS Name to resolve
    :return: ip
    """
    zeroconf = Zeroconf()
    ess_info = zeroconf.get_service_info("_pmsctrl._tcp.local.", f"LGE_ESS-{name}._pmsctrl._tcp.local.")
    zeroconf.close()
    ip = [socket.inet_ntoa(ip) for ip in ess_info.addresses][0]
    return ip


def get_ess_pw(ip="192.168.23.1"):
    """
    This method only works on the wifi provided by the box.
    Contact the box and fetch the password that belongs to the box.

    (my box uses 192.168.23.1 for its ip on its own wifi so that is the default)
    :param ip: the IP to contact
    :return: password
    """
    res = requests.post(f"https://{ip}/v1/user/setting/read/password", json={"key": "lgepmsuser!@#"},
                        headers={"Charset": "UTF-8", "Content-Type": "application/json"}, verify=False,
                        timeout=1).json()
    if res['status'] == 'success':
        return res['password']
    logger.exception("could not fetch password")
    raise LookupError("could not look up password")


def autodetect_ess():
    """
    Runs an mdns scan and returns the first ESS device that is found as a list of two strings, IP and Name

    >>> ip, name = autodetect_ess()

    :return: ip, name
    """
    name = find_all_esses()[0]
    name = extract_name_from_zeroconf(name)

    zeroconf = Zeroconf()
    ess_info = zeroconf.get_service_info("_pmsctrl._tcp.local.", f"LGE_ESS-{name}._pmsctrl._tcp.local.")
    zeroconf.close()
    ip = [socket.inet_ntoa(ip) for ip in ess_info.addresses][0]
    return ip, name


def extract_name_from_zeroconf(zeroconf_name):
    """
    helper function to extract ESS name from zeroconf host name
    :param zeroconf_name:
    :return: name
    """
    name = re.sub(r"LGE_ESS-(.+)\._pmsctrl\._tcp\.local\.", r"\g<1>", zeroconf_name)
    return name


def find_all_esses():
    """
    scan for all esses via mdns and return a list of mdns name strings.
    :return:
    """
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

    if len(esses) == 0:
        raise ESSException("could not find any ESS devices via mdns")
    return esses


def mitm_for_ess(name, ip="127.0.0.1"):
    """
    Announce an IP address via mdns just like an actual LG ESS device would announce itsself
    Useful for unit tests
    :param name: The name to announce on the network
    :return:
    """
    import socket
    info = ServiceInfo(
        "_pmsctrl._tcp.local.",
        f"LGE_ESS-{name}._pmsctrl._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=80,
        properties={b'Device': b'LGEESS', b'HWRevison': b'1.5'},
        server="myaddress.local.",
    )

    zeroconf = Zeroconf()
    zeroconf.register_service(info)
