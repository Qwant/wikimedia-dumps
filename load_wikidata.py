#!/usr/bin/env python3
import bz2
import json
import multiprocessing
import psycopg2
import psycopg2.pool
import re
import sys

from config import *


SQL_CREATE_SITELINK_TABLE = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_WIKIDATA_SITELINKS} (
        id      varchar(64)     NOT NULL,
        site    varchar(256)    NOT NULL,
        lang    varchar(16),
        title   varchar(256)    NOT NULL,
        UNIQUE(id, site, lang)
    );
'''

SQL_CREATE_LABEL_TABLE = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_WIKIDATA_LABELS} (
        id      varchar(64)     NOT NULL,
        lang    varchar(16)     NOT NULL,
        value   varchar(256)    NOT NULL,
        UNIQUE(id, lang)
    );
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

connexion = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
)

# Create new tables
cursor = connexion.cursor()
cursor.execute(SQL_CREATE_SITELINK_TABLE)
cursor.execute(SQL_CREATE_LABEL_TABLE)
cursor.close()

connexion.commit()
connexion.close()

#   ___                     _   _
#  |_ _|_ __  ___  ___ _ __| |_(_) ___  _ __
#   | || '_ \/ __|/ _ \ '__| __| |/ _ \| '_ \
#   | || | | \__ \  __/ |  | |_| | (_) | | | |
#  |___|_| |_|___/\___|_|   \__|_|\___/|_| |_|
#

processed = 0
log_files = dict()
connexions = dict()


def process_line(line):
    '''
    Process a line from Wikidata's dump in its raw format.
    Return a list of SQL requests to execute.
    '''
    global processed
    process_name = multiprocessing.current_process().name

    try:
        item = json.loads(line.decode().strip()[:-1])
    except json.decoder.JSONDecodeError as e:
        print('Error while decoding JSON:', e, file=sys.stderr)
        print(line, file=sys.stderr)
        return

    #  Manualy connect to DB for current process
    if process_name not in connexions:
        connexions[process_name] = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
        )

    # Decide or not to add the field in the database
    rejected_filename = 'rejected_' + process_name + '.txt'
    accepted_filename = 'accepted_' + process_name + '.txt'

    if rejected_filename not in log_files:
        log_files[rejected_filename] = open(rejected_filename, 'a')
        log_files[accepted_filename] = open(accepted_filename, 'a')

    if not has_wikipedia_page(item):
        print(item['id'], file=log_files[rejected_filename])
        return
    else:
        print(item['id'], file=log_files[accepted_filename])

    #  Insertion into the database
    processed += 1
    cursor = connexions[process_name].cursor()

    for site in item['sitelinks'].values():
        match = re.search('(\w+)wiki$', site['site'])

        if not match or match.group(1) not in WIKIDATA_FILTER_WIKI_LANGUAGE:
            continue

        try:
            cursor.execute(
                f'INSERT INTO {TABLE_WIKIDATA_SITELINKS}'
                ' VALUES (%s, %s, %s, %s)'
                ' ON CONFLICT DO NOTHING',
                (item['id'], 'wiki', match.group(1), site['title']),
            )
        except Exception as e:
            print('PSQL Query error:', e, file=sys.stderr)

    for label in item['labels'].values():
        if label['language'] not in WIKIDATA_LABEL_LANGUAGES:
            continue

        try:
            cursor.execute(
                f'INSERT INTO {TABLE_WIKIDATA_LABELS}'
                ' VALUES (%s, %s, %s)'
                ' ON CONFLICT DO NOTHING',
                (item['id'], label['language'], label['value']),
            )
        except Exception as e:
            print('PSQL Query error:', e, file=sys.stderr)

    cursor.close()

    if processed % 1000 == 0:
        connexions[process_name].commit()


#  Concurent insertion
pool = multiprocessing.Pool()

with bz2.open('wikidata.json.bz2', 'r') as wikidata:
    for count, line in enumerate(wikidata):
        pool.apply_async(process_line, (line,))

pool.close()
pool.join()

# Close process connexions and files

for connexion in connexions.values():
    connexion.close()

for f in log_files.values():
    f.close()
