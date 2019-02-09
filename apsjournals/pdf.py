"""PDF utilities
"""


import collections
import fpdf
import os
import pathlib
import PyPDF2 as pypdf
import tempfile
import time
import typing
import apsjournals


ArticleMeta = collections.namedtuple('ArticleMeta', 'article file pages')
LinkMeta = collections.namedtuple('LinkMeta', 'source_page target_page x y w h')
BookmarkMeta = collections.namedtuple('BookmarkMeta', 'name page parent')


def clean_path(path: str):
    """Clean path for pdf article"""
    return path.replace(',', '')


def get_issue_meta(issue, dir: str, throttle: int=2) -> typing.List[ArticleMeta]:
    """Download Issue contents and return meta data about where the articles
    have been download. 

    Args:
        issue: 
            Issue, the issue whose articles to download
        dir:
            str, the directory name
        throttle:
            int, the number of seconds between downloads, used to 

    Returns:

    """
    if not os.path.exists(dir):
        os.mkdir(dir)
    meta = []
    for article in issue.articles:
        time.sleep(throttle)
        path = os.path.join(dir, clean_path(article.name)) + '.pdf'
        article.pdf(path)
        with open(path, 'rb') as fid:
            meta.append(ArticleMeta(article, path, pypdf.PdfFileReader(fid).getNumPages()))
    return meta


class ApsPDF(fpdf.FPDF):
    """Create a PDF of all issue contents with Table of Contents"""
    def __init__(self, issue, out_file, orientation='P',unit='mm',format='letter'):
        super().__init__(orientation=orientation, unit=unit, format=format)
        self.alias_nb_pages()
        self.set_font('Arial', '', size=10)
        self._meta_x = 0
        self._meta_y = 0
        self._meta_links = []
        self._meta_bookmarks = []
        self._meta_issue = issue
        self._meta_out_file = out_file 
        self._sync_page_no()
        out_path = pathlib.Path(self._meta_out_file)
        self._meta_pre_path = (out_path.parent / ('pre_' + out_path.name)).as_posix()

    ####################### META DATA CURATION #######################

    def _meta_link(self, s, t, x, y, w, h):
        self.links.append(LinkMeta(s, t, x, y, w, h))

    def _meta_bookmark(self, name, page, parent=None):
        b = BookmarkMeta(name, page, parent)
        self._meta_bookmarks.append(b)
        return b

    def _sync_page_no(self):
        self._meta_page = self.page_no()

    ####################### OVERRIDDEN METHODS #######################

    def add_page(self, orientation=''):
        self._meta_x, self._meta_y = 0, 0
        super().add_page(orientation=orientation)
        self._sync_page_no()

    def cell(self, w, h=0, txt='', border=0, ln=0, align='', fill=0, link='', meta_link: str=None):
        if meta_link is not None:
            self._meta_links.append(LinkMeta(meta_link.source_page, meta_link.target_page, self._meta_x, self._meta_y, w, h))
        super().cell(w, h, txt, border, ln, align, fill, link)
        page = self.page_no()
        if page > self._meta_page: # crossed over into new page
            self._meta_x, self._meta_y = w, h # reset
            self._sync_page_no()
        self._meta_x += w
        self._meta_y += h

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, "Prepared by apsjournals version {}".format(apsjournals.__version__), 0, 1, align='C', link=apsjournals.__github_url__)

    #######################  ADDITIONAL  PAGES  #######################

    def add_page_cover(self):
        """Add cover page"""
        self.add_page()
        self.cell(0, 50, '', ln=1)  # padding
        self.set_font_size(20)
        self.cell(0, 10, self._meta_issue.vol.journal.name, align='C', ln=1)
        self.cell(0, 10, "Volume {:d} Issue {:d}".format(self._meta_issue.vol.num, self._meta_issue.num), align='C', ln=1)
        # self.cell(0, 170, '', ln=1)  # padding

    def add_page_contents(self, meta_cache):
        """Add Table of Contents"""
        self.add_page()
        max_authors = 10
        line_items = list(self._meta_issue.contents(True))
        contents_pages = len(line_items) * 10 // 208 + 1 + 1
        page = contents_pages + 1
        for level, member in line_items:
            if member.__class__.__name__ == 'Section':  # figure out dependency issue here
                self.set_font('Arial', style='', size=16 - 2 * level)
                self.cell(0, 10, txt=member.name, ln=1)
            else:  # Article
                meta = meta_cache[member.name]
                indent = 10 * ' '

                # Create link
                link = LinkMeta(self.page_no() - 1, page, None, None, None, None)

                # add article title
                self.set_font('Arial', style='I', size=10)
                self.cell(50, 7, txt=indent + member.name, ln=0, meta_link=link)

                # add page number at end of title line
                self.set_font('Arial', style='', size=10)
                self.cell(0, 7, txt=str(page + contents_pages), ln=1, align='R')

                # add author line
                self.set_font('Arial', style='', size=8)
                author_text = 2 * indent + ', '.join(a.last_name for a in member.authors[:max_authors]) + (' et. al.' if len(member.authors) > max_authors else '')
                self.cell(10, 2, txt=author_text, ln=1, meta_link=link)  # author name
                self.cell(10, 4, txt='', ln=1)  # padding below author name
                page = page + meta.pages

    ####################### META INFO BUILDERS #######################

    def add_bookmarks(self):
        """Add bookmarks to document"""
        with open(self._meta_out_file, 'wb') as out_fid:
            with open(self._meta_pre_path, 'rb') as pre_fid:
                reader = pypdf.PdfFileReader(pre_fid)
                writer = pypdf.PdfFileWriter()
                page_bookmarks = {b.page: [] for b in self._meta_bookmarks} # TODO refactor for defaultdict
                for b in self._meta_bookmarks:
                    page_bookmarks[b.page].append(b)
                bookmark_cache = {}
                page_links = {l.target_page: l for l in self._meta_links}
                for n in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(pageNumber=n))
                    if n == 1:
                        writer.addBookmark('Cover', 0)
                    elif n == 2:
                        writer.addBookmark('Contents', 1)
                    elif n in page_bookmarks:
                        for bookmark in page_bookmarks[n]:
                            bookmark_handle = writer.addBookmark(bookmark.name, bookmark.page, parent=bookmark_cache.get(bookmark.parent, None)) 
                            bookmark_cache[bookmark] = bookmark_handle
                    # if n in page_links: # TODO resolve the mismatched placement of the links
                    #     link = page_links[n]
                    #     print('Adding Link: ({:d}, {:d}, {:d}, {:d}) {:d} -> {:d}'.format(link.h, link.w, link.x, link.y, link.source_page, link.target_page))
                    #     writer.addLink(link.source_page, link.target_page, rect=(link.x, link.y, link.w, link.h))
                writer.write(out_fid)

    def cleanup(self):
        """Remove the temp file"""
        os.remove(self._meta_pre_path)

    ####################### PRIMARY INTERFACE BUILD #######################

    def build(self):
        """Build the pdf"""
        with tempfile.TemporaryDirectory('.aps-tmp') as tmp:
            # Build issue 
            metas = get_issue_meta(self._meta_issue, str(tmp))
            meta_cache = {m.article.name: m for m in metas}

            # output cover pages
            self.add_page_cover()
            self.add_page_contents(meta_cache)
            self.output(os.path.join(str(tmp), 'cover.pdf'))

            # Get overall writer
            writer = pypdf.PdfFileWriter()

            # Write out fully assembled file
            with open(self._meta_pre_path, 'wb') as out_fid:
                # writer.write(fid)

                # Establish cover pages
                with open(os.path.join(str(tmp), 'cover.pdf'), 'rb') as fid:
                    cover_reader = pypdf.PdfFileReader(fid)
                    page = cover_reader.getNumPages()
                    writer.appendPagesFromReader(cover_reader, after_page_append=0)
                    writer.write(out_fid)
    
                # Walk through individual article pdfs and add each to the overall PDF
                parents = {1: None}
                for level, item in self._meta_issue.contents(include_level=True):
                    if item.__class__.__name__ == 'Section':
                        parents[level + 1] = self._meta_bookmark(item.name, page, parent=parents.get(level, None))
                    else:  # Article
                        meta = meta_cache[item.name]
                        with open(meta.file, 'rb') as fid:
                            reader = pypdf.PdfFileReader(fid)
                            writer.appendPagesFromReader(reader, after_page_append=page)
                            writer.write(out_fid)
                            self._meta_bookmark(meta.article.name, page, parent=parents[level])
                        page += meta.pages
                # writer.write(out_fid)    
            self.add_bookmarks()
        self.cleanup()
