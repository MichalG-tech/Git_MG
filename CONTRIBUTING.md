# Contributing Guidelines

Thank you for contributing to the Power BI Enterprise PoC! This document outlines our contribution process and standards.

## 🎯 Contribution Process

### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/add-customer-segment-measure` - New feature
- `bugfix/fix-revenue-calculation` - Bug fix
- `hotfix/urgent-dax-error` - Urgent production fix
- `docs/update-architecture-guide` - Documentation
- `chore/update-dependencies` - Maintenance

### 2. Make Changes

- Edit TMDL files, Python code, or documentation
- Keep commits small and focused
- Write clear commit messages

### 3. Validate Locally

```bash
python python-utilities/scripts/run-all-checks.py
```

This validates:
- TMDL syntax
- DAX expressions
- Best practices
- Data quality
- Code style

### 4. Commit with Convention

```bash
git commit -m "type(scope): subject

Body explaining WHY, not WHAT

Closes #123"
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `perf` - Performance improvement
- `docs` - Documentation
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance

**Example:**
```bash
git commit -m "feat(sales-model): Add customer lifetime value measure

- Calculates total revenue per customer across all time
- Used in customer segmentation reports  
- Performance optimized with SUMMARIZE

Closes #45"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create PR on GitHub with:
- Clear title (same as commit)
- Description of changes
- Related issues
- Testing notes

### 6. Automated Validation

GitHub Actions automatically validates:
- ✅ TMDL syntax
- ✅ DAX best practices
- ✅ Naming conventions
- ✅ Documentation completeness
- ✅ Commit message format

### 7. Code Review

- Request 2+ reviewers for production changes
- Address feedback promptly
- Keep commits clean (squash if needed)

### 8. Merge

Once approved:
```bash
# Merge via GitHub UI (preferred)
# or locally:
git checkout develop
git merge --no-ff feature/your-feature-name
git push origin develop
```

## 📋 Code Standards

### TMDL Files

- Use consistent naming: `Dim*`, `Fact*` for tables
- Measures: `measure_` prefix for calculated measures
- Clear descriptions for all objects
- Proper relationships defined
- RLS rules for sensitive data

### DAX Expressions

- Use meaningful variable names
- Comment complex calculations
- Avoid SUM(IF(...)) anti-patterns
- Optimize with SUMMARIZE where appropriate
- Format consistently

### Python Code

- Follow PEP 8 style guide
- Use type hints for functions
- Write docstrings for modules
- Keep functions under 50 lines
- Use logging, not print()

### Documentation

- Use clear, professional language
- Include examples where helpful
- Update table of contents
- Link to related docs
- Keep current and accurate

## 🔍 Code Review Checklist

Reviewers should verify:

- [ ] Commit message is clear and follows convention
- [ ] Code/TMDL changes are focused on issue
- [ ] No breaking changes without discussion
- [ ] Tests pass (GitHub Actions)
- [ ] Documentation is updated
- [ ] No credentials or secrets committed
- [ ] Performance impact considered

## 🐛 Bug Reports

Submit bugs via GitHub Issues with:
1. Clear title
2. Description of issue
3. Steps to reproduce
4. Expected vs actual behavior
5. Environment info (OS, Python version, etc.)
6. Screenshots/logs if applicable

## ✨ Feature Requests

Suggest features via Issues with:
1. Clear description of need
2. Proposed solution
3. Alternative approaches considered
4. Use cases / examples
5. Impact assessment

## 📚 Documentation Contributions

- Update docs/ when making changes
- Create new guides if needed
- Use markdown consistently
- Include examples
- Link between related docs
- Update README.md if appropriate

## 🔐 Security

- Never commit credentials, keys, or secrets
- Use environment variables for sensitive data
- Review security implications before committing
- Report security issues privately (don't open public issue)

## 🎓 Development Environment

### Setup

```bash
# Clone repo
git clone https://github.com/MichalG-tech/Git_MG.git
cd Git_MG

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r python-utilities/requirements.txt

# Install in editable mode
pip install -e python-utilities/
```

### Running Validation

```bash
# Full validation suite
python python-utilities/scripts/run-all-checks.py

# Individual checks
python python-utilities/scripts/validate-model.py
python python-utilities/scripts/generate-data.py
```

### Running Tests

```bash
pytest python-utilities/tests/
pytest python-utilities/tests/test_tmdl_validator.py -v
```

## 📞 Questions?

- Check [docs/troubleshooting/FAQ.md](docs/troubleshooting/FAQ.md)
- Review [docs/development/FEATURE_WORKFLOW.md](docs/development/FEATURE_WORKFLOW.md)
- Ask in discussions or reach out to maintainers

## 🙏 Thank You!

Your contributions make this PoC better for everyone. Thank you for helping!

---

**Happy contributing!**
