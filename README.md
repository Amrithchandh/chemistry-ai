# Chemistry AI

A personal chemistry study assistant: a light-themed dashboard with an AI chat,
study progress, a drawing whiteboard, quick actions, a study calendar and live
system readings. Dark mode is one click away.

## Structure

```
chemistry-ai/
├── backend/main.py     FastAPI server (chat with tool calling, uploads, memory, reminders)
├── backend/tools.py    Tool registry and built-in tools
├── plugins/            Drop-in plugins (example: molar_mass.py)
├── web/index.html      Dashboard (HTML, CSS and JavaScript in one file)
├── requirements.txt
├── .env.example
└── README.md
```

## Install

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

## Configure

Edit `.env`:

| Variable | Meaning |
|---|---|
| `APP_NAME` | Name shown in the UI and page title |
| `USER_NAME` | Name used in the greeting |
| `LLM_BASE_URL` | Base URL of an OpenAI-compatible API |
| `LLM_API_KEY` | Your API key (kept on the server, never sent to the browser) |
| `LLM_MODEL` | Model name your provider offers |

## One-time setup for browser control

```bash
playwright install chromium
```

## Run

```bash
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000

## Customize

- Subjects, calendar events and quick-action prompts: the `SUBJECTS`, `EVENTS`,
  `CHIPS` and `QUICK` arrays near the top of the script in `web/index.html`.
- Colors: the CSS variables at the top of the same file.
- Tutor behavior: `SYSTEM_PROMPT` in `backend/main.py`.

## Features and how to use them

| Feature | How |
|---|---|
| Voice and wake word | Click "Wake word: off" to turn it on (Chrome or Edge, microphone allowed), then say "Hey Wanda, ..." |
| Animated avatar | Pulses while listening, moves its mouth while speaking |
| Volume, brightness, open apps | "Set volume to 40", "Open Calculator". Each action asks for approval first |
| Browser and YouTube | "Play lo-fi chemistry music on YouTube", "Open https://..." (needs Playwright setup) |
| Web search and weather | "Search for ...", "Weather in Kozhikode" |
| Documents | Quick action "Upload notes" (PDF, DOCX, XLSX, TXT, CSV), then ask about it |
| Screen vision | "What is on my screen?" (asks for approval) |
| Reminders | "Remind me to revise in 10 minutes" |
| Email | Set SMTP_* in `.env`, then "Email ... to ..." (asks for approval) |
| Memory | "Remember that my exam is on Oct 14". See or delete facts under "What I remember" |

## Plugins

Create `plugins/my_tool.py` with a `register(tool)` function, as in `plugins/molar_mass.py`,
and restart the server. The AI can then call it.

## Notes

- Voice runs in the browser, so it needs Chrome or Edge. Use HTTPS or localhost.
- System, screen and email tools run on the machine hosting the server, so keep those for local use.
