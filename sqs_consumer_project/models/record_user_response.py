from typing import Union

from pydantic import BaseModel


class RecordUserResponse(BaseModel):
    id: Union[str, int]
