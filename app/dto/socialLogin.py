from pydantic import BaseModel


class SocialLoginRequest(BaseModel):
    provider: str
    token: str
