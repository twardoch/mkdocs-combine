# Changelog

## Recent Changes (2025-06-25)

### Code Quality Improvements
- **Major code refactoring**: Extensive refactoring of the entire codebase for better readability and maintainability
- **Python 3 compatibility**: Improved support for Python 3 (str/unicode type handling)
- **Code style improvements**: Better formatting and consistency across all modules

### Bug Fixes
- **Header level processing**: Fixed issue where header levels were being changed inside code blocks (by Ir1dXD)
- **Cross-reference regex**: Made regex more robust for handling cross-references (by Ir1dXD)

### Previous Release (0.4.0.0) by Daniel Nüst
- Add verbose option and some logging
- Single version definition in setup.py
- Switch to mkdocs 1.0.4 or later, including support for new "nav" config property, which deprecates "pages"

### Known Issues
- Python 2.7 is still the primary supported version, but Python 3 compatibility has been improved
- Some imports and type handling may need further refinement for full Python 3 support
- The project note mentions that MkDocs now supports plugins that provide a better architecture for this task