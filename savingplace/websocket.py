#!/usr/bin/env python3

import json
import time
import socket
import asyncio
from datetime import datetime

import websockets
import websockets.exceptions as wsexcept

from .version import USER_AGENT
from .log import status_log
from .sync import sync_lock
from .scrape import get_websocket_url
from .serial import decode_ws_msg, write_increment, open_change_output

WS_ORIGIN = "https://www.reddit.com"

async def worker(syncmon, fp, url):
    headers = (("User-Agent", USER_AGENT),)
    synchndl = await syncmon.register()
    try:
        await syncmon.log(synchndl,
            "Connecting to WebSocket: '{}'".format(url))

        async with websockets.connect(url, origin=WS_ORIGIN,
                                      extra_headers=headers) as ws:
            await syncmon.log(synchndl, "Connected.")

            while True:
                msg = await ws.recv()
                x, y, colour, author = decode_ws_msg(msg)
                if x is None:
                    await syncmon.log(synchndl, 
                        "Can't parse message: {}".format(msg))
                    continue

                await syncmon.put((x, y, colour, author),
                                  time.time())

                if sync_lock.locked():
                    continue

                for ts, msg in (await syncmon.get()):
                    write_increment(fp, ts, *msg)
    finally:
        await syncmon.deregister(synchndl)

async def monitor_place(syncmon, directory):
    retry_time = 0.5
    last_retry = time.time()
    while True:
        try:
            url = get_websocket_url()
            if not url:
                status_log("URI could not be obtained.")
            else:
                fp = open_change_output(directory)
                await worker(syncmon, fp, url)

        except wsexcept.InvalidURI:
            status_log("'{}' is not a valid WebSocket URI.".format(url))

        except (wsexcept.InvalidHandshake,
                wsexcept.ConnectionClosed,
                socket.error) as e:
            if isinstance(e, wsexcept.ConnectionClosed):
                status_log("Connection closed ({}): {}".format(
                    e.code, e.reason))
            else:
                status_log("Cannot connect: {}".format(str(e)))

        finally:
            fp.close()
            status_log("WebSocket closed.")

        if (retry_time > 5 and
            (datetime.now().timestamp() - last_retry) > retry_time):
            retry_time = 0.5

        if retry_time > 600:
            status_log("Retry time greater than 600s.")
            break

        status_log("Retrying in {}s...".format(retry_time))
        await asyncio.sleep(retry_time)

        retry_time *= 2
        last_retry = datetime.now().timestamp()

