from mkdocs_combine.slugify import slugify

class Page(object):
    def __init__(self, title, parent=None, file_path=None, is_section=False):
        self.title = title
        self.parent = parent
        self.file_path = file_path
        self.is_section = is_section
        self.heading_index = {}
        self.headings = []

    def get_slug(self):
        slugs = []

        current_page = self
        while(current_page is not None):
            slugs.insert(0, slugify(current_page.get_title()))
            current_page = current_page.get_parent()
        
        if len(slugs) == 0:
            return None

        slug = "--".join(slugs)
        return slug
    
    def get_is_section():
        return self.is_section 

    def get_title(self):
        return self.title
    
    def get_parent(self):
        return self.parent

    def get_file_path(self):
        return self.file_path

    def add_heading(self, heading):
        if len(self.headings) == 0:
            # title heading
            self.heading_index[self.get_slug()] = heading
        else:
            while heading.get_unique_title_slug() in self.heading_index:
                title_id = heading.get_unique_title_id()
                heading.set_unique_title_id(title_id + 1)

        self.headings.append(heading)
        self.heading_index[heading.get_unique_title_slug()] = heading

    def get_heading(self, heading_slug):
        if heading_slug in self.heading_index:
            return self.heading_index[heading_slug]
        
        if len(self.headings) > 0:
            # title heading
            return self.headings[0]
        
        return None
    
    def get_headings(self):
        return self.headings

    def get_level(self):
        level = 0
        current_page = self

        while(current_page is not None):
            level += 1
            current_page = current_page.get_parent()
        
        return level

    def __repr__(self):
        return "Page(title: {}, file_path: {})".format(self.get_title(), self.get_file_path())