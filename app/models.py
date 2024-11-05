from pydantic import BaseModel

class LawDocument(BaseModel):
    title: str
    text: str
    metadata: dict
