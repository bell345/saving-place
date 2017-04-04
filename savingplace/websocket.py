#!/usr/bin/env python3

import json
import time
import socket
import asyncio
import concurrent.futures
from datetime import datetime

import websockets
import websockets.exceptions

from .version import USER_AGENT
from .log import status_log, async_log
from .scrape import get_websocket_url
from .serial import decode_ws_msg, write_increment, open_change_output

WS_ORIGIN = "https://www.reddit.com"

async def worker(supervisor, fp, url):
    syncmon = supervisor.syncmon
    headers = (("User-Agent", USER_AGENT),)
    synchndl = await syncmon.register()
    try:
        await syncmon.log(synchndl,
            "Connecting to WebSocket: '{}'".format(url))

        async with websockets.connect(url, origin=WS_ORIGIN,
                                      extra_headers=headers) as ws:
            await syncmon.log(synchndl, "Connected.")
            await supervisor.register(ws)

            while True:
                msg = await ws.recv()
                x, y, colour, author = decode_ws_msg(msg)
                if x is None:
                    await syncmon.log(synchndl, 
                        "Can't parse message: {}".format(msg))
                    continue

                await syncmon.put((x, y, colour, author),
                                  time.time())

                for ts, msg in (await syncmon.get()):
                    write_increment(fp, ts, *msg)

    except concurrent.futures.CancelledError as e:
        await syncmon.log(synchndl, "WebSocket cancelled.")

    finally:
        await supervisor.deregister()
        await syncmon.deregister(synchndl)

async def task_monitor(supervisor, directory):
    retry_time = 0.5
    last_retry = time.time()
    while True:
        try:
            url = get_websocket_url()
            if not url:
                await async_log("URI could not be obtained.")
            else:
                fp = open_change_output(directory)
                await worker(supervisor, fp, url)

        except websockets.exceptions.InvalidURI:
            await async_log("'{}' is not a valid WebSocket URI.".format(url))

        except (websockets.exceptions.InvalidHandshake,
                websockets.exceptions.ConnectionClosed,
                socket.error) as e:
            if isinstance(e, websockets.exceptions.ConnectionClosed):
                await async_log("Connection closed ({}): {}".format(
                    e.code, e.reason))
            else:
                await async_log("Cannot connect: {}".format(str(e)))

        finally:
            fp.close()
            await async_log("WebSocket closed.")

        if (retry_time > 5 and
            (datetime.now().timestamp() - last_retry) > retry_time):
            retry_time = 0.5

        if retry_time > 600:
            await async_log("Retry time greater than 600s.")
            break

        await async_log("Retrying in {}s...".format(retry_time))
        await asyncio.sleep(retry_time)

        retry_time *= 2
        last_retry = datetime.now().timestamp()

