#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import json
import urllib3
import argparse
from pyess.ess import find_all_esses, get_ess_pw, extract_name_from_zeroconf, autodetect_ess, ESS
from pyess.constants import STATE_URLS

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


def get_password(args):
    print(
        "Fetching ess password. For this you must be connected to the ESS wifi (or recently have been connected to it)")
    pw = get_ess_pw("192.168.1.253")
    return


def get_data(args):
    if not args.password:
        print("--password must be given for get_data")
    result = {}
    ip, name = autodetect_ess()
    ess = ESS(name, args.password)
    for i in STATE_URLS.keys():
        result[i] = ess.get_state(i)
    print(json.dumps(result))


actions = {"list_ess": list_esses, "get_password": get_password, "get_data": get_data}


def main():
    parser = argparse.ArgumentParser(prog='greet', description='Command line interface for pyess')
    parser.add_argument(
        '--loglevel', default='info', help='Log level',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
    )
    parser.add_argument("--action", default="list_ess", help="what to do", choices=actions.keys())
    parser.add_argument("--password", default=None, help="password (required for get_data)")

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel.upper())

    actions[args.action](args)


if __name__ == "__main__":
    main()
