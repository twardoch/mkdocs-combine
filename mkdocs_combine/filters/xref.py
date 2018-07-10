# Copyright 2015 Johannes Grassler <johannes@btw23.de>
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

import re
import posixpath

from mkdocs_combine.page import Page
from mkdocs_combine.heading import Heading
from mkdocs_combine.slugify import slugify

def strip_extension(filepath):
    return posixpath.splitext(filepath)[0]

def code_block_expr():
    return r'[`][`][`]'

class HeadingIndexer(object):
    def __init__(self, page, previous_heading, numbered_headings: bool):
        """
        :param page:               the current page
        :param numbered_headings:  whether or not to show headings with numbers
        """
        self.page = page
        self.previous_heading = previous_heading
        self.numbered_headings = numbered_headings
        self.current_heading = None

    def get_current_heading(self):
        return self.current_heading

    def run(self, lines): 
        last_heading_number = [0]

        if self.previous_heading is not None:
            last_heading_number = self.previous_heading.get_number_array()

        code_block = False

        for line in lines:
            match = re.search(code_block_expr(), line)
            if match != None:
                code_block = not code_block
                continue

            if code_block:
                continue

            # match on the headings
            match = re.search(r'^(#+)(.*)', line)
            if match != None:
                level = len(match.group(1))
                title = match.group(2).strip()
                
                number = None
                if self.numbered_headings:
                    number = list(last_heading_number)
                    
                    if len(number) > level:
                        number = number[0:level]
                    
                    if level > len(number):
                        number = number + [0]
                    
                    number[-1] += 1

                heading = Heading(title, level, self.page, number)
                self.current_heading = heading
                self.page.add_heading(heading)

                title_slug = heading.get_title_slug()

                unique_title_slug = heading.get_unique_title_slug()

                last_heading_number = number

    def get_heading_index(self):
        return self.heading_index

class XrefFilter(object):
    """Replaces mkdocs style cross-references by just their title"""

    def __init__(self, page, page_index, text_refs: bool, numbered_headings: bool):
        """
        :param page:               the current page
        :param page_index:         index associating file paths (relative to doc root) 
                                   to pages
        :param text_refs:          whether or not to replace internal references with
                                   just a text reference (rather than a hyperlink)
        :param numbered_headings:  whether or not to show headings with numbers
        """
        self.page = page
        self.page_index = page_index
        self.text_refs = text_refs
        self.numbered_headings = numbered_headings
        self.processed_headings = []
    
    def run(self, lines):
        """Filter method"""

        ret = list(lines)
        code_block = False

        line_index = -1
        for line_index in range(0, len(lines)):
            line = ret[line_index]

            match = re.search(code_block_expr(), line)
            if match != None:
                code_block = not code_block
                continue

            if code_block:
                continue

            heading_expr = r'^(#+)(.*)'
            match = re.search(heading_expr, line)
            if match != None:
                level = len(match.group(1))
                title = match.group(2).strip()

                heading = Heading(title, level, self.page)
                
                indexed_heading = self.page.get_heading(heading.get_unique_title_slug())

                while indexed_heading in self.processed_headings:
                    heading.set_unique_title_id(heading.get_unique_title_id() + 1)
                    indexed_heading = self.page.get_heading(heading.get_unique_title_slug())
                    
                    if self.page.is_page_heading(indexed_heading):
                        break
                
                self.processed_headings.append(indexed_heading)

                new_title = indexed_heading.get_title(True, True)

                if self.numbered_headings:
                    line = re.sub(r'^(#+)(.*)', new_title, line, count=1)
            
            # match on the links [title](document.md#subheading)
            link_expr = r'\[(.*?)\]\(([^#]*?\.md)?(#(.*?))?\)'
            for match in re.finditer(link_expr, line):
                old_link = match.group(0)
                title = match.group(1)
                file = match.group(2)
                subheading_slug = match.group(4)

                if file is None and subheading_slug is None:
                    continue

                page_dir = posixpath.dirname(self.page.get_file_path())

                link_page = None

                if file is not None:
                    link_file = posixpath.normpath(posixpath.join(page_dir, file))

                    if link_file[0] == '/':
                        link_file = link_file[1:]

                    link_page = self.page_index[link_file]
                else:
                    link_page = self.page

                matching_heading = link_page.get_heading(subheading_slug)

                if self.text_refs:
                    line = line.replace(old_link, matching_heading.get_text_reference())
                else:
                    line = line.replace(old_link, matching_heading.get_reference_link())
                    pass

            ret[line_index] = line

        return ret
