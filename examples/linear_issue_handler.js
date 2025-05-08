// Example of handling Linear issue events with Codegen SDK
const { LinearClient } = require('@linear/sdk');
const Sentry = require('@sentry/node');
const { CodegenSDK } = require('codegen-sdk'); // This is a placeholder, use actual import

// Initialize Sentry
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
});

// Initialize Linear client
const linearClient = new LinearClient({
  apiKey: process.env.LINEAR_API_KEY,
});

// Initialize Codegen SDK
const cg = new CodegenSDK({
  apiKey: process.env.CODEGEN_API_KEY,
});

// Handle Linear issue events
async function handleLinearIssue(event) {
  console.log(`Issue created: ${JSON.stringify(event)}`);
  
  try {
    // Get codebase
    const codebase = await cg.get_codebase({
      repo: process.env.DEFAULT_REPO, // Configure default repo for Linear issues
    });
    
    // Example: Analyze codebase based on issue description
    const issueData = event.data;
    
    // If issue contains specific labels, perform different actions
    if (issueData.labels && issueData.labels.some(label => label.name === 'bug')) {
      // For bugs, analyze the codebase for potential issues
      const analysisResult = await cg.analyze_code({
        codebase,
        query: issueData.description,
      });
      
      // Comment back on the Linear issue with analysis results
      await linearClient.commentCreate({
        issueId: issueData.id,
        body: `Code analysis results:\n\n${JSON.stringify(analysisResult, null, 2)}`,
      });
    }
    
    return {
      message: "Linear Issue event handled",
      num_files: codebase.files.length,
      num_functions: codebase.functions.length,
    };
  } catch (error) {
    Sentry.captureException(error);
    console.error("Error handling Linear Issue event:", error);
    throw error;
  }
}

// Export the handler
module.exports = {
  handleLinearIssue,
};

