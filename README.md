# PR Commenter

Automatically post comments to GitHub PRs to trigger AI reviews.

## Overview

This tool allows you to automatically post a series of predefined comments to GitHub Pull Requests when they are created. This is particularly useful for triggering reviews from various AI code review bots like CodiumAI, Sourcery, Gemini, etc.

## Features

- Automatically posts comments to PRs when they are created
- Reads comments from a `comments.txt` file or environment variable
- Can be used as a GitHub Action or run locally
- Supports custom GitHub API tokens
- Configurable via environment variables

## Setup Options

### Option 1: GitHub Actions (Recommended)

1. Add the `.github/workflows/pr-commenter.yml` file to your repository
2. Create a `comments.txt` file in the root of your repository with one comment per line
3. That's it! The workflow will automatically run when a PR is created

### Option 2: Node.js Script

1. Clone this repository
2. Install dependencies: `npm install`
3. Create a `.env` file based on `.env.example`
4. Run the script: `npm start`

## Configuration

### comments.txt

Create a `comments.txt` file with one comment per line. For example:

```
@CodiumAI-Agent /review

@sourcery-ai review

/gemini review

/review

/improve

/korbit-review

@codecov-ai-reviewer review

@Codegen Implement and upgrade this PR with above Considerations and suggestions from other AI bots
```

### Environment Variables

- `GITHUB_API_TOKEN` or `GITHUB_TOKEN`: Your GitHub API token (required)
- `GITHUB_OWNER`: GitHub username or organization (for local usage)
- `GITHUB_REPO`: Repository name (for local usage)
- `PR_NUMBER`: PR number to comment on (for local usage)
- `COMMENTS_PATH`: Path to comments file (defaults to `./comments.txt`)
- `COMMENTS`: Comments as a string, used if comments.txt is not found

## GitHub Secrets

If you don't want to commit your `comments.txt` file to the repository, you can store the comments as a GitHub Secret:

1. Go to your repository settings
2. Navigate to Secrets and Variables > Actions
3. Create a new repository secret named `COMMENTS` with your comments (one per line)
4. Uncomment the `COMMENTS: ${{ secrets.COMMENTS }}` line in the workflow file

## License

MIT
