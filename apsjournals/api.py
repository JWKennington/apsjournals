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
            s = scrapers.VolumeIndexScraper()
            info = s.load(journal=self.url_path, volume=None)
            for i in info:
                self._volumes[i.num] = Volume(journal=self, num=i.num, start=i.start, end=i.end)
        return list(self._volumes.keys())

    def volume(self, n: int=None):
        volumes = self.volumes
        if n is None:
            n = volumes[0]
        elif n not in volumes:
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
            s = scrapers.IssueIndexScraper()
            info = s.load(journal=self.journal.url_path, volume=self.num, issue=None)
            for i in info:
                self._issues[i.num] = Issue(vol=self, num=i.num)
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
        self._contents = []

    def __repr__(self):
        return "Issue({!r}, {:d}, {:d})".format(self.journal.name, self.vol.num, self.num)

    @property
    def journal(self):
        return self.vol.journal

    @property
    def contents(self):
        if not self._contents:
            s = scrapers.IssueScraper()
            info = s.load(journal=self.journal.url_path, volume=self.vol.num, issue=self.num)
            self._contents = parse_contents_from_info(info, issue=self)
        return self._contents


class Author:
    def __init__(self, name: str):
        if ', ' in name: # nonstandard aps format
            last, first = name.split(', ')
        elif ' ' in name:
            pieces = name.split(' ')
            first, last = pieces[0], ' '.join(pieces[1:])
        else:
            first, last = name, name
            # raise ValueError('Unable to parse Author name: {}'.format(name))
        self.first_name = first
        self.last_name = last

    def __repr__(self):
        return "Author({!r}, {!r})".format(self.last_name, self.first_name)

    @property
    def name(self):
        return '{}, {}'.format(self.last_name, self.first_name)


class Section:
    def __init__(self, name, members):
        self.name = name
        self.members = members

    def __repr__(self):
        return "Section({}, {:d} members)".format(self.name, len(self.members))


class Article:
    def __init__(self, issue: Issue, name: str, authors: typing.List[Author], url: str, pdf_url: str, teaser: str=None):
        self.issue = issue
        self.name = name
        self.authors = authors
        self.url = url
        self.pdf_url = pdf_url
        self.teaser = teaser

    def __repr__(self):
        return "Article({!r})".format(self.name)

    @property
    def journal(self):
        return self.issue.vol.journal


def parse_contents_from_info(info: typing.List[typing.Union[scrapers.DividerInfo, scrapers.SectionInfo, scrapers.ArticleInfo]], issue: Issue) -> typing.List[Section]:
    contents = []
    for n, i in enumerate(info):
        if isinstance(i, scrapers.DividerInfo):
            divider_info = []
            while len(info) > n + 1 and not isinstance(info[n+1], scrapers.DividerInfo):
                divider_info.append(info.pop(n+1))
            divider_contents = parse_contents_from_info(divider_info, issue=issue)
            contents.append(Section(i.name, members=divider_contents))
        elif isinstance(i, scrapers.SectionInfo):
            contents.append(Section(name=i.name, members=parse_contents_from_info(i.articles, issue=issue)))
        elif isinstance(i, scrapers.ArticleInfo):
            contents.append(Article(issue=issue,
                                    name=i.name,
                                    authors=[Author(n.strip()) for n in i.author.replace('and', '').encode('ascii', 'ignore').decode('ascii').split(',')],
                                    url=i.url,
                                    pdf_url=i.pdf_url,
                                    teaser=i.teaser))
        else:
            raise ValueError('Unable to parse contents from type {}'.format(type(i)))
    return contents
