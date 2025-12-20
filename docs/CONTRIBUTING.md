# 🤝 Contributing to Autom8

Thank you for your interest in contributing to Autom8! This document provides guidelines and instructions for contributing.

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Our Standards

**Positive behavior includes**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes**:
- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

## How to Contribute

### Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md):

1. Check existing issues first
2. Use a clear, descriptive title
3. Provide detailed steps to reproduce
4. Include system information
5. Add screenshots if applicable

### Suggesting Features

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md):

1. Check if feature already requested
2. Explain the problem it solves
3. Describe your proposed solution
4. Consider alternatives

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Update documentation
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/orenyalphy256-glitch/op-alpha-systems-automation.git
cd op-alpha-systems-automation
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

### 5. Run Tests

```bash
pytest tests/ -v
```

## Coding Standards

### Python Style Guide

- Follow **PEP 8**
- Use **Black** for formatting (line length: 100)
- Use **type hints** for function signatures
- Write **docstrings** for all public functions/classes

### Code Formatting

```bash
# Format code
black autom8/ tests/

# Sort imports
isort autom8/ tests/ --profile black

# Check linting
flake8 autom8/ tests/
```

### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

## Testing Requirements

### Writing Tests

- Place tests in `tests/` directory
- Use descriptive test names: `test_<functionality>_<scenario>`
- Follow AAA pattern (Arrange, Act, Assert)
- Aim for >80% code coverage

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=autom8 --cov-report=html

# Specific test file
pytest tests/unit/test_api.py -v

# Watch mode
pytest-watch
```

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(api): add contact search endpoint

Implement search functionality for contacts with
filtering by name, phone, and email.

Closes #123
```

```
fix(security): resolve JWT token expiration issue

Fixed bug where tokens were not properly validated
for expiration time.

Fixes #456
```

## Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

**Examples**:
- `feature/contact-search`
- `fix/jwt-expiration`
- `docs/api-reference`

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code is formatted (Black, isort)
- [ ] Linting passes (Flake8)
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] Branch is up-to-date with main

### PR Template

Use the provided [PR template](.github/PULL_REQUEST_TEMPLATE.md)

### Review Process

1. **Automated checks** run (CI/CD pipeline)
2. **Code review** by maintainer
3. **Feedback** addressed
4. **Approval** and merge

## Documentation

### Update Documentation

When adding features:
- Update relevant `.md` files
- Add docstrings to code
- Update API documentation
- Add examples

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep formatting consistent

## Release Process

1. Update version in `setup.py` and `__init__.py`
2. Update `CHANGELOG.md`
3. Create release tag
4. Build and test
5. Deploy to production

## Questions?

- **Email**: orenyalphy256@gmail.com
- **Issues**: [GitHub Issues](https://github.com/orenyalphy256-glitch/op-alpha-systems-automation/issues)

---

Thank you for contributing to Autom8! 🚀
