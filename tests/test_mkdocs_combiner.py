import pytest
from mkdocs_combine.mkdocs_combiner import MkDocsCombiner

# TODO: Create dummy mkdocs.yml and docs/ files for testing

def test_mkdocs_combiner_instantiation(tmp_path):
    """
    Test that MkDocsCombiner can be instantiated.
    """
    # Create a dummy mkdocs.yml file
    mkdocs_yml_content = """
site_name: Test Site
docs_dir: docs
nav:
    - Home: index.md
"""
    mkdocs_yml_file = tmp_path / "mkdocs.yml"
    mkdocs_yml_file.write_text(mkdocs_yml_content)

    # Create a dummy docs/index.md file
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    index_md_content = """
# Home
This is the home page.
"""
    index_md_file = docs_dir / "index.md"
    index_md_file.write_text(index_md_content)

    try:
        combiner = MkDocsCombiner(config_file=str(mkdocs_yml_file))
        assert combiner is not None
    except Exception as e:
        pytest.fail(f"MkDocsCombiner instantiation failed: {e}")


def test_mkdocs_combiner_combine_basic(tmp_path):
    """
    Test basic document combination.
    """
    # Create a dummy mkdocs.yml file
    mkdocs_yml_content = """
site_name: Test Site
docs_dir: docs
nav:
    - Home: index.md
    - About: about.md
"""
    mkdocs_yml_file = tmp_path / "mkdocs.yml"
    mkdocs_yml_file.write_text(mkdocs_yml_content)

    # Create dummy Markdown files
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    index_md_content = """
# Home
This is the home page.
""".strip()
    index_md_file = docs_dir / "index.md"
    index_md_file.write_text(index_md_content)

    about_md_content = """
# About
This is the about page.
""".strip()
    about_md_file = docs_dir / "about.md"
    about_md_file.write_text(about_md_content)

    combiner = MkDocsCombiner(config_file=str(mkdocs_yml_file))
    combined_lines = combiner.combine()

    expected_lines = [
        '# Home {: .page-title}',
        '',
        '## Home', # Offset by HeadlevelFilter
        'This is the home page.',
        '',
        '# About {: .page-title}',
        '',
        '## About', # Offset by HeadlevelFilter
        'This is the about page.',
        '',
    ]
    assert combined_lines == expected_lines


def test_mkdocs_combiner_keep_metadata(tmp_path):
    """
    Test document combination with strip_metadata=False.
    YAML metadata should be kept.
    """
    mkdocs_yml_content = """
site_name: Test Site
docs_dir: docs
nav:
    - Home: index.md
"""
    mkdocs_yml_file = tmp_path / "mkdocs.yml"
    mkdocs_yml_file.write_text(mkdocs_yml_content)

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    index_md_content = """---
title: My Document Title
author: Test Author
---
# Content Title
This is the actual content.
""".strip()
    (docs_dir / "index.md").write_text(index_md_content)

    # increase_heads=True (default), add_chapter_heads=True (default)
    # HeadlevelFilter.offset will be 1.
    combiner = MkDocsCombiner(config_file=str(mkdocs_yml_file), strip_metadata=False)
    combined_lines = combiner.combine()

    expected_lines = [
        '# Home {: .page-title}', # Chapter head
        '',
        '---',                    # Metadata kept
        'title: My Document Title',
        'author: Test Author',
        '---',
        '## Content Title',       # Original H1, offset by HeadlevelFilter
        'This is the actual content.',
        '',
    ]
    assert combined_lines == expected_lines


def test_mkdocs_combiner_combine_no_chapter_heads(tmp_path):
    """
    Test document combination with add_chapter_heads=False.
    Titles from mkdocs.yml should not be added.
    """
    mkdocs_yml_content = """
site_name: Test Site
docs_dir: docs
nav:
    - Home: index.md
    - About: about.md
"""
    mkdocs_yml_file = tmp_path / "mkdocs.yml"
    mkdocs_yml_file.write_text(mkdocs_yml_content)

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    index_md_content = """
# Home Content
This is the home page.
""".strip()
    (docs_dir / "index.md").write_text(index_md_content)

    about_md_content = """
# About Content
This is the about page.
""".strip()
    (docs_dir / "about.md").write_text(about_md_content)

    # increase_heads is True by default, so content headers will be offset.
    # HeadlevelFilter.offset will be 1.
    combiner = MkDocsCombiner(config_file=str(mkdocs_yml_file), add_chapter_heads=False)
    combined_lines = combiner.combine()

    expected_lines = [
        '## Home Content', # Original H1, offset by HeadlevelFilter
        'This is the home page.',
        '',
        '## About Content', # Original H1, offset by HeadlevelFilter
        'This is the about page.',
        '',
    ]
    assert combined_lines == expected_lines


def test_mkdocs_combiner_combine_no_increase_heads(tmp_path):
    """
    Test document combination with increase_heads=False.
    Header levels in content should not change.
    """
    mkdocs_yml_content = """
site_name: Test Site
docs_dir: docs
nav:
    - Page1: page1.md
    - Section:
        - Page2: page2.md
"""
    mkdocs_yml_file = tmp_path / "mkdocs.yml"
    mkdocs_yml_file.write_text(mkdocs_yml_content)

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    page1_md_content = """
# Page 1 Title
Content of page 1.
## Subheading
""".strip()
    (docs_dir / "page1.md").write_text(page1_md_content)

    page2_md_content = """
# Page 2 Title
Content of page 2.
### SubSubheading
""".strip()
    (docs_dir / "page2.md").write_text(page2_md_content)

    combiner = MkDocsCombiner(config_file=str(mkdocs_yml_file), increase_heads=False)
    combined_lines = combiner.combine()

    # Expected: Chapter titles added, original headers unchanged.
    # HeadlevelFilter.offset would be 2 for Page2 if increase_heads was True.
    expected_lines = [
        '# Page1 {: .page-title}',
        '',
        '# Page 1 Title',
        'Content of page 1.',
        '## Subheading',
        '',
        '# Section {: .page-title}', # This is a section title, not a file
        '',
        '', # Empty line for the section itself
        '## Page2 {: .page-title}', # page title for page2, level 2
        '',
        '# Page 2 Title',
        'Content of page 2.',
        '### SubSubheading',
        '',
    ]
    assert combined_lines == expected_lines
