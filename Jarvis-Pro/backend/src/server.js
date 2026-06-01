const path = require('path');
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

const distPath = path.join(__dirname, '..', 'frontend', 'dist');

// Serve static UI
app.use('/', express.static(distPath));

// Basic health endpoint
app.get('/api/health', (req, res) => {
  res.json({ ok: true });
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  const { message } = req.body || {};
  if (!message || typeof message !== 'string') {
    return res.status(400).json({ error: 'message is required' });
  }

  // Minimal command router stub.
  // Later you can map intents to your existing Python automation agents.
  const normalized = message.trim().toLowerCase();

  const reply = (() => {
    if (normalized === 'help' || normalized === '/help') {
      return [
        'Jarvis-Pro prototype running.',
        'Try commands like:',
        '- open youtube: <query>',
        '- play music spotify',
        '- control volume up/down',
        '- system status',
        '- (PC control actions to be wired to your automation modules)'
      ].join('\n');
    }

    if (normalized.includes('system status') || normalized.includes('pc status')) {
      return 'Status: prototype only (integration pending).';
    }

    if (normalized.startsWith('open youtube')) {
      const q = message.replace(/open youtube/i, '').trim();
      return `You asked to open YouTube${q ? ` for: ${q}` : ''}. (Integration pending)';`;
    }

    if (normalized.includes('volume up')) return 'Volume up requested. (Integration pending)';
    if (normalized.includes('volume down')) return 'Volume down requested. (Integration pending)';

    return `You said: "${message}"\n(Prototype router received the message; next step is wiring this to your PC/browser automation modules.)`;
  })();

  res.json({ reply });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Jarvis-Pro backend listening on http://localhost:${port}`);
});

