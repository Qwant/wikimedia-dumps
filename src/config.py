# Wikimedia dump server only allows for a limited amount of per-ip connections
# as defined here: https://dumps.wikimedia.org/
#
# NOTE: in practice the actual limitation appears to be set to 3
WIKIDATA_PARALLEL_DOWNLOADS = 2

#  __        ___ _    _ ____        _
#  \ \      / (_) | _(_)  _ \  __ _| |_ __ _
#   \ \ /\ / /| | |/ / | | | |/ _` | __/ _` |
#    \ V  V / | |   <| | |_| | (_| | || (_| |
#     \_/\_/  |_|_|\_\_|____/ \__,_|\__\__,_|
#

# Only import items that have a Wikipedia page for one of these languages
WIKIDATA_FILTER_WIKI_LANGUAGE = ['fr', 'en', 'de']

# Languages we want to import for Wikipedia pages
WIKIDATA_WIKI_LANGUAGE = WIKIDATA_FILTER_WIKI_LANGUAGE

# Languages we want translations for
WIKIDATA_LABEL_LANGUAGES = WIKIDATA_FILTER_WIKI_LANGUAGE

#  ____  _        _   _     _   _
# / ___|| |_ __ _| |_(_)___| |_(_) ___ ___
# \___ \| __/ _` | __| / __| __| |/ __/ __|
#  ___) | || (_| | |_| \__ \ |_| | (__\__ \
# |____/ \__\__,_|\__|_|___/\__|_|\___|___/
#

# Directory where to download dumps
STATS_DUMP_DIR = 'dumps/stats'

# Base URL to download dumps
STATS_ENDPOINT = 'https://dumps.wikimedia.org/other/pageviews'

# Files to download and load
STATS_DUMP_FILES = [
    '{year:04d}/{year:04d}-{month:02d}/'
    'pageviews-{year:04d}{month:02d}{day:02d}-{hour:02d}0000.gz'.format(
        year=2019, month=month, day=day, hour=hour
    )
    for month in range(3, 4)
    for day in range(1, 32)
    for hour in range(24)
]

# Sites we want statistics for
STATS_SITES = ['fr', 'en', 'de']
