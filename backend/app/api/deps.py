"""Reusable HTTP dependencies."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import unauthorized
from app.core.security import decode_token
from app.db.models import User
from app.db.session import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep, settings: SettingsDep
) -> User:
    user_id = decode_token(encoded_token=token, expected_type="access", settings=settings)
    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized("User account is unavailable")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
