#!/usr/bin/env python3

import os
import sys
import argparse

import praw

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

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    if not client_id:
        return abort(
            "Please provide a reddit client_id in the environment "
            "variable REDDIT_CLIENT_ID. You can obtain one from: "
            "https://www.reddit.com/prefs/apps")

    if not client_secret:
        return abort(
            "Please provide the reddit client_secret for the client_id "
            "{} in the environment variable REDDIT_CLIENT_SECRET.".format(
                client_id))

    if not username or not password:
        return abort(
            "Please provide a reddit username and password combination "
            "in the environment variables REDDIT_USERNAME and "
            "REDDIT_PASSWORD. This information is not stored and is "
            "provided to reddit servers via a secure connection.")

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         username=username,
                         password=password,
                         user_agent=USER_AGENT)

    print("Logged in as: {}".format(reddit.user.me()))

