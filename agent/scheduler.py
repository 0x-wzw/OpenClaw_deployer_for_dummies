"""
Heartbeat / cron scheduler.

Reads workspace/CRON.json and fires each task on its configured interval.
Tasks call a named skill; the gateway passes a skill-runner callable at init.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Coroutine

log = logging.getLogger(__name__)

CRON_PATH = Path("workspace/CRON.json")


class Scheduler:
    """
    Lightweight cron engine driven by CRON.json.

    Each entry::

        {
          "task": "heartbeat",
          "description": "...",
          "interval_seconds": 60,
          "skill": "heartbeat"
        }

    The ``skill_runner`` callable receives the skill name and must return an
    awaitable.
    """

    def __init__(
        self,
        skill_runner: Callable[[str], Coroutine[Any, Any, None]],
        cron_path: Path = CRON_PATH,
    ):
        self._runner = skill_runner
        self._cron_path = cron_path
        self._tasks: list[asyncio.Task] = []
        self._running = False

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        jobs = self._load_jobs()
        for job in jobs:
            task = asyncio.create_task(self._job_loop(job), name=job["task"])
            self._tasks.append(task)
        log.info("Scheduler started with %d job(s)", len(jobs))

    async def stop(self) -> None:
        self._running = False
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        log.info("Scheduler stopped")

    # ── Internal ─────────────────────────────────────────────────────────────

    def _load_jobs(self) -> list[dict]:
        if not self._cron_path.exists():
            log.warning("CRON.json not found at %s — no jobs scheduled", self._cron_path)
            return []
        with self._cron_path.open() as fh:
            jobs = json.load(fh)
        return [j for j in jobs if isinstance(j, dict) and "task" in j]

    async def _job_loop(self, job: dict) -> None:
        interval = job.get("interval_seconds", 60)
        skill = job.get("skill", job["task"])
        name = job["task"]

        # Stagger startup so all jobs don't fire at once
        await asyncio.sleep(interval * 0.1)

        while self._running:
            next_run = time.monotonic() + interval
            try:
                log.debug("Running scheduled job: %s (skill=%s)", name, skill)
                await self._runner(skill)
            except Exception as exc:
                log.error("Scheduled job %s failed: %s", name, exc)

            sleep_for = max(0, next_run - time.monotonic())
            await asyncio.sleep(sleep_for)
