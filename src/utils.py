from datetime import date, timedelta


def timeperiod(start: date, end: date, step=timedelta(days=1)):
    current = start

    while current < end:
        yield current
        current += step


def wikimedia_stats_dump_path(year, month, day, hour):
    """
    Give the the path of a stats dump from wikimedia endpoint here:
    https://dumps.wikimedia.org/other/pageviews/.
    """
    return (
        '{year:04d}/{year:04d}-{month:02d}/'
        'pageviews-{year:04d}{month:02d}{day:02d}-{hour:02d}0000.gz'
    ).format(year=year, month=month, day=day, hour=hour)
