#!/usr/bin/env python3

import time
import asyncio
from pathlib import Path
from datetime import datetime

import requests.exceptions

from .log import status_log, async_log
from .scrape import get_initial_bitmap

class SyncMonitor:
    
    def __init__(self):
        self.clients = set()
        self.msg_queue = {}
        self.lock = asyncio.Lock()
        self._next_id = 1

    async def register(self):
        with (await self.lock):
            i = self._next_id
            self._next_id += 1
            self.clients.add(i)

        return i

    async def deregister(self, i):
        with (await self.lock):
            self.clients.remove(i)

    async def log(self, i, msg):
        await async_log("({}) {}".format(i, msg))

    async def put(self, msg, timestamp):
        with (await self.lock):
            if msg in self.msg_queue:
                ts = self.msg_queue[msg]
                if timestamp < ts:
                    ts = timestamp

                self.msg_queue[msg] = ts

            else:
                self.msg_queue[msg] = timestamp

    async def get(self):
        msg_queue = {}
        with (await self.lock):
            msg_queue = self.msg_queue.copy()
            self.msg_queue = {}

        return [(ts, msg) for msg, ts in msg_queue.items()]

sync_lock = asyncio.Lock()

async def sync_place(directory, interval=600):
    while True:
        with (await sync_lock):
            await async_log("Retrieving bitmap...")
            try:
                img = get_initial_bitmap()
            except requests.exceptions.ConnectionError as e:
                await async_log("Failed to retrieve bitmap: ")
                await async_log(str(e))

            timestamp = int(time.time())
            filename = Path(directory) / "place-{}.png".format(timestamp)
            await async_log("Saving {}...".format(filename.stem))
            img.save(str(filename.absolute()))

        await asyncio.sleep(interval)

