from mkdocs_combine.slugify import slugify

class Heading(object):
    def __init__(self, title, level, page, number=None, unique_title_id=0):
        self.title = title
        self.level = level
        self.number = number
        self.unique_title_id = unique_title_id

        if self.number is not None:
            if self.level != len(self.number):
                print("Warning: levels don't match number {} and level {}".format(self.level, self.number))

        self.page = page

    def get_unique_title_id(self):
        return self.unique_title_id

    def set_unique_title_id(self, unique_title_id):
        self.unique_title_id = unique_title_id

    def get_page(self):
        return self.page

    def get_title_slug(self):
        """get slug which is just the title (e.g. "heading-title")."""
        return slugify(self.title)

    def get_slug(self):
        """get a slug which is composed of the filename which 
        this heading resides in, and the slug of the title 
        of this heading"""

        slug = self.page.get_slug() + "--" + self.get_unique_title_slug()
        return slug

    def get_unique_title_slug(self):
        """
        See self.set_unique_title_id()
        :param no_numbers_first: whether or not to prepend the slug with an "n"
                                 if there is a number as the first character
                                 because pandoc doesn't like nubmers being first
                                 in id slugs
        """
        slugs = []

        # page_slug = self.page.get_slug()
        # if page_slug is not None:
        #     slugs.append(page_slug)

        if self.get_unique_title_id() > 0:
            slugs.append(self.get_title_slug() + "_" + str(self.get_unique_title_id()))
        else:
            slugs.append(self.get_title_slug())

        # if no_numbers_first:
        #     number_expr = r'^[0-9]+.*'
        #     m = re.search(number_expr, slug)
        #     if m is not None:
        #         slug = "n" + slug
        
        slug = "-|-".join(slugs)
        return slug

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

    def get_title(self, numbered=False, pandoc_id=False):
        """get the title (e.g. "Heading Title")
        
        :param numbered:  get the title with the heading number prepended 
                          (e.g. "1.5.5 Heading Title")
        :param pandoc_id: get the title with the pandoc id attached
                          (e.g. "Heading Title {#heading-title}") 
                         
        """
        title = self.title

        if numbered:
            number = self.get_number_string()
            if number is not None:
                title = "#"*self.level + "{}  {}".format(number, title)

        if pandoc_id:
            title = "{} {{#{}}}".format(title, self.get_slug())

        return title

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
        return "[{}](#{})".format(self.get_reference_title(), self.get_slug())

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

    def __repr__(self):
        return "Heading(title: {}, unique_title_slug: {}, slug: {}".format(self.get_title(), self.get_unique_title_slug(), self.get_slug())