import asyncio

from ..app import APP
from ..models.asic import Asic

@APP.route('/')
def hello_world():
    return 'Hello, World!'

