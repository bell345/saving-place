#!/usr/bin/env python3

import sys
import asyncio
import threading
from datetime import datetime

status_lock = threading.Lock()
async_lock = asyncio.Lock()

def status_log(msg):
    with status_lock:
        print("[{}] {}".format(datetime.now().isoformat(), msg))
        sys.stdout.flush()

async def async_log(msg):
    with (await async_lock):
        status_log(msg)

