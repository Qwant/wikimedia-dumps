#!/usr/bin/env python3
import os
import sys
import urllib.request

from config import *


def download_stats():
    for i, dump_file in enumerate(STATS_DUMP_FILES):
        path = os.path.join(STATS_DUMP_DIR, dump_file)

        if os.path.exists(path):
            print(
                '({}/{}) Skipped existing {}'.format(
                    i + 1, len(STATS_DUMP_FILES), path
                )
            )
            continue

        url = os.path.join(STATS_ENDPOINT, dump_file)
        print('({}/{}) {}'.format(i + 1, len(STATS_DUMP_FILES), path))

        # Download the file
        os.makedirs(os.path.dirname(path), exist_ok=True)

        try:
            urllib.request.urlretrieve(url, path)
        except Exception as e:
            print('Skipped:', e, file=sys.stdout)
