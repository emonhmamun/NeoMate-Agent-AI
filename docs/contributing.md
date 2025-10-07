# How to Contribute to NeoMate AI

> **Welcome to the NeoMate AI community!**  
> We appreciate your interest in helping us build a cutting-edge AI companion. Your contributions—whether code, documentation, bug reports, or ideas—are invaluable.

## Table of Contents

- [Getting Started](#getting-started)
- [Ways to Contribute](#ways-to-contribute)
- [Your First Contribution](#your-first-contribution)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Running Tests](#running-tests)
- [Pull Request Process](#pull-request-process)
- [Review & Merging](#review--merging)
- [Community Guidelines](#community-guidelines)
- [Recognition](#recognition)
- [Need Help?](#need-help)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Resources](#resources)

## Getting Started

### Connect with Us

- **GitHub Issues**: Report bugs or request features.
- **GitHub Discussions**: Share ideas or ask questions.
- **Chat**: Join our Discord/Slack (coming soon).
- **Email**: ehm.businessbd@gmail.com for private matters.

### Ways to Contribute

| Type                  | Description                               |
| --------------------- | ----------------------------------------- |
| **Report Bugs**       | Help us identify and fix issues.          |
| **Suggest Features**  | Propose enhancements or new ideas.        |
| **Write Code**        | Implement features or fixes.              |
| **Improve Docs**      | Make our documentation clearer.           |
| **Test**              | Verify functionality and report problems. |
| **Support Community** | Assist others and mentor newcomers.       |

### Your First Contribution

- Look for issues tagged `good first issue` or `beginner-friendly`.
- Start small and build confidence.
- Ask questions anytime—we’re here to help!

## Development Setup

1. **Prerequisites**:

   - Python 3.8+ installed.
   - Git installed.
   - Code editor (VS Code recommended).

2. **Clone the Repo**:

   - Fork NeoMate-AI on GitHub.
   - Clone your fork:  
     `git clone https://github.com/your-username/NeoMate-AI.git`
   - Navigate: `cd NeoMate-AI`

3. **Install Dependencies**:

   - Using Poetry: `poetry install`
   - Or Pip: `pip install -r requirements.txt`
   - Conda users: `conda env create -f environment.yml`

4. **Run & Test**:

   - Follow instructions in [README.md](../README.md).
   - Verify local setup works.

5. **Branching**:
   - Create a feature branch:  
     `git checkout -b feature/your-feature-name`

## Project Structure

```
NeoMate-AI/
├── config/          # Configuration files
├── data/            # Data storage
├── deployment/      # Deployment scripts
├── docs/            # Documentation
├── external/        # External dependencies
├── logs/            # Log files
├── scripts/         # Utility scripts
├── src/             # Source code
├── tests/           # Test files
└── README.md        # Main readme
```

## Coding Standards

- **Language**: Python (primary), JavaScript (UI).
- **Formatting**: Use Black (`black .`).
- **Linting**: Use Ruff (`ruff check .`).
- **Naming**:
  - Variables/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Type Hints**: Use consistently.
- **Docstrings**: Google style.
- **Commits**: Clear, meaningful messages.
- **Tests**: Add unit tests; aim for 80%+ coverage.
- **Security**: Avoid committing secrets; use env vars.

Example:

```python
def greet_user(name: str) -> str:
    """
    Generate a personalized greeting.

    Args:
        name: User's name.

    Returns:
        Greeting string.
    """
    return f"Hello, {name}! Welcome to NeoMate."
```

## Running Tests

- Run unit tests: `pytest`
- Run with coverage: `pytest --cov=src`
- Lint code: `ruff check .`
- Format code: `black .`

## Pull Request Process

1. Fork and branch your repo.
2. Commit changes with meaningful messages.
3. Push branch to GitHub.
4. Open a Pull Request (PR) against the main repo.
5. Describe your changes and link issues (e.g., Closes #123).
6. Ensure:
   - Code is formatted.
   - Tests pass.
   - Documentation updated.
7. Respond to review feedback promptly.

## Review & Merging

- Reviews take 1-3 days.
- Maintainers may request changes.
- Approved PRs are merged by maintainers.
- Rejected PRs include explanations.

## Community Guidelines

- Be respectful and inclusive.
- Collaborate and credit others.
- Contributions are under MIT License.
- Follow our [Code of Conduct](code-of-conduct.md).

## Recognition

Contributors are acknowledged in:

- Release notes.
- README contributors section.
- Special mentions for major work.

## Need Help?

- Check Issues and Discussions.
- Join community chats.
- Contact maintainers for urgent help.

## Frequently Asked Questions

**Q: How do I report a bug?**  
A: Open a GitHub Issue with steps to reproduce.

**Q: Can I contribute without coding?**  
A: Yes, documentation and testing are valuable.

**Q: What if my PR is rejected?**  
A: We'll explain why; you can resubmit.

## Resources

- [Project Vision](../docs/project_vision.md)
- [Architecture](../docs/architecture.md)
- [Technical Specs](../docs/technical_specs.md)
- [GitHub Repository](https://github.com/emonhmamun/NeoMate-AI)

Thank you for helping build NeoMate AI!

---

_Maintained by the NeoMate AI team. Updates at [GitHub](https://github.com/emonhmamun)._
