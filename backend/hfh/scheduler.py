import asyncio

import structlog
from flask_apscheduler import APScheduler

from .app import APP

LOGGER = structlog.get_logger(__name__)

SCHEDULER = APScheduler()
SCHEDULER.init_app(APP)


@SCHEDULER.task("interval", id="periodically_sample", seconds=60)
def periodically_sample() -> None:
    from .services.sampling_service import SamplingService

    with APP.app_context():
        asyncio.run(SamplingService().sample_all_active(interval=60))
