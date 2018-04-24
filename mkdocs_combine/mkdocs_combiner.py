# Copyright 2015 Johannes Grassler <johannes@btw23.de>
# Copyright 2017 Adam Twardoch <adam+github@twardoch.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import codecs
import os
import re

import markdown
import mkdocs.config
import mkdocs.utils

import mkdocs_combine.filters.anchors
import mkdocs_combine.filters.chapterhead
import mkdocs_combine.filters.exclude
import mkdocs_combine.filters.headlevels
import mkdocs_combine.filters.images
import mkdocs_combine.filters.include
import mkdocs_combine.filters.math
import mkdocs_combine.filters.metadata
import mkdocs_combine.filters.tables
import mkdocs_combine.filters.toc
import mkdocs_combine.filters.xref
import mkdocs_combine.filters.heading
import mkdocs_combine.filters.admonitions

from mkdocs_combine.exceptions import FatalError

from mkdocs_combine.page import Page


class MkDocsCombiner:
    """Top level converter class. Instatiate separately for each mkdocs.yml."""

    def __init__(self, **kwargs):
        self.config_file = kwargs.get('config_file', 'mkdocs.yml')
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.exclude = kwargs.get('exclude', None)
        self.filter_tables = kwargs.get('filter_tables', True)
        self.filter_xrefs = kwargs.get('filter_xrefs', True)
        self.image_ext = kwargs.get('image_ext', None)
        self.strip_anchors = kwargs.get('strip_anchors', True)
        self.strip_metadata = kwargs.get('strip_metadata', True)
        self.strip_heading = kwargs.get('strip_heading', None)
        self.convert_math = kwargs.get('convert_math', True)
        self.width = kwargs.get('width', 100)
        self.add_chapter_heads = kwargs.get('add_chapter_heads', True)
        self.add_page_break = kwargs.get('add_page_break', False)
        self.increase_heads = kwargs.get('increase_heads', True)
        self.numbered_headings = kwargs.get('numbered_headings', False)
        self.convert_admonition_md = kwargs.get('convert_admonition_md', False)
        self.text_refs = kwargs.get('text_refs', False)
        self.combined_md_lines = []
        self.html_bare = u''
        self.html = u''

        try:
            cfg = codecs.open(self.config_file, 'r', self.encoding)
        except IOError as e:
            raise FatalError("Couldn't open %s for reading: %s" % (self.config_file,
                                                                   e.strerror), 1)

        self.config = mkdocs.config.load_config(config_file=self.config_file)

        if not u'docs_dir' in self.config:
            self.config[u'docs_dir'] = u'docs'

        if not u'site_dir' in self.config:
            self.config[u'site_dir'] = u'site'

        # Set filters depending on markdown extensions from config
        # Defaults first...
        self.filter_include = False
        self.filter_toc = False

        # ...then override defaults based on config, if any:

        if u'markdown_extensions' in self.config:
            for ext in self.config[u'markdown_extensions']:
                extname = u''
                # extension entries may be dicts (for passing extension parameters)
                if type(ext) is dict:
                    extname = list(ext.keys())[0].split(u'(')[0]
                if type(ext) is str or type(ext) is self.encoding:
                    extname = ext

                if extname == u'markdown_include.include':
                    self.filter_include = True
                if extname == u'toc':
                    self.filter_toc = True

        cfg.close()

    def flatten_pages(self, pages, parent=None):
        """Recursively flattens pages data structure into a one-dimensional data structure"""
        flattened = []

        for page in pages:
            if type(page) in (str, self.encoding):
                flattened.append(Page(mkdocs.utils.filename_to_title(page), parent, page))

            if type(page) is list:
                flattened.append(page[1], parent, page[0])

            if type(page) is dict:
                if type(list(page.values())[0]) in (str, self.encoding):
                    flattened.append(Page(list(page.keys())[0], parent, list(page.values())[0]))

                if type(list(page.values())[0]) is list:
                    section_page = Page(list(page.keys())[0], parent, None, True)
                    flattened.append(section_page)

                    # Add children sections
                    flattened.extend(
                        self.flatten_pages(
                            list(page.values())[0],
                            section_page)
                    )

        return flattened


    def read_lines(self, page):
        lines_tmp = []
        if page.get_file_path() is not None:
            fname = os.path.join(self.config[u'docs_dir'], page.get_file_path())
            try:
                with codecs.open(fname, 'r', self.encoding) as p:
                    for line in p.readlines():
                        lines_tmp.append(line.rstrip())
            except IOError as e:
                raise FatalError("Couldn't open %s for reading: %s" % (fname,
                                                                        e.strerror), 1)
        else:
            # this is a parent section
            heading_line = '#' * page.get_level() + " " + page.get_title()
            lines_tmp.append(heading_line)
            
        return lines_tmp


    def combine(self):
        """User-facing conversion method. Returns combined document as a list of
        lines."""
        lines = []

        pages = self.flatten_pages(self.config[u'pages'])

        f_exclude = mkdocs_combine.filters.exclude.ExcludeFilter(
            exclude=self.exclude)

        f_include = mkdocs_combine.filters.include.IncludeFilter(
            base_path=self.config[u'docs_dir'],
            encoding=self.encoding)

        # build the page index used for cross referencing
        page_index = {}
        previous_heading = None

        for page in pages:
            page_index[page.get_file_path()] = page

            lines_tmp = self.read_lines(page)

            # Adjust header levels, insert chapter headings and adjust image paths.
            if self.increase_heads:
                f_headlevel = mkdocs_combine.filters.headlevels.HeadlevelFilter(page)
                lines_tmp = f_headlevel.run(lines_tmp)

            # strip an entire section (defined by its heading) out of the document
            if self.strip_heading is not None:
                lines_tmp = mkdocs_combine.filters.heading.HeadingFilter(self.strip_heading).run(lines_tmp)

            f_heading_indexer = mkdocs_combine.filters.xref.HeadingIndexer(
                page,
                previous_heading,
                self.numbered_headings)
            
            f_heading_indexer.run(lines_tmp)
            previous_heading = f_heading_indexer.get_current_heading()

            

        for page in pages:
            # exclude file if it is listed in the excludes
            if self.exclude is not None:
                if page.get_file_path() in self.exclude:
                    continue

            lines_tmp = self.read_lines(page)
            
            f_chapterhead = mkdocs_combine.filters.chapterhead.ChapterheadFilter(
                headlevel=page.get_level(),
                title=page.get_title()
            )

            f_image = mkdocs_combine.filters.images.ImageFilter(
                filename=page.get_file_path(),
                image_path=self.config[u'site_dir'],
                image_ext=self.image_ext)

            f_xref = mkdocs_combine.filters.xref.XrefFilter(
                page, 
                page_index,
                self.text_refs,
                self.numbered_headings)

            if self.exclude:
                lines_tmp = f_exclude.run(lines_tmp)

            if self.filter_include:
                lines_tmp = f_include.run(lines_tmp)

            lines_tmp = mkdocs_combine.filters.metadata.MetadataFilter().run(lines_tmp)

            # Adjust header levels, insert chapter headings and adjust image paths.
            if self.increase_heads:
                f_headlevel = mkdocs_combine.filters.headlevels.HeadlevelFilter(page)
                lines_tmp = f_headlevel.run(lines_tmp)
            if self.add_chapter_heads:
                lines_tmp = f_chapterhead.run(lines_tmp)
            lines_tmp = f_image.run(lines_tmp)

            # strip an entire section (defined by its heading) out of the document
            if self.strip_heading is not None:
                lines_tmp = mkdocs_combine.filters.heading.HeadingFilter(self.strip_heading).run(lines_tmp)

            # Fix cross references
            if self.filter_xrefs:
                lines_tmp = f_xref.run(lines_tmp)

            lines.extend(lines_tmp)
            # Add an empty line between pages to prevent text from a previous
            # file from butting up against headers in a subsequent file.
            lines.append('')
            if self.add_page_break:
                lines.append('\\newpage')
                lines.append('')

        # Strip anchor tags
        if self.strip_anchors:
            lines = mkdocs_combine.filters.anchors.AnchorFilter().run(lines)

        # Convert math expressions
        if self.convert_math:
            lines = mkdocs_combine.filters.math.MathFilter().run(lines)

            # Convert admonitions already for Markdown output
        if self.convert_admonition_md:
            lines = mkdocs_combine.filters.admonitions.AdmonitionFilter().run(lines)
        if self.filter_toc:
            lines = mkdocs_combine.filters.toc.TocFilter().run(lines)

        if self.filter_tables:
            lines = mkdocs_combine.filters.tables.TableFilter().run(lines)

        self.combined_md_lines = lines
        return (self.combined_md_lines)

    def to_html(self):
        md = u"\n".join(self.combined_md_lines)
        mkdocs_extensions = self.config.get(u'markdown_extensions', [])
        extensions = ['markdown.extensions.attr_list']
        extension_configs = self.config.get(u'mdx_configs', [])
        for ext in mkdocs_extensions:
            if type(ext) is str or type(ext) is self.encoding:
                extname = str(ext)
                extensions.append(extname)
            elif type(ext) is dict:
                extname = str(ext.keys()[0])
                extensions.append(extname)
                extension_configs[extname] = ext[extname]
        self.html_bare = markdown.markdown(md, extensions=extensions,
                                           extension_configs=extension_configs,
                                           output_format='html5')
        self.html = u"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        </head>
        <body>
        {}
        </body>
        </html>
        """.format(self.html_bare)
        return (self.html)
