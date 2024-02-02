from pydantic import BaseModel


class ExampleSQSMessageModel(BaseModel):
    name: str
    age: int
