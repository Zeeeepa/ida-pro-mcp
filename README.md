# Modal Webhook Server for GitHub and Linear

This project sets up a webhook server using [Modal](https://modal.com/) to handle GitHub and Linear webhook events. It includes Sentry for monitoring and error tracking, and Supabase for event storage.

## Features

- Receive and process GitHub webhook events
- Receive and process Linear webhook events
- Store webhook events in Supabase for persistence and analysis
- Monitor application performance and errors with Sentry
- Deploy as a serverless application using Modal

## Prerequisites

- Modal account and CLI installed
- GitHub repository with webhook configuration
- Linear workspace with webhook configuration
- Sentry project for monitoring
- Supabase project for data storage

## Setup

### 1. Install Modal CLI

```bash
pip install modal
```

### 2. Set up secrets in Modal

You need to create the following secrets in Modal:

```bash
modal secret create github-webhook-secret --value "your-github-webhook-secret"
modal secret create linear-api-key --value "your-linear-api-key"
modal secret create sentry-dsn --value "your-sentry-dsn"
modal secret create supabase-credentials --json '{"url": "your-supabase-url", "key": "your-supabase-anon-key"}'
```

### 3. Create Supabase table

Create a `webhook_events` table in your Supabase project with the following structure:

```sql
CREATE TABLE webhook_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  received_at TIMESTAMP WITH TIME ZONE NOT NULL,
  processed BOOLEAN DEFAULT FALSE,
  processed_at TIMESTAMP WITH TIME ZONE
);

-- Create index for faster queries
CREATE INDEX webhook_events_source_event_type_idx ON webhook_events (source, event_type);
CREATE INDEX webhook_events_processed_idx ON webhook_events (processed);
```

### 4. Deploy the webhook server

```bash
modal deploy modal.js
```

After deployment, Modal will provide you with a URL for your webhook server.

### 5. Configure webhooks

#### GitHub Webhooks

1. Go to your GitHub repository settings
2. Navigate to Webhooks
3. Add a new webhook:
   - Payload URL: `https://your-modal-app-url/webhooks/github`
   - Content type: `application/json`
   - Secret: The same secret you configured in Modal
   - Events: Select the events you want to receive (e.g., Pull requests, Issues, etc.)

#### Linear Webhooks

1. Go to your Linear workspace settings
2. Navigate to API > Webhooks
3. Add a new webhook:
   - URL: `https://your-modal-app-url/webhooks/linear`
   - Events: Select the events you want to receive

## Advanced Sentry Use Cases

Here are some advanced Sentry use cases for this application:

1. **Performance Monitoring**: Track the performance of webhook processing to identify bottlenecks.

2. **Error Tracking and Alerting**: Set up alerts for critical errors in webhook processing to be notified immediately.

3. **Custom Contexts**: Add custom context to Sentry events to include relevant information about the webhook event being processed.

4. **Release Tracking**: Track deployments and correlate errors with specific releases.

5. **User Identification**: Associate webhook events with users or repositories to understand impact.

6. **Custom Metrics**: Track custom metrics like webhook processing time, success rates, etc.

7. **Distributed Tracing**: Trace requests across different services to understand the full flow of webhook processing.

8. **Session Replay**: Capture and replay user sessions to understand the context of errors.

9. **Breadcrumbs**: Add breadcrumbs to track the flow of webhook processing for better debugging.

10. **Environment Segmentation**: Separate development, staging, and production environments for better error analysis.

11. **Anomaly Detection**: Set up anomaly detection to identify unusual patterns in webhook processing.

12. **Custom Dashboards**: Create custom dashboards to visualize webhook processing metrics.

## Usage

Once deployed, the webhook server will automatically process incoming webhook events from GitHub and Linear. Events will be stored in Supabase and can be queried for analysis.

You can extend the event handlers in `modal.js` to implement custom logic for different event types.

## License

MIT

