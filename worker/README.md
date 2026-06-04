# AI Signal Chat Worker

## Setup
1. Open a terminal in `C:\Users\vdesai\OneDrive - Microsoft\Documents\tvfr\6-AIProj\Newsletter\ext-host\worker`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set the OpenRouter API key:
   ```bash
   npx wrangler secret put OPENROUTER_API_KEY
   ```
4. Start local development:
   ```bash
   npx wrangler dev
   ```
5. Deploy the worker:
   ```bash
   npx wrangler deploy
   ```

## API
- Endpoint: `POST /api/chat`
- Body:
  ```json
  {
    "messages": [
      { "role": "user", "content": "Summarize today's AI news." }
    ],
    "model": "google/gemma-3-4b-it:free"
  }
  ```
- `model` is optional and defaults to `google/gemma-3-4b-it:free`.
- Responses are streamed back as Server-Sent Events (SSE).

## Notes
- The worker applies a 20 requests per IP per day in-memory rate limit with a daily UTC reset.
- CORS headers allow the request origin for browser calls from your site.
- Requests must use `Content-Type: application/json`.
- The worker injects an `AI Signal` system prompt and caps `max_tokens` at `1024`.
