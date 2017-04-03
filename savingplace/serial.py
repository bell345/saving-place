#!/usr/bin/env python3

import time
import json
import struct
from datetime import datetime
from pathlib import Path

from .log import status_log

def save_image(img, directory):
    d = Path(directory)
    d /= "place-{}.png".format(int(time.time()))
    img.save(str(d.absolute()))

def open_change_output(directory):
    d = Path(directory)
    d /= "changes-{}.bin".format(int(time.time()))
    return open(str(d.absolute()), "ab")

def decode_ws_msg(msg):
    no_resp = None, None, None, None
    try:
        obj = json.loads(msg)
        if obj["type"] != "place":
            return no_resp

        payload = obj["payload"]

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        status_log("Failed to retrieve payload: {!s}".format(e))
        return no_resp

    try:
        x, y, colour, author = (
            payload["x"], payload["y"],
            payload["color"], payload["author"])

    except KeyError as e:
        status_log("Failed to retrieve properties: {!s}".format(e))

    if not (x or y or colour or author):
        status_log("Properties invalid")
        return no_resp

    return x, y, colour, author

#
# The binary format represents each pixel change as an entry.
# Each entry immediately follows the previous, and has the following format:
#
# Normal entries:
# xx xx yz zz zz NN NN .. NN NN 00
#
# x: UNIX timestamp delta (milliseconds), x != 0
# y: colour (0x0-0xF)
# z: index (0-999999)
# N: name (zero-terminated UTF-8 string)
#
# A special entry, where x = 0 and z = 1 is a keyframe entry, which
# specifies an absolute timestamp. The "timestamp delta" of every following
# normal entry adds to this timestamp value accumulatively to obtain their
# absolute timestamp.
#
# Keyframe entries:
# 00 00 00 00 00 01 00
# xx xx xx xx yy yy yy yy
#
# x: UNIX timestamp (seconds)
# y: UNIX timestamp (milliseconds)
#

# Writes a binary keyframe corresponding to `timestamp` to the file
# pointer `fp`.
def write_keyframe(fp, timestamp):
    sec, ms = int(timestamp), int((timestamp % 1) * 1e6)
    fp.write(b'\x00\x00\x00\x00\x01\x00')
    fp.write(struct.pack("!II", sec, ms))

last_timestamp = None

# Writes a single pixel change which occured at `timestamp` at position
# (`x`, `y`) of colour `colour` by the author /u/`author` to the file
# pointer `fp`.
def write_increment(fp, timestamp, x, y, colour, author):
    global last_timestamp

    if not last_timestamp:
        write_keyframe(fp, timestamp)
        timestamp_delta = 0
    else:
        timestamp_delta = int((timestamp - last_timestamp) * 1e6)
        if timestamp_delta >= 2**16:
            write_keyframe(fp, timestamp)
            timestamp_delta = 0

    if timestamp_delta == 0:
        timestamp_delta = 1

    index = y * 1000 + x
    short12 = timestamp_delta & 0xFFFF
    byte3 = ((colour & 0x0F) << 4) | ((index >> 16) & 0x0F)
    short45 = (index) & 0xFFFF
    fp.write(struct.pack("!HBH", short12, byte3, short45))
    fp.write(author.encode('utf8') + b'\x00')

    last_timestamp = timestamp

def decode(fp):
    ts_delta = fp.read(2)
    index_colour = fp.read(3)
    name = b''
    char = fp.read(1)
    while char != b'\x00':
        name += char
        if not char:
            return None
        char = fp.read(1)

    (td,) = struct.unpack("!H", ts_delta)
    (ic1,ic2,ic3) = struct.unpack("!BBB", index_colour)
    colour = (ic1 >> 4) & 0x0F
    index = ((ic1 & 0x0F) << 16) | (ic2 << 8) | ic3
    if td == 0 and colour == 0 and index == 1:
        (sec,ms) = struct.unpack("!II", fp.read(8))
        return datetime.fromtimestamp(sec + (ms/1e6)).isoformat()

    else:
        return td, colour, index, name


