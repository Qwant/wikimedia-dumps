#!/usr/bin/env python3
import argparse
import sys

from download_stats import download_stats
from load_stats import load_stats
from load_wikidata import load_wikidata


# Read CLI arguments

parser = argparse.ArgumentParser(
    description='Import datas from various wikidata sources'
)
subparsers = parser.add_subparsers()

# command: load-wikidata

cmd_load_wikidata = subparsers.add_parser(
    'load-wikidata', description='Load a JSON Wikidata dump'
)

cmd_load_wikidata.add_argument(
    '--dump',
    type=str,
    default='wikidata.json.bz2',
    help='A wikidata dump in JSON format: '
    'https://www.wikidata.org/wiki/Wikidata:Database_download',
)
cmd_load_wikidata.add_argument(
    '--output_sitelinks',
    type=str,
    default='sitelinks.csv.gz',
    help='Output file for CSV links datas',
)
cmd_load_wikidata.add_argument(
    '--output_labels',
    type=str,
    default='labels.csv.gz',
    help='Output file for CSV labels datas',
)

cmd_load_wikidata.set_defaults(
    func=lambda args: load_wikidata(
        args.dump, args.output_sitelinks, args.output_labels
    )
)

# command: load-stats

cmd_load_stats = subparsers.add_parser(
    'load-stats', description='Load view statistics about wikimedia sites'
)

cmd_load_stats.add_argument(
    '--output',
    type=str,
    default='stats.csv.gz',
    help='Output file for CSV stats',
)
cmd_load_stats.add_argument(
    '--download',
    action='store_true',
    help='First download stats from files defined in config.py',
)


def start_load_stats(args):
    if args.download:
        download_stats()

    load_stats(args.output)


cmd_load_stats.set_defaults(func=start_load_stats)

args = parser.parse_args(sys.argv[1:])
args.func(args)
