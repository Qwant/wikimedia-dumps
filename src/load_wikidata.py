#!/usr/bin/env python3
import bz2
import csv
import gzip
import json
import multiprocessing
import re
import sys

import config


def has_wikipedia_page(item):
    '''
    Check if a wikidata item has a wikipedia page referenced among the
    selection of languages defined in `WIKIDATA_FILTER_WIKI_LANGUAGE`.
    '''
    if 'sitelinks' not in item:
        return False

    for site in item['sitelinks'].values():
        match = re.search(r'(\w+)wiki$', site['site'])

        if match and match.group(1) in config.WIKIDATA_FILTER_WIKI_LANGUAGE:
            return True

    return False


def process_line(line):
    '''
    Process a line from Wikidata's dump in its raw format.
    Update the cache with eventual new line to insert in output files.
    '''
    process_name = multiprocessing.current_process().name

    try:
        item = json.loads(line.decode().strip().rstrip(','))
    except json.decoder.JSONDecodeError as e:
        print('Error while decoding JSON:', e, file=sys.stderr)
        print(line, file=sys.stderr)
        return [], []

    if not has_wikipedia_page(item):
        return [], []

    # Fetch sitelinks
    sitelinks = []

    for site in item['sitelinks'].values():
        match = re.search(r'(\w+)wiki$', site['site'])

        if (
            not match
            or match.group(1) not in config.WIKIDATA_FILTER_WIKI_LANGUAGE
        ):
            continue

        sitelinks.append((item['id'], 'wiki', match.group(1), site['title']))

    # Fetch labels
    labels = []

    for label in item['labels'].values():
        if label['language'] not in config.WIKIDATA_LABEL_LANGUAGES:
            continue

        labels.append((item['id'], label['language'], label['value']))

    return sitelinks, labels


def load_wikidata(dump_filename, sitelinks_filename, labels_filename):
    # Open output files
    links_file = gzip.open(sitelinks_filename, 'wt')
    links_writer = csv.writer(links_file)
    links_writer.writerow(('id', 'site', 'language', 'title'))

    labels_file = gzip.open(labels_filename, 'wt')
    labels_writer = csv.writer(labels_file)
    labels_writer.writerow(('title', 'language', 'value'))

    def apply_output(links, labels):
        links_writer.writerows(links)
        labels_writer.writerows(labels)

    # Concurent insertion
    pool = multiprocessing.Pool()

    with bz2.open(dump_filename, 'r') as wikidata:
        for line in wikidata:

            pool.apply_async(
                process_line,
                (line, sitelinks_filename, labels_filename),
                callback=lambda lines: apply_output(*lines) if lines else (),
            )

    pool.close()
    pool.join()

    links_file.close()
    labels_file.close()
