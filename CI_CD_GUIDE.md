# 🚀 CI/CD Pipeline Guide - Autom8

A comprehensive guide to the Continuous Integration and Continuous Deployment pipeline for the Autom8 project.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Pipeline Stages](#pipeline-stages)
3. [Running Locally](#running-locally)
4. [GitHub Actions](#github-actions)
5. [Pre-commit Hooks](#pre-commit-hooks)
6. [Quality Gates](#quality-gates)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## 🎯 Overview

The Autom8 CI/CD pipeline automates the entire software delivery process:

| Feature | Description |
|---------|-------------|
| ✅ Code Quality | Linting with Flake8, formatting with Black |
| ✅ Security Scanning | Bandit for static analysis, pip-audit for dependencies |
| ✅ Automated Testing | Unit and integration tests with pytest |
| ✅ Coverage Enforcement | Minimum 80% code coverage required |
| ✅ Docker Build | Containerized deployment with multi-stage builds |
| ✅ Deployment Automation | Automated staging and production deploys |

### Pipeline Philosophy

- **Fast Feedback** — Complete pipeline in under 10 minutes
- **Fail Fast** — Stop immediately on critical errors
- **Quality Gates** — Enforce standards before deployment
- **Automation First** — Minimize manual intervention

---

## 🔄 Pipeline Stages

### Stage 1: Environment Setup

**Purpose:** Prepare the execution environment

```bash
✓ Verify Python version (3.11+)
✓ Validate virtual environment
✓ Check required tool installation
```

**Duration:** ~10 seconds

---

### Stage 2: Linting

**Purpose:** Enforce code quality standards

```bash
✓ Run Flake8 linter
✓ Check PEP8 compliance
✓ Identify code smells and complexity issues
```

**Quality Gate:** Non-blocking (warnings only)

**Quick Fix:**
```bash
flake8 autom8/ --count --statistics   # View issues
black autom8/                          # Auto-fix formatting
```

---

### Stage 3: Code Formatting

**Purpose:** Ensure consistent code style

```bash
✓ Run Black in check mode
✓ Verify isort import ordering
```

**Quality Gate:** Non-blocking

**Quick Fix:**
```bash
black autom8/                    # Format Python files
isort autom8/ --profile black    # Sort imports
```

---

### Stage 4: Security Analysis

**Purpose:** Identify security vulnerabilities

```bash
✓ Run Bandit security scanner
✓ Check for common security anti-patterns
✓ Scan dependencies with pip-audit
```

**Quality Gate:** Blocking on HIGH/CRITICAL severity

---

### Stage 5: Testing ⚠️ CRITICAL

**Purpose:** Verify application functionality

```bash
✓ Execute unit tests
✓ Execute integration tests
✓ Generate coverage report
```

**Quality Gate:**
- ✅ All tests must pass
- ✅ Code coverage ≥ 80%
- ❌ **Pipeline STOPS if tests fail**

> **Note:** This is a hard stop — the pipeline cannot proceed without passing tests.

---

### Stage 6: Docker Build

**Purpose:** Create production-ready container image

```bash
✓ Build Docker image
✓ Tag with 'latest' and timestamp
✓ Optimize image layers with caching
```

**Quality Gate:** Blocking — build must complete successfully

---

### Stage 7: Container Security Scan

**Purpose:** Scan container for vulnerabilities

```bash
✓ Run Trivy vulnerability scanner
✓ Check for CVEs in base images
✓ Validate image security posture
```

**Quality Gate:** Non-blocking (informational)

---

### Stage 8: Staging Deployment

**Purpose:** Deploy to staging environment

```bash
✓ Stop existing containers
✓ Deploy updated containers
✓ Verify deployment health
```

**Quality Gate:** Blocking

---

### Stage 9: Smoke Tests

**Purpose:** Validate deployment health

```bash
✓ Test API health endpoint
✓ Verify all services are responding
✓ Check database connectivity
```

**Quality Gate:** Blocking

---

## 🏃 Running Locally

### Full Pipeline

```bash
# Using batch script (Windows)
run-pipeline.bat

# Using Python directly
python ci_pipeline.py
```

**Expected Duration:** 5-8 minutes

---

### Quick Validation

```bash
# Lint and test only
flake8 autom8/
pytest tests/ -v

# Or use batch script
run-pipeline-quick.bat
```

**Expected Duration:** 2-3 minutes

---

### Auto-Fix Issues

```bash
# Format code automatically
black autom8/
isort autom8/ --profile black

# Or use batch script
run-pipeline-fix.bat
```

---

## 🤖 GitHub Actions

### Automatic Triggers

The pipeline runs automatically on:

| Trigger | Description |
|---------|-------------|
| Push to `main` | Production deployment |
| Push to `develop` | Staging deployment |
| Pull Request to `main` | Validation only |
| Manual Dispatch | On-demand execution |

### Viewing Results

1. Navigate to your GitHub repository
2. Click the **Actions** tab
3. Select the workflow run
4. View detailed logs for each job

### Status Badge

Add to your README.md:

```markdown
![CI/CD Pipeline](https://github.com/YOUR_USERNAME/autom8/workflows/CI%2FCD%20Pipeline/badge.svg)
```

---

## 🪝 Pre-commit Hooks

### Configured Hooks

Pre-commit hooks run automatically before every commit:

| Hook | Purpose |
|------|---------|
| trailing-whitespace | Remove trailing whitespace |
| end-of-file-fixer | Ensure files end with newline |
| black | Format Python code |
| isort | Sort imports |
| flake8 | Lint Python code |
| bandit | Security scanning |

### Installation

```bash
# Install hooks (one-time setup)
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

### Emergency Bypass

```bash
# Skip hooks (use sparingly!)
git commit --no-verify -m "Emergency fix"
```

> ⚠️ **Warning:** Only use `--no-verify` in genuine emergencies. Skipping hooks can introduce issues.

---

## 🚦 Quality Gates

### Blocking Gates

These gates will stop the pipeline if they fail:

| Gate | Requirement |
|------|-------------|
| Tests | All tests must pass |
| Coverage | Minimum 80% coverage |
| Build | Docker image must build successfully |
| Deploy | Deployment must complete |

### Non-Blocking Gates

These gates provide warnings but won't stop the pipeline:

| Gate | Purpose |
|------|---------|
| Lint | Code quality suggestions |
| Format | Style recommendations |
| Security (LOW) | Minor security advisories |

---

## 🐛 Troubleshooting

### Lint Stage Failures

**Problem:** Flake8 reports errors

**Solution:**
```bash
# View all issues
flake8 autom8/ --count --statistics

# Auto-fix formatting issues
black autom8/
isort autom8/ --profile black
```

---

### Test Stage Failures

**Problem:** Tests are failing

**Solution:**
```bash
# Run tests with verbose output
pytest tests/ -v --tb=short

# Run specific failing test
pytest tests/unit/test_models.py::test_specific_function -v

# Debug with print statements
pytest tests/ -v -s
```

---

### Coverage Below Threshold

**Problem:** Coverage is below 80%

**Solution:**
```bash
# Generate detailed coverage report
pytest --cov=autom8 --cov-report=html

# Open htmlcov/index.html in browser
# Identify uncovered code and add tests
```

---

### Docker Build Failures

**Problem:** Docker image won't build

**Solution:**
```bash
# Build locally with verbose output
docker build -t autom8:test . --no-cache

# Check for syntax errors in Dockerfile
docker build --check .

# Clear Docker cache
docker builder prune -f
```

---

### Deployment Failures

**Problem:** Containers won't start

**Solution:**
```bash
# Validate compose configuration
docker compose config

# View container logs
docker compose logs -f

# Restart with fresh state
docker compose down -v
docker compose up -d
```

---

### Pre-commit Hook Failures

**Problem:** Commit is blocked by hooks

**Solution:**
```bash
# Run hooks manually to see all issues
pre-commit run --all-files

# Fix issues
black autom8/
flake8 autom8/

# Retry commit
git add .
git commit -m "Your message"
```

---

## 📊 Pipeline Metrics

### Performance Benchmarks

| Stage | Duration | Expected Pass Rate |
|-------|----------|-------------------|
| Setup | ~10s | 100% |
| Lint | ~30s | 95%+ |
| Format | ~20s | 98%+ |
| Security | ~45s | 100% |
| Tests | ~2m 30s | 100% |
| Build | ~1m 45s | 100% |
| Deploy | ~45s | 100% |
| Smoke Test | ~15s | 100% |

**Total Pipeline Duration:** ~6-8 minutes

---

## 🎯 Best Practices

### Before Committing

```bash
# 1. Run tests locally
pytest tests/ -v

# 2. Check linting
flake8 autom8/

# 3. Format code
black autom8/

# 4. Run pre-commit hooks
pre-commit run --all-files
```

### During Development

- Enable format-on-save in your IDE (VSCode + Black extension)
- Run tests frequently with `pytest --lf` (last failed)
- Use `pytest --watch` for continuous testing

### Before Pushing

```bash
# Run the full pipeline
python ci_pipeline.py

# Ensure all stages pass
# Then push to remote
git push origin <branch>
```

---

## 🔐 Security Guidelines

### Never Commit

- ❌ API keys or tokens
- ❌ Passwords or credentials
- ❌ Private certificates
- ❌ Environment-specific secrets

### Use Instead

- ✅ `.env` files (add to .gitignore)
- ✅ GitHub Secrets for CI/CD
- ✅ Environment variables

### GitHub Secrets Configuration

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add your secrets (e.g., `DOCKER_HUB_TOKEN`)
4. Reference in workflows:

```yaml
- name: Login to Docker Hub
  env:
    DOCKER_TOKEN: ${{ secrets.DOCKER_HUB_TOKEN }}
```

---

## 📈 Continuous Improvement

### Speed Optimization

- Cache dependencies between runs
- Parallelize independent jobs
- Skip unchanged stages with smart caching

### Reliability Improvements

- Add retry logic for flaky tests
- Improve error messages and logs
- Implement health check endpoints

### Coverage Expansion

- Add tests for edge cases
- Increase integration test coverage
- Implement end-to-end tests

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Framework](https://pre-commit.com/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linter](https://flake8.pycqa.org/)

---

*© 2025 Autom8 Project — Professional Systems Automation Toolkit*
