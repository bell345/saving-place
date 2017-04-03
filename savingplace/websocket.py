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
from .serial import decode_ws_msg, write_increment, open_change_output

WS_ORIGIN = "https://www.reddit.com"

async def worker(fp, url):
    headers = (("User-Agent", USER_AGENT),)
    status_log("Connecting to WebSocket...")
    async with websockets.connect(url, origin=WS_ORIGIN,
                                  extra_headers=headers) as ws:
        status_log("Connected.")
        msg_buffer = []
        while True:
            msg = await ws.recv()
            msg_buffer.append((time.time(), msg))

            if sync_lock.locked():
                continue

            while len(msg_buffer) > 0:
                ts, msg = msg_buffer.pop()
                x, y, colour, author = decode_ws_msg(msg)
                if x is None:
                    status_log("Can't parse message: {}".format(msg))
                    continue
                write_increment(fp, ts, x, y, colour, author)

async def monitor_place(url, directory):
    while True:
        retry_time = 5
        last_retry = time.time()
        try:
            fp = open_change_output(directory)
            await worker(fp, url)

        except wsexcept.InvalidURI:
            status_log("'{}' is not a valid WebSocket URI.".format(url))
            break

        except (wsexcept.InvalidHandshake,
                wsexcept.ConnectionClosed,
                socket.error) as e:
            if isinstance(e, wsexcept.ConnectionClosed):
                status_log("Connection closed ({}): {}".format(
                    e.code, e.reason))
            else:
                status_log("Cannot connect: {}".format(str(e)))

            if (retry_time > 5 and
                (datetime.now().timestamp() - last_retry) > retry_time):
                retry_time = 5

            if retry_time > 600:
                break

            status_log("Retrying in {}s...".format(retry_time))
            await asyncio.sleep(retry_time)

            retry_time *= 2
            last_retry = datetime.now().timestamp()

        finally:
            fp.close()

