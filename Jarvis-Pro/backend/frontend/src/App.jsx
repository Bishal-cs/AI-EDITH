import React, { useEffect, useMemo, useState } from 'react';

function Bubble({ who, text }) {
  return (
    <div className={who === 'user' ? 'msg user' : 'msg ai'}>
      <div className="bubble">{text}</div>
    </div>
  );
}

export default function App() {
  const [status, setStatus] = useState('starting...');
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState([
    {
      who: 'ai',
      text:
        'Jarvis-Pro prototype ready.\nType: help\nThen try: open youtube cats\n(Integration with PC/browser control will be wired next.)',
    },
  ]);

  const canSend = useMemo(() => input.trim().length > 0 && !busy, [input, busy]);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch('/api/health');
        if (!r.ok) throw new Error('health failed');
        setStatus('online');
      } catch (e) {
        setStatus('offline (backend not reachable)');
      }
    })();
  }, []);

  async function send() {
    const msg = input.trim();
    if (!msg) return;

    setMessages((m) => [...m, { who: 'user', text: msg }]);
    setInput('');
    setBusy(true);

    try {
      const r = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg }),
      });

      const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        setMessages((m) => [
          ...m,
          { who: 'ai', text: data?.error ? String(data.error) : 'Request failed.' },
        ]);
      } else {
        setMessages((m) => [...m, { who: 'ai', text: String(data.reply ?? '') }]);
      }
    } catch (e) {
      setMessages((m) => [...m, { who: 'ai', text: 'Network error: cannot reach backend.' }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="wrap">
      <div className="top">
        <div className="brand">
          <div className="logo" />
          <div>
            <div className="title">Jarvis-Pro</div>
            <div className="status">{status}</div>
          </div>
        </div>
        <div className="hint">
          Router commands: <span className="kbd">help</span> · <span className="kbd">open youtube ...</span> ·{' '}
          <span className="kbd">volume up</span>
        </div>
      </div>

      <div className="card">
        <div className="chat">
          {messages.map((m, idx) => (
            <Bubble key={idx} who={m.who} text={m.text} />
          ))}
        </div>
        <div className="composer">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') send();
            }}
            placeholder="Ask Jarvis..."
            disabled={busy}
          />
          <button onClick={send} disabled={!canSend}>
            {busy ? 'Thinking...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

