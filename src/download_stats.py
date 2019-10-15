#!/usr/bin/env python3
import os
import sys
import urllib.request

import config


def download_stats():
    for i, dump_file in enumerate(config.STATS_DUMP_FILES):
        path = os.path.join(config.STATS_DUMP_DIR, dump_file)

        if os.path.exists(path):
            print(
                '({}/{}) Skipped existing {}'.format(
                    i + 1, len(config.STATS_DUMP_FILES), path
                )
            )
            continue

        url = os.path.join(config.STATS_ENDPOINT, dump_file)
        print('({}/{}) {}'.format(i + 1, len(config.STATS_DUMP_FILES), path))

        # Download the file
        os.makedirs(os.path.dirname(path), exist_ok=True)

        try:
            urllib.request.urlretrieve(url, path)
        except Exception as e:
            print('Skipped:', e, file=sys.stdout)
