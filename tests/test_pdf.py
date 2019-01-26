

import functools
import mock
import unittest
import apsjournals


class PdfTests(unittest.TestCase):
    def test_issue_download(self):
        apsjournals.authenticate('jwkennington', 'blackSWAN10sigma')
        issue = apsjournals.PRL.issue(121, 6)
        issue.pdf('p.pdf')