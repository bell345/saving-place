#!/usr/bin/env python3

import os
import sys
import asyncio

from .log import async_log

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

class Supervisor:
    
    def __init__(self, interval=30):
        self.syncmon = SyncMonitor()
        self.sockets = {}
        self.pings = {}
        self.handles = {}
        self.lock = asyncio.Lock()
        self.interval = interval
        self._next_id = 1

    async def register(self, ws):
        task = asyncio.Task.current_task()
        with (await self.lock):
            self.sockets[task] = ws
            hndl = self._next_id
            self._next_id += 1
            self.handles[task] = hndl
    
    async def deregister(self):
        task = asyncio.Task.current_task()
        with (await self.lock):
            del self.sockets[task]
            del self.handles[task]

    async def log(self, msg, task=None):
        if not task:
            task = asyncio.Task.current_task()
        hndl = self.handles.get(task, -1)
        await async_log("({}) {}".format(hndl, msg))

    async def task(self):
        while True:
            with (await self.lock):
                for task, ws in self.sockets.items():
                    try:
                        ping = self.pings[task]
                        # ws is responding
                        if ping.done() and not ping.cancelled():
                            self.pings[task] = await ws.ping()

                        # pong not received, socket is hung
                        else:
                            await self.log(
                                "Pong not received, cancelling...", task=task)
                            task.cancel()

                    except KeyError:
                        self.pings[task] = await ws.ping()

            await asyncio.sleep(self.interval)

