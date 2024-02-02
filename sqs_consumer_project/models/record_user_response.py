from pydantic import BaseModel


class RecordUserResponse(BaseModel):
    user_id: str
