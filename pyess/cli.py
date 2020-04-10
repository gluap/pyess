#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import logging
import json
import sys
import time
import graphyte
import urllib3
import argparse

from pyess.ess import find_all_esses, get_ess_pw, extract_name_from_zeroconf, autodetect_ess, ESS
from pyess.constants import STATE_URLS

logger = logging.getLogger(__name__)

log = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def list_esses(args):
    print("Searching for LG ESS devices on the network")
    esses = find_all_esses()
    print("found {} devices:".format(len(esses)))
    i = 1
    for ess in esses:
        print(" {}  {}".format(i, extract_name_from_zeroconf(ess)))
        i += 1


def log_against_graphite(args):
    if not args.password:
        print("--password must be given for get_data")
        return
    result = {}
    graphyte.init(args.graphite, port=2003, protocol="udp")
    ip, name = autodetect_ess()
    ess = ESS(name, args.password)
    while True:
        time.sleep(10 if not args.once else 0)
        home = ess.get_state("home")
        common = ess.get_state("common")
        for key in home:
            for key2 in home[key]:
                try:
                    graphyte.send("home." + key + "." + key2, float(home[key][key2]))
                except:
                    pass
        for key in common:
            for key2 in common[key]:
                try:
                    graphyte.send("common." + key + "." + key2, float(common[key][key2]))
                except:
                    pass
        logger.info(datetime.datetime.now())
        if args.once:
            break


def get_password(args):  # pragma: no cover
    print(
        "Fetching ess password. For this you must be connected to the ESS wifi (or recently have been connected to it)")
    pw = get_ess_pw("192.168.23.1")
    logger.info("password: {}".format(pw))
    return


def get_data(args):
    if not args.password:
        print("--password must be given for get_data")
        return
    result = {}
    ip, name = autodetect_ess()
    ess = ESS(name, args.password)
    for i in STATE_URLS.keys():
        result[i] = ess.get_state(i)
    print(json.dumps(result))


actions = {"list_ess": list_esses, "get_password": get_password, "get_data": get_data,
           "log_against_graphite": log_against_graphite}


def main(arguments=None):
    parser = argparse.ArgumentParser(prog='pyess', description='Command line interface for pyess')
    parser.add_argument(
        '--loglevel', default='info', help='Log level',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
    )
    parser.add_argument("--action", default="list_ess", help="what to do", choices=actions.keys())
    parser.add_argument("--password", default=None, help="password (required for everything but get_password)")
    parser.add_argument("--once", default=False, type=bool, help="only loop once in graphite upload")
    parser.add_argument("--graphite", default="192.168.1.222", help="server")

    args = parser.parse_args(arguments)
    logging.basicConfig(level=args.loglevel.upper())

    actions[args.action](args)


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
