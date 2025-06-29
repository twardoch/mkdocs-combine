# TODO List for mkdocs-combine

## Immediate Tasks (Critical)

- [ ] Migrate codebase from Python 2.7 to Python 3.8+
- [ ] Replace all `unicode` and string type checks with Python 3 equivalents
- [ ] Update setup.py to use modern Python packaging standards
- [ ] Fix all imports to use Python 3 style
- [ ] Update exception handling syntax throughout codebase
- [ ] Replace `codecs.open()` with built-in `open()` with encoding

## Testing and Quality

- [ ] Create test directory structure
- [ ] Write unit tests for each filter class
- [ ] Add integration tests for full document processing
- [ ] Set up pytest configuration
- [ ] Add GitHub Actions workflow for CI/CD
- [ ] Configure pre-commit hooks with black, ruff, and mypy
- [ ] Add .gitignore entries for Python 3 artifacts

## Code Refactoring

- [ ] Break down MkDocsCombiner class into smaller components
- [ ] Create abstract base class for filters
- [ ] Implement proper error handling with custom exceptions
- [ ] Add type hints to all functions and methods
- [ ] Use pathlib instead of os.path for file operations
- [ ] Implement logging instead of print statements

## Feature Additions

- [ ] Add direct PDF output support
- [ ] Add EPUB generation capability
- [ ] Implement progress bar for processing
- [ ] Add dry-run mode
- [ ] Support for copying images to output directory
- [ ] Add support for Mermaid diagrams
- [ ] Implement YAML frontmatter preservation option

## Documentation

- [ ] Update README.md with Python 3 requirements
- [ ] Create comprehensive API documentation
- [ ] Add usage examples for each output format
- [ ] Write migration guide from v0.4 to new version
- [ ] Document all command-line options
- [ ] Create CONTRIBUTING.md
- [ ] Add inline code documentation

## Packaging and Distribution

- [ ] Create pyproject.toml
- [ ] Update package metadata in setup.py
- [ ] Create GitHub release workflow
- [ ] Set up automatic PyPI deployment
- [ ] Create Docker image
- [ ] Update installation instructions

## Performance

- [ ] Profile current performance bottlenecks
- [ ] Optimize regex patterns in filters
- [ ] Implement caching for repeated operations
- [ ] Add option for parallel processing

## Bug Fixes

- [ ] Fix Windows path handling issues
- [ ] Handle missing includes gracefully
- [ ] Fix table cell wrapping breaking URLs
- [ ] Improve cross-reference handling

## Future Considerations

- [ ] Investigate converting to MkDocs plugin
- [ ] Add VS Code extension
- [ ] Create web-based version
- [ ] Support for multiple input formats
- [ ] Integration with documentation hosting services