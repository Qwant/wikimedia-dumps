#!/usr/bin/env python3
import csv
import gzip
import multiprocessing
import os
import sys
from collections import defaultdict

import config
from utils import timeperiod, wikimedia_stats_dump_path


def load_file(input_filename):
    """
    Load stats for an input file into a dictionary: dict[lang][page] contains
    the count of views of `page` for the language `lang`.
    """
    stats = {site: defaultdict(int) for site in config.STATS_SITES}

    try:
        input_file = gzip.open(input_filename, 'rt')
    except FileNotFoundError as e:
        print(
            'Skipped unexisting file',
            input_filename,
            'consider using the `--download` parameter',
            file=sys.stderr,
        )
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


def load_stats():
    files = [
        os.path.join(
            config.STATS_DUMP_DIR,
            wikimedia_stats_dump_path(day.year, day.month, day.day, hour),
        )
        for day in timeperiod(
            config.STATS_PERIOD_START, config.STATS_PERIOD_END
        )
        for hour in range(24)
    ]

    stats = {site: defaultdict(int) for site in config.STATS_SITES}

    # Keep one free CPU core to help the main process keeping up with the
    # collection step.
    #
    #  NOTE: If this becomes a real issue a fine way to fix this would be to
    #        distribute the collection step into the loading tasks by using a
    #        global lock on the computed structure.
    pool = multiprocessing.Pool(max(1, multiprocessing.cpu_count() - 1))

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

    return stats


def load_dump_stats(output_file):
    stats = load_stats()

    with gzip.open(output_file, 'wt') as f:
        writer = csv.writer(f)
        writer.writerow(('lang', 'title', 'views'))

        for i, (lang, pages) in enumerate(stats.items()):
            print('Writing lang {}/{}: {}'.format(i + 1, len(stats), lang))

            for page, views in pages.items():
                writer.writerow((lang, page, views))
