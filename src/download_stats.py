#!/usr/bin/env python3
import multiprocessing
import os
import urllib.request

import config


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

    for i, msg in enumerate(
        pool.imap(apply_download, config.STATS_DUMP_FILES)
    ):
        print('({}/{})'.format(i + 1, len(config.STATS_DUMP_FILES)), msg)

    pool.close()
    pool.join()
