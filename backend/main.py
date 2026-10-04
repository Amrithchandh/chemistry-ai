"""Chemistry AI backend: chat with tool calling, memory, uploads, reminders, stats."""
import asyncio, json, os
from pathlib import Path

import psutil
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()
from backend import tools as T  # noqa: E402  (after load_dotenv so env is ready)

APP_NAME = os.getenv("APP_NAME", "Chemistry AI")
USER_NAME = os.getenv("USER_NAME", "Student")
SYSTEM_PROMPT = (
    "You are Chemistry AI, a friendly voice-first chemistry tutor. Keep spoken answers short and "
    "plain (no markdown). Use tools when they help: search, weather, files, reminders, system "
    "control, browser, screen. Save lasting facts about the user with the remember tool. "
    "Explain step by step, state units, and say so when unsure."
)
T.load_plugins()
app = FastAPI(title=APP_NAME)


class Msg(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(max_length=8000)


class ChatReq(BaseModel):
    messages: list[Msg] = Field(min_length=1, max_length=40)
    approve: list[str] = []  # tool names the user approved for this request


@app.get("/api/config")
def config():
    return {"appName": APP_NAME, "userName": USER_NAME}


@app.get("/api/stats")
def stats():
    return {"cpu": psutil.cpu_percent(interval=0.2), "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage(str(Path.home())).percent}


@app.get("/api/memory")
def memory():
    return [{"id": i, "fact": f} for i, f in T.memories()]


@app.delete("/api/memory/{mid}")
def forget(mid: int):
    with T.db() as c:
        c.execute("DELETE FROM memory WHERE id=?", (mid,))
    return {"ok": True}


@app.get("/api/reminders/due")
def reminders():
    return T.due_reminders()


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    name = Path(file.filename or "file").name
    if Path(name).suffix.lower() not in {".pdf", ".docx", ".xlsx", ".xlsm", ".txt", ".md", ".csv"}:
        raise HTTPException(400, "Supported files: PDF, DOCX, XLSX, TXT, MD, CSV.")
    data = await file.read()
    if len(data) > 15_000_000:
        raise HTTPException(413, "File is larger than 15 MB.")
    (T.UPLOADS / name).write_bytes(data)
    return {"filename": name}


@app.post("/api/chat")
async def chat(req: ChatReq):
    facts = "\n".join(f"- {f}" for _, f in T.memories())
    msgs = [{"role": "system", "content": SYSTEM_PROMPT + (f"\nKnown facts about the user:\n{facts}" if facts else "")}]
    msgs += [m.model_dump() for m in req.messages]
    schemas = [t["schema"] for t in T.TOOLS.values()]
    try:
        for _ in range(5):
            m = (await asyncio.to_thread(T.chat_sync, msgs, schemas))["choices"][0]["message"]
            calls = m.get("tool_calls")
            if not calls:
                return {"reply": m.get("content") or ""}
            msgs.append(m)
            for c in calls:
                name, args = c["function"]["name"], json.loads(c["function"]["arguments"] or "{}")
                t = T.TOOLS.get(name)
                if t and t["confirm"] and name not in req.approve:
                    return {"confirm": {"tool": name, "args": args}}
                try:
                    out = await asyncio.to_thread(t["fn"], **args) if t else "Unknown tool."
                except Exception as e:
                    out = f"Tool failed: {e}"
                msgs.append({"role": "tool", "tool_call_id": c["id"], "content": str(out)[:6000]})
        return {"reply": "I could not finish that. Please try again."}
    except Exception as e:
        raise HTTPException(502, f"AI provider error: {e}. Check LLM_API_KEY, LLM_BASE_URL and LLM_MODEL.")


app.mount("/", StaticFiles(directory=T.ROOT / "web", html=True), name="web")
