#!/usr/bin/env python3

import time
import asyncio
from pathlib import Path

import requests
import requests.exceptions
from PIL import Image

from .log import async_log
from .version import USER_AGENT

HEADERS = { "User-Agent": USER_AGENT }
BITMAP_URL = "https://www.reddit.com/api/place/board-bitmap"

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

def get_place_bitmap():
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

async def task_bitmap(directory, interval=600):
    while True:
        await async_log("Retrieving bitmap...")
        try:
            img = get_place_bitmap()
        except requests.exceptions.ConnectionError as e:
            await async_log("Failed to retrieve bitmap: ")
            await async_log(str(e))

        p = Path(directory)
        p.mkdir(parents=True, exist_ok=True)
        p /= "place-{}.png".format(int(time.time()))

        await async_log("Saving {}...".format(p.name))
        img.save(str(p.absolute()))

        await asyncio.sleep(interval)
