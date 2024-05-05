import asyncio

from ..app import APP
from ..models.asic import Asic
from ..services.asic_service import get_asic_data
from ..utils.asyncish import async_context

@APP.route('/')
def hello_world():
    return 'Hello, World!'

@APP.route('/api/test')
def test_json():
    a = Asic.with_name("141")
    d = asyncio.run(get_asic_data(a))
    return d

