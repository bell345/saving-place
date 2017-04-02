#!/usr/bin/env python3

import json
from datetime import datetime

import websockets

from .version import USER_AGENT

WS_ORIGIN = "https://www.reddit.com"

async def monitor_place(fp, url):
    headers = (("User-Agent", USER_AGENT),)
    print("Connecting to WebSocket...")
    async with websockets.connect(url, origin=WS_ORIGIN,
                                  extra_headers=headers) as ws:
        print("Connected.")
        while True:
            msg = await ws.recv()

            try:
                obj = json.loads(msg)
                if obj["type"] != "place":
                    continue

                payload = obj["payload"]

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print("Failed to retrieve payload: {!s}".format(e))
                continue

            try:
                x, y, colour, author = (
                    payload["x"], payload["y"],
                    payload["color"], payload["author"])

            except KeyError as e:
                print("Failed to retrieve properties: {!s}".format(e))

            if not (x or y or colour or author):
                print("Properties invalid")
                continue

            fp.write(",".join(map(str, [
                datetime.now().timestamp(),
                x, y, colour, author])) + "\n")

