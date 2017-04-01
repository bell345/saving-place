#!/usr/bin/env python3

import argparse

from .version import APP_NAME, APP_VERSION

def main():
    parser = argparse.ArgumentParser(prog=APP_NAME,
        description="Recording reddit's /r/place experiment, one pixel at a time.",
        epilog="(C) Thomas Bell 2017, MIT License. REDDIT is a registered trademark of reddit inc.")
    parser.add_argument("--version", action="version", version=APP_VERSION)

    args = parser.parse_args()

    # You get nothing! You lose! Good day sir!

