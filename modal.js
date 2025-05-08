// modal.js - Webhook server for GitHub and Linear events
const modal = require('modal');
const { Webhooks } = require('@octokit/webhooks');
const { LinearClient } = require('@linear/sdk');
const * as Sentry from '@sentry/node';
const { createClient } = require('@supabase/supabase-js');
const express = require('express');
const bodyParser = require('body-parser');

// Initialize Sentry for error tracking and monitoring
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    // Enable HTTP capturing for webhook requests
    new Sentry.Integrations.Http({ tracing: true }),
    // Express integration for request monitoring
    new Sentry.Integrations.Express(),
    // Enable Node.js specific integrations
    ...Sentry.autoDiscoverNodePerformanceMonitoringIntegrations(),
  ],
  // Performance monitoring - capture 100% of transactions in development, adjust for production
  tracesSampleRate: 1.0,
  // Set this to lower value like 0.1 in production
  profilesSampleRate: 1.0,
});

// Create Supabase client for event storage
const supabaseClient = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// Initialize GitHub webhooks handler with secret
const githubWebhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET,
});

// Initialize Linear client
const linearClient = new LinearClient({
  apiKey: process.env.LINEAR_API_KEY
});

// Create Express app for handling webhook requests
const createWebhookApp = () => {
  const app = express();
  
  // Sentry request handler must be the first middleware
  app.use(Sentry.Handlers.requestHandler());
  
  // Parse JSON bodies
  app.use(bodyParser.json());
  
  // GitHub webhook endpoint
  app.post('/webhooks/github', async (req, res) => {
    const signature = req.headers['x-hub-signature-256'];
    const id = req.headers['x-github-delivery'];
    const name = req.headers['x-github-event'];
    
    try {
      // Verify and process the webhook
      await githubWebhooks.verifyAndReceive({
        id,
        name,
        payload: JSON.stringify(req.body),
        signature,
      });
      
      res.status(200).send('Webhook received');
    } catch (error) {
      Sentry.captureException(error);
      console.error('Error processing GitHub webhook:', error);
      res.status(500).send('Error processing webhook');
    }
  });
  
  // Linear webhook endpoint
  app.post('/webhooks/linear', async (req, res) => {
    try {
      // Linear doesn't provide signature verification out of the box
      // You may implement custom verification if needed
      
      // Process the Linear webhook
      const event = req.body;
      
      // Store event in Supabase
      await storeEvent('linear', event);
      
      // Emit the event to be processed by handlers
      await processLinearEvent(event);
      
      res.status(200).send('Webhook received');
    } catch (error) {
      Sentry.captureException(error);
      console.error('Error processing Linear webhook:', error);
      res.status(500).send('Error processing webhook');
    }
  });
  
  // Health check endpoint
  app.get('/health', (req, res) => {
    res.status(200).send('OK');
  });
  
  // Sentry error handler must be before any other error middleware
  app.use(Sentry.Handlers.errorHandler());
  
  // Generic error handler
  app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).send('Internal Server Error');
  });
  
  return app;
};

// Store webhook events in Supabase
async function storeEvent(source, event) {
  try {
    const { data, error } = await supabaseClient
      .from('webhook_events')
      .insert({
        source,
        event_type: event.type || event.action,
        payload: event,
        received_at: new Date().toISOString(),
      });
    
    if (error) {
      Sentry.captureException(error);
      console.error('Error storing event in Supabase:', error);
    }
    
    return data;
  } catch (error) {
    Sentry.captureException(error);
    console.error('Error storing event:', error);
  }
}

// Process GitHub events
githubWebhooks.on('*', async ({ id, name, payload }) => {
  console.log(`Received GitHub event: ${name}`);
  
  // Store the event in Supabase
  await storeEvent('github', { id, name, payload });
  
  // Create a transaction for this webhook processing
  const transaction = Sentry.startTransaction({
    op: 'webhook.github',
    name: `process_github_${name}`,
  });
  
  Sentry.configureScope(scope => {
    scope.setSpan(transaction);
  });
  
  try {
    // Handle specific GitHub events
    if (name === 'pull_request' && payload.action === 'labeled') {
      await handlePullRequestLabeled(payload);
    }
    
    // Add more event handlers as needed
    
  } catch (error) {
    Sentry.captureException(error);
    console.error(`Error processing GitHub ${name} event:`, error);
  } finally {
    transaction.finish();
  }
});

// Process Linear events
async function processLinearEvent(event) {
  console.log(`Received Linear event: ${event.type}`);
  
  // Create a transaction for this webhook processing
  const transaction = Sentry.startTransaction({
    op: 'webhook.linear',
    name: `process_linear_${event.type}`,
  });
  
  Sentry.configureScope(scope => {
    scope.setSpan(transaction);
  });
  
  try {
    // Handle specific Linear events
    if (event.type === 'Issue') {
      await handleLinearIssue(event);
    }
    
    // Add more event handlers as needed
    
  } catch (error) {
    Sentry.captureException(error);
    console.error(`Error processing Linear ${event.type} event:`, error);
  } finally {
    transaction.finish();
  }
}

// Handler for GitHub pull_request:labeled events
async function handlePullRequestLabeled(event) {
  console.log("PR labeled");
  console.log(`PR head sha: ${event.pull_request.head.sha}`);
  
  try {
    // This is where you would implement the Codegen SDK functionality
    // For example:
    // const codebase = await cg.get_codebase();
    // await codebase.checkout(commit=event.pull_request.head.sha);
    // const file = await codebase.get_file("README.md");
    // await create_pr_comment(codebase, event.pull_request.number, `File content:\n\`\`\`python\n${file.content}\n\`\`\``);
    
    // For now, we'll just log the event
    console.log("Would process PR labeled event here");
    
    return {
      message: "PR event handled",
      // num_files: codebase.files.length,
      // num_functions: codebase.functions.length
    };
  } catch (error) {
    Sentry.captureException(error);
    console.error("Error handling PR labeled event:", error);
    throw error;
  }
}

// Handler for Linear Issue events
async function handleLinearIssue(event) {
  console.log(`Issue created: ${JSON.stringify(event)}`);
  
  try {
    // This is where you would implement the Codegen SDK functionality
    // For example:
    // const codebase = await cg.get_codebase();
    
    // For now, we'll just log the event
    console.log("Would process Linear Issue event here");
    
    return {
      message: "Linear Issue event handled",
      // num_files: codebase.files.length,
      // num_functions: codebase.functions.length
    };
  } catch (error) {
    Sentry.captureException(error);
    console.error("Error handling Linear Issue event:", error);
    throw error;
  }
}

// Create the base image with dependencies
const base_image = modal.Image.debian_slim(python_version="3.13")
  .apt_install("git")
  .pip_install(
    // =====[ Codegen ]=====
    // "codegen",
    `git+https://github.com/codegen-sh/codegen-sdk.git@6a0e101718c247c01399c60b7abf301278a41786`,
    // =====[ Rest ]=====
    "openai>=1.1.0",
    "fastapi[standard]",
    "slack_sdk",
  )
  .run_commands(
    // Install Node.js and npm
    "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
    "apt-get install -y nodejs",
    // Install required npm packages
    "npm install @octokit/webhooks @linear/sdk @sentry/node @supabase/supabase-js express body-parser"
  );

// Create the Modal app
const app = modal.App("codegen-webhooks");

// Deploy the webhook server as a Modal function
app.function({
  image: base_image,
  secrets: [
    modal.Secret.from_name("github-webhook-secret"),
    modal.Secret.from_name("linear-api-key"),
    modal.Secret.from_name("sentry-dsn"),
    modal.Secret.from_name("supabase-credentials")
  ]
})
  .asgi_app()
  .export("webhook_server", () => {
    console.log("Starting webhook server");
    return createWebhookApp();
  });

// Export the Modal app
module.exports = app;

