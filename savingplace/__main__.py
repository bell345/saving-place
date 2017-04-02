#!/usr/bin/env python3

import os
import sys
import argparse

from .scrape import get_websocket_url
from .version import APP_NAME, APP_VERSION, USER_AGENT

def abort(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog=APP_NAME,
        description="Recording reddit's /r/place experiment, one pixel at a time.",
        epilog="(C) Thomas Bell 2017, MIT License. REDDIT is a registered trademark of reddit inc.")
    parser.add_argument("--version", action="version", version=APP_VERSION)

    args = parser.parse_args()

    url = get_websocket_url()
    print(url)

