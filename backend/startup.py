import hfh.controllers  # noqa: F401
import hfh.db
import hfh.models.all  # noqa: F401
from hfh.app import APP
from hfh.scheduled_tasks import SCHEDULER

if __name__ == "__main__":
    SCHEDULER.start()
    APP.run(host="0.0.0.0", port=5000)
