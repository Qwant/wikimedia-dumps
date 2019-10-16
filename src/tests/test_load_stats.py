import csv
import gzip
import os
import pytest

import config
from load_stats import load_file, load_stats, load_dump_stats


@pytest.fixture(autouse=True)
def init_dump_files(tmpdir):
    with gzip.open(os.path.join(tmpdir, 'test1.gz'), 'wt') as f:
        print(
            'fr Albert_Einstein 10 0',
            'en Albert_Einstein 15 0',
            'en Michael_Jackson 85 0',
            'fr Michael_Jackson 50 0',
            sep='\n',
            file=f,
        )

    with gzip.open(os.path.join(tmpdir, 'test2.gz'), 'wt') as f:
        print(
            'en Michael_Jackson 80 0',
            'fr Michael_Jackson 55 0',
            'en Eiffel_Tower 50 0',
            'fr Tour_Eiffel 65 0',
            'es Torre_Eiffel 55 0',
            sep='\n',
            file=f,
        )

    with gzip.open(os.path.join(tmpdir, 'test3.gz'), 'wt') as f:
        print(
            'fr Michael_Jackson 55 0',
            'fr Badly_formatted ? 10 0',
            'fr Albert_Einstein 10 0',
            sep='\n',
            file=f,
        )


@pytest.fixture(autouse=True)
def init_test_config(tmpdir):
    config.STATS_DUMP_DIR = tmpdir
    config.STATS_DUMP_FILES = ['test1.gz', 'test2.gz']
    config.STATS_SITES = ['fr', 'en', 'es']


def test_load_file(tmpdir):
    config.STATS_SITES = ['fr']
    stats = load_file(os.path.join(tmpdir, 'test1.gz'))

    assert stats.keys() == {'fr'}
    assert stats['fr']['Albert Einstein'] == 10
    assert stats['fr']['Michael Jackson'] == 50


def test_load_unexisting_file(tmpdir):
    stats = load_file(os.path.join(tmpdir, 'this_is_a_fake_file.gz'))
    assert all(not stats[lang] for lang in stats)


def test_load_errored_file(tmpdir):
    stats = load_file(os.path.join(tmpdir, 'test3.gz'))

    assert stats['fr']['Michael Jackson'] == 55
    assert stats['fr']['Albert Einstein'] == 10


def test_filter_sites(tmpdir):
    config.STATS_SITES = []
    stats = load_stats()
    assert all(not stats[lang] for lang in stats)

    config.STATS_SITES = ['es']
    stats = load_stats()
    assert stats.keys() == {'es'}

    config.STATS_SITES = ['fr', 'en', 'es']
    stats = load_stats()
    assert stats.keys() == {'fr', 'en', 'es'}


def test_load_stats(tmpdir):
    config.STATS_DUMP_FILES = ['test1.gz', 'test2.gz']
    config.STATS_SITES = ['fr', 'en', 'es']

    stats = load_stats()

    assert stats.keys() == {'fr', 'en', 'es'}
    assert stats['es']['Torre Eiffel'] == 55
    assert stats['fr']['Albert Einstein'] == 10
    assert stats['en']['Michael Jackson'] == 85 + 80
    assert stats['fr']['Michael Jackson'] == 50 + 55


def test_load_dump_file(tmpdir):
    config.STATS_DUMP_FILES = ['test1.gz', 'test2.gz']
    config.STATS_SITES = ['fr', 'en']

    output_file = os.path.join(tmpdir, 'output.gz')
    load_dump_stats(output_file)

    # Compare CSV content with actual result of load_stats
    stats = load_stats()

    with gzip.open(output_file, 'rt') as f:
        for lang, title, views in list(csv.reader(f))[1:]:
            assert stats[lang][title] == int(views)
            del stats[lang][title]

    assert all(not stats[lang] for lang in stats)
