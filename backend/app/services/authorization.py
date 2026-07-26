"""Organization-scoped authorization checks used by domain endpoints."""

from collections.abc import Collection
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import forbidden, not_found
from app.db.models import Membership, Project, Role


async def require_organization_role(
    *,
    session: AsyncSession,
    user_id: UUID,
    organization_id: UUID,
    allowed_roles: Collection[Role],
) -> Membership:
    membership = await session.scalar(
        select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == user_id,
        )
    )
    if membership is None:
        raise forbidden("No active membership for this organization")
    if membership.role not in allowed_roles:
        raise forbidden("Your organization role cannot perform this action")
    return membership


async def get_project_for_member(
    *, session: AsyncSession, user_id: UUID, project_id: UUID, allowed_roles: Collection[Role]
) -> Project:
    project = await session.get(Project, project_id)
    if project is None:
        raise not_found("Project not found")
    await require_organization_role(
        session=session,
        user_id=user_id,
        organization_id=project.organization_id,
        allowed_roles=allowed_roles,
    )
    return project
