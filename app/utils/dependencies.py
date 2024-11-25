from typing import Annotated, Tuple

from fastapi import Depends

from app.utils.functions import pagination_dependency

PaginationDep = Annotated[Tuple[int, int], Depends(pagination_dependency)]
