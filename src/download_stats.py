#!/usr/bin/env python3
import multiprocessing
import os
import urllib.request

import config
from utils import timeperiod, wikimedia_stats_dump_path


def apply_download(dump_file):
    path = os.path.join(config.STATS_DUMP_DIR, dump_file)
    url = os.path.join(config.STATS_ENDPOINT, dump_file)

    if os.path.exists(path):
        return 'skipped existing {}'.format(path)

    # Download the file
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        urllib.request.urlretrieve(url, path)
    except Exception as e:
        return 'skipped {}: {}'.format(path, e)

    return '{} done'.format(path)


def download_stats():
    pool = multiprocessing.Pool(config.WIKIMEDIA_PARALLEL_DOWNLOADS)

    dump_files = [
        wikimedia_stats_dump_path(day.year, day.month, day.day, hour)
        for day in timeperiod(
            config.STATS_PERIOD_START, config.STATS_PERIOD_END
        )
        for hour in range(24)
    ]

    for i, msg in enumerate(pool.imap(apply_download, dump_files)):
        print('({}/{})'.format(i + 1, len(dump_files)), msg)

    pool.close()
    pool.join()
