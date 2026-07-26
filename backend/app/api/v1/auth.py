"""Identity endpoints with credential and token rotation flows."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, SessionDep, SettingsDep
from app.core.errors import conflict, unauthorized
from app.core.security import create_token, hash_password, verify_password
from app.db.models import User
from app.schemas.contracts import RefreshRequest, TokenPair, UserRead, UserRegistration

router = APIRouter(prefix="/auth", tags=["authentication"])


def issue_tokens(*, user: User, settings: SettingsDep) -> TokenPair:
    return TokenPair(
        access_token=create_token(
            subject=user.id,
            token_type="access",
            ttl_seconds=settings.access_token_ttl_seconds,
            settings=settings,
        ),
        refresh_token=create_token(
            subject=user.id,
            token_type="refresh",
            ttl_seconds=settings.refresh_token_ttl_seconds,
            settings=settings,
        ),
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegistration, session: SessionDep) -> User:
    user = User(
        email=str(payload.email).lower(),
        password_hash=hash_password(payload.password),
        display_name=payload.display_name.strip(),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflict("An account with this email already exists") from exc
    await session.refresh(user)
    return user


@router.post("/token", response_model=TokenPair)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    settings: SettingsDep,
) -> TokenPair:
    user = await session.scalar(select(User).where(User.email == form_data.username.lower()))
    if (
        user is None
        or not user.is_active
        or not verify_password(form_data.password, user.password_hash)
    ):
        raise unauthorized("Incorrect email or password")
    return issue_tokens(user=user, settings=settings)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, session: SessionDep, settings: SettingsDep) -> TokenPair:
    from app.core.security import decode_token

    user_id = decode_token(
        encoded_token=payload.refresh_token, expected_type="refresh", settings=settings
    )
    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized("User account is unavailable")
    return issue_tokens(user=user, settings=settings)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUser) -> User:
    return current_user
