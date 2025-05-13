from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str | bytes
    token_type: str
