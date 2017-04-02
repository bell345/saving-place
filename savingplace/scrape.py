#!/usr/bin/env python3

import re
import json

import requests
from bs4 import BeautifulSoup
from PIL import Image

from .version import USER_AGENT

HEADERS = { "User-Agent": USER_AGENT }
PLACE_URL = "https://www.reddit.com/place?webview=true"
BITMAP_URL = "https://www.reddit.com/api/place/board-bitmap"

DICT_RE = re.compile(r'\{.+\}')
WSURL_RE = re.compile(r'"place_websocket_url": *"([^"]+)"')

COLOURS = [
    (255, 255, 255),
    (228, 228, 228),
    (136, 136, 136),
    (34, 34, 34),
    (255, 167, 209),
    (229, 0, 0),
    (229, 149, 0),
    (160, 106, 66),
    (229, 217, 0),
    (148, 224, 68),
    (2, 190, 1),
    (0, 211, 221),
    (0, 131, 199),
    (0, 0, 234),
    (207, 110, 228),
    (130, 0, 128)
]

#
# This is perhaps the most hacky part of the project.
# Our goal is to get a URL that we can hook a WebSocket
# up to, and the only way I've found to do this is to
# load /place like a browser and parse the HTML.
#
def get_websocket_url():
    r = requests.get(PLACE_URL, headers=HEADERS)

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

def get_initial_bitmap():
    r = requests.get(BITMAP_URL, headers=HEADERS)

    binary = r.content
    img = Image.new("RGB", (1000, 1000))
    get_xy = lambda i: (i % 1000, i // 1000)

    for offset in range((1000*1000)//2):
        packed = binary[offset]
        pix1 = (packed >> 4) & 0x0F
        pix2 = packed & 0x0F
        img.putpixel(get_xy(offset*2), COLOURS[pix1])
        img.putpixel(get_xy(offset*2+1), COLOURS[pix2])

    return img

