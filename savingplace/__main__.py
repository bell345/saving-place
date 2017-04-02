#!/usr/bin/env python3

import os
import sys
import asyncio
import argparse

from .scrape import get_websocket_url, get_initial_bitmap
from .websocket import monitor_place
from .version import APP_NAME, APP_VERSION, USER_AGENT

def abort(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog=APP_NAME,
        description="Recording reddit's /r/place experiment, one pixel at a time.",
        epilog="(C) Thomas Bell 2017, MIT License. REDDIT is a registered trademark of reddit inc.")
    parser.add_argument("--version", action="version", version=APP_VERSION)

    parser.add_argument("initial_png", type=argparse.FileType("wb"),
        help="PNG encoded output for initial /place bitmap.")
    parser.add_argument("change_output", type=argparse.FileType("a"),
        help="CSV formatted output file for incremental changes.")

    args = parser.parse_args()

    print("Retrieving initial bitmap...")
    img = get_initial_bitmap()
    print("Saving to file...")
    img.save(args.initial_png)

    url = get_websocket_url()
    if not url:
        return abort("Unable to get WebSocket URL.")

    fp = args.change_output
    try:
        task = monitor_place(fp, url)
        asyncio.get_event_loop().run_until_complete(task)
    finally:
        fp.close()

if __name__ == "__main__":
    main()

