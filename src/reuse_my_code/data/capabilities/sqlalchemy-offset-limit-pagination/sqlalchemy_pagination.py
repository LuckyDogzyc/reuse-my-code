from __future__ import annotations

from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.pagination.params import PaginationParams


async def paginate_select(session: AsyncSession, statement: Select[Any], params: PaginationParams) -> tuple[list[Any], int]:
    page_statement = statement.offset(params.offset).limit(params.page_size)
    items = list((await session.execute(page_statement)).scalars().all())

    count_statement = select(func.count()).select_from(statement.subquery())
    total = int((await session.execute(count_statement)).scalar_one())
    return items, total
