#!/usr/bin/env python3

import os
import sys
import asyncio
import argparse
from time import sleep
from pathlib import Path

from .scrape import get_websocket_url, get_initial_bitmap
from .websocket import monitor_place
from .sync import sync_place
from .serial import save_image
from .log import status_log
from .version import APP_NAME, APP_VERSION, USER_AGENT

def abort(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog=APP_NAME,
        description="Recording reddit's /r/place experiment, one pixel at a time.",
        epilog="(C) Thomas Bell 2017, MIT License. REDDIT is a registered trademark of reddit inc.")
    parser.add_argument("--version", action="version", version=APP_VERSION)

    parser.add_argument("-o", "--output", type=str, default="./",
        help="Directory to output bitmaps and incremental changes. "
             "Defaults to current working directory.")

    parser.add_argument("-i", "--interval", type=float, default=600,
        help="Interval (in seconds) at which bitmaps are recorded. "
             "Defaults to 10 minutes.")

    args = parser.parse_args()

    status_log("Retrieving initial bitmap...")
    img = get_initial_bitmap()
    status_log("Saving to file...")
    save_image(img, args.output)

    url = get_websocket_url()
    if not url:
        return abort("Unable to get WebSocket URL.")

    loop = asyncio.get_event_loop()
    task1 = monitor_place(url, args.output)
    task2 = sync_place(args.output, args.interval)
    loop.run_until_complete(asyncio.gather(task1, task2))

if __name__ == "__main__":
    main()

