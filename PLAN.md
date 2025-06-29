# Improvement Plan for mkdocs-combine

## Overview
This document outlines a comprehensive plan to modernize and improve the mkdocs-combine project. The project currently converts MkDocs documentation into a single Markdown file, but it's built on older standards (Python 2.7) and needs significant updates to remain relevant and maintainable.

## 1. Python Modernization

### 1.1 Full Python 3 Migration
Currently, the codebase targets Python 2.7 which reached end-of-life in 2020. This creates security risks and limits the use of modern Python features.

**Steps:**
1. Update all string handling to use Python 3's unified string type
2. Replace all `unicode` references with proper Python 3 string handling
3. Update print statements to print functions throughout the codebase
4. Use `pathlib` for path operations instead of `os.path`
5. Replace `codecs.open()` with built-in `open()` with encoding parameter
6. Update exception handling syntax from `except Exception, e:` to `except Exception as e:`
7. Use type hints throughout the codebase for better maintainability

### 1.2 Dependencies Update
- Update minimum Python version to 3.8+ (or 3.9+ for better type hints)
- Update all dependencies to their latest compatible versions
- Add proper dependency version constraints in setup.py

## 2. Code Architecture Improvements

### 2.1 Plugin Architecture
The README mentions that MkDocs now supports plugins that provide better architecture. We should consider:
1. Investigating the MkDocs plugin architecture
2. Potentially rewriting this as a proper MkDocs plugin
3. Or at minimum, align with MkDocs plugin conventions

### 2.2 Modular Design
The current `MkDocsCombiner` class is monolithic (300+ lines). Break it down into:
- `ConfigManager`: Handle configuration loading and validation
- `PageProcessor`: Handle individual page processing
- `FilterChain`: Manage the filter pipeline
- `OutputFormatter`: Handle different output formats

### 2.3 Filter System Refactoring
Current filters are somewhat scattered. Create a proper filter interface:
```python
class BaseFilter(ABC):
    @abstractmethod
    def process(self, lines: List[str]) -> List[str]:
        pass
```

## 3. Feature Enhancements

### 3.1 Output Format Support
Currently supports Markdown and basic HTML. Add:
- **PDF generation**: Direct PDF output using libraries like WeasyPrint or ReportLab
- **EPUB generation**: Direct EPUB output without requiring pandoc
- **DOCX support**: Microsoft Word format output
- **AsciiDoc output**: For technical documentation workflows

### 3.2 Enhanced Markdown Processing
- Support for Mermaid diagrams
- Better handling of footnotes
- Support for definition lists
- Enhanced table processing with alignment preservation

### 3.3 Asset Management
Currently, image handling is basic. Improve:
- Copy referenced images to output directory
- Support for relative image paths
- Handle other assets (CSS, JS for HTML output)
- Option to embed images as base64 in HTML output

## 4. Quality and Testing

### 4.1 Test Suite
Currently no visible test suite. Implement:
- Unit tests for each filter
- Integration tests for full document processing
- Test fixtures with sample MkDocs projects
- Property-based testing for filters
- Coverage target: 80%+

### 4.2 Code Quality Tools
- Add pre-commit hooks
- Configure black for code formatting
- Use ruff for linting
- Add mypy for type checking
- Configure GitHub Actions for CI/CD

### 4.3 Documentation
- Comprehensive API documentation
- Usage examples for each feature
- Migration guide from current version
- Contributing guidelines

## 5. Packaging and Distribution

### 5.1 Modern Packaging
- Migrate from setup.py to pyproject.toml
- Use Poetry or PDM for dependency management
- Proper semantic versioning
- Automated releases via GitHub Actions

### 5.2 Installation Methods
- Ensure pip installation works smoothly
- Consider conda-forge distribution
- Docker image for easy usage
- Homebrew formula for macOS users

## 6. Performance Optimization

### 6.1 Processing Speed
- Profile current performance bottlenecks
- Implement parallel processing for multiple files
- Optimize regex operations in filters
- Consider using compiled regex patterns

### 6.2 Memory Usage
- Stream processing for large documents
- Lazy loading of files
- Efficient string concatenation

## 7. User Experience

### 7.1 CLI Improvements
- Better progress indicators
- Colored output for better readability
- Interactive mode for configuration
- Dry-run option to preview changes

### 7.2 Error Handling
- Clear error messages with actionable advice
- Validate MkDocs configuration before processing
- Handle missing files gracefully
- Provide debugging mode with detailed logs

## 8. Compatibility and Integration

### 8.1 MkDocs Version Support
- Test with multiple MkDocs versions
- Handle deprecated features gracefully
- Support for MkDocs themes and their specific requirements

### 8.2 Ecosystem Integration
- VS Code extension for live preview
- GitHub Action for automated documentation building
- GitLab CI templates
- Integration with Read the Docs

## Implementation Priority

### Phase 1: Foundation (1-2 months)
1. Python 3 migration
2. Basic test suite
3. CI/CD setup
4. Code formatting and linting

### Phase 2: Architecture (2-3 months)
1. Modular design implementation
2. Filter system refactoring
3. Comprehensive testing
4. Performance optimization

### Phase 3: Features (2-3 months)
1. New output formats
2. Enhanced Markdown processing
3. Asset management
4. CLI improvements

### Phase 4: Polish (1-2 months)
1. Documentation
2. Examples and tutorials
3. Community building
4. Release preparation

## Success Metrics
- Python 3 only codebase
- 80%+ test coverage
- Support for 3+ additional output formats
- 50% performance improvement
- Active community with regular contributions
- Compatible with latest MkDocs versions