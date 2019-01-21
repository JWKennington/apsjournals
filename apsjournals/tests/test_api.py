

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
