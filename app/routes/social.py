from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security.password import (
    create_access_token,
    create_refresh_token,
)
from app.database import get_session
from app.dto.socialLogin import SocialLoginRequest
from app.models.user import User
from app.models.userProvider import UserProvider

router = APIRouter()

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.post("/login")
async def social_login(
    payload: SocialLoginRequest, session: AsyncSession = Depends(get_session)
):
    """Handle social login."""
    if payload.provider != "google":
        raise HTTPException(status_code=400, detail="Unsupported provider")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {payload.access_token}"},
        )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    data = response.json()
    google_user_id = data["sub"]
    email = data.get("email")
    name = data.get("name", "")

    result = session.exec(
        select(UserProvider).where(
            UserProvider.provider == "google",
            UserProvider.provider_user_id == google_user_id,
        )
    )
    user_provider: Optional[UserProvider] = result.first()

    if user_provider:
        user = user_provider.user
    else:
        user = User(email=email, name=name)
        session.add(user)
        session.flush()

        user_provider = UserProvider(
            provider="google", provider_user_id=google_user_id, user_id=user.id
        )
        session.add(user_provider)

    session.commit()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {"access_token": access_token, "refresh_token": refresh_token}
