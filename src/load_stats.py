#!/usr/bin/env python3
import csv
import gzip
import multiprocessing
import os
import sys
from collections import defaultdict

import config


def load_file(input_filename: str) -> dict:
    """
    Load stats for an input file into a dictionary: dict[lang][page] contains
    the count of views of `page` for the language `lang`.
    """
    stats = {site: defaultdict(int) for site in config.STATS_SITES}

    try:
        input_file = gzip.open(input_filename, 'rt')
    except FileNotFoundError as e:
        print('Skipped unexisting file', input_filename, file=sys.stderr)
        return dict()

    for i_line, line in enumerate(input_file):
        try:
            #  `responses` is ignored as it appears to always be 0
            site, page, views, _responses = line.strip().split()
        except Exception as e:
            print(
                'Error at {}:{},'.format(input_filename, i_line),
                e,
                file=sys.stderr,
            )
            continue

        page = page.replace('_', ' ')

        if site not in config.STATS_SITES:
            continue

        stats[site][page] += int(views)

    input_file.close()
    return stats


def load_stats(output_file):
    files = list(
        map(
            lambda dump: os.path.join(config.STATS_DUMP_DIR, dump),
            config.STATS_DUMP_FILES,
        )
    )

    #   ____                   __     ___
    #  / ___| _   _ _ __ ___   \ \   / (_) _____      _____
    #  \___ \| | | | '_ ` _ \   \ \ / /| |/ _ \ \ /\ / / __|
    #   ___) | |_| | | | | | |   \ V / | |  __/\ V  V /\__ \
    #  |____/ \__,_|_| |_| |_|    \_/  |_|\___| \_/\_/ |___/
    #

    stats = {site: defaultdict(int) for site in config.STATS_SITES}
    pool = multiprocessing.Pool()

    for i_file, file_stats in enumerate(pool.imap(load_file, files)):
        print(
            "({}/{}) {}: updating {} items".format(
                i_file + 1,
                len(files),
                files[i_file],
                sum(len(lang) for lang in file_stats.values()),
            )
        )

        for lang, pages in file_stats.items():
            for page, views in pages.items():
                stats[lang][page] += views

    pool.close()
    pool.join()

    #    ___        _               _
    #   / _ \ _   _| |_ _ __  _   _| |_
    #  | | | | | | | __| '_ \| | | | __|
    #  | |_| | |_| | |_| |_) | |_| | |_
    #   \___/ \__,_|\__| .__/ \__,_|\__|
    #                  |_|

    with gzip.open(output_file, 'wt') as f:
        writer = csv.writer(f)
        writer.writerow(('lang', 'title', 'views'))

        for i, (lang, pages) in enumerate(stats.items()):
            print('Writing lang {}/{}: {}'.format(i + 1, len(stats), lang))

            for page, views in pages.items():
                writer.writerow((lang, page, views))
