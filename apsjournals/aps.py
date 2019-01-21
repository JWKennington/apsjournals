"""Primary API
"""


import collections
import datetime
import typing
from apsjournals.web import scrapers


class Journal:
    def __init__(self, name: str, url_path: str, description: str=None, short_name: str=None):
        self.name = name
        self.url_path = url_path
        self.description = description
        self.short_name = short_name
        self._volumes = collections.OrderedDict() # cache

    def __repr__(self):
        return 'Journal({!r})'.format(self.name if self.short_name is None else self.short_name)

    @property
    def volumes(self) -> typing.List[int]:
        if not self._volumes:
            for info in scrapers.journal_index(self.url_path):
                self._volumes[info.num] = Volume(journal=self, num=info.num, start=info.start, end=info.end)
        return list(self._volumes.keys())

    def volume(self, n: int):
        volumes = self.volumes
        if n not in volumes:
            raise ValueError('Invalid volume number {} for journal {}, valid numbers are: {}'.format(n, self, volumes)) # load volume info from web
        return self._volumes[n]


class Volume:
    def __init__(self, journal: Journal, num: int, start: datetime.date, end: datetime.date):
        self.journal = journal
        self.num = num
        self._issues = collections.OrderedDict()

    def __repr__(self):
        return 'Volume({!r}, {:d})'.format(self.journal.name if self.journal.short_name is None else self.journal.short_name, self.num)

    @property
    def issues(self) -> typing.List[int]:
        if not self._issues:
            pass # load issue numbers from web
        return list(self._issues.keys())

    def issue(self, num: int):
        issues = self.issues
        if num not in issues:
            raise ValueError('Invalid issue number, valid numbers include: {}'.format(issues))
        if self._issues[num] is None:
            pass # load issue from web and cache
        return self._issues[num]


class Issue:
    def __init__(self, vol: Volume, num: int):
        self.vol = vol
        self.num = num

    @property
    def journal(self):
        return self.vol.journal

    def contents(self):
        raise NotImplementedError


class Author:
    def __init__(self, name: str):
        if ', ' in name:
            last, first = name.split(', ')
        elif ' ' in name:
            first, last, *_ = name.split(' ')
        else:
            raise ValueError('Unable to parse Author name: {}'.format(name))
        self.first_name = first
        self.last_name = last

    @property
    def name(self):
        return '{}, {}'.format(self.last_name, self.first_name)


class Article:
    def __init__(self, issue: Issue, name: str, authors: typing.List[Author], url: str, pdf_url: str, teaser: str=None):
        self.issue = issue
        self.name = name
        self.authors = authors
        self.url = url
        self.pdf_url = pdf_url
        self.teaser = teaser

    @property
    def journal(self):
        return self.issue.vol.journal

