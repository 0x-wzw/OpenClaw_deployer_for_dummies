"""
Write-ahead message delivery queue.

Messages are persisted to disk before being sent, so a crash between receive
and deliver cannot cause message loss.  Each item is a single JSON line in
queue/<queue_id>.jsonl.  Once successfully delivered the item is marked done.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional

log = logging.getLogger(__name__)

QUEUE_DIR = Path(os.getenv("QUEUE_DIR", "./queue"))


class QueueItem:
    def __init__(self, payload: dict, item_id: str | None = None):
        self.id = item_id or uuid.uuid4().hex
        self.payload = payload
        self.created_at = time.time()
        self.attempts = 0
        self.done = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "payload": self.payload,
            "created_at": self.created_at,
            "attempts": self.attempts,
            "done": self.done,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "QueueItem":
        item = cls(d["payload"], item_id=d["id"])
        item.created_at = d.get("created_at", 0)
        item.attempts = d.get("attempts", 0)
        item.done = d.get("done", False)
        return item


class WriteAheadQueue:
    """
    Simple file-backed write-ahead queue.

    Usage::

        queue = WriteAheadQueue("telegram")
        await queue.enqueue({"chat_id": 123, "text": "hello"})
        await queue.flush(deliver_fn)
    """

    def __init__(self, name: str, max_retries: int = 5):
        self.name = name
        self.max_retries = max_retries
        self._path = QUEUE_DIR / f"{name}.jsonl"
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    # ── Write ────────────────────────────────────────────────────────────────

    async def enqueue(self, payload: dict) -> QueueItem:
        """Persist a payload and return the item."""
        item = QueueItem(payload)
        await asyncio.to_thread(self._append, item)
        log.debug("Enqueued %s/%s", self.name, item.id)
        return item

    def _append(self, item: QueueItem) -> None:
        with self._path.open("a") as fh:
            fh.write(json.dumps(item.to_dict()) + "\n")

    # ── Read ─────────────────────────────────────────────────────────────────

    def _load_pending(self) -> list[QueueItem]:
        if not self._path.exists():
            return []
        items: list[QueueItem] = []
        with self._path.open() as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    item = QueueItem.from_dict(d)
                    if not item.done and item.attempts < self.max_retries:
                        items.append(item)
                except json.JSONDecodeError:
                    pass
        return items

    # ── Flush ────────────────────────────────────────────────────────────────

    async def flush(
        self,
        deliver: Callable[[dict], Coroutine[Any, Any, bool]],
    ) -> tuple[int, int]:
        """
        Attempt delivery of every pending item.

        ``deliver`` must be an async callable that accepts the payload dict
        and returns True on success, False on transient failure.

        Returns (delivered, failed) counts.
        """
        pending = await asyncio.to_thread(self._load_pending)
        delivered = failed = 0
        for item in pending:
            item.attempts += 1
            try:
                ok = await deliver(item.payload)
            except Exception as exc:
                log.warning("Delivery error for %s: %s", item.id, exc)
                ok = False

            if ok:
                item.done = True
                delivered += 1
                log.debug("Delivered %s/%s", self.name, item.id)
            else:
                failed += 1
                log.warning(
                    "Delivery failed for %s/%s (attempt %d/%d)",
                    self.name, item.id, item.attempts, self.max_retries,
                )

        if pending:
            await asyncio.to_thread(self._rewrite, pending)

        return delivered, failed

    def _rewrite(self, items: list[QueueItem]) -> None:
        """Overwrite the queue file with updated item states."""
        tmp = self._path.with_suffix(".tmp")
        with tmp.open("w") as fh:
            for item in items:
                fh.write(json.dumps(item.to_dict()) + "\n")
        tmp.replace(self._path)

    def pending_count(self) -> int:
        return len(self._load_pending())
