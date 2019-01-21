"""Primary interface and object model definition for APS journals. 

Object Model:
    For the purposes of this package, the highest-level publication is a Journal. Each Journal 
    consists of Issues that are published in Volumes. Each Issue is essentially a collection of articles,
    though the articles may be grouped into sections or subsections.

Classes defined with brief descriptions:
    Journal - the APS publication
    Volume - a volume of a particular journal, a collection of issues
    Issue - a particular instance of the publication, a collection of articles
    Section - a part of an Issue, may contain subsections or articles
    Article - an individual article published in the Journal
    Author - A contributor to an article
"""


import collections
import datetime
import itertools
import typing
from apsjournals.web import scrapers


class Journal:
    def __init__(self, name: str, url_path: str, description: str=None, short_name: str=None):
        """The highest-level abstraction in the library, the Journal represents an APS publication
        
        Args:
            name: 
                str, the name of the publication, e.g. "Physical Review Letters"
            url_path: 
                str, the piece of the URL that specifies the journal, i.e. "prl"
            description: 
                str, default None, the description of the Journal
            short_name: 
                str, the short name of the Journal, used in the repr if specified
        """
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
        """Get a particular Volume of the journal

        Args:
            n: 
                int, the volume number

        Returns:
            Volume
        """
        volumes = self.volumes
        if n is None:
            n = volumes[0]
        elif n not in volumes:
            raise ValueError('Invalid volume number {} for journal {}, valid numbers are: {}'.format(n, self, volumes)) # load volume info from web
        return self._volumes[n]

    def issue(self, vol: int, issue: int):
        return self.volume(vol).issue(issue)


class Volume:
    def __init__(self, journal: Journal, num: int, start: datetime.date, end: datetime.date):
        """A Volume of a journal is an increment of issuance, containing one or more Issues

        Args:
            journal: 
                Journal, the journal from which the Volume comes
            num: 
                int, the Volume number
            start: 
                datetime.date, the starting date of the Volume (if known)
            end:
                datetime.date, the ending date of the Volume (if known) 
        """
        self.journal = journal
        self.num = num
        self.start = start
        self.end = end
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
        """Load a particular Issue from this volume

        Args:
            num: 
                int, the number of the issue. If None, get the most recent Issue

        Returns:
            Issue
        """
        issues = self.issues
        if num not in issues:
            raise ValueError('Invalid issue number, valid numbers include: {}'.format(issues))
        if self._issues[num] is None:
            pass # load issue from web and cache
        return self._issues[num]


class Issue:
    def __init__(self, vol: Volume, num: int):
        """An Issue is the most granular unit of the Journal, in that it is the immediate
        container of Articles

        Args:
            vol: 
                Volume, the Volume from which the Issue comes
            num: 
                int, the issue number
        """
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
        """Load the contents of the Issue, returning a list of Sections and Articles
        
        Returns:
            List[Union[Section, Article]]
        """
        if not self._contents:
            s = scrapers.IssueScraper()
            info = s.load(journal=self.journal.url_path, volume=self.vol.num, issue=self.num)
            self._contents = parse_contents_from_info(info, issue=self)
        return self._contents

    @property
    def articles(self):
        def extract_articles(x):
            if isinstance(x, Article):
                return [x]
            elif isinstance(x, Section):
                return list(itertools.chain.from_iterable([extract_articles(m) for m in x.members]))
        return list(itertools.chain.from_iterable([extract_articles(c) for c in self.contents]))


class Author:
    def __init__(self, name: str):
        """An author is a contributor to an Article.

        Args:
            name: 
        """
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
        return "Author({!r})".format(self.name)

    @property
    def name(self):
        return '{}, {}'.format(self.last_name, self.first_name)


class Section:
    def __init__(self, name, members):
        """A section contains subsections or Articles

        Args:
            name: 
                str, the name of the section
            members: 
                List[Union[Section, Article]]
        """
        self.name = name
        self.members = members

    def __repr__(self):
        return "Section({}, {:d} members)".format(self.name, len(self.members))


class Article:
    def __init__(self, issue: Issue, name: str, authors: typing.List[Author], url: str, pdf_url: str, teaser: str=None):
        """An article represents a published paper in an APS journal. It is organized into 
        a parent Issue, and has several pieces of meta data (authors, url, etc.).

        Args:
            issue: 
                Issue, the issue in which the Article is published
            name: 
                str, the name of the article
            authors: 
                List[Author], the list of authors
            url: 
                str, the url for the Article webpage
            pdf_url: 
                str, the url for the PDF format of the Article
            teaser: 
                str or None, the teaser for the article if one exists
        """
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
    """Convert an iterable of raw web-scraped information into api objects.

    Args:
        info: 
            List[Union[DividerInfo, SectionInfo, ArticleInfo]]
        issue:
            Issue, the issue to which the contents belong 

    Returns:
        List of Section and Article instances
    """
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
