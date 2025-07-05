from pydantic import BaseModel


class SocialLoginRequest(BaseModel):
    provider: str
    access_token: str
