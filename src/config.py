from datetime import date, timedelta

# Wikimedia dump server only allows for a limited amount of per-ip connections
# as defined here: https://dumps.wikimedia.org/
#
# NOTE: in practice the actual limitation appears to be set to 3
WIKIMEDIA_PARALLEL_DOWNLOADS = 2

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

# Base URL to download dumps.
#
# The official wikimedia endpoint can be found there:
#   https://dumps.wikimedia.org/other/pageviews
# However, you may prefer using unofficial mirrors with higher access
# limitations, a list of mirrors is available here:
#    https://dumps.wikimedia.org/mirrors.html
STATS_ENDPOINT = 'https://ftp.acc.umu.se/mirror/wikimedia.org/other/pageviews/'

# Period of time to load dumps from (end excluded)
STATS_PERIOD_START = date.today() - timedelta(days=90)
STATS_PERIOD_END = date.today()

# Sites we want statistics for
STATS_SITES = ['fr', 'en', 'de']
