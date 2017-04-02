#!/usr/bin/env python3

import re
import json

import requests
from bs4 import BeautifulSoup

from .version import USER_AGENT

PLACE_URL = "https://www.reddit.com/place?webview=true"

DICT_RE = re.compile(r'\{.+\}')
WSURL_RE = re.compile(r'"place_websocket_url": *"([^"]+)"')

#
# This is perhaps the most hacky part of the project.
# Our goal is to get a URL that we can hook a WebSocket
# up to, and the only way I've found to do this is to
# load /place like a browser and parse the HTML.
#
def get_websocket_url():
    headers = { "User-Agent": USER_AGENT }
    r = requests.get(PLACE_URL, headers=headers)

    try:
        # the compliant way
        dom = BeautifulSoup(r.text, "html.parser")
        element = dom.find(id='config')
        match = DICT_RE.search(element.text)
        obj = json.loads(match.group(0))
        return obj["place_websocket_url"]

    except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
        # the hacky way
        match = WSURL_RE.search(r.text)
        if not match:
            return None
        else:
            return match.group(1)

