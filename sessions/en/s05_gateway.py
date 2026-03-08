"""
OpenClaw Production Gateway  —  sessions/en/s05_gateway.py

Runs the agent loop continuously, wires together:
  - MCP tool dispatch (agent/core.py)
  - Write-ahead delivery queue (agent/queue.py)
  - Cron scheduler (agent/scheduler.py)
  - Resilience / retry layer (agent/resilience.py)
  - JSONL session persistence
  - Optional Telegram channel

Start with:
    python sessions/en/s05_gateway.py

Or via Docker:
    docker compose up
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# Allow imports from repo root
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agent.core import OpenClawMCP
from agent.queue import WriteAheadQueue
from agent.resilience import TokenBudget
from agent.scheduler import Scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("gateway")

# ── Config ────────────────────────────────────────────────────────────────────

SESSIONS_DIR = Path(os.getenv("SESSIONS_DIR", str(ROOT / "sessions")))
MCP_CONFIG = ROOT / "mcp_config.json"
CONTEXT_LINES = int(os.getenv("CONTEXT_WINDOW_LINES", "50"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS_PER_REQUEST", "8192"))
MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS_PER_TURN", "20"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


# ── Session JSONL persistence ─────────────────────────────────────────────────

def session_path(session_id: str) -> Path:
    path = SESSIONS_DIR / f"{session_id}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_session(session_id: str) -> list[dict]:
    """Return the last CONTEXT_LINES messages for a session."""
    p = session_path(session_id)
    if not p.exists():
        return []
    lines = p.read_text().splitlines()[-CONTEXT_LINES:]
    messages = []
    for line in lines:
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return messages


def append_message(session_id: str, message: dict) -> None:
    with session_path(session_id).open("a") as fh:
        fh.write(json.dumps(message) + "\n")


# ── Gateway ───────────────────────────────────────────────────────────────────

class Gateway:
    def __init__(self):
        self.agent = OpenClawMCP()
        self.queue = WriteAheadQueue("outbound")
        self.scheduler: Scheduler | None = None
        self._running = False

    # ── Startup / shutdown ───────────────────────────────────────────────────

    async def start(self) -> None:
        log.info("OpenClaw Gateway starting up...")

        if MCP_CONFIG.exists():
            await self.agent.connect_to_servers(str(MCP_CONFIG))
        else:
            log.warning("mcp_config.json not found — running without MCP tools")

        self.scheduler = Scheduler(skill_runner=self._run_skill)
        self.scheduler.start()

        self._running = True
        log.info("Gateway ready")

    async def stop(self) -> None:
        self._running = False
        if self.scheduler:
            await self.scheduler.stop()
        await self.agent.close()
        log.info("Gateway stopped")

    # ── Message handling ─────────────────────────────────────────────────────

    async def handle_message(
        self,
        text: str,
        session_id: str = "default",
        *,
        deliver_fn=None,
    ) -> str:
        """
        Process one user message end-to-end:
        1. Restore session context
        2. Run agent loop (with tool-call guard)
        3. Persist exchange
        4. Enqueue outbound message, flush immediately
        """
        # 1. Restore context into the agent's history
        history = load_session(session_id)
        self.agent.messages = [self.agent.messages[0]]  # keep system prompt
        self.agent.messages.extend(history)

        # 2. Token / tool-call guard
        budget = TokenBudget(MAX_TOKENS)

        user_msg = {"role": "user", "content": text}
        append_message(session_id, user_msg)

        try:
            reply = await self.agent.chat(text)
        except RuntimeError as exc:
            reply = f"[Safety limit reached: {exc}]"

        # 3. Persist assistant reply
        append_message(session_id, {"role": "assistant", "content": reply})

        # 4. Deliver via queue
        if deliver_fn:
            item = await self.queue.enqueue({"session_id": session_id, "text": reply})
            delivered, _ = await self.queue.flush(deliver_fn)
            if delivered == 0:
                log.warning("Outbound message %s not yet delivered — queued", item.id)

        return reply

    # ── Skill runner (used by scheduler) ─────────────────────────────────────

    async def _run_skill(self, skill_name: str) -> None:
        log.info("Running skill: %s", skill_name)
        if skill_name == "heartbeat":
            log.info("Heartbeat OK at %s", time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        elif skill_name == "queue_status":
            pending = self.queue.pending_count()
            log.info("Queue status: %d item(s) pending", pending)
            if pending:
                await self.queue.flush(self._noop_deliver)
        elif skill_name == "session_summary":
            log.info("Session compaction triggered (stub)")
        else:
            log.warning("Unknown skill: %s", skill_name)

    @staticmethod
    async def _noop_deliver(payload: dict) -> bool:
        """Fallback deliver — just logs. Replace with real channel deliver."""
        log.info("Flushed queued message for session %s", payload.get("session_id"))
        return True


# ── Telegram integration (optional) ──────────────────────────────────────────

async def _run_telegram(gateway: Gateway) -> None:
    try:
        from telegram import Update
        from telegram.ext import Application, MessageHandler, filters
    except ImportError:
        log.warning("python-telegram-bot not installed — Telegram channel disabled")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    async def on_message(update: Update, context) -> None:
        if not update.message or not update.message.text:
            return
        session_id = f"tg_{update.effective_chat.id}"
        text = update.message.text

        async def deliver(payload: dict) -> bool:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=payload["text"],
                )
                return True
            except Exception as exc:
                log.error("Telegram send failed: %s", exc)
                return False

        await gateway.handle_message(text, session_id=session_id, deliver_fn=deliver)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    log.info("Telegram bot polling...")
    await app.run_polling()


# ── CLI fallback ──────────────────────────────────────────────────────────────

async def _run_cli(gateway: Gateway) -> None:
    print("OpenClaw Gateway (CLI mode) — type 'exit' to quit")
    while True:
        try:
            user_input = await asyncio.to_thread(input, "\nYou: ")
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input.strip():
            continue
        reply = await gateway.handle_message(user_input)
        print(f"\nOpenClaw: {reply}")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    gateway = Gateway()
    await gateway.start()

    try:
        if TELEGRAM_TOKEN:
            await _run_telegram(gateway)
        else:
            await _run_cli(gateway)
    finally:
        await gateway.stop()


if __name__ == "__main__":
    asyncio.run(main())
