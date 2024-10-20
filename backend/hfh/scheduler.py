import asyncio

import structlog
from flask_apscheduler import APScheduler

from .app import APP

LOGGER = structlog.get_logger(__name__)

SCHEDULER = APScheduler()
SCHEDULER.init_app(APP)


@SCHEDULER.task("interval", id="periodically_update_asic_status", seconds=60)
def periodically_update_asic_status() -> None:
    from .services.asic_service import update_status_of_all_active

    with APP.app_context():
        asyncio.run(update_status_of_all_active())
