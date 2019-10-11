#!/usr/bin/env python3
import bz2
import csv
import json
import multiprocessing
import re
import sys

from config import *


def has_wikipedia_page(item):
    '''
    Check if a wikidata item has a wikipedia page referenced among the
    selection of languages defined in `WIKIDATA_FILTER_WIKI_LANGUAGE`.
    '''
    if 'sitelinks' not in item:
        return False

    for site in item['sitelinks'].values():
        match = re.search('(\w+)wiki$', site['site'])

        if match and match.group(1) in WIKIDATA_FILTER_WIKI_LANGUAGE:
            return True

    return False


#   ___                     _   _
#  |_ _|_ __  ___  ___ _ __| |_(_) ___  _ __
#   | || '_ \/ __|/ _ \ '__| __| |/ _ \| '_ \
#   | || | | \__ \  __/ |  | |_| | (_) | | | |
#  |___|_| |_|___/\___|_|   \__|_|\___/|_| |_|
#

# Init cache and write titles to outputs
proc_cache = dict()

with open(WIKIDATA_SITELINKS_FILE, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(('id', 'site', 'language', 'title'))

with open(WIKIDATA_LABELS_FILE, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(('title', 'language', 'value'))


def flush_cache(process_name, filename, force=False):
    '''Flush the cache if required'''
    if force or len(proc_cache[process_name][filename]) > 10 ** 3:
        with open(filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(proc_cache[process_name][filename])
            proc_cache[process_name][filename].clear()


def process_line(line):
    '''
    Process a line from Wikidata's dump in its raw format.
    Update the cache with eventual new line to insert in output files.
    '''
    global processed
    process_name = multiprocessing.current_process().name

    #  Init local caches
    if process_name not in proc_cache:
        proc_cache[process_name] = {
            WIKIDATA_LABELS_FILE: [],
            WIKIDATA_SITELINKS_FILE: [],
        }

    try:
        item = json.loads(line.decode().strip()[:-1])
    except json.decoder.JSONDecodeError as e:
        print('Error while decoding JSON:', e, file=sys.stderr)
        print(line, file=sys.stderr)
        return

    if not has_wikipedia_page(item):
        return

    # Fetch sitelinks
    for site in item['sitelinks'].values():
        match = re.search('(\w+)wiki$', site['site'])

        if not match or match.group(1) not in WIKIDATA_FILTER_WIKI_LANGUAGE:
            continue

        proc_cache[process_name][WIKIDATA_SITELINKS_FILE].append(
            (item['id'], 'wiki', match.group(1), site['title'])
        )

    # Fetch labels
    for label in item['labels'].values():
        if label['language'] not in WIKIDATA_LABEL_LANGUAGES:
            continue

        proc_cache[process_name][WIKIDATA_LABELS_FILE].append(
            (item['id'], label['language'], label['value'])
        )

    # Flush caches
    flush_cache(process_name, WIKIDATA_LABELS_FILE)
    flush_cache(process_name, WIKIDATA_SITELINKS_FILE)


# Concurent insertion
pool = multiprocessing.Pool()

with bz2.open('wikidata.json.bz2', 'r') as wikidata:
    for count, line in enumerate(wikidata):
        pool.apply_async(process_line, (line,))

pool.close()
pool.join()

# Flush what remains of caches
for process_name in proc_cache:
    flush_cache(process_name, WIKIDATA_LABELS_FILE, force=True)
    flush_cache(process_name, WIKIDATA_SITELINKS_FILE, force=True)
