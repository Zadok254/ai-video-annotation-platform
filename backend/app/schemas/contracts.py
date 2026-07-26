"""Public API request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models import Role


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class UserRegistration(APIModel):
    email: EmailStr
    password: str = Field(min_length=14, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)


class UserRead(APIModel):
    id: UUID
    email: EmailStr
    display_name: str
    is_active: bool


class TokenPair(APIModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(APIModel):
    refresh_token: str = Field(min_length=1)


class OrganizationCreate(APIModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$")
    name: str = Field(min_length=2, max_length=160)


class OrganizationRead(APIModel):
    id: UUID
    slug: str
    name: str
    created_at: datetime
    role: Role


class ProjectCreate(APIModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$")
    name: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=10_000)


class ProjectRead(APIModel):
    id: UUID
    organization_id: UUID
    slug: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class DatasetCreate(APIModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$")
    name: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=10_000)


class DatasetRead(APIModel):
    id: UUID
    project_id: UUID
    slug: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
