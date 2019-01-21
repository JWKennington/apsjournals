"""Miscellaneous utilities
"""


import datetime


def month_name_to_num(m: str):
    return datetime.datetime.strptime(m, '%B').month

def parse_start_end(tr: str):
    start, end = tr.split(' - ')
    if end == 'Present':
        year = datetime.date.today().year
        end = datetime.date(year, datetime.date.today().month, 1)
        start = datetime.date(year, month_name_to_num(start), 1)
    else:
        year = int(end.split(' ')[-1])
        end = datetime.date(year, datetime.date.today().month, 1)
        start = datetime.date(year, month_name_to_num(start), 1)
    return start, end