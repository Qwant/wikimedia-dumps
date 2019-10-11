#!/usr/bin/env python3
import os
import urllib.request

from config import *


def download_stats():
    for i, dump_file in enumerate(STATS_FILES):
        path = os.path.join(STATS_DUMP_DIR, dump_file)
        url = os.path.join(STATS_ENDPOINT, dump_file)
        print('({}/{}) {}'.format(i + 1, len(STATS_FILES), path))

        # Download the file
        os.makedirs(os.path.dirname(path), exist_ok=True)
        urllib.request.urlretrieve(url, path)
