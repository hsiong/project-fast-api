# app/api/profile.py
from fastapi import APIRouter, Request

from core.dto.result_bean import Result
from core.util.bean_util import dict_to_bean

router = APIRouter()


@router.get("test")
async def render_page(profile_id: str, page_type: str, request: Request):
    return Result.ok(
        data=dict_to_bean({"profile_id": profile_id, "page_type": page_type})
    )
