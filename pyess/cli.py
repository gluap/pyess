#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import argparse
from pyess.ess import find_all_esses, get_ess_pw, extract_name_from_zeroconf

log = logging.getLogger(__name__)


def list_esses():
    print("Searching for LG ESS devices on the network")
    esses = find_all_esses()
    print("found {} devices:".format(len(esses)))
    i = 1
    for ess in esses:
        print(" {}  {}".format(i, extract_name_from_zeroconf(ess)))
        i += 1


def get_password():
    print("Fetching ess password. For this you must be connected to the ESS wifi (or recently have been connected to it)")
    pw = get_ess_pw("192.168.1.253")
    return


actions = {"list_ess": list_esses, "get_password": get_password}


def main():
    parser = argparse.ArgumentParser(prog='greet', description='Command line interface for pyess')
    parser.add_argument(
        '--loglevel', default='info', help='Log level',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
    )
    parser.add_argument("--action", default="list_ess", help="what to do", choices=actions.keys())
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel.upper())

    actions[args.action]()


if __name__ == "__main__":
    main()
