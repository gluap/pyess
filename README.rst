=====
pyess
=====

------------------------------------------------------------------------------
Python library for LG ESS Solar power converters with EnerVU app compatibility
------------------------------------------------------------------------------


.. image:: https://travis-ci.org/gluap/pyess.svg?branch=master
    :target: https://travis-ci.org/gluap/pyess?branch=master
.. image:: https://coveralls.io/repos/github/gluap/pyess/badge.svg?branch=master
    :target: https://coveralls.io/github/gluap/pyess?branch=master


Python library for communication with LG ESS power converter / energy storage devices for photovoltaic solar generators

This library is **not endorsed by the manufacturer**. It was written for lack of an official API. It should allow to
design home automation around the current state of a solar energy system - e.g. turn appliances on when there is surplus
solar power. LG only offers access via a badly scriptable web page or alternatively via a proprietary app that - at least
on my phone - crashes at least twice for every successful startup.

**Disclaimer:**
For this python module I reverse-engineered the communication between the *LG EnerVu Plus 1.2.3* Android
App and the Energy Storage / Inverter device, so there is some likelihood that it will work for devices that
can be accessed via that app. Nevertheless it looks like some of the interface is delivered by the ESS as html via the
network. Therefore it may be that not all commands work against all boxes. I only have customer-level access to my own
box, so this module only offers those parts of the API that are accessible to me as a customer. As far as I can tell
the installer has higher privileges and can fiddle with internal parameters of the system from what I saw him do when he
installed the system.


Usage
=====


Command Line
------------
This module comes with a rudimentary command line interface that allows for the following actions.

Fetch the device password
.........................

Caveat: **To fetch the device password you need to be connected to the devices wifi.** Once you are on the wifi you can
run the following to get the password. Write it down, it seems it is a static password per device::

    esscli --action get_password

The command assumes that the ess device is listening on ``192.168.23.1`` on its own wifi, in my setup it reproducibly
chooses that IP.

Find the esses on your network
..............................
Get a list of ESS devices on the local network (your home wifi, not the one of ess)::

    esscli --action list_ess


Fetch the state from ess as json
................................
fetch a bunch of json states as json and display the result on the command line::

    esscli --action get_data --password <your ess_password>

Examples for the data available:
- current power from and to the grid and the battery
- current voltage and power from both strings of the photovoltaic system independently
- current ip address
- details on grid power, battery state, daily and monthly statistics

Log ess state into a graphite server
....................................
This command will fetch the ``home`` and ``common`` info from ess every 10 seconds and log them against a graphite
server (assuming standard port and udp as protocol). Running this command requires the ess password to be passed on
the command line::

    esscli --action log_against_graphite --password <your_ess_password> --graphite <ip_of_graphite_server>

API
---
For the time being please use the docstrings in the code on https://github.com/gluap/pyess as documentation for the
API. A good place to start is pyess/cli.py where you can find the implementation of the CLI. One thing available
via the API but not yet via the CLI is the data for the daily / weekly / monthly / yearly statistics graphs that can
be accessed via the EnerVu App.


Changelog
=========

**2020-04-15 0.1.0**
- fix issue with fetch_password using wrong IP
- fix documentation
- add new mqtt synchronization service script

**2019-11-03 0.0.3**
- add aiohttp-based backend for use with asyncio

**2019-10-12 0.0.2**
- some minor fixes

**2019-10-09 0.0.1**
- More documentation
- Initial commit for pypi relase

**License**::

    Copyright (c) 2019 Paul Görgen

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
