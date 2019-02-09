import functools
import mock
import os
import pathlib
import PyPDF2 as pypdf
import unittest
import apsjournals
from apsjournals.web.constants import EndPoint
from tests.test_api import get_aps_static


_PDF_NUM = 0
PDF_ROOT = pathlib.Path(__file__).parent / 'static' / 'pdfs'


def mock_download_pdf(pdf_url: str, out_file: str):
    global _PDF_NUM
    pdf_file = PDF_ROOT / ('a b c'.split()[_PDF_NUM % 3] + '.pdf')
    with open(pdf_file.as_posix(), 'rb') as in_file:
        with open(out_file, 'wb') as fid:
            fid.write(in_file.read())
    _PDF_NUM += 1


class PdfTests(unittest.TestCase):
    def test_issue_download(self):
        with mock.patch('apsjournals.web.scrapers.download_pdf', side_effect=mock_download_pdf):
            with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
                issue = apsjournals.PRL.issue(121, 6)
            with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Issue)):
                issue.pdf((PDF_ROOT / 'test.pdf').as_posix())
        with open((PDF_ROOT / 'test.pdf').as_posix(), 'rb') as pre_fid:
            reader = pypdf.PdfFileReader(pre_fid)
            self.assertEqual(reader.getNumPages(), 181)
        os.remove((PDF_ROOT / 'test.pdf').as_posix()) # cleanup
