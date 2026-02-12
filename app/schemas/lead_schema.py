from pydantic import BaseModel


class LeadSchema(BaseModel):
    nome: str
    price: int
