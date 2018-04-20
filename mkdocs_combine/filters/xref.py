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

def slugify(string):
    slug = string.strip()
    slug = slug.replace(' ', '-')
    slug = slug.replace('/', '-')
    slug = slug.replace('.', '-')
    slug = slug.lower()
    return slug

def strip_extension(filepath):
    return posixpath.splitext(filepath)[0]

class Heading(object):
    def __init__(self, title, level, page, number = None, unique_title_id=0):
        self.title = title
        self.level = level
        self.number = number
        self.unique_title_id = unique_title_id

        # print("title: {},  level: {},  number: {}".format(self.title, self.level, self.number))
        if self.number is not None:
            if self.level != len(self.number):
                print("Warning: levels don't match number {} and level {}".format(self.level, self.number))

        self.page = page

    def set_unique_title_id(self, new_unique_title_id: int):
        """set the unique id used during self.get_unique_title_slug()
        to produce a unique title slug. For example, if you call
        self.set_unique_title_id(5) and the title of the heading
        is "Heading Title", this will produce "heading-title-5".
        If the unique title id is 0, then the resulting slug will
        be "heading-title"."""
        self.unique_title_id = new_unique_title_id

    def get_page_slug(self):
        """get a slug which is composed of the filename which 
        this heading resides in (e.g. "subfolder-heading-title")"""

        filename_filepath = strip_extension(self.page[u'file'])
        return slugify(filename_filepath)

    def get_title_slug(self):
        """get slug which is just the title (e.g. "heading-title")."""
        return slugify(self.title)

    def get_slug(self):
        """get a slug which is composed of the filename which 
        this heading resides in, and the slug of the title 
        of this heading"""

        slug = self.get_page_slug() + "-" + self.get_title_slug()
        return slug

    def get_unique_title_slug(self):
        """
        See self.set_unique_title_id()
        """
        if self.unique_title_id > 0:
            return self.get_title_slug() + "-" + str(self.unique_title_id)
        else:
            return self.get_title_slug()

    def get_number_array(self):
        """ get the heading number as an array of integers (e.g. [1, 3, 5])"""
        return self.number

    def get_number_string(self):
        """get the heading number as a string (e.g. "1.3.5")"""
        if self.number is not None:
            return ".".join([str(i) for i in self.number])
        else:
            return None

    def __eq__(self, other):
        if isinstance(other, Heading):
            return self.get_slug() == other.get_slug()
        else:
            return False

    def get_title(self):
        """get the title (e.g. "Heading Title")"""
        return self.title

    def get_numbered_title(self):
        """get the title with the heading number prepended 
        (e.g. "1.5.5 Heading Title")"""
        title = self.title
        number = self.get_number_string()

        if number is not None:
            title = "#"*self.level + "{}  {}".format(number, title)
        
        return title

    def get_reference_link(self):
        """Get a markdown reference link to this heading
        (e.g. "[(1.3.5) Heading Title](#heading-title-5)" if this
        happens to be the 5th occurance of a heading with the title
        "Heading Title")."""
        return "[{}](#{})".format(self.get_reference_title(), self.get_unique_title_slug())

    def get_reference_title(self):
        """Get the title with its reference number, provided the number is
        present, otherwise just returns the title. 
        (e.g. "(1.3.5) Heading Title")."""
        number = self.get_number_string()

        if number is not None:
            return "({}) {}".format(number, self.title)
        else:
            return self.title

    def get_text_reference(self):
        """Get the text form of a reference to this heading
        (e.g. ***`(1.3.5) Heading Title`***"""
        return "**`{}`**".format(self.get_reference_title())

class HeadingIndexer(object):
    def __init__(self, page, heading_index, title_count_index, unique_title_index, numbered_headings: bool):
        """
        :param page:               the current page
        :param heading_index:      the index associating heading slugs (based on file paths)
                                   to the headings themselves
        :param title_count_index:  index associating a title slug to a count of how
                                   many times that title has been used
        :param unique_title_index: index associating unique title slugs to the
                                   headings themselves
        :param numbered_headings:  whether or not to show headings with numbers
        """
        self.page = page
        self.heading_index = heading_index
        self.title_count_index = title_count_index
        self.unique_title_index = unique_title_index
        self.numbered_headings = numbered_headings
        self.position_in_page = 0

    def run(self, lines): 
        last_heading_number = [0]

        if len(self.heading_index) > 0:
            last_item = list(self.heading_index.values())[-1]
            last_heading_number = last_item.get_number_array()

        for line in lines:
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
                self.heading_index[heading.get_slug()] = heading

                title_slug = heading.get_title_slug()
                new_title_count = 0
                if title_slug in self.title_count_index:
                    new_title_count = self.title_count_index[title_slug] + 1
                else:
                    new_title_count = 0

                heading.set_unique_title_id(new_title_count)
                unique_title_slug = heading.get_unique_title_slug()
                self.title_count_index[title_slug] = new_title_count
                self.unique_title_index[unique_title_slug] = heading

                # if it's the first heading on the page, then make this heading
                # correspond to the page slug
                if self.position_in_page == 0:
                    self.heading_index[heading.get_page_slug()] = heading

                last_heading_number = number
                self.position_in_page += 1

    def get_heading_index(self):
        return self.heading_index

class XrefFilter(object):
    """Replaces mkdocs style cross-references by just their title"""

    def __init__(self, page, page_index, heading_index, unique_title_index, text_refs: bool, numbered_headings: bool):
        """
        :param page:               the current page
        :param page_index:         index associating file paths (relative to doc root) 
                                   to pages
        :param heading_index:      the index associating heading slugs (based on file paths)
                                   to the headings themselves
        :param unique_title_index: index associating unique title slugs to the
                                   headings themselves
        :param text_refs:          whether or not to replace internal references with
                                   just a text reference (rather than a hyperlink)
        :param numbered_headings:  whether or not to show headings with numbers
        """
        self.page = page
        self.page_index = page_index
        self.heading_index = heading_index
        self.unique_title_index = unique_title_index
        self.text_refs = text_refs
        self.numbered_headings = numbered_headings
    
    def run(self, lines):
        """Filter method"""

        ret = list(lines)

        line_index = -1
        for line_index in range(0, len(lines)):
            line = ret[line_index]

            heading_expr = r'^(#+)(.*)'
            match = re.search(heading_expr, line)
            if match != None:
                level = len(match.group(1))
                title = match.group(2).strip()

                heading = Heading(title, level, self.page)

                numbered_heading = self.heading_index[heading.get_slug()]

                new_title = numbered_heading.get_numbered_title()

                if self.numbered_headings:
                    line = re.sub(r'^(#+)(.*)', new_title, line, count=1)
            
            # match on the links
            link_expr =r'\[(.*?)\]\((.*?\.md)#?(.*?)\)'
            for match in re.finditer(link_expr, line):
                old_link = match.group(0)
                title = match.group(1)
                file = match.group(2)
                subheading_slug = match.group(3)

                page_dir = posixpath.dirname(self.page[u'file'])
                link_file = posixpath.normpath(posixpath.join(page_dir, file))

                link_slug = slugify(strip_extension(link_file))
                
                if subheading_slug:
                    link_slug += "-" + subheading_slug

                matching_heading = self.heading_index[link_slug]

                link_page = self.page_index[link_file]
                
                if self.text_refs:
                    line = line.replace(old_link, matching_heading.get_text_reference())
                else:
                    line = line.replace(old_link, matching_heading.get_reference_link())
                    pass

            ret[line_index] = line

        return ret
