

import functools
import mock
import unittest
from apsjournals import api
from apsjournals.web.constants import EndPoint
from apsjournals.web.tests.test_scrapers import get_aps_static


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.j = api.Journal('PRL', 'prl', 'PRL Desc')

    def test_lazy_init(self):
        self.assertEqual(repr(self.j), "Journal('PRL')")

    def test_volumes(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            vols = self.j.volumes
        self.assertEqual(tuple(vols), tuple(range(1, 123)[::-1]))

    def test_volume(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            v = self.j.volume(121)
        self.assertIsInstance(v, api.Volume)
        self.assertEqual(str(v), "Volume('PRL', 121)")


class VolumeTests(unittest.TestCase):
    def setUp(self):
        self.j = api.Journal('PRL', 'prl', 'PRL Desc')
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            self.v = self.j.volume(121)

    def test_issues(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            issues = self.v.issues
        self.assertEqual(tuple(issues), tuple(range(1, 27)))

    def test_issue(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            i = self.v.issue(6)
        self.assertIsInstance(i, api.Issue)
        self.assertEqual(str(i), "Issue('PRL', 121, 6)")


class IssueTests(unittest.TestCase):
    def setUp(self):
        self.j = api.Journal('PRL', 'prl', 'PRL Desc')
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            self.v = self.j.volume(121)

        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            self.i = self.v.issue(6)

    def test_contents(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Issue)):
            contents = self.i.contents
        self.assertEqual(repr(contents), "[Section(HIGHLIGHTED ARTICLES, 6 members), Section(LETTERS, 10 members)]")

