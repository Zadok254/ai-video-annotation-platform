"""Organization and membership-bound project endpoints."""

from uuid import UUID

from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, SessionDep
from app.core.errors import conflict
from app.db.models import Membership, Organization, Project, Role
from app.schemas.contracts import (
    OrganizationCreate,
    OrganizationRead,
    ProjectCreate,
    ProjectRead,
)
from app.services.authorization import require_organization_role

router = APIRouter(prefix="/organizations", tags=["organizations"])
_project_write_roles = {Role.OWNER, Role.ADMIN}
_project_read_roles = {Role.OWNER, Role.ADMIN, Role.ANNOTATOR, Role.REVIEWER, Role.VIEWER}


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate, current_user: CurrentUser, session: SessionDep
) -> OrganizationRead:
    organization = Organization(slug=payload.slug, name=payload.name.strip())
    session.add(organization)
    try:
        await session.flush()
        session.add(
            Membership(organization_id=organization.id, user_id=current_user.id, role=Role.OWNER)
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflict("An organization with this slug already exists") from exc
    await session.refresh(organization)
    return OrganizationRead(
        id=organization.id,
        slug=organization.slug,
        name=organization.name,
        created_at=organization.created_at,
        role=Role.OWNER,
    )


@router.get("", response_model=list[OrganizationRead])
async def list_organizations(
    current_user: CurrentUser, session: SessionDep
) -> list[OrganizationRead]:
    rows = (
        await session.execute(
            select(Organization, Membership.role)
            .join(Membership, Membership.organization_id == Organization.id)
            .where(Membership.user_id == current_user.id)
            .order_by(Organization.name)
        )
    ).all()
    return [
        OrganizationRead(
            id=organization.id,
            slug=organization.slug,
            name=organization.name,
            created_at=organization.created_at,
            role=role,
        )
        for organization, role in rows
    ]


@router.post(
    "/{organization_id}/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED
)
async def create_project(
    organization_id: UUID, payload: ProjectCreate, current_user: CurrentUser, session: SessionDep
) -> Project:
    await require_organization_role(
        session=session,
        user_id=current_user.id,
        organization_id=organization_id,
        allowed_roles=_project_write_roles,
    )
    project = Project(
        organization_id=organization_id,
        slug=payload.slug,
        name=payload.name.strip(),
        description=payload.description,
    )
    session.add(project)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflict("A project with this slug already exists in this organization") from exc
    await session.refresh(project)
    return project


@router.get("/{organization_id}/projects", response_model=list[ProjectRead])
async def list_projects(
    organization_id: UUID, current_user: CurrentUser, session: SessionDep
) -> list[Project]:
    await require_organization_role(
        session=session,
        user_id=current_user.id,
        organization_id=organization_id,
        allowed_roles=_project_read_roles,
    )
    return list(
        await session.scalars(
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.created_at.desc())
        )
    )
