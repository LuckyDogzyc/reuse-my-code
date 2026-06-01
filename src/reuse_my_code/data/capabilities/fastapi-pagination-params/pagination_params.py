from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status


@dataclass(frozen=True)
class PaginationParams:
    page: int = 1
    page_size: int = 20
    max_page_size: int = 100

    def __post_init__(self) -> None:
        if self.page < 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page must be >= 1")
        if self.page_size < 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page_size must be >= 1")
        if self.page_size > self.max_page_size:
            object.__setattr__(self, "page_size", self.max_page_size)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
