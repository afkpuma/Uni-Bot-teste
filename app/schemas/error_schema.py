from pydantic import BaseModel


class ErrorSchema(BaseModel):
    error: str
    details: str
