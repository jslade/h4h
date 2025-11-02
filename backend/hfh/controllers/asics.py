import asyncio
from flask import request
import structlog

from ..app import APP
from ..dtos.asics import AsicsListDto, AsicSummaryDto, OverrideDto
from ..models.asic import Asic
from ..services.asic_service import (
    get_asic_data,
    get_asic_data_extended,
    get_asic_errors,
    set_hashing,
    set_override,
    set_power_limit,
)
from ..services.auth_service import AuthService

from ..utils.data import deep_dict
from ..utils.validate_pydantic_response import validate_pydantic_response


LOGGER = structlog.get_logger(__name__)


@APP.route("/api/asic/<name>/raw", methods=["GET"])
def get_asic_raw(name: str) -> dict:
    asic = Asic.with_name(name)
    data = asyncio.run(get_asic_data(asic))
    raw = deep_dict(data.asdict())
    return raw


@APP.route("/api/asic/<name>/raw/extended", methods=["GET"])
def get_asic_raw_extended(name: str) -> dict:
    asic = Asic.with_name(name)
    data = asyncio.run(get_asic_data_extended(asic))
    raw = deep_dict(data)
    return raw


@APP.route("/api/asic/<name>/raw/errors", methods=["GET"])
def get_asic_raw_errors(name: str) -> dict:
    asic = Asic.with_name(name)
    data = asyncio.run(get_asic_errors(asic))
    raw = [deep_dict(d) for d in data]
    return raw


@APP.route("/api/asic/active", methods=["GET"])
def get_asic_list_active() -> dict:
    active = Asic.all_active()

    with validate_pydantic_response():
        return AsicsListDto(asics=[asic.name for asic in active]).model_dump()


@APP.route("/api/asic/<name>/summary", methods=["GET"])
def get_asic_summary(name: str) -> dict:
    asic = Asic.with_name(name)

    with validate_pydantic_response():
        return AsicSummaryDto.from_asic(asic).model_dump()


@APP.route("/api/asic/<name>/set-override", methods=["POST"])
def post_override(name: str) -> dict:
    user = AuthService.get_current_user()
    if not user:
        return {"error": "Not authenticated"}, 401

    data = request.get_json()
    if not data:
        return {"error": "Request body must be JSON"}, 400

    LOGGER.info(
        "override requested",
        user=user.name,
        asic=name,
        override=data,
    )

    override = OverrideDto.model_validate(**data)
    asic = Asic.with_name(name)

    asyncio.run(
        set_override(
            asic,
            hashing=override.hashing,
            hours=override.hours,
        )
    )

    LOGGER.info(
        "override set",
        user=user.name,
        asic=name,
        override=asic.override_interval,
    )


@APP.route("/api/asic/<name>/set-hashing/<state>", methods=["PUT", "PATCH"])
def set_asic_hashing(name: str, state: str) -> dict:
    asic = Asic.with_name(name)

    hashing = state.lower() in ["true", "1", "yes"]
    asyncio.run(set_hashing(asic, hashing))

    return AsicSummaryDto.from_asic(asic).model_dump()


@APP.route("/api/asic/<name>/set-power-limit/<power_limit>", methods=["PUT", "PATCH"])
def set_asic_power_limit(name: str, power_limit: int) -> dict:
    asic = Asic.with_name(name)

    asyncio.run(set_power_limit(asic, power_limit))

    return AsicSummaryDto.from_asic(asic).model_dump()
