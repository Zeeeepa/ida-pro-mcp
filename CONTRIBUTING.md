# Contributing to PR Static Analysis

Thank you for considering contributing to PR Static Analysis! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/pr-static-analysis.git
cd pr-static-analysis

# Install development dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=pr_static_analysis

# Run linting
flake8

# Run formatting
black .
```

## Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Update the README.md with details of changes to the interface, if applicable
3. Update the documentation, if applicable
4. The PR should work for Python 3.8, 3.9, and 3.10
5. The PR should pass all tests and linting checks

## Style Guidelines

- Follow PEP 8 style guide
- Use docstrings for all functions, classes, and modules
- Write clear commit messages

## Documentation

- Update the README.md if necessary
- Add docstrings to all new functions, classes, and modules
- Update any relevant documentation files

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.

