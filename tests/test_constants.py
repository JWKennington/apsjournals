import unittest
from apsjournals.web.constants import EndPoint, URL, Url


class UrlTests(unittest.TestCase):
    def setUp(self):
        self.u1 = Url('{a}/{b}')

    def test_parameters(self):
        self.assertEqual(tuple(self.u1.parameters), ('a', 'b'))

    def test_format(self):
        self.assertEqual(self.u1.format(a='1', b='bee'), '1/bee')
        with self.assertRaises(ValueError):
            self.u1.format(c='oops')

    def test_as_re(self):
        self.assertEqual(self.u1.as_re(compile=False), r"(?P<a>\w*)/(?P<b>\w*)")


class ConstantsTests(unittest.TestCase):
    def test_url(self):
        self.assertEqual(URL.Root, 'https://journals.aps.org')

    def test_endpoints(self):
        self.assertEqual(EndPoint.Volume, 'https://journals.aps.org/{journal}/issues/{volume}')
        self.assertEqual(EndPoint.Issue, 'https://journals.aps.org/{journal}/issues/{volume}/{issue}')
