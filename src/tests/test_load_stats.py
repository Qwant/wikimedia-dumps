import csv
import gzip
import os
from datetime import date
from shutil import copy

import pytest

import config
from load_stats import load_file, load_stats, load_dump_stats
from utils import wikimedia_stats_dump_path


@pytest.fixture(scope="session")
def dump_dir(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp('dumps')

    with gzip.open(tmpdir.join('test1.gz'), 'wt') as f:
        print(
            'fr Albert_Einstein 10 0',
            'en Albert_Einstein 15 0',
            'en Michael_Jackson 85 0',
            'fr Michael_Jackson 50 0',
            sep='\n',
            file=f,
        )

    with gzip.open(tmpdir.join('test2.gz'), 'wt') as f:
        print(
            'en Michael_Jackson 80 0',
            'fr Michael_Jackson 55 0',
            'en Eiffel_Tower 50 0',
            'fr Tour_Eiffel 65 0',
            'es Torre_Eiffel 55 0',
            sep='\n',
            file=f,
        )

    with gzip.open(tmpdir.join('test3.gz'), 'wt') as f:
        print(
            'fr Michael_Jackson 55 0',
            'fr Badly_formatted ? 10 0',
            'fr Albert_Einstein 10 0',
            sep='\n',
            file=f,
        )

    # Reorganise files as the usual hierachy tree
    os.makedirs(tmpdir.join('2019/2019-01'))
    copy(
        tmpdir.join('test1.gz'),
        tmpdir.join(wikimedia_stats_dump_path(2019, 1, 1, 3)),
    )
    copy(
        tmpdir.join('test2.gz'),
        tmpdir.join(wikimedia_stats_dump_path(2019, 1, 1, 6)),
    )

    return tmpdir


@pytest.fixture(autouse=True)
def init_test_config(dump_dir):
    config.STATS_DUMP_DIR = dump_dir
    config.STATS_PERIOD_START = date(2019, 1, 1)
    config.STATS_PERIOD_END = date(2019, 1, 2)
    config.STATS_SITES = ['fr', 'en', 'es']


def test_load_file(dump_dir):
    config.STATS_SITES = ['fr']
    stats = load_file(os.path.join(dump_dir, 'test1.gz'))
    print(os.path.join(dump_dir, 'test1.gz'))

    assert stats.keys() == {'fr'}
    assert stats['fr']['Albert Einstein'] == 10
    assert stats['fr']['Michael Jackson'] == 50


def test_load_unexisting_file(dump_dir):
    stats = load_file(os.path.join(dump_dir, 'this_is_a_fake_file.gz'))
    assert all(not stats[lang] for lang in stats)


def test_load_errored_file(dump_dir):
    stats = load_file(os.path.join(dump_dir, 'test3.gz'))

    assert stats['fr']['Michael Jackson'] == 55
    assert stats['fr']['Albert Einstein'] == 10


def test_filter_sites(dump_dir):
    config.STATS_SITES = []
    stats = load_stats()
    assert all(not stats[lang] for lang in stats)

    config.STATS_SITES = ['es']
    stats = load_stats()
    assert stats.keys() == {'es'}

    config.STATS_SITES = ['fr', 'en', 'es']
    stats = load_stats()
    assert stats.keys() == {'fr', 'en', 'es'}


def test_load_stats(dump_dir):
    config.STATS_SITES = ['fr', 'en', 'es']
    stats = load_stats()

    assert stats.keys() == {'fr', 'en', 'es'}
    assert stats['es']['Torre Eiffel'] == 55
    assert stats['fr']['Albert Einstein'] == 10
    assert stats['en']['Michael Jackson'] == 85 + 80
    assert stats['fr']['Michael Jackson'] == 50 + 55


def test_load_dump_file(dump_dir):
    config.STATS_SITES = ['fr', 'en']
    output_file = os.path.join(dump_dir, 'output.gz')
    load_dump_stats(output_file)

    # Compare CSV content with actual result of load_stats
    stats = load_stats()

    with gzip.open(output_file, 'rt') as f:
        for lang, title, views in list(csv.reader(f))[1:]:
            assert stats[lang][title] == int(views)
            del stats[lang][title]

    assert all(not stats[lang] for lang in stats)
