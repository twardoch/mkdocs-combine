import re

def slugify(string):
    slug = string.strip()
    slug = slug.replace(' ', '-')
    slug = slug.lower()
    slug = re.sub(r'([^a-z0-9\-\_])', '', slug)
    return slug
