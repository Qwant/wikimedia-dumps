#   ____           _                 ____   ___  _
#  |  _ \ ___  ___| |_ __ _ _ __ ___/ ___| / _ \| |
#  | |_) / _ \/ __| __/ _` | '__/ _ \___ \| | | | |
#  |  __/ (_) \__ \ || (_| | | |  __/___) | |_| | |___
#  |_|   \___/|___/\__\__, |_|  \___|____/ \__\_\_____|
#                     |___/

# Postgress connection
POSTGRES_DB = 'gis'
POSTGRES_USER = 'gis'
POSTGRES_PASSWORD = ''
POSTGRES_HOST = '172.18.0.2'
POSTGRES_PORT = 5432

#  __        ___ _    _ ____        _
#  \ \      / (_) | _(_)  _ \  __ _| |_ __ _
#   \ \ /\ / /| | |/ / | | | |/ _` | __/ _` |
#    \ V  V / | |   <| | |_| | (_| | || (_| |
#     \_/\_/  |_|_|\_\_|____/ \__,_|\__\__,_|
#

# Table names
TABLE_WIKIDATA_SITELINKS = 'wikidata_sitelinks'
TABLE_WIKIDATA_LABELS = 'wikidata_labels'

# Only import items that have a Wikipedia page for one of these languages
WIKIDATA_FILTER_WIKI_LANGUAGE = ['fr', 'en', 'de']

# Languages we want translations for
WIKIDATA_LABEL_LANGUAGES = ['fr', 'en', 'de', 'ja']

#  ____  _        _   _     _   _
# / ___|| |_ __ _| |_(_)___| |_(_) ___ ___
# \___ \| __/ _` | __| / __| __| |/ __/ __|
#  ___) | || (_| | |_| \__ \ |_| | (__\__ \
# |____/ \__\__,_|\__|_|___/\__|_|\___|___/
#

# Directory where to download dumps
STATS_DUMP_DIR = 'dumps/stats'

# Files to download and load
STATS_FILES = [
    "{year:04d}/{year:04d}-{month:02d}/pageviews-{year:04d}{month:02d}{day:02d}-{hour:02d}0000.gz".format(
        year=2019, month=9, day=day, hour=hour
    )
    for day in range(1, 31)
    for hour in range(24)
]

# Base URL to download dumps
STATS_ENDPOINT = 'https://dumps.wikimedia.org/other/pageviews'

# Table to store stats in
TABLE_STATISTICS = 'wikimedia_stats'

# Sites we want statistics for
STATISTICS_SITES = ['fr', 'en', 'de', 'ja']
