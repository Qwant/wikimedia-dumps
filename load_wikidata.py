#!/usr/bin/env python3
import bz2
import itertools
import json
import psycopg2
import re

POSTGRES_DB = 'gis'
POSTGRES_USER = 'gis'
POSTGRES_PASSWORD = ''
POSTGRES_HOST = '172.18.0.2'
POSTGRES_PORT = 5432

TABLE_NAME = 'osm_poi_point'
SQL_LOAD_IDS = f'''
    SELECT DISTINCT tags->'wikidata' AS id
    FROM {TABLE_NAME}
    WHERE tags ? 'wikidata'
'''


conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
)

cursor = conn.cursor()
cursor.execute(SQL_LOAD_IDS)
wikidata_ids = set(wd_id for wd_id, in cursor)

count = 0

with bz2.open("wikidata.json.bz2", "r") as wikidata:
    for line in wikidata:
        line = line.decode().strip()[:-1]

        try:
            item = json.loads(line)
        except json.decoder.JSONDecodeError as e:
            continue

        if item['id'] not in wikidata_ids:
            continue

        count += 1
        print('---', count)

        #   _
        #  | |    __ _ _ __   __ _ _   _  __ _  __ _  ___
        #  | |   / _` | '_ \ / _` | | | |/ _` |/ _` |/ _ \
        #  | |__| (_| | | | | (_| | |_| | (_| | (_| |  __/
        #  |_____\__,_|_| |_|\__, |\__,_|\__,_|\__, |\___|
        #                    |___/             |___/

        updates = {
            'name:' + label['language']: label['value']
            for label in item['labels'].values()
        }

        #  __        ___ _    _                _ _
        #  \ \      / (_) | _(_)_ __   ___  __| (_) __ _
        #   \ \ /\ / /| | |/ / | '_ \ / _ \/ _` | |/ _` |
        #    \ V  V / | |   <| | |_) |  __/ (_| | | (_| |
        #     \_/\_/  |_|_|\_\_| .__/ \___|\__,_|_|\__,_|
        #                      |_|

        for site in item['sitelinks'].values():
            match = re.search(r'(\w+)wiki', site['site'])

            if match and match.group(1) != 'commons':
                lang = match.group(1)
                updates['wiki:' + lang] = site['title']

        if updates:
            print(updates)
            cursor.execute(
                f'UPDATE {TABLE_NAME} SET tags = tags'
                + '||hstore(%s, %s)' * len(updates)
                + 'WHERE tags->\'wikidata\' = %s',
                list(itertools.chain(*updates.items())) + [item['id']],
            )

        conn.commit()
