"""Chat page and floating chat widget for the AI Signal site."""

from __future__ import annotations

import json
from pathlib import Path

from .config import Config

CHAT_API_URL = "https://ai-signal-chat.vik-desai.workers.dev/api/chat"

_SYSTEM_PROMPT = (
    "You are the AI Signal assistant. You help users explore AI industry news and trends. "
    "Use the provided article context to give informed, specific answers. Always cite "
    "article titles when referencing specific news. If you don't have relevant articles, "
    "say so and provide general knowledge."
)

_MODELS = [
    ("google/gemma-4-31b-it:free", "Gemma 4 31B (Free)"),
    ("meta-llama/llama-3.3-70b-instruct:free", "Llama 3.3 70B (Free)"),
    ("qwen/qwen3-coder:free", "Qwen3 Coder (Free)"),
    ("nousresearch/hermes-3-llama-3.1-405b:free", "Hermes 3 405B (Free)"),
]

_STARTERS = [
    "What's happening with NVIDIA?",
    "Latest AI regulation news",
    "Tell me about Microsoft Build 2026",
]


def _model_options() -> str:
    return "".join(
        f'<option value="{model}"{" selected" if i == 0 else ""}>{label}</option>'
        for i, (model, label) in enumerate(_MODELS)
    )


_MODEL_OPTIONS_HTML = _model_options()
_STARTERS_HTML = "".join(
    f'<button type="button" class="ai-chat-starter" data-starter="{question}">{question}</button>'
    for question in _STARTERS
)


CHAT_CSS = """
.visually-hidden{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.chat-page-shell{display:grid;gap:20px}
.chat-page-intro{background:linear-gradient(135deg,rgba(13,107,94,.08),rgba(16,185,129,.12));border:1px solid rgba(13,107,94,.16);border-radius:20px;padding:22px 24px;display:grid;gap:14px}
.chat-page-intro h2{margin:0;border:none;padding:0;font-size:24px;color:var(--brand)}
.chat-page-intro p{margin:0;color:#475569;font-size:15px;max-width:72ch}
.chat-page-chips{display:flex;flex-wrap:wrap;gap:10px}
.chat-page-chip{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border-radius:999px;background:#fff;border:1px solid rgba(13,107,94,.15);color:var(--brand);font-size:12px;font-weight:700;letter-spacing:.02em;text-transform:uppercase}
.ai-chat-app{background:var(--card);border:1px solid var(--border);border-radius:24px;box-shadow:0 20px 45px rgba(15,23,42,.08);overflow:hidden}
.ai-chat-app--page{min-height:72vh;display:grid;grid-template-rows:auto minmax(420px,1fr) auto}
.ai-chat-app--panel{height:100%;display:grid;grid-template-rows:auto minmax(0,1fr) auto;border:none;box-shadow:none;border-radius:22px}
.ai-chat-toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 20px;border-bottom:1px solid var(--border);background:linear-gradient(135deg,rgba(13,107,94,.06),rgba(15,153,131,.08))}
.ai-chat-toolbar-main{display:grid;gap:4px}
.ai-chat-toolbar-title{margin:0;font-size:20px;color:var(--brand);display:flex;align-items:center;gap:10px}
.ai-chat-toolbar-subtitle{margin:0;font-size:13px;color:var(--muted)}
.ai-chat-toolbar-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap;justify-content:flex-end}
.ai-chat-model{display:grid;gap:6px;font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.ai-chat-model select{min-width:240px;max-width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:#fff;color:var(--text);font:inherit;text-transform:none;letter-spacing:0}
.ai-chat-clear{padding:10px 14px;border-radius:12px;border:1px solid rgba(13,107,94,.18);background:#fff;color:var(--brand);font-size:13px;font-weight:700;cursor:pointer;transition:all .2s}
.ai-chat-clear:hover,.ai-chat-send:hover,.ai-chat-starter:hover,.ai-chat-open-full:hover,.ai-chat-bubble-launch:hover,.ai-chat-panel-close:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(13,107,94,.14)}
.ai-chat-clear:hover,.ai-chat-open-full:hover,.ai-chat-panel-close:hover{border-color:rgba(15,153,131,.45);color:var(--brand-light)}
.ai-chat-status{padding:10px 20px 0;color:var(--muted);font-size:12px;min-height:24px}
.ai-chat-messages{padding:18px 20px 16px;display:flex;flex-direction:column;gap:14px;overflow:auto;min-height:0;background:linear-gradient(180deg,rgba(240,245,244,.45),rgba(255,255,255,.95) 120px,#fff)}
.ai-chat-empty{padding:28px 24px;border:1px dashed rgba(13,107,94,.2);border-radius:18px;background:rgba(13,107,94,.03);color:#475569}
.ai-chat-empty strong{display:block;color:var(--brand);margin-bottom:6px}
.ai-chat-message{display:flex;flex-direction:column;gap:6px;max-width:min(82%,760px)}
.ai-chat-message[data-role='user']{align-self:flex-end;align-items:flex-end}
.ai-chat-message[data-role='assistant']{align-self:flex-start;align-items:flex-start}
.ai-chat-bubble{padding:14px 16px;border-radius:20px;line-height:1.6;font-size:14px;white-space:pre-wrap;word-break:break-word}
.ai-chat-message[data-role='user'] .ai-chat-bubble{background:linear-gradient(135deg,var(--brand),var(--brand-light));color:#fff;border-bottom-right-radius:8px}
.ai-chat-message[data-role='assistant'] .ai-chat-bubble{background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.24);color:#12343a;border-bottom-left-radius:8px}
.ai-chat-meta{font-size:11px;color:var(--muted);padding:0 6px}
.ai-chat-typing{display:inline-flex;align-items:center;gap:5px;min-height:18px}
.ai-chat-typing span{width:8px;height:8px;border-radius:50%;background:var(--accent2);opacity:.25;animation:ai-chat-pulse 1.1s infinite ease-in-out}
.ai-chat-typing span:nth-child(2){animation-delay:.15s}
.ai-chat-typing span:nth-child(3){animation-delay:.3s}
.ai-chat-suggestions{padding:0 20px 16px;display:flex;flex-wrap:wrap;gap:10px}
.ai-chat-starter{padding:10px 14px;border-radius:999px;border:1px solid rgba(13,107,94,.14);background:#fff;color:var(--brand);font-size:13px;font-weight:700;cursor:pointer;transition:all .2s}
.ai-chat-starter:hover{background:rgba(16,185,129,.08);border-color:rgba(16,185,129,.3)}
.ai-chat-form{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;padding:18px 20px 20px;border-top:1px solid var(--border);background:#fff}
.ai-chat-input-wrap{position:relative}
.ai-chat-input{width:100%;min-height:56px;max-height:160px;resize:vertical;padding:15px 16px;border:1px solid var(--border);border-radius:16px;font:inherit;color:var(--text);background:#fff;box-shadow:inset 0 1px 2px rgba(15,23,42,.03)}
.ai-chat-input:focus,.ai-chat-model select:focus{outline:none;border-color:var(--brand-light);box-shadow:0 0 0 4px rgba(15,153,131,.12)}
.ai-chat-send{align-self:end;padding:0 20px;height:56px;border:none;border-radius:16px;background:linear-gradient(135deg,var(--brand),var(--accent2));color:#fff;font-size:14px;font-weight:800;cursor:pointer;transition:all .2s}
.ai-chat-send:disabled,.ai-chat-clear:disabled,.ai-chat-starter:disabled{opacity:.55;cursor:default;transform:none;box-shadow:none}
.ai-chat-footnote{padding:0 20px 18px;color:var(--muted);font-size:12px}
.ai-chat-bubble-launch{position:fixed;top:90px;right:24px;z-index:140;width:58px;height:58px;border:none;border-radius:50%;background:linear-gradient(135deg,var(--brand),var(--brand-light));color:#fff;display:flex;align-items:center;justify-content:center;font-size:24px;cursor:pointer;box-shadow:0 18px 36px rgba(13,107,94,.28)}
.ai-chat-bubble-panel{position:fixed;top:156px;right:24px;z-index:145;width:min(400px,calc(100vw - 24px));height:500px;background:var(--card);border:1px solid rgba(13,107,94,.14);border-radius:24px;box-shadow:0 24px 60px rgba(15,23,42,.2);overflow:hidden;display:none}
.ai-chat-bubble-panel.is-open{display:block}
.ai-chat-panel-shell{display:grid;grid-template-rows:auto minmax(0,1fr);height:100%}
.ai-chat-panel-topbar{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:14px 16px;border-bottom:1px solid var(--border);background:linear-gradient(135deg,rgba(13,107,94,.08),rgba(245,158,11,.08))}
.ai-chat-panel-brand{display:flex;align-items:center;gap:10px;font-weight:800;color:var(--brand)}
.ai-chat-panel-actions{display:flex;align-items:center;gap:10px}
.ai-chat-open-full,.ai-chat-panel-close{display:inline-flex;align-items:center;justify-content:center;padding:8px 12px;border-radius:12px;border:1px solid rgba(13,107,94,.16);background:#fff;color:var(--brand);text-decoration:none;font-size:12px;font-weight:800;cursor:pointer;transition:all .2s}
.ai-chat-panel-close{width:36px;padding:0;font-size:18px;line-height:1}
body.page-chat .ai-chat-bubble-launch,body.page-chat .ai-chat-bubble-panel{display:none!important}
@keyframes ai-chat-pulse{0%,80%,100%{opacity:.25;transform:scale(.9)}40%{opacity:1;transform:scale(1)}}
@media(max-width:900px){
  .ai-chat-toolbar{align-items:flex-start;flex-direction:column}
  .ai-chat-toolbar-actions{width:100%;justify-content:flex-start}
  .ai-chat-model select{min-width:min(100%,260px)}
}
@media(max-width:640px){
  .chat-page-intro{padding:18px}
  .chat-page-intro h2{font-size:21px}
  .ai-chat-app--page{min-height:calc(100vh - 220px)}
  .ai-chat-message{max-width:100%}
  .ai-chat-form{grid-template-columns:1fr}
  .ai-chat-send{width:100%}
  .ai-chat-bubble-launch{top:auto;bottom:24px;right:16px}
  .ai-chat-bubble-panel{top:auto;right:12px;bottom:92px;left:12px;width:auto;height:min(70vh,520px)}
}
"""


def _chat_shell(mode: str, title: str, subtitle: str, compact: bool = False) -> str:
    empty = (
        "Ask about companies, policy, products, or events. Relevant article summaries "
        "from AI Signal will be added as context automatically."
    )
    footnote = (
        "Responses are generated by free AI models using relevant articles from AI Signal as context."
    )
    return f"""
<div class="ai-chat-app ai-chat-app--{mode}" data-ai-chat-root data-chat-mode="{mode}">
  <div class="ai-chat-toolbar">
    <div class="ai-chat-toolbar-main">
      <h3 class="ai-chat-toolbar-title">💬 {title}</h3>
      <p class="ai-chat-toolbar-subtitle">{subtitle}</p>
    </div>
    <div class="ai-chat-toolbar-actions">
      <label class="ai-chat-model">Model
        <select data-chat-model aria-label="Select AI model">
          {_MODEL_OPTIONS_HTML}
        </select>
      </label>
      <button type="button" class="ai-chat-clear" data-chat-clear>Clear chat</button>
    </div>
  </div>
  <div class="ai-chat-status" data-chat-status aria-live="polite"></div>
  <div class="ai-chat-messages" data-chat-messages>
    <div class="ai-chat-empty" data-chat-empty>
      <strong>Ask AI Signal anything about the latest industry news.</strong>
      <span>{empty}</span>
    </div>
  </div>
  <div class="ai-chat-suggestions" data-chat-suggestions>
    {_STARTERS_HTML}
  </div>
  <form class="ai-chat-form" data-chat-form>
    <div class="ai-chat-input-wrap">
      <label class="visually-hidden" for="chat-input-{mode}">Message</label>
      <textarea id="chat-input-{mode}" class="ai-chat-input" data-chat-input rows="2" placeholder="Ask about AI news, companies, regulation, or events…"></textarea>
    </div>
    <button type="submit" class="ai-chat-send" data-chat-send>Send</button>
  </form>
  <div class="ai-chat-footnote">{footnote if not compact else 'Searches 60 days of curated AI news to answer your questions.'}</div>
</div>
"""


_CHAT_SHARED_JS = r"""
<script>
(function(){
  if(window.__AI_SIGNAL_CHAT_READY__) return;
  window.__AI_SIGNAL_CHAT_READY__ = true;

  const CHAT_API_URL = __CHAT_API_URL__;
  const BASE_SYSTEM_PROMPT = __SYSTEM_PROMPT__;
  // Resolve articles.json and chat.html relative to the current page
  const PAGE_PATH = window.location.pathname;
  const BASE_DIR = PAGE_PATH.substring(0, PAGE_PATH.lastIndexOf('/') + 1);
  // Walk up from subdirectories (snapshots/, entities/, events/, topics/) to site root
  const DEPTH = (BASE_DIR.match(/\//g) || []).length - 1;
  const REL_PREFIX = DEPTH > 0 ? '../'.repeat(DEPTH) : '';
  // On file:// protocol or root-level pages, use direct path
  const ARTICLES_URL = (window.location.protocol === 'file:' ? '' : REL_PREFIX) + 'articles.json';
  const OPEN_FULL_CHAT_URL = (window.location.protocol === 'file:' ? '' : REL_PREFIX) + 'chat.html';
  const STOP_WORDS = new Set([
    'a','an','and','are','as','at','be','but','by','for','from','how','i','if','in','into','is','it','latest',
    'me','news','of','on','or','the','to','tell','what','whats','when','where','who','with','you','your'
  ]);

  function renderMarkdown(text){
    // Convert markdown to HTML for chat display
    let html = escapeHtml(text);
    // Headers: ### → <strong>
    html = html.replace(/^#{1,4}\s+(.+)$/gm, '<strong>$1</strong>');
    // Bold: **text** or __text__
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');
    // Italic: *text* or _text_
    html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code style="background:#e2e8f0;padding:1px 5px;border-radius:3px;font-size:0.9em">$1</code>');
    // Bullet lists: * or - at line start
    html = html.replace(/^[\*\-]\s+(.+)$/gm, '• $1');
    // Numbered lists: 1. 2. etc.
    html = html.replace(/^\d+\.\s+(.+)$/gm, function(m, p1){ return '&bull; ' + p1; });
    // Markdown tables: strip pipe formatting
    html = html.replace(/^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$/gm, '');
    html = html.replace(/^\|(.+)\|$/gm, function(m, inner){
      return inner.split('|').map(function(c){ return c.trim(); }).filter(Boolean).join(' — ');
    });
    // Links: [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener" style="color:var(--brand-light)">$1</a>');
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  function escapeHtml(value){
    return String(value ?? '')
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;')
      .replace(/'/g,'&#39;');
  }

  function normalizeWhitespace(value){
    return String(value ?? '').replace(/\s+/g,' ').trim();
  }

  function autoResize(textarea){
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
  }

  function extractTerms(query){
    const lower = String(query || '').toLowerCase();
    const phraseMatches = [...lower.matchAll(/"([^"]+)"/g)].map(match => normalizeWhitespace(match[1])).filter(Boolean);
    const remainder = lower.replace(/"[^"]+"/g, ' ');
    const words = remainder.match(/[a-z0-9][a-z0-9.+-]*/g) || [];
    const filtered = words.filter(word => word.length > 1 && !STOP_WORDS.has(word));
    const unique = [...new Set([...phraseMatches, ...filtered])];
    if(!unique.length && normalizeWhitespace(lower)) unique.push(normalizeWhitespace(lower));
    return unique.slice(0, 12);
  }

  function articleBlob(article){
    return [
      article.title,
      article.summary,
      article.source,
      ...(article.entities || []),
      ...(article.themes || []),
      article.event || ''
    ].join(' ').toLowerCase();
  }

  async function loadArticles(state){
    if(state.articles) return state.articles;
    if(state.articlesPromise) return state.articlesPromise;
    state.articlesPromise = fetch(ARTICLES_URL, {cache:'no-store'})
      .then(response => {
        if(!response.ok) throw new Error('Unable to load articles.json');
        return response.json();
      })
      .then(items => Array.isArray(items) ? items : [])
      .catch(() => [])
      .finally(() => { state.articlesPromise = null; });
    state.articles = await state.articlesPromise;
    return state.articles;
  }

  function rankArticles(query, articles){
    const terms = extractTerms(query);
    const fullQuery = normalizeWhitespace(String(query || '').toLowerCase());
    return articles
      .map(article => {
        const title = String(article.title || '').toLowerCase();
        const summary = String(article.summary || '').toLowerCase();
        const entities = (article.entities || []).join(' ').toLowerCase();
        const themes = (article.themes || []).join(' ').toLowerCase();
        const eventName = String(article.event || '').toLowerCase();
        let score = 0;
        for(const term of terms){
          if(title.includes(term)) score += 8;
          if(summary.includes(term)) score += 5;
          if(entities.includes(term)) score += 6;
          if(themes.includes(term)) score += 3;
          if(eventName.includes(term)) score += 4;
        }
        if(fullQuery){
          if(title.includes(fullQuery)) score += 10;
          if(summary.includes(fullQuery)) score += 6;
        }
        return {article, score, blob: articleBlob(article)};
      })
      .filter(item => item.score > 0 || (fullQuery && item.blob.includes(fullQuery)))
      .sort((a, b) => {
        if(b.score !== a.score) return b.score - a.score;
        return String(b.article.date || '').localeCompare(String(a.article.date || ''));
      })
      .slice(0, 5)
      .map(item => item.article);
  }

  async function buildContext(query, state){
    const articles = await loadArticles(state);
    const matches = rankArticles(query, articles);
    const context = matches.length
      ? matches.map((article, index) => {
          const summary = normalizeWhitespace(article.summary || '').slice(0, 400);
          const source = normalizeWhitespace(article.source || 'Unknown source');
          const date = normalizeWhitespace(article.date || 'Unknown date');
          return `${index + 1}. Title: ${article.title || 'Untitled'}\n   Date: ${date}\n   Source: ${source}\n   Summary: ${summary}`;
        }).join('\n')
      : 'No relevant article context found.';
    return {
      matches,
      systemPrompt: `${BASE_SYSTEM_PROMPT}\n\nArticle context:\n${context}`
    };
  }

  function coerceText(value){
    if(typeof value === 'string') return value;
    if(Array.isArray(value)) return value.map(coerceText).join('');
    if(value && typeof value === 'object'){
      if(typeof value.text === 'string') return value.text;
      if(typeof value.content === 'string') return value.content;
      if(Array.isArray(value.content)) return value.content.map(coerceText).join('');
    }
    return '';
  }

  function extractDelta(payload){
    if(typeof payload === 'string') return payload;
    if(!payload || typeof payload !== 'object') return '';
    if(typeof payload.output_text === 'string') return payload.output_text;
    if(typeof payload.content === 'string') return payload.content;
    if(payload.delta) return coerceText(payload.delta);
    if(payload.response && payload.response.output_text && typeof payload.response.output_text.delta === 'string') {
      return payload.response.output_text.delta;
    }
    if(Array.isArray(payload.choices) && payload.choices.length){
      const choice = payload.choices[0];
      return coerceText(choice.delta?.content)
        || coerceText(choice.message?.content)
        || coerceText(choice.text)
        || coerceText(choice.delta)
        || '';
    }
    return '';
  }

  async function streamResponse(requestBody, onToken){
    const response = await fetch(CHAT_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream, application/json'
      },
      body: JSON.stringify(requestBody)
    });

    if(!response.ok){
      const message = await response.text().catch(() => 'The chat service returned an error.');
      throw new Error(message || 'The chat service returned an error.');
    }

    const contentType = response.headers.get('content-type') || '';
    if(!response.body || !/event-stream/i.test(contentType)){
      const raw = await response.text().catch(() => '');
      let payload;
      try {
        payload = raw ? JSON.parse(raw) : {};
      } catch {
        payload = {content: raw};
      }
      const text = extractDelta(payload) || coerceText(payload.message) || coerceText(payload.output) || coerceText(payload.response);
      if(text) onToken(text);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    const processChunk = chunk => {
      const events = chunk.split(/\r?\n\r?\n/);
      buffer = events.pop() || '';
      for(const event of events){
        const lines = event.split(/\r?\n/).filter(line => line.startsWith('data:'));
        for(const line of lines){
          const raw = line.slice(5).trim();
          if(!raw) continue;
          if(raw === '[DONE]') return true;
          try {
            const parsed = JSON.parse(raw);
            const delta = extractDelta(parsed);
            if(delta) onToken(delta);
          } catch {
            onToken(raw);
          }
        }
      }
      return false;
    };

    while(true){
      const {value, done} = await reader.read();
      if(done) break;
      buffer += decoder.decode(value, {stream:true});
      if(processChunk(buffer)) return;
    }

    if(buffer.trim()) processChunk(buffer + '\n\n');
  }

  function renderMessage(messagesEl, role, content){
    const wrapper = document.createElement('div');
    wrapper.className = 'ai-chat-message';
    wrapper.dataset.role = role;

    const bubble = document.createElement('div');
    bubble.className = 'ai-chat-bubble';
    bubble.innerHTML = renderMarkdown(content);

    const meta = document.createElement('div');
    meta.className = 'ai-chat-meta';
    meta.textContent = role === 'user' ? 'You' : 'AI Signal';

    wrapper.appendChild(bubble);
    wrapper.appendChild(meta);
    messagesEl.appendChild(wrapper);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return {wrapper, bubble};
  }

  function renderTyping(messagesEl){
    const rendered = renderMessage(messagesEl, 'assistant', '');
    rendered.bubble.innerHTML = '<span class="ai-chat-typing"><span></span><span></span><span></span></span>';
    return rendered;
  }

  function setBusy(root, busy){
    root.querySelectorAll('button, textarea, select').forEach(el => { el.disabled = !!busy; });
  }

  function updateStatus(root, message){
    const status = root.querySelector('[data-chat-status]');
    if(status) status.textContent = message || '';
  }

  function clearChat(root, state){
    state.messages = [];
    const messagesEl = root.querySelector('[data-chat-messages]');
    messagesEl.innerHTML = '<div class="ai-chat-empty" data-chat-empty><strong>Ask AI Signal anything about the latest industry news.</strong><span>Ask about companies, policy, products, or events. Relevant article summaries from AI Signal will be added as context automatically.</span></div>';
    updateStatus(root, '');
  }

  function initChat(root){
    if(root.dataset.chatInitialized === 'true') return;
    root.dataset.chatInitialized = 'true';

    const state = {messages: [], articles: null, articlesPromise: null, busy: false};
    const form = root.querySelector('[data-chat-form]');
    const input = root.querySelector('[data-chat-input]');
    const messagesEl = root.querySelector('[data-chat-messages]');
    const starters = root.querySelector('[data-chat-suggestions]');
    const modelSelect = root.querySelector('[data-chat-model]');
    const clearButton = root.querySelector('[data-chat-clear]');

    autoResize(input);

    input.addEventListener('input', () => autoResize(input));
    clearButton.addEventListener('click', () => clearChat(root, state));

    starters.addEventListener('click', event => {
      const button = event.target.closest('[data-starter]');
      if(!button || state.busy) return;
      input.value = button.dataset.starter || '';
      autoResize(input);
      form.requestSubmit();
    });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      const text = String(input.value || '').trim();
      if(!text || state.busy) return;

      const empty = root.querySelector('[data-chat-empty]');
      if(empty) empty.remove();

      state.busy = true;
      setBusy(root, true);
      updateStatus(root, 'Searching article context…');
      renderMessage(messagesEl, 'user', text);
      state.messages.push({role:'user', content:text});
      input.value = '';
      autoResize(input);

      const typing = renderTyping(messagesEl);
      let assistantText = '';
      let receivedToken = false;

      try {
        const context = await buildContext(text, state);
        updateStatus(root, context.matches.length
          ? `Using ${context.matches.length} relevant article${context.matches.length === 1 ? '' : 's'} as context.`
          : 'No strong article matches found. Using general model knowledge too.');

        await streamResponse({
          model: modelSelect.value,
          stream: true,
          messages: [{role:'system', content: context.systemPrompt}, ...state.messages]
        }, token => {
          if(!receivedToken){
            typing.bubble.textContent = '';
            receivedToken = true;
          }
          assistantText += token;
          typing.bubble.innerHTML = renderMarkdown(assistantText);
          messagesEl.scrollTop = messagesEl.scrollHeight;
        });

        if(!assistantText.trim()){
          assistantText = 'I did not receive a response from the chat service. Please try again.';
          typing.bubble.textContent = assistantText;
        }
      } catch (error) {
        assistantText = `Sorry — the chat service failed: ${error?.message || 'unknown error'}`;
        typing.bubble.textContent = assistantText;
        updateStatus(root, 'Chat request failed.');
      } finally {
        state.messages.push({role:'assistant', content: assistantText});
        state.busy = false;
        setBusy(root, false);
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }
    });
  }

  function initBubble(){
    const launch = document.querySelector('[data-chat-launch]');
    const panel = document.querySelector('[data-chat-panel]');
    const close = document.querySelector('[data-chat-close]');
    const fullLinks = document.querySelectorAll('[data-chat-open-full]');
    if(!launch || !panel || !close) return;

    const openPanel = () => {
      panel.classList.add('is-open');
      launch.setAttribute('aria-expanded', 'true');
    };
    const closePanel = () => {
      panel.classList.remove('is-open');
      launch.setAttribute('aria-expanded', 'false');
    };

    launch.addEventListener('click', () => panel.classList.contains('is-open') ? closePanel() : openPanel());
    close.addEventListener('click', closePanel);
    document.addEventListener('keydown', event => {
      if(event.key === 'Escape') closePanel();
    });
    document.addEventListener('click', event => {
      if(!panel.classList.contains('is-open')) return;
      if(panel.contains(event.target) || launch.contains(event.target)) return;
      closePanel();
    });
    fullLinks.forEach(link => link.setAttribute('href', OPEN_FULL_CHAT_URL));
  }

  document.querySelectorAll('[data-ai-chat-root]').forEach(initChat);
  initBubble();
})();
</script>
""".replace("__CHAT_API_URL__", json.dumps(CHAT_API_URL)).replace("__SYSTEM_PROMPT__", json.dumps(_SYSTEM_PROMPT))


CHAT_BUBBLE_HTML = (
    """
<button type="button" class="ai-chat-bubble-launch" data-chat-launch aria-label="Open AI Signal chat" aria-expanded="false">💬</button>
<div class="ai-chat-bubble-panel" data-chat-panel aria-label="AI Signal chat panel">
  <div class="ai-chat-panel-shell">
    <div class="ai-chat-panel-topbar">
      <div class="ai-chat-panel-brand">📡 AI Signal Chat</div>
      <div class="ai-chat-panel-actions">
        <a class="ai-chat-open-full" data-chat-open-full href="chat.html">Open full chat</a>
        <button type="button" class="ai-chat-panel-close" data-chat-close aria-label="Close chat">×</button>
      </div>
    </div>
"""
    + _chat_shell("panel", "Quick chat", "Ask about recent AI Signal coverage in a compact view.", compact=True)
    + """
  </div>
</div>
"""
    + _CHAT_SHARED_JS
)


def build_chat_page(cfg: Config, site: Path, canonical: list[dict], entity_files: dict[str, str]) -> int:
    """Build the dedicated AI chat page."""
    del cfg, entity_files
    from .site import _render, _write

    body = (
        """
<section class="chat-page-shell">
  <div class="chat-page-intro">
    <div>
      <h2>Chat with AI Signal</h2>
      <p>Ask questions about the latest AI industry news. The assistant searches through the last 60 days of news articles collected from the web, finds the most relevant stories, and uses them to give you informed, grounded answers.</p>
    </div>
    <div class="chat-page-chips">
      <span class="chat-page-chip">1,700+ curated articles</span>
      <span class="chat-page-chip">60 days of coverage</span>
      <span class="chat-page-chip">Powered by free AI models</span>
    </div>
  </div>
"""
        + _chat_shell("page", "AI Signal assistant", "Ask about companies, regulation, infrastructure, events, or any AI topic.")
        + """
</section>
"""
    )
    _write(
        site / "chat.html",
        _render(
            "AI Chat",
            body,
            active="chat",
            subtitle=f"Chat across {len(canonical):,} indexed AI Signal articles",
        ),
    )
    return 1
