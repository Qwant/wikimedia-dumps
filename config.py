# Postgress connection
POSTGRES_DB = 'gis'
POSTGRES_USER = 'gis'
POSTGRES_PASSWORD = ''
POSTGRES_HOST = '172.18.0.2'
POSTGRES_PORT = 5432

# Table names
TABLE_WIKIDATA_SITELINKS = 'wikidata_sitelinks'
TABLE_WIKIDATA_LABELS = 'wikidata_labels'

# Only import items that have a Wikipedia page for one of these languages
WIKIDATA_FILTER_WIKI_LANGUAGE = ['fr', 'en', 'de']

# Languages we want translations for
WIKIDATA_LABEL_LANGUAGES = ['fr', 'en', 'de', 'ja']
