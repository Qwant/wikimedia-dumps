#!/usr/bin/env python3
import gzip
import os
import psycopg2
import sys

from config import *

#   ____                   __     ___
#  / ___| _   _ _ __ ___   \ \   / (_) _____      _____
#  \___ \| | | | '_ ` _ \   \ \ / /| |/ _ \ \ /\ / / __|
#   ___) | |_| | | | | | |   \ V / | |  __/\ V  V /\__ \
#  |____/ \__,_|_| |_| |_|    \_/  |_|\___| \_/\_/ |___/
#

stats = {site: dict() for site in STATISTICS_SITES}

for i, dump_file in enumerate(STATS_FILES):
    path = os.path.join(STATS_DUMP_DIR, dump_file)
    print('({}/{}) {}'.format(i + 1, len(STATS_FILES), path))

    for i, line in enumerate(gzip.open(path)):
        try:
            site, page, views, responses = line.decode().strip().split()
        except Exception as e:
            print('Error at line', i, ':', e, file=sys.stderr)

        page = page.replace('_', ' ')

        if site not in STATISTICS_SITES:
            continue

        if page not in stats[site]:
            stats[site][page] = int(views)
        else:
            stats[site][page] += int(views)

#   _   _           _       _         ____  ____
#  | | | |_ __   __| | __ _| |_ ___  |  _ \| __ )
#  | | | | '_ \ / _` |/ _` | __/ _ \ | | | |  _ \
#  | |_| | |_) | (_| | (_| | ||  __/ | |_| | |_) |
#   \___/| .__/ \__,_|\__,_|\__\___| |____/|____/
#        |_|

SQL_CREATE_STATS_TABLE = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_STATISTICS} (
        domain_code         varchar(64),
        page_title          varchar(1024),
        count_views         integer,
        total_response_size integer,
        UNIQUE(domain_code, page_title)
    );
'''

connexion = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
)
cursor = connexion.cursor()
cursor.execute(SQL_CREATE_STATS_TABLE)

# Insert rows into the DB
for i, (lang, pages) in enumerate(stats.items()):
    print('Lang {}/{}'.format(i + 1, len(stats)))

    for page, views in pages.items():
        cursor.execute(
            f'INSERT INTO {TABLE_STATISTICS}'
            ' VALUES (%s, %s, %s, %s)'
            ' ON CONFLICT(domain_code, page_title)'
            ' DO UPDATE SET count_views = %s',
            (lang, page, views, 0, views),
        )

    connexion.commit()
