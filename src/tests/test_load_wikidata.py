import bz2
import csv
import gzip
import json
import os
import pytest

import config
from load_wikidata import has_wikipedia_page, process_line, load_wikidata

WIKIDATA = [
    {
        'pageid': 138,
        'ns': 0,
        'title': 'Q42',
        'lastrevid': 1032477235,
        'modified': '2019-10-15T13:06:58Z',
        'type': 'item',
        'id': 'Q42',
        'labels': {
            'fr': {'language': 'fr', 'value': 'Douglas Adams l\'anglais'},
            'en': {'language': 'en', 'value': 'Douglas Adams the British'},
            'en-gb': {'language': 'en-gb', 'value': 'Douglas Adams'},
            'de': {'language': 'de', 'value': 'Douglas Adams'},
            'ru': {'language': 'ru', 'value': 'Дуглас Адамс'},
        },
        'descriptions': {},
        'aliases': {},
        'claims': {},
        'sitelinks': {
            'frwiki': {
                'site': 'frwiki',
                'title': 'Douglas Adams',
                'badges': [],
                'url': 'https://fr.wikipedia.org/wiki/Douglas_Adams',
            },
            'enwiki': {
                'site': 'enwiki',
                'title': 'Douglas Adams',
                'badges': [],
                'url': 'https://en.wikipedia.org/wiki/Douglas_Adams',
            },
            'enwikiquote': {
                'site': 'enwiki',
                'title': 'Douglas Adams',
                'badges': [],
                'url': 'https://en.wikipedia.org/wiki/Douglas_Adams',
            },
        },
    },
    {
        'pageid': 43698155,
        'ns': 0,
        'title': 'Q42424242',
        'lastrevid': 972500947,
        'modified': '2019-07-01T16:40:21Z',
        'type': 'item',
        'id': 'Q42424242',
        'labels': {
            'en': {
                'language': 'en',
                'value': 'church in Baranów Sandomierski, Poland',
            },
            'ru': {
                'language': 'ru',
                'value': 'kościół w Baranowie Sandomierskim',
            },
        },
        'descriptions': {},
        'aliases': {},
        'claims': {},
        'sitelinks': {
            'commonswiki': {
                'site': 'commons',
                'title': 'Category:Church of St. John the Baptist, Baranów Sandomierski',
                'badges': [],
                'url': 'https://commons.wikimedia.org/wiki/Category:Church_of_St._John_the_Baptist,_Baran%C3%B3w_Sandomierski',
            },
            'plwiki': {
                'site': 'plwiki',
                'title': 'Kościół Ścięcia św. Jana Chrzciciela w Baranowie Sandomierskim',
                'badges': [],
                'url': 'https://pl.wikipedia.org/wiki/Ko%C5%9Bci%C3%B3%C5%82_%C5%9Aci%C4%99cia_%C5%9Bw._Jana_Chrzciciela_w_Baranowie_Sandomierskim',
            },
        },
    },
    {
        'pageid': 257,
        'ns': 0,
        'title': 'Q123',
        'lastrevid': 1033128008,
        'modified': '2019-10-16T09:26:13Z',
        'type': 'item',
        'id': 'Q123',
        'labels': {'en': {'language': 'en', 'value': 'September'}},
        'descriptions': {},
        'aliases': {},
        'claims': {},
        'sitelinks': {
            'enwiki': {
                'site': 'enwiki',
                'title': 'September',
                'badges': [],
                'url': 'https://en.wikipedia.org/wiki/September',
            }
        },
    },
]


@pytest.fixture(autouse=True)
def init_dump_files(tmpdir):
    with bz2.open(os.path.join(tmpdir, 'wikidata.json.bz2'), 'wt') as f:
        f.write('[\n' + ',\n'.join(map(json.dumps, WIKIDATA)) + '\n]')


def test_init_dump_files(tmpdir):
    with bz2.open(os.path.join(tmpdir, 'wikidata.json.bz2'), 'rt') as f:
        assert json.loads(f.read())


@pytest.fixture(autouse=True)
def init_test_config():
    config.WIKIDATA_FILTER_WIKI_LANGUAGE = ['fr', 'en', 'de']
    config.WIKIDATA_WIKI_LANGUAGE = ['fr', 'en', 'de']
    config.WIKIDATA_LABEL_LANGUAGES = ['fr', 'en', 'de']


def test_has_wikipedia_page():
    assert has_wikipedia_page(WIKIDATA[0])
    assert not has_wikipedia_page(WIKIDATA[1])


def test_process_line():
    sitelinks, labels = process_line(json.dumps(WIKIDATA[1]))
    assert not sitelinks and not labels

    sitelinks, labels = process_line(json.dumps(WIKIDATA[0]))
    assert set(sitelinks) == {
        ('Q42', 'wiki', 'fr', 'Douglas Adams'),
        ('Q42', 'wiki', 'en', 'Douglas Adams'),
    }
    assert set(labels) == {
        ('Q42', 'fr', 'Douglas Adams l\'anglais'),
        ('Q42', 'en', 'Douglas Adams the British'),
        ('Q42', 'de', 'Douglas Adams'),
    }


def test_load_wikidata(tmpdir):
    dump_path = os.path.join(tmpdir, 'wikidata.json.bz2')
    sitelinks_path = os.path.join(tmpdir, 'sitelinks.csv.gz')
    labels_path = os.path.join(tmpdir, 'labels.csv.gz')

    load_wikidata(dump_path, sitelinks_path, labels_path)

    with gzip.open(sitelinks_path, 'rt') as f:
        print(f.read())

    with gzip.open(sitelinks_path, 'rt') as f:
        sitelinks = list(tuple(line) for line in csv.reader(f))[1:]

    with gzip.open(labels_path, 'rt') as f:
        labels = list(tuple(line) for line in csv.reader(f))[1:]

    assert set(sitelinks) == {
        ('Q42', 'wiki', 'fr', 'Douglas Adams'),
        ('Q42', 'wiki', 'en', 'Douglas Adams'),
        ('Q123', 'wiki', 'en', 'September'),
    }
    assert set(labels) == {
        ('Q42', 'fr', 'Douglas Adams l\'anglais'),
        ('Q42', 'en', 'Douglas Adams the British'),
        ('Q42', 'de', 'Douglas Adams'),
        ('Q123', 'en', 'September'),
    }
