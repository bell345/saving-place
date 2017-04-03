#!/usr/bin/env python3

import time
import asyncio
from pathlib import Path
from datetime import datetime

import requests.exceptions

from .log import status_log
from .scrape import get_initial_bitmap

sync_lock = asyncio.Lock()

async def sync_place(directory, interval=600):
    while True:
        with (await sync_lock):
            status_log("Retrieving bitmap...")
            try:
                img = get_initial_bitmap()
            except requests.exceptions.ConnectionError as e:
                status_log("Failed to retrieve bitmap: ")
                status_log(str(e))

            timestamp = int(time.time())
            filename = Path(directory) / "place-{}.png".format(timestamp)
            status_log("Saving {}...".format(filename.stem))
            img.save(str(filename.absolute()))

        await asyncio.sleep(interval)

