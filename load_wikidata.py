#!/usr/bin/env python3
import bz2
import json
import multiprocessing
import psycopg2
import psycopg2.pool
import re

from config import *


SQL_CREATE_SITELINK_TABLE = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_WIKIDATA_SITELINKS} (
        id      varchar(64)     NOT NULL,
        site    varchar(256)    NOT NULL,
        lang    varchar(16),
        title   varchar(256)    NOT NULL,
        UNIQUE(id, site, lang)
    );
    TRUNCATE {TABLE_WIKIDATA_SITELINKS};
'''

SQL_CREATE_LABEL_TABLE = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_WIKIDATA_LABELS} (
        id      varchar(64)     NOT NULL,
        lang    varchar(16)     NOT NULL,
        value   varchar(256)    NOT NULL,
        UNIQUE(id, lang)
    );
    TRUNCATE {TABLE_WIKIDATA_LABELS};
'''


def has_wikipedia_page(item):
    if 'sitelinks' not in item:
        return False

    for site in item['sitelinks'].values():
        match = re.search('(\w+)wiki$', site['site'])

        if match and match.group(1) in WIKIDATA_FILTER_WIKI_LANGUAGE:
            return True

    return False


#  ___       _ _
# |_ _|_ __ (_) |_
#  | || '_ \| | __|
#  | || | | | | |_
# |___|_| |_|_|\__|
#

psql_pool = psycopg2.pool.ThreadedConnectionPool(
    8,
    8,
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
)
connexion = psql_pool.getconn()

# Create new tables
cursor = connexion.cursor()
cursor.execute(SQL_CREATE_SITELINK_TABLE)
cursor.execute(SQL_CREATE_LABEL_TABLE)
cursor.close()
connexion.commit()

#   ___                     _   _
#  |_ _|_ __  ___  ___ _ __| |_(_) ___  _ __
#   | || '_ \/ __|/ _ \ '__| __| |/ _ \| '_ \
#   | || | | \__ \  __/ |  | |_| | (_) | | | |
#  |___|_| |_|___/\___|_|   \__|_|\___/|_| |_|
#

processed = 0


def process_line(line):
    '''
    Process a line from Wikidata's dump in its raw format.
    Return a list of SQL requests to execute.
    '''
    global processed
    process_name = multiprocessing.current_process().name

    line = line.decode().strip()[:-1]

    try:
        item = json.loads(line)
    except json.decoder.JSONDecodeError:
        return

    if not has_wikipedia_page(item):
        return

    processed += 1
    connexion = psql_pool.getconn(key=process_name)
    cursor = connexion.cursor()

    for site in item['sitelinks'].values():
        match = re.search('(\w+)wiki$', site['site'])

        if not match or match.group(1) not in WIKIDATA_FILTER_WIKI_LANGUAGE:
            continue

        a = cursor.execute(
            f'INSERT INTO {TABLE_WIKIDATA_SITELINKS} VALUES (%s, %s, %s, %s)',
            (item['id'], 'wiki', match.group(1), site['title']),
        )

    for label in item['labels'].values():
        if label['language'] not in WIKIDATA_LABEL_LANGUAGES:
            continue

        cursor.execute(
            f'INSERT INTO {TABLE_WIKIDATA_LABELS} VALUES (%s, %s, %s)',
            (item['id'], label['language'], label['value']),
        )

    connexion.commit()

    # Sometime close the connexion to avoid memory leaks
    if processed > 10 ** 3:
        processed = 0
        connexion.close()

    psql_pool.putconn(connexion, key=process_name)


#  Concurent insertion
pool = multiprocessing.Pool()

with bz2.open("wikidata.json.bz2", "r") as wikidata:
    for count, line in enumerate(wikidata):
        pool.apply_async(process_line, (line,))

        if count % 10000 == 0:
            connexion.commit()

connexion.commit()
pool.close()
pool.join()
