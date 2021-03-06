#!/usr/bin/env python3

import os
import sys
import asyncio
import argparse
from time import sleep
from pathlib import Path

from .websocket import task_monitor
from .supervisor import Supervisor
from .bitmap import task_bitmap
from .version import APP_NAME, APP_VERSION

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

    loop = asyncio.get_event_loop()
    supervisor = Supervisor()
    task0 = supervisor.task()
    task1 = task_monitor(supervisor, args.output)
    task2 = task_monitor(supervisor, args.output)
    task3 = task_bitmap(args.output, args.interval)
    loop.run_until_complete(asyncio.gather(task0, task1, task2, task3))

if __name__ == "__main__":
    main()

