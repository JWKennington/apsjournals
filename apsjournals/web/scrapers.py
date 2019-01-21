"""Website wrappers for APS site
"""


import collections
import requests
import scrapy
import typing
from apsjournals import util
from apsjournals.web.constants import EndPoint


# Info namedtuples for storing intermediate scraping results
VolumeInfo = collections.namedtuple('VolumeInfo', 'url num start end')
IssueInfo = collections.namedtuple('IssueInfo', 'url name label')
DividerInfo = collections.namedtuple('DividerInfo', 'name')
ArticleInfo = collections.namedtuple('ArticleInfo', 'name author teaser url pdf_url')
SectionInfo = collections.namedtuple('SectionInfo', 'name articles')


def get_aps(url: str, **kwargs):
    response = requests.get(url=url, params=kwargs)
    # TODO add error handling and authentication
    return response.content


class Scraper:
    def __init__(self, endpoint: EndPoint):
        self.endpoint = endpoint

    def extract(self, source: str):
        raise NotImplementedError

    def get(self, **kwargs):
        return get_aps(url=self.endpoint.format(**kwargs))

    def load(self, **kwargs):
        source = self.get(**kwargs)
        return self.extract(source)


class VolumeIndexScraper(Scraper):
    def __init__(self):
        super().__init__(endpoint=EndPoint.Volume)

    def extract(self, source) -> typing.List[VolumeInfo]:
        s = scrapy.Selector(text=source)
        vols = s.css('div[class=volume-issue-list]')
        info = [(v.css('a::attr(href)').extract()[0], v.css('small::text').extract()[0]) for v in vols]
        info = [(v[0].split('#v')[0], int(v[0].split('#v')[1]), v[1]) for v in info]
        return [VolumeInfo(*(v[:2] + util.parse_start_end(v[2]))) for v in info]


class IssueIndexScraper(Scraper):
    def __init__(self):
        super().__init__(endpoint=EndPoint.Issue)

    def extract(self, source) -> typing.List[IssueInfo]:
        s = scrapy.Selector(text=source)
        vols = s.css('div[class=volume-issue-list]')
        _vol = [v for v in vols if int(v.css('h4::attr(id)').extract_first()[1:]) == volume][0]
        issues = _vol.css('div[class=volume-issue-list]').css('li')
        return [IssueInfo(i.css('a::attr(href)').extract_first(), 
                          i.css('a::text').extract_first(),
                          i.css('li::text').extract_first()) for i in issues]


class IssueScraper(Scraper):
    def __init__(self):
        super().__init__(endpoint=EndPoint.Issue)

    def _extract_issue_item(self, x):
        tag = x.root.tag
        if tag == 'h2':  # Section title
            return DividerInfo(name=x.css('::text').extract_first())
        elif tag == 'div':  # Article
            title = x.css('[class="title"]')
            name, url = title.css('a::text').extract_first(), title.css('a::attr(href)').extract_first()
            author = x.css('h6[class="authors"]::text').extract_first()
            teaser = x.css('[class="teaser"]').css('p::text').extract_first()
            pdf_url = x.css('a[class="tiny button left-button"]::attr(href)').extract_first()
            return ArticleInfo(name=name, author=author, teaser=teaser, url=url, pdf_url=pdf_url)
        elif tag == 'section':
            name = x.css('h4::text').extract_first()
            articles = [self._extract_issue_item(a) for a in x.css('div[class="article panel article-result"]')]
            return SectionInfo(name=name, articles=articles)
        else:
            raise ValueError('unknown tag {}'.format(tag))
    
    def extract(self, source: str) -> typing.List[typing.Union[DividerInfo, ArticleInfo, SectionInfo]]:
        sel = scrapy.Selector(text=source)
        results = sel.css('div[class="search-results"]')[0]
        items = results.xpath('(h2|div|section)')
        parsed = [self._extract_issue_item(i) for i in items]
        return parsed
