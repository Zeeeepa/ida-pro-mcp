#!/usr/bin/env node

const { Octokit } = require('@octokit/rest');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// Get GitHub token from environment variable
const token = process.env.GITHUB_API_TOKEN || process.env.GITHUB_TOKEN;

if (!token) {
  console.error('Error: GitHub API token not found. Please set GITHUB_API_TOKEN in your .env file.');
  process.exit(1);
}

// Initialize Octokit
const octokit = new Octokit({
  auth: token
});

async function postComments(owner, repo, prNumber, comments) {
  console.log(`Posting ${comments.length} comments to PR #${prNumber} in ${owner}/${repo}`);
  
  for (const comment of comments) {
    if (comment.trim()) {
      try {
        console.log(`Posting comment: ${comment}`);
        await octokit.issues.createComment({
          owner,
          repo,
          issue_number: prNumber,
          body: comment
        });
        
        // Add a small delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`Error posting comment: ${error.message}`);
      }
    }
  }
}

async function main() {
  try {
    // Check if running in GitHub Actions
    const isGitHubAction = process.env.GITHUB_ACTIONS === 'true';
    
    let owner, repo, prNumber, comments;
    
    if (isGitHubAction) {
      // Get PR details from GitHub Actions context
      const eventPath = process.env.GITHUB_EVENT_PATH;
      if (!eventPath) {
        throw new Error('GITHUB_EVENT_PATH not set');
      }
      
      const event = JSON.parse(fs.readFileSync(eventPath, 'utf8'));
      owner = event.repository.owner.login;
      repo = event.repository.name;
      prNumber = event.pull_request.number;
      
      // Try to read comments from the repository
      if (fs.existsSync('./comments.txt')) {
        comments = fs.readFileSync('./comments.txt', 'utf8')
          .split('\n')
          .filter(line => line.trim() !== '');
      } else {
        // If file doesn't exist, try to use environment variable
        const commentsEnv = process.env.COMMENTS;
        if (commentsEnv) {
          comments = commentsEnv.split('\n').filter(line => line.trim() !== '');
        } else {
          throw new Error('No comments found in comments.txt or COMMENTS environment variable');
        }
      }
    } else {
      // Running locally, get parameters from command line or .env
      owner = process.env.GITHUB_OWNER || process.argv[2];
      repo = process.env.GITHUB_REPO || process.argv[3];
      prNumber = process.env.PR_NUMBER || process.argv[4];
      
      if (!owner || !repo || !prNumber) {
        console.error('Usage: node pr-commenter.js <owner> <repo> <pr-number>');
        console.error('Or set GITHUB_OWNER, GITHUB_REPO, and PR_NUMBER in your .env file');
        process.exit(1);
      }
      
      // Read comments from comments.txt
      const commentsPath = process.env.COMMENTS_PATH || './comments.txt';
      if (!fs.existsSync(commentsPath)) {
        throw new Error(`Comments file not found: ${commentsPath}`);
      }
      
      comments = fs.readFileSync(commentsPath, 'utf8')
        .split('\n')
        .filter(line => line.trim() !== '');
    }
    
    await postComments(owner, repo, prNumber, comments);
    console.log('All comments posted successfully!');
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
