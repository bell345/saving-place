#!/usr/bin/env python3

import sys
import threading
from datetime import datetime

status_lock = threading.Lock()

def status_log(msg):
    with status_lock:
        print("[{}] {}".format(datetime.now().isoformat(), msg))
        sys.stdout.flush()

