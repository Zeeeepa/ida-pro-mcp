# PR Static Analysis Examples

This directory contains examples of how to use the PR static analysis system.

## Generate Report

The `generate_report.py` script demonstrates how to generate a report from analysis results.

```bash
# Run the example
python generate_report.py
```

This will:

1. Create a sample PR context
2. Create some sample analysis results
3. Create a reporting system
4. Add a file system delivery channel
5. Process the results
6. Save the report to the `reports` directory

## Configuration

The `config.json` file contains a sample configuration for the reporting system.

```json
{
  "default_format": "markdown",
  "include_visualizations": true,
  "delivery": {
    "github_pr_comment": {
      "enabled": false
    },
    "file_system": {
      "enabled": true,
      "output_dir": "reports"
    },
    "email": {
      "enabled": false,
      "smtp": {
        "server": "smtp.example.com",
        "port": 587,
        "use_tls": true,
        "username": "",
        "password": "",
        "sender": "pr-analysis@example.com"
      },
      "recipients": []
    }
  }
}
```

You can modify this configuration to suit your needs.

