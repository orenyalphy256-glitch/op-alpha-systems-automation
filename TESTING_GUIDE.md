# 🧪 Testing Guide - Autom8 Systems

Complete guide to testing the Autom8 application.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Coverage](#coverage)
6. [Best Practices](#best-practices)
7. [Load testing](#load-testing)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Run All Tests

```bash
# Full test suite with coverage
run-tests.bat

# Quick run (unit tests only, stop on first failure)
run-tests-quick.bat
```

### Run Specific Test Types

```bash
# Unit tests only
run-tests-unit.bat

# Integration tests only
run-tests-integration.bat
```

### Watch Mode (Auto-rerun on changes)

```bash
run-tests-watch.bat
```

---

## 📁 Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_models.py       # Model tests
│   ├── test_core.py         # Core utility tests
│   └── test_tasks.py        # Task function tests
├── integration/             # Integration tests (slower, with dependencies)
│   ├── __init__.py
│   ├── test_api.py          # API endpoint tests
│   ├── test_database.py     # Database integration tests
│   └── test_scheduler.py    # Scheduler integration tests
└── fixtures/                # Test data and fixtures
    ├── __init__.py
```

---

## 🏃 Running Tests

### Command Line Options

```bash
# Verbose output
pytest -v

# Stop on first failure
pytest --maxfail=1

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test function
pytest tests/unit/test_models.py::test_contact_creation

# Run specific test class
pytest tests/unit/test_models.py::TestContactModel

# Run tests matching pattern
pytest -k "contact"

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration

# Run tests with markers
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### Coverage Options

```bash
# Run with coverage
pytest --cov=autom8

# Coverage with missing lines
pytest --cov=autom8 --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=autom8 --cov-report=html
# Open htmlcov/index.html in browser

# Fail if coverage below threshold
pytest --cov=autom8 --cov-fail-under=80
```

---

## ✍ Writing Tests

### Test File Naming

- **Files:** `test_*.py` or `*_test.py`
- **Functions:** `test_*`
- **Classes:** `Test*`
- **Methods:** `test_*`

### Basic Test Structure (AAA Pattern)

```python
def test_example():
    # ARRANGE: Set up test data
    input_data = {"key": "value"}

    # ACT: Perform the action
    result = function_to_test(input_data)

    # ASSERT: Verify the result
    assert result == expected_output
```

### Using Fixtures

```python
def test_with_fixture(test_db, sample_contact):
    """Test using shared fixtures from conftest.py"""
    # test_db and sample_contact automatically provided
    contact = Contact(**sample_contact)
    test_db.add(contact)
    test_db.commit()

    assert contact.id is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    """Test multiple inputs with one function."""
    assert square(input) == expected
```

### Testing Exceptions

```python
def test_exception_raised():
    """Test that function raises expected exception."""
    with pytest.raises(ValueError):
        function_that_should_raise()

def test_exception_message():
    """Test exception message matches pattern."""
    with pytest.raises(ValueError, match="invalid input"):
        function_that_should_raise()
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mock objects."""
    mock_service = Mock()
    mock_service.call.return_value = "mocked result"

    result = function_using_service(mock_service)

    mock_service.call.assert_called_once()
    assert result == "mocked result"

@patch('module.external_function')
def test_with_patch(mock_function):
    """Test using patch decorator."""
    mock_function.return_value = "patched"

    result = function_that_calls_external()

    assert result == "patched"
```

---

## 📊 Coverage

### Understanding Coverage

**Coverage Types:**

- **Line Coverage:** % of code lines executed
- **Branch Coverage:** % of code branches (if/else) taken
- **Function Coverage:** % of functions called

**Example:**

```python
def calculate_discount(price, is_member):
    if is_member:           # Line 1 ✅
        discount = 0.20     # Line 2 ✅
    else:                   # Line 3 ✅
        discount = 0.10     # Line 4 ❌ Not covered!
    return price * discount # Line 5 ✅

# Test only covers is_member=True branch
# Line coverage: 80% (4/5 lines)
# Branch coverage: 50% (1/2 branches)
```

### Coverage Goals

- **Minimum:** 70% (acceptable)
- **Target:** 80% (good)
- **Excellent:** 90%+ (great)
- **100%:** Usually overkill (diminishing returns)

### Viewing Coverage Reports

**Terminal:**

```bash
pytest --cov=autom8 --cov-report=term-missing
```

**HTML Report:**

```bash
pytest --cov=autom8 --cov-report=html
# Open htmlcov/index.html
```

**Coverage for Specific Files:**

```bash
coverage report --include="autom8/models.py"
```

---

## 💡 Best Practices

### DO ✅

1. **Follow AAA Pattern:** Arrange, Act, Assert
2. **One assertion per test:** Test one thing at a time
3. **Use descriptive names:** `test_user_creation_with_valid_data`
4. **Use fixtures:** Reuse setup code
5. **Test edge cases:** Empty lists, None values, boundaries
6. **Keep tests fast:** Unit tests in milliseconds
7. **Make tests independent:** Each test should run standalone
8. **Test behavior, not implementation:** Focus on what, not how
9. **Use markers:** Organize tests (`@pytest.mark.unit`)
10. **Write tests first (TDD):** Red → Green → Refactor

### DON'T ❌

1. **Don't test external services:** Mock them instead
2. **Don't hardcode values:** Use fixtures and variables
3. **Don't skip cleanup:** Use fixtures with yield
4. **Don't test frameworks:** Trust Flask, SQLAlchemy work
5. **Don't make tests dependent:** Test order shouldn't matter
6. **Don't ignore warnings:** Fix them
7. **Don't commit failing tests:** Fix or skip (@pytest.mark.skip)
8. **Don't duplicate test code:** Use fixtures and helpers
9. **Don't test private methods:** Test through public interface
10. **Don't aim for 100% coverage:** Focus on critical paths

---

## 🎯 Test Markers

### Available Markers

```python
@pytest.mark.unit        # Unit tests (fast, isolated)
@pytest.mark.integration # Integration tests (slower)
@pytest.mark.slow        # Slow tests (can skip in quick runs)
@pytest.mark.api         # API endpoint tests
@pytest.mark.database    # Database tests
@pytest.mark.scheduler   # Scheduler tests
```

### Using Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run API and database tests
pytest -m "api or database"
```

---

## 🐝 Load Testing

Autom8 uses **Locust** for distributed load testing. The included `locustfile.py` is configured with smart discovery logic.

### Running a Load Test

```bash
# Standard test (Headless)
locust -f locustfile.py --headless -u 10 -r 2 -t 5m --host=http://localhost:5000

# Web Interface (Best for live monitoring)
locust -f locustfile.py --host=http://localhost:5000
# Open http://localhost:8089 in your browser
```

### Smart ID Tracking
The load testing script automatically queries `/api/v1/contacts` on startup to discover existing IDs. This prevents `404 Not Found` errors during DELETE and GET tasks.

---

## 🔍 Troubleshooting

### Tests Not Found

**Problem:** Pytest doesn't find your tests

**Solution:**

- Check file naming: `test_*.py` or `*_test.py`
- Check function naming: `test_*`
- Check class naming: `Test*`
- Verify `__init__.py` exists in test directories

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'autom8'`

**Solution:**

```bash
# Install package in development mode
pip install -e .

# Or add to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;C:\path\to\project
```

### Database Locked

**Problem:** `sqlite3.OperationalError: database is locked`

**Solution:**

- Use in-memory database for tests: `sqlite:///:memory:`
- Close database connections in fixtures
- Use `scope="function"` for db fixtures

### Tests Pass Individually But Fail Together

**Problem:** Tests interfere with each other

**Solution:**

- Make tests independent
- Use fresh fixtures (`scope="function"`)
- Check for global state mutation
- Clean up after each test

### Slow Tests

**Problem:** Tests take too long

**Solution:**

- Move slow tests to integration suite
- Use `@pytest.mark.slow` marker
- Mock external services
- Use in-memory databases
- Run unit tests only: `pytest tests/unit`

### Coverage Not Accurate

**Problem:** Coverage shows 100% but code not tested

**Solution:**

- Check assertions: Are you actually verifying results?
- Review excluded lines in `.coveragerc`
- Look at branch coverage: `pytest --cov-branch`
- Coverage measures execution, not correctness!

---

## 📈 Coverage Improvement Tips

### Identify Untested Code

```bash
# Generate HTML report
pytest --cov=autom8 --cov-report=html

# Open htmlcov/index.html
# Red lines = not covered
# Yellow lines = partially covered
# Green lines = covered
```

### Focus on Critical Paths

1. **Business logic:** Core functionality
2. **Public APIs:** User-facing interfaces
3. **Error handling:** Exception paths
4. **Edge cases:** Boundary conditions

### Don't Over-Test

**Skip:**

- Framework code (Flask, SQLAlchemy)
- Third-party libraries
- Trivial getters/setters
- Configuration files

---

## 🎓 Example Test Workflow

### 1. Write Failing Test (Red)

```python
def test_new_feature():
    result = new_feature(input_data)
    assert result == expected
```

Run: `pytest -k test_new_feature` → ❌ FAILS

### 2. Write Minimal Code (Green)

```python
def new_feature(data):
    return expected  # Just enough to pass
```

Run: `pytest -k test_new_feature` → ✅ PASSES

### 3. Refactor (Blue)

```python
def new_feature(data):
    # Proper implementation
    processed = process_data(data)
    return calculate_result(processed)
```

Run: `pytest` → ✅ ALL PASS

### 4. Check Coverage

```bash
pytest --cov=autom8 --cov-report=term-missing
```

---

## 📚 Additional Resources

### Pytest Documentation

- [Official Docs](https://docs.pytest.org/)
- [Fixtures Guide](https://docs.pytest.org/en/stable/fixture.html)
- [Parametrization](https://docs.pytest.org/en/stable/parametrize.html)

### Coverage Documentation

- [Coverage.py](https://coverage.readthedocs.io/)

### Testing Philosophy

- [Test-Driven Development (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)
- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

---

## ✅ Testing Checklist

- [ ] Install pytest and dependencies
- [ ] Configure pytest.ini
- [ ] Create test directory structure
- [ ] Write shared fixtures (conftest.py)
- [ ] Write unit tests for models
- [ ] Write unit tests for core utilities
- [ ] Write unit tests for tasks
- [ ] Write integration tests for API
- [ ] Write integration tests for database
- [ ] Create test runner scripts
- [ ] Configure coverage (.coveragerc)
- [ ] Run full test suite
- [ ] Achieve 80%+ coverage
- [ ] Generate coverage reports
- [ ] Document testing approach
- [ ] Create TESTING_GUIDE.md
