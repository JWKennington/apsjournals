import datetime
import mock
import pathlib
import unittest
from apsjournals.web import scrapers
from apsjournals.web.constants import EndPoint


STATIC_DIR = pathlib.Path(__file__).parent / 'static' 


def get_params_from_url(url: str) -> tuple:
    params = None
    for e in EndPoint:
        pattern = e.as_re()
        m = pattern.match(url)
        if m is not None:
            params = m.groups()
            break
    if params is None:
        raise ValueError('Unable to match url against known endpoints: {}'.format(url))
    return params


def get_aps_static(url: str):
    params = get_params_from_url(url)
    if len(params) == 2: # missing issue
        params = params + (None,)
    journal, volume, issue = params
    file_name = str(volume) + ('' if issue is None else '-' + str(issue)) + '.htm'
    p = STATIC_DIR / journal / file_name
    with open(p.as_posix()) as fid:
        return fid.read()


class StaticTests(unittest.TestCase):
    def test_get_params_from_url(self):
        url = EndPoint.Volume.format(journal='prl', volume=121)
        self.assertEqual(get_params_from_url(url), ('prl', '121'))

    def test_get_aps_static(self):
        source = get_aps_static('prl', 121)
        self.assertEqual(source[:20], "<!DOCTYPE html>\n<!--")

    def test_get_aps_static_issue(self):
        source = get_aps_static('prl', 121, 6)
        self.assertEqual(source[:20], "<!DOCTYPE html>\n<!--")


class ScraperTests(unittest.TestCase):
    def test_base_scraper(self):
        s = scrapers.Scraper(endpoint=EndPoint.Volume)
        source = s.get(journal='prl', volume=121)
        self.assertEqual(source[:30].decode(), "<!DOCTYPE html><!--[if IE 8]><")

    def test_volume_index_scraper(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=get_aps_static):
            s = scrapers.VolumeIndexScraper()
            info = s.load(journal='prl', volume=121)
            self.assertEqual(info[0], scrapers.VolumeInfo(url='https://journals.aps.org/prl/issues/122', num=122, start=datetime.date(2019, 1, 1), end=datetime.date(2019, 1, 1)))

