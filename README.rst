pyess
-----
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
Network so it may be that not all commands funcition against all boxes. I only have customer-level access to my own
box, so this module only offers those parts of the API that are accessibl to me as a customer (as opposed to the
installer who has higher privileges and can fiddle with internal parameters of the system as I saw him do when he
installed the system).

Usage
-----
