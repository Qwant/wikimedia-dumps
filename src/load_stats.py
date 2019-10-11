#!/usr/bin/env python3
import csv
import gzip
import os
import sys

from config import *

#   ____                   __     ___
#  / ___| _   _ _ __ ___   \ \   / (_) _____      _____
#  \___ \| | | | '_ ` _ \   \ \ / /| |/ _ \ \ /\ / / __|
#   ___) | |_| | | | | | |   \ V / | |  __/\ V  V /\__ \
#  |____/ \__,_|_| |_| |_|    \_/  |_|\___| \_/\_/ |___/
#

stats = {site: dict() for site in STATS_SITES}

for i, dump_file in enumerate(STATS_DUMP_FILES):
    path = os.path.join(STATS_DUMP_DIR, dump_file)
    print('({}/{}) {}'.format(i + 1, len(STATS_DUMP_FILES), path))

    for i, line in enumerate(gzip.open(path)):
        try:
            site, page, views, responses = line.decode().strip().split()
        except Exception as e:
            print('Error at line', i, ':', e, file=sys.stderr)

        page = page.replace('_', ' ')

        if site not in STATS_SITES:
            continue

        if page not in stats[site]:
            stats[site][page] = int(views)
        else:
            stats[site][page] += int(views)

#    ___        _               _
#   / _ \ _   _| |_ _ __  _   _| |_
#  | | | | | | | __| '_ \| | | | __|
#  | |_| | |_| | |_| |_) | |_| | |_
#   \___/ \__,_|\__| .__/ \__,_|\__|
#                  |_|

# Insert rows into the DB
with open(STATS_FILE, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(('lang', 'title', 'views'))

    for i, (lang, pages) in enumerate(stats.items()):
        print('Lang {}/{}: {}'.format(i + 1, len(stats), lang))

        for page, views in pages.items():
            writer.writerow((lang, page, views))
