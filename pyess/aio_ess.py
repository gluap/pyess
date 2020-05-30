#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import datetime
import logging
import time

from aiohttp.client_exceptions import ContentTypeError

from json import JSONDecodeError

import aiohttp

from pyess.constants import LOGIN_URL, TIMESYNC_URL, GRAPH_TIMESPANS, GRAPH_DEVICES, GRAPH_PARAMS, \
    GRAPH_TFORMATS, SWITCH_URL, STATE_URLS, BATT_URL


class ESSException(Exception):
    pass


class ESSAuthException(ESSException):
    pass


logger = logging.getLogger(__name__)


class ESS:
    @classmethod
    async def create(cls, name=None, password=None, ip=None):
        ess = cls(name, password, ip)
        await ess._login()
        return ess

    def __init__(self, name, pw, ip=None):
        self.name = name
        self.pw = pw
        self.ip = ip
        self.logged_in = False
        self.auth_key = None
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                             timeout=aiohttp.ClientTimeout(connect=60,sock_read=60, sock_connect=60, total=180))

    async def _login(self, retry=1):
        """
        Login to the ESS device. Called by __init__
        :return:
        """
        url = LOGIN_URL.format(self.ip)
        logger.info("fetching auth key")
        async with self.session.put(url, json={"password": self.pw}) as r:
            response_json = await r.json()
        if "status" in response_json and response_json["status"] == "password mismatched":
            raise ESSAuthException("wrong password")
        # r = requests.put(url, json={"password": self.pw}, verify=False, headers={"Content-Type": "application/json"})
        auth_key = response_json["auth_key"]
        timesync_info = {
            "auth_key": auth_key,
            "by": "phone",
            "date_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }
        async with self.session.put(TIMESYNC_URL.format(self.ip), json=timesync_info) as r:
            try:
                response_json = await r.json()
                #        rt = requests.put(TIMESYNC_URL.format(self.ip), json=timesync_info, verify=False,
                #                          headers={"Content-Type": "application/json"})

                assert response_json['status'] == 'success', response_json
            except (JSONDecodeError, ContentTypeError):
                time.sleep(retry)
                return await self._login(retry=retry * 2)
        self.auth_key = auth_key
        self.logged_in = True
        return auth_key

    async def get_graph(self, device: str, timespan: str, date: datetime.datetime):
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
        return await self.post_json_with_auth(url, extra_json_data={
            GRAPH_PARAMS[timespan]: date.strftime(GRAPH_TFORMATS[GRAPH_PARAMS[timespan]])})

    async def post_json_with_auth(self, url: str, retries: int = 15, extra_json_data: dict = None):
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

        async with self.session.post(url, json=json) as r:
            response_json = await r.json()
            response_status = r.status
        # r = requests.post(url, json=json, verify=False, headers={"Content-Type": "application/json"})
        if (response_status == 200 or ((response_json != {'auth': 'auth_key failed'}) and
                                       (response_json != {'auth': 'auth failed'}))):
            return response_json
        logger.info("seems we got logged out, retrying after {} seconds".format(retries))
        await asyncio.sleep(retries)
        await self._login()
        return await self.post_json_with_auth(url, retries=retries * 2, extra_json_data=extra_json_data)

    async def get_network(self):  # pragma: no cover
        return await self.get_state("network")

    async def get_systeminfo(self):  # pragma: no cover
        return await self.get_state("systeminfo")

    async def get_batt(self):  # pragma: no cover
        return await self.get_state("batt")

    async def get_home(self):  # pragma: no cover
        return await self.get_state("home")

    async def get_common(self):  # pragma: no cover
        return await self.get_state("common")

    async def get_state(self, state):
        return await self.post_json_with_auth(STATE_URLS[state].format(self.ip))

    async def switch_on(self):  # pragma: no cover
        """
        switch on operation.
        :return:
        """
        async with self.session.put(SWITCH_URL.format(self.ip), json={"auth_key": self.auth_key, "operation": "start"}) as r:
            response_json = await r.json()

    async def switch_off(self):  # pragma: no cover
        """
        switch off operation.
        :return:
        """
        async with self.session.put(SWITCH_URL.format(self.ip), json={"auth_key": self.auth_key, "operation": "stop"}) as r:
            response_json = await r.json()

    async def get_batt_settings(self):
        """
        fetch current batt settings
        :return: dict with current settings
        """
        return await self.post_json_with_auth(BATT_URL.format(self.ip))

    async def set_batt_settings(self, command):
        command.update({"auth_key": self.auth_key})
        async with self.session.put(BATT_URL.format(self.ip), json=command) as r:
            await r.json()

    async def winter_off(self):  # pragma: no cover
        """
        switch off winter mode
        :return:
        """
        return await self.set_batt_settings({"wintermode": "off"})

    async def winter_on(self):  # pragma:no cover
        """
        switch off winter mode
        :return:
        """
        return await self.set_batt_settings({"wintermode": "on"})

    async def fastcharge_on(self):  # pragma:no cover
        """
        switch off winter mode
        :return:
        """
        return await self.set_batt_settings({"alg_setting": "on"})

    async def fastcharge_off(self):  # pragma:no cover
        """
        switch off winter mode
        :return:
        """
        return await self.set_batt_settings({"alg_setting": "off"})

    # setting winter start and end dates:
    # "startdate" "MMDD"
    # "stopdate" "MMDD"

    def __del__(self, *args):
        """
        tear down connector to avoid warnings, especially in unit tests.
        :return:
        """
        try:
            asyncio.ensure_future(self.session.close())
        except RuntimeError:
            # if there's no event loop we don't have to close the aiohttp session
            pass

    async def destruct(self, *args):
        """
        tear down connector to avoid warnings, especially in unit tests.
        :return:
        """
        await self.session.close()
