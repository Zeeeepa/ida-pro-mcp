// Example of handling GitHub PR events with Codegen SDK
const { Webhooks } = require('@octokit/webhooks');
const Sentry = require('@sentry/node');
const { CodegenSDK } = require('codegen-sdk'); // This is a placeholder, use actual import

// Initialize Sentry
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
});

// Initialize GitHub webhooks handler
const githubWebhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET,
});

// Initialize Codegen SDK
const cg = new CodegenSDK({
  apiKey: process.env.CODEGEN_API_KEY,
});

// Handle pull_request.labeled events
githubWebhooks.on('pull_request.labeled', async ({ payload }) => {
  console.log("PR labeled");
  console.log(`PR head sha: ${payload.pull_request.head.sha}`);
  
  try {
    // Get codebase
    const codebase = await cg.get_codebase({
      repo: payload.repository.full_name,
    });
    
    // Checkout the commit
    console.log("> Checking out commit");
    await codebase.checkout({
      commit: payload.pull_request.head.sha,
    });
    
    // Get files
    console.log("> Getting files");
    const file = await codebase.get_file("README.md");
    
    // Create PR comment
    await cg.create_pr_comment({
      repo: payload.repository.full_name,
      pr_number: payload.pull_request.number,
      body: `File content:\n\`\`\`markdown\n${file.content}\n\`\`\``,
    });
    
    return {
      message: "PR event handled",
      num_files: codebase.files.length,
      num_functions: codebase.functions.length,
    };
  } catch (error) {
    Sentry.captureException(error);
    console.error("Error handling PR labeled event:", error);
    throw error;
  }
});

// Export the webhooks handler
module.exports = githubWebhooks;

