import argparse
import asyncio
import logging
import sys
from distutils.util import strtobool

from asyncio_mqtt import Client

from pyess.aio_ess import ESS
from pyess.ess import autodetect_ess

logger = logging.getLogger(__name__)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


async def send_loop(client, ess, once=False, interval_seconds=10):
    logger.info("starting send loop")
    while True:
        if not once:
            await asyncio.sleep(1)
        home = await ess.get_state("home")
        common = await ess.get_state("common")
        for key in home:
            for key2 in home[key]:
                try:
                    await client.publish("ess/home/" + key + "/" + key2, home[key][key2])
                except:
                    pass
        for key in common:
            for key2 in common[key]:
                try:
                    await client.publish("ess/common/" + key + "/" + key2, common[key][key2])
                except:
                    pass
        if once:
            break
        await asyncio.sleep(interval_seconds - 1)


def main(arguments=None):
    loop = asyncio.get_event_loop()
    asyncio.run(_main(arguments))
    # .run(_main, arguments)


async def _main(arguments=None):
    parser = argparse.ArgumentParser(prog='pyess', description='Command line interface for pyess')
    parser.add_argument(
        '--loglevel', default='info', help='Log level',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
    )

    parser.add_argument("--ess_password", default=None, help="password (required for everything but get_password)")
    parser.add_argument("--mqtt_server", default="192.168.1.220", help="mqtt server")
    parser.add_argument("--mqtt_port", default=1883, type=int, help="mqtt port")
    parser.add_argument("--mqtt_password", default=None, help="mqtt password")
    parser.add_argument("--mqtt_user", default=None, help="mqtt user")
    parser.add_argument("--ess_host", default=None, help="hostname or IP of mqtt host (discover via mdns if not set)")
    parser.add_argument("--once", default=False, type=bool, help="no loop, only one pass")
    parser.add_argument("--interval_seconds", default=10, type=int, help="update interval (default: 10 seconds)")

    args = parser.parse_args(arguments)

    if args.ess_host is None:
        ip, name = autodetect_ess()
    else:
        ip, name = args.ess_host, args.ess_host

    logging.basicConfig(level=args.loglevel.upper())

    ess = await ESS.create(name, args.ess_password, ip)

    async def switch_winter(state: bool):
        logger.info(f"switching winter mode to {state}")
        if state:
            await ess.winter_off()
        else:
            await ess.winter_on()

    async def switch_fastcharge(state: bool):
        logger.info(f"switching fast charge mode to {state}")
        if state:
            await ess.fastcharge_on()
        else:
            await ess.fastcharge_off()

    async def switch_active(state: bool):
        logger.info("switching ess {}".format("on" if state else "off"))
        if state:
            await ess.switch_on()
        else:
            await ess.switch_off()

    async def handle_control(client,control,path):
        async with client.filtered_messages(path) as messages:
            async for msg in messages:
                logger.info(f"control message received {msg}")
                try:
                    state = strtobool(msg.decode())
                    await control(state)
                except ValueError:
                    logger.warning(f"ignoring incompatible value {msg} for switching")


    async with Client(args.mqtt_server, port=args.mqtt_port, logger=logger, username=args.mqtt_user,
                      password=args.mqtt_password) as client:

        await client.subscribe('/ess/control/#')
        asyncio.create_task(handle_control(client, switch_winter, "/ess/control/winter_mode"))
        asyncio.create_task(handle_control(client, switch_fastcharge, "/ess/control/fastcharge"))
        asyncio.create_task(handle_control(client, switch_active, "/ess/control/active"))

        await send_loop(client, ess, once=args.once, interval_seconds=args.interval_seconds)


if __name__ == "__main__":
    main(sys.argv[1:])
