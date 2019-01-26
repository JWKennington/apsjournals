"""PDF utilities
"""


import collections
import fpdf
import os
import PyPDF2 as pypdf
import tempfile
import typing
import apsjournals


ArticleMeta = collections.namedtuple('ArticleMeta', 'article file pages')
LinkMeta = collections.namedtuple('LinkMeta', 'source_page target_page x y w h')
BookmarkMeta = collections.namedtuple('BookmarkMeta', 'name page parent')


def clean_path(path: str):
    return path.replace(',', '')


def get_issue_meta(issue, dir: str) -> typing.List[ArticleMeta]:
    """Download Issue contents and return meta data about where the articles
    have been download. 

    Args:
        issue: 
            Issue, the issue whose articles to download

    Returns:

    """
    if not os.path.exists(dir):
        os.mkdir(dir)
    meta = []
    for article in issue.articles:
        path = os.path.join(dir, clean_path(article.name)) + '.pdf'
        article.pdf(path)
        with open(path, 'rb') as fid:
            meta.append(ArticleMeta(article, path, pypdf.PdfFileReader(fid).getNumPages()))
    return meta


class TocPDF(fpdf.FPDF):
    """Custom PDF Class for Table of contents and Cover Page"""
    def header(self):
        pass

    def footer(self):
        self.set_font('Arial', 'I', 8)
        self.cell(0, 0, "Prepared by apsjournals version {}".format(apsjournals.__version__), 0, 0, align='C', link=apsjournals.__github_url__)


class ApsPDF:
    def __init__(self, issue, out_file):
        self.x = 0
        self.y = 0
        self.pdf = TocPDF(format='letter')
        self.pdf.alias_nb_pages()
        self.pdf.set_font('Arial', '', size=10)
        self.links = []
        self.bookmarks = []
        self.issue = issue
        self.out_file = out_file 
        self.page = self.pdf.page_no()

    def add_page(self):
        self.x, self.y = 0, 0
        self.pdf.add_page()

    def set_font_size(self, size: int):
        self.pdf.set_font_size(size)

    def cell(self, w, h=0, txt='', border=0, ln=0, align='', fill=0, link=None):
        self.x += w
        self.y += h
        if link is None:
            link = ''
        else:
            self.links.append(LinkMeta(link.source_page, link.target_page, self.x, self.y, w, h))
        self.pdf.cell(w, h, txt, border, ln, align, fill)
        page = self.pdf.page_no()
        if page > self.page: # crossed over into new page
            self.x, self.y = w, h # reset
        # TODO properly handle 0 for x and y
        

    def link(self, s, t, x, y, w, h):
        self.links.append(LinkMeta(s, t, x, y, w, h))

    def bookmark(self, name, page, parent=None):
        b = BookmarkMeta(name, page, parent)
        self.bookmarks.append(b)
        return b

    def add_cover_page(self):
        self.add_page()
        self.cell(0, 50, '', ln=1)  # padding
        self.set_font_size(20)
        self.cell(0, 10, self.issue.vol.journal.name, align='C', ln=1)
        self.cell(0, 10, "Volume {:d} Issue {:d}".format(self.issue.vol.num, self.issue.num), align='C', ln=1)
        self.cell(0, 0, '', ln=1)  # padding

    def add_toc(self, meta_cache):
        self.add_page()
        max_authors = 10
        line_items = list(self.issue.contents(True))
        contents_pages = len(line_items) * 10 // 208 + 1 + 1
        page = contents_pages + 1
        for level, member in line_items:
            if member.__class__.__name__ == 'Section':  # figure out dependency issue here
                self.pdf.set_font('Arial', style='', size=16 - 2 * level)
                self.cell(0, 10, txt=member.name, ln=1)
            else:  # Article
                meta = meta_cache[member.name]
                indent = 10 * ' '

                # Create link
                link = LinkMeta(self.pdf.page_no(), page, None, None, None, None)

                # add article title
                self.pdf.set_font('Arial', style='I', size=10)
                self.cell(50, 7, txt=indent + member.name, ln=0, link=link)

                # add page number at end of title line
                self.pdf.set_font('Arial', style='', size=10)
                self.cell(0, 7, txt=str(page + contents_pages), ln=1, align='R')

                # add author line
                self.pdf.set_font('Arial', style='', size=8)
                author_text = 2 * indent + ', '.join(a.last_name for a in member.authors[:max_authors]) + (' et. al.' if len(member.authors) > max_authors else '')
                self.cell(10, 2, txt=author_text, ln=1, link=link)  # author name
                self.cell(10, 4, txt='', ln=1)  # padding below author name
                page = page + meta.pages

    def build(self):
        with tempfile.TemporaryDirectory('.aps-tmp') as tmp:
            # Build issue 
            metas = get_issue_meta(self.issue, str(tmp))
            meta_cache = {m.article.name: m for m in metas}
            
            # output cover pages
            self.add_cover_page()
            self.add_toc(meta_cache)
            self.pdf.output(os.path.join(str(tmp), 'cover.pdf'))

            # Get overall writer
            writer = pypdf.PdfFileWriter()

            # Write out fully assembled file
            with open('pre_' + self.out_file, 'wb') as out_fid:
                # writer.write(fid)

                # Establish cover pages
                with open(os.path.join(str(tmp), 'cover.pdf'), 'rb') as fid:
                    cover_reader = pypdf.PdfFileReader(fid)
                    page = cover_reader.getNumPages()
                    writer.appendPagesFromReader(cover_reader, after_page_append=0)
                    writer.write(out_fid)
    
                # Walk through individual article pdfs and add each to the overall PDF
                parents = {1: None}
                for level, item in self.issue.contents(include_level=True):
                    if item.__class__.__name__ == 'Section':
                        parents[level + 1] = self.bookmark(item.name, page, parent=parents.get(level, None))
                    else:  # Article
                        meta = meta_cache[item.name]
                        with open(meta.file, 'rb') as fid:
                            reader = pypdf.PdfFileReader(fid)
                            writer.appendPagesFromReader(reader, after_page_append=page)
                            writer.write(out_fid)
                            self.bookmark(meta.article.name, page, parent=parents[level])
                        page += meta.pages
                # writer.write(out_fid)    
            self.add_bookmarks()

    def add_bookmarks(self):
        # apple bookmarks
        print('Writing final links and bookmarks')
        with open(self.out_file, 'wb') as out_fid:
            with open('pre_' + self.out_file, 'rb') as pre_fid:
                reader = pypdf.PdfFileReader(pre_fid)
                writer = pypdf.PdfFileWriter()
                page_bookmarks = {b.page: b for b in self.bookmarks}
                bookmark_cache = {}
                page_links = {l.target_page: l for l in self.links}
                for n in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(pageNumber=n))
                    if n in page_bookmarks:
                        bookmark = page_bookmarks[n]
                        print('Adding Bookmark: ' + bookmark.name)
                        bookmark_cache[bookmark] = writer.addBookmark(bookmark.name, bookmark.page, parent=bookmark_cache.get(bookmark.parent, None))
                    if n in page_links:
                        link = page_links[n]
                        writer.addLink(link.source_page, link.target_page, rect=(link.x, link.y, link.w, link.h))
                writer.write(out_fid)

