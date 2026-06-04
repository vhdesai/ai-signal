const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
const DEFAULT_MODEL = "google/gemma-3-4b-it:free";
const MAX_TOKENS = 1024;
const DAILY_LIMIT = 20;
const SYSTEM_PROMPT = `You are AI Signal, the embedded assistant for AI Signal, a daily AI news intelligence site. Help users quickly understand important AI developments, summarize articles, compare models, and surface actionable insights. Be accurate, concise, practical, and transparent about uncertainty. When relevant, emphasize what matters for operators, builders, and decision-makers following the AI ecosystem.`;

const rateLimitStore = new Map();
let currentDayKey = getDayKey();

function getDayKey() {
  return new Date().toISOString().slice(0, 10);
}

function resetRateLimitStoreIfNeeded() {
  const dayKey = getDayKey();
  if (dayKey !== currentDayKey) {
    rateLimitStore.clear();
    currentDayKey = dayKey;
  }
}

function getClientIp(request) {
  const cfIp = request.headers.get("CF-Connecting-IP");
  if (cfIp) {
    return cfIp.trim();
  }

  const forwardedFor = request.headers.get("X-Forwarded-For");
  if (forwardedFor) {
    return forwardedFor.split(",")[0].trim();
  }

  return "unknown";
}

function getCorsHeaders(origin) {
  const allowedOrigin = origin && /^https?:\/\//i.test(origin) ? origin : "*";

  return {
    "Access-Control-Allow-Origin": allowedOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin"
  };
}

function isJsonRequest(request) {
  const contentType = request.headers.get("Content-Type");
  return Boolean(contentType && contentType.toLowerCase().includes("application/json"));
}

function getSecurityHeaders() {
  return {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "accelerometer=(), autoplay=(), camera=(), geolocation=(), gyroscope=(), microphone=(), payment=(), usb=()",
    "Cross-Origin-Resource-Policy": "same-site",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
  };
}

function buildHeaders(origin, extras = {}) {
  return {
    ...getCorsHeaders(origin),
    ...getSecurityHeaders(),
    ...extras
  };
}

function jsonResponse(payload, status, origin, extras = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: buildHeaders(origin, {
      "Content-Type": "application/json; charset=utf-8",
      ...extras
    })
  });
}

function validateMessages(messages) {
  if (!Array.isArray(messages) || messages.length === 0) {
    return "The 'messages' field must be a non-empty array.";
  }

  for (const message of messages) {
    if (!message || typeof message !== "object" || Array.isArray(message)) {
      return "Each message must be an object.";
    }

    if (typeof message.role !== "string" || message.role.trim() === "") {
      return "Each message must include a non-empty string 'role'.";
    }

    const contentType = typeof message.content;
    const hasValidContent = contentType === "string" || Array.isArray(message.content);
    if (!hasValidContent) {
      return "Each message must include 'content' as a string or content array.";
    }
  }

  return null;
}

function consumeRateLimit(ip) {
  resetRateLimitStoreIfNeeded();

  const count = rateLimitStore.get(ip) ?? 0;
  if (count >= DAILY_LIMIT) {
    return false;
  }

  rateLimitStore.set(ip, count + 1);
  return true;
}

function buildUpstreamPayload(body) {
  const requestedModel = typeof body.model === "string" && body.model.trim() ? body.model.trim() : DEFAULT_MODEL;

  return {
    model: requestedModel,
    stream: true,
    max_tokens: MAX_TOKENS,
    messages: [
      {
        role: "system",
        content: SYSTEM_PROMPT
      },
      ...body.messages
    ]
  };
}

async function handleChat(request, env) {
  const origin = request.headers.get("Origin");

  if (!env.OPENROUTER_API_KEY) {
    return jsonResponse({ error: "Server is missing OPENROUTER_API_KEY." }, 500, origin);
  }

  const ip = getClientIp(request);
  if (!consumeRateLimit(ip)) {
    return jsonResponse(
      { error: "Rate limit exceeded. Max 20 requests per IP per day." },
      429,
      origin,
      { "Retry-After": "86400" }
    );
  }

  if (!isJsonRequest(request)) {
    return jsonResponse({ error: "Content-Type must be application/json." }, 415, origin);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "Request body must be valid JSON." }, 400, origin);
  }

  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return jsonResponse({ error: "Request body must be a JSON object." }, 400, origin);
  }

  const validationError = validateMessages(body.messages);
  if (validationError) {
    return jsonResponse({ error: validationError }, 400, origin);
  }

  let upstreamResponse;
  try {
    upstreamResponse = await fetch(OPENROUTER_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        "HTTP-Referer": origin || "https://ai-signal.local",
        "X-Title": "AI Signal"
      },
      body: JSON.stringify(buildUpstreamPayload(body))
    });
  } catch {
    return jsonResponse({ error: "Failed to reach OpenRouter." }, 502, origin);
  }

  if (!upstreamResponse.ok) {
    const errorText = await upstreamResponse.text();
    let details = errorText;

    try {
      details = JSON.parse(errorText);
    } catch {
      // Keep raw text details when upstream does not return JSON.
    }

    return jsonResponse(
      {
        error: "OpenRouter request failed.",
        details
      },
      upstreamResponse.status || 502,
      origin
    );
  }

  if (!upstreamResponse.body) {
    return jsonResponse({ error: "OpenRouter returned an empty response body." }, 502, origin);
  }

  return new Response(upstreamResponse.body, {
    status: 200,
    headers: buildHeaders(origin, {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform"
    })
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin");
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: buildHeaders(origin)
      });
    }

    if (url.pathname !== "/api/chat") {
      return jsonResponse({ error: "Not found." }, 404, origin);
    }

    if (request.method !== "POST") {
      return jsonResponse({ error: "Method not allowed." }, 405, origin, { Allow: "POST, OPTIONS" });
    }

    return handleChat(request, env);
  }
};
