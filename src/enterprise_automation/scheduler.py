"""Simple recurring report scheduler."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from collections.abc import Callable

import schedule

LOGGER = logging.getLogger(__name__)


def run_scheduler(job: Callable[[], object], every_minutes: int = 60) -> None:
    """Run a job immediately, then repeat every N minutes until interrupted."""
    if every_minutes < 1:
        raise ValueError("every_minutes must be at least 1.")
    LOGGER.info("Running initial scheduled report.")
    job()
    schedule.every(every_minutes).minutes.do(job)
    LOGGER.info("Scheduler started; interval=%s minute(s). Press Ctrl+C to stop.", every_minutes)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        LOGGER.info("Scheduler stopped by user.")
