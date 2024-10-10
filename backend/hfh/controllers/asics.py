import asyncio


from ..app import APP
from ..dtos.asics import AsicStatus, AsicSummaryDto, AsicsSummaryDto
from ..models.asic import Asic
from ..services.asic_service import get_asic_data
from ..utils.data import deep_dict
from ..utils.validate_pydantic_response import validate_pydantic_response

@APP.route('/api/asic/raw/<name>', methods=['GET'])
def get_asic_raw(name) -> dict:
    asic = Asic.with_name(name)
    data = asyncio.run(get_asic_data(asic))
    raw = deep_dict(data.asdict())
    return raw

@APP.route('/api/asic/summary', methods=['GET'])
def get_asic_summary_all() -> dict:
    active = Asic.all_active()

    with validate_pydantic_response():
        return AsicsSummaryDto(
            asics=[AsicSummaryDto.from_asic(asic) for asic in active]
        ).model_dump()

