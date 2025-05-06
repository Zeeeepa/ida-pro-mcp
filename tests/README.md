# Testing Module Imports

This directory contains tests to verify that all module imports resolve correctly. These tests help prevent import path issues before they cause runtime errors in production.

## Available Tests

1. **test_imports.py**: Tests that all modules in the package can be imported without errors.
2. **test_static_imports.py**: Uses pylint to perform static analysis of import-related issues.
3. **run_tests.py**: A convenience script to run all tests.

## Running the Tests

You can run the tests in several ways:

### Using the run_tests.py script

```bash
python tests/run_tests.py
```

### Using unittest directly

```bash
python -m unittest discover -s tests
```

### Using pytest

```bash
pytest
```

## CI Integration

These tests are integrated into the CI/CD pipeline via GitHub Actions. The workflow is defined in `.github/workflows/test-imports.yml`.

The CI pipeline will:
1. Run the import tests on every pull request
2. Run the static analysis tests
3. Fail the build if any module imports fail

## Adding New Tests

If you need to add new import-related tests:

1. Create a new test file in the `tests/` directory with a name starting with `test_`
2. Implement your test cases using the `unittest` framework
3. Run the tests to ensure they work as expected

## Troubleshooting

If the tests fail, check the following:

1. Are all required dependencies installed?
2. Are there any syntax errors in the modules?
3. Are there any circular import dependencies?
4. Are the import paths correct?

For more information on module import best practices, see the [Module Guidelines](../docs/module_guidelines.md) document.

