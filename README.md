Wikimedia Dumps
===============

Filter and restructure data from Wikimedia sources to prepare use for
QwantMaps.

Running
-------

### Loading Wikidata dumps

You first need to download a complete Wikidata dump from
[Wikimedia](https://dumps.wikimedia.org/wikidatawiki/entities/) in JSON format.

Then you can generate CSV data for site links and labels:

```bash
src/main.py load-wikidata --dump latest-all.json.bz2
```

### Loading stats dumps

You can download and extract data from Wikimedia statistics with a single
command:

```bash
# Omit `--download` if you already downloaded raw dumps
src/main.py load-stats --download
```

Configuration
-------------

`src/config.py` holds configuration for the languages to include in the dumps
and the list of the files to load for statistics.
