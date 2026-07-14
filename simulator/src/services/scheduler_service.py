import logging
from typing import Optional

from src.config.settings import settings
from src.utils.time_utils import parse_duration

logger = logging.getLogger(__name__)


class SchedulerService:
    """Handles scheduled scenario activation/deactivation. Uses APScheduler if available."""

    def __init__(self):
        self._scheduler = None

    def start(self):
        if not settings.enable_scheduling:
            return
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            self._scheduler = AsyncIOScheduler()
            self._scheduler.start()
            logger.info("APScheduler started")
        except ImportError:
            logger.warning("APScheduler not available, scheduling disabled")
        except Exception as e:
            logger.warning(f"Failed to start scheduler: {e}")

    def stop(self):
        if self._scheduler:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception:
                pass

    def schedule_deactivation(self, scenario_id: str, duration_str: str):
        if not self._scheduler:
            return
        try:
            from apscheduler.triggers.date import DateTrigger
            from src.services.scenario_service import scenario_service
            from src.utils.time_utils import now_utc

            run_at = now_utc() + parse_duration(duration_str)
            self._scheduler.add_job(
                scenario_service.deactivate_scenario,
                trigger=DateTrigger(run_date=run_at),
                args=[scenario_id],
                id=f"deactivate-{scenario_id}",
                replace_existing=True,
            )
        except Exception as e:
            logger.warning(f"Failed to schedule deactivation: {e}")


scheduler_service = SchedulerService()
