from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Item
from app.pagination.params import PaginationParams
from app.pagination.response import PaginatedResponse
from app.pagination.sqlalchemy_pagination import paginate_select
from app.schemas import ItemRead

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=PaginatedResponse[ItemRead])
async def list_items(
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse[ItemRead]:
    params = PaginationParams(page=page, page_size=page_size)
    statement = select(Item).order_by(Item.id.desc())
    items, total = await paginate_select(session, statement, params)
    return PaginatedResponse[ItemRead].create(
        items=[ItemRead.model_validate(item) for item in items],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )
