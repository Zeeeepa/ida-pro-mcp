# GitHub Integration for PR Static Analysis

This package provides components for integrating with GitHub to perform static analysis on pull requests and post results as comments.

## Components

### GitHubPRClient

Client for interacting with GitHub pull requests. Provides methods for retrieving PR data and posting comments.

```python
from ida_pro_mcp.github_integration import GitHubPRClient

# Initialize the client
client = GitHubPRClient(token="your_github_token")

# Get PR data
pr_data = client.get_pr("owner/repo", 123)

# Post a comment
client.post_comment("owner/repo", 123, "This is a comment")

# Get file content
content = client.get_file_content("owner/repo", 123, "path/to/file.py")

# Get PR diff
diff = client.get_diff("owner/repo", 123)
```

### GitHubCommentFormatter

Formatter for converting analysis results into GitHub comments with Markdown formatting.

```python
from ida_pro_mcp.github_integration import GitHubCommentFormatter

# Initialize the formatter
formatter = GitHubCommentFormatter()

# Format analysis results
results = {
    "issues": [
        {
            "severity": "error",
            "message": "Missing return statement",
            "file": "main.py",
            "line": 42
        }
    ],
    "recommendations": [
        "Add a return statement to the function"
    ]
}

comment = formatter.format_results(results)
```

### GitHubWebhookHandler

Handler for GitHub webhook events. Processes webhook payloads, validates signatures, and triggers analysis for pull request events.

```python
from ida_pro_mcp.github_integration import (
    GitHubWebhookHandler,
    GitHubPRClient,
    GitHubCommentFormatter,
    CorePRAnalyzer
)

# Initialize components
client = GitHubPRClient(token="your_github_token")
formatter = GitHubCommentFormatter()
analyzer = CorePRAnalyzer(client)

# Initialize the webhook handler
handler = GitHubWebhookHandler(
    pr_analyzer=analyzer,
    pr_client=client,
    comment_formatter=formatter,
    webhook_secret="your_webhook_secret"
)

# Handle a webhook event
event_type = "pull_request"
payload = {
    "action": "opened",
    "pull_request": {"number": 123},
    "repository": {"full_name": "owner/repo"}
}

result = handler.handle_webhook(event_type, payload)
```

### GitHubWebhookServer

Flask web server for receiving and processing GitHub webhook events.

```python
from ida_pro_mcp.github_integration import (
    GitHubWebhookHandler,
    GitHubPRClient,
    GitHubCommentFormatter,
    CorePRAnalyzer,
    create_webhook_server
)

# Initialize components
client = GitHubPRClient(token="your_github_token")
formatter = GitHubCommentFormatter()
analyzer = CorePRAnalyzer(client)

# Initialize the webhook handler
handler = GitHubWebhookHandler(
    pr_analyzer=analyzer,
    pr_client=client,
    comment_formatter=formatter,
    webhook_secret="your_webhook_secret"
)

# Create and run the webhook server
server = create_webhook_server(handler, host="0.0.0.0", port=5000)
server.run(debug=True)
```

### PRAnalyzer and CorePRAnalyzer

Interface and implementation for analyzing pull requests and generating analysis results.

```python
from ida_pro_mcp.github_integration import (
    GitHubPRClient,
    CorePRAnalyzer,
    RuleEngine
)

# Initialize components
client = GitHubPRClient(token="your_github_token")
rule_engine = RuleEngine()

# Add rules to the rule engine
rule_engine.add_rule({
    "id": "missing_return",
    "pattern": r"def\s+\w+\([^)]*\):\s*(?!.*return)",
    "message": "Function is missing a return statement",
    "severity": "warning"
})

# Initialize the analyzer
analyzer = CorePRAnalyzer(client, rule_engine)

# Analyze a PR
results = analyzer.analyze_pr("owner/repo", 123)
```

## Command-line Usage

The package provides a command-line script for running the webhook server and performing manual analysis of PRs.

### Analyzing a PR

```bash
# Set your GitHub token
export GITHUB_TOKEN=your_github_token

# Analyze a PR
github-pr-analysis analyze owner/repo 123

# Analyze a PR and post results as a comment
github-pr-analysis analyze owner/repo 123 --post-comment
```

### Running the Webhook Server

```bash
# Set your GitHub token and webhook secret
export GITHUB_TOKEN=your_github_token
export WEBHOOK_SECRET=your_webhook_secret

# Run the webhook server
github-pr-analysis server

# Run the webhook server with custom host and port
github-pr-analysis server --host 127.0.0.1 --port 8000
```

## Configuration

The package uses the following environment variables for configuration:

- `GITHUB_TOKEN`: GitHub API token for authentication
- `WEBHOOK_SECRET`: Secret for validating webhook payloads
- `WEBHOOK_HOST`: Host to bind the webhook server to (default: 0.0.0.0)
- `WEBHOOK_PORT`: Port to bind the webhook server to (default: 5000)

## Testing

Run the tests using pytest:

```bash
pytest tests/github_integration
```

