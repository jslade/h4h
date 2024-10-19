import hfh.controllers  # noqa: F401
import hfh.db
import hfh.models.all  # noqa: F401
from hfh.app import APP

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=5000)
