#  __        ___ _    _ ____        _
#  \ \      / (_) | _(_)  _ \  __ _| |_ __ _
#   \ \ /\ / /| | |/ / | | | |/ _` | __/ _` |
#    \ V  V / | |   <| | |_| | (_| | || (_| |
#     \_/\_/  |_|_|\_\_|____/ \__,_|\__\__,_|
#

# Output files
WIKIDATA_SITELINKS_FILE = 'sitelinks.csv'
WIKIDATA_LABELS_FILE = 'labels.csv'


# Only import items that have a Wikipedia page for one of these languages
WIKIDATA_FILTER_WIKI_LANGUAGE = ['fr', 'en', 'de']

# Languages we want to import for Wikipedia pages
WIKIDATA_WIKI_LANGUAGE = WIKIDATA_FILTER_WIKI_LANGUAGE

# Languages we want translations for
WIKIDATA_LABEL_LANGUAGES = ['fr', 'en', 'de', 'ja']

#  ____  _        _   _     _   _
# / ___|| |_ __ _| |_(_)___| |_(_) ___ ___
# \___ \| __/ _` | __| / __| __| |/ __/ __|
#  ___) | || (_| | |_| \__ \ |_| | (__\__ \
# |____/ \__\__,_|\__|_|___/\__|_|\___|___/
#

# Output files
STATS_FILE = 'stats.csv'

# Directory where to download dumps
STATS_DUMP_DIR = 'dumps/stats'

# Base URL to download dumps
STATS_ENDPOINT = 'https://dumps.wikimedia.org/other/pageviews'

# Files to download and load
STATS_DUMP_FILES = [
    '{year:04d}/{year:04d}-{month:02d}/'
    'pageviews-{year:04d}{month:02d}{day:02d}-{hour:02d}0000.gz'.format(
        year=2019, month=9, day=day, hour=hour
    )
    for day in range(1, 30)
    for hour in range(24)
]

# Sites we want statistics for
STATS_SITES = ['fr', 'en', 'de', 'ja']
