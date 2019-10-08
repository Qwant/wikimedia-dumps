#!/usr/bin/env python3
import gzip
import psycopg2
from urllib.request import urlopen

URLS = [
    'https://dumps.wikimedia.org/other/pageviews/2019/2019-10/pageviews-20191001-{:02d}0000.gz'.format(
        i
    )
    for i in range(24)
]

#   ____                      _                 _
#  |  _ \  _____      ___ __ | | ___   __ _  __| |
#  | | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |
#  | |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |
#  |____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|
#

stats = dict()

for url in URLS:
    print("Loading", url, "...")
    resp = urlopen(url)

    for i, line in enumerate(gzip.open(resp)):
        lang, page, views, responses = line.decode().strip().split()
        page = page.replace('_', ' ')

        if lang not in stats:
            stats[lang] = dict()

        if page not in stats[lang]:
            stats[lang][page] = int(views)
        else:
            stats[lang][page] += int(views)

#   _   _           _       _         ____  ____
#  | | | |_ __   __| | __ _| |_ ___  |  _ \| __ )
#  | | | | '_ \ / _` |/ _` | __/ _ \ | | | |  _ \
#  | |_| | |_) | (_| | (_| | ||  __/ | |_| | |_) |
#   \___/| .__/ \__,_|\__,_|\__\___| |____/|____/
#        |_|


POSTGRES_DB = 'gis'
POSTGRES_USER = 'gis'
POSTGRES_PASSWORD = ''
POSTGRES_HOST = '172.18.0.2'
POSTGRES_PORT = 5432

TABLE_NAME = 'wikimedia_stats'
TABLE_CREATE = f'''
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    domain_code         varchar(64),
    page_title          varchar(1024),
    count_views         integer,
    total_response_size integer
);
TRUNCATE {TABLE_NAME};
'''

conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
)

cursor = conn.cursor()
cursor.execute(TABLE_CREATE)

for (i, (lang, pages)) in enumerate(stats.items()):
    for page, views in pages.items():
        cursor.execute(
            f'INSERT INTO {TABLE_NAME} VALUES (%s, %s, %s, %s)',
            (lang, page, views, 0),
        )

    print('Lang {}/{}'.format(i + 1, len(stats)))
    conn.commit()


#  print("Write result")
#  with open("stats.txt", "w") as file:
#      for lang, pages in stats.items():
#          for page, views in pages.items():
#              file.write("{} {} {} 0\n".format(lang, page, views))
