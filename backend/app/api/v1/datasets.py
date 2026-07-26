"""Dataset management endpoints constrained by project membership."""

from uuid import UUID

from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, SessionDep
from app.core.errors import conflict
from app.db.models import Dataset, Role
from app.schemas.contracts import DatasetCreate, DatasetRead
from app.services.authorization import get_project_for_member

router = APIRouter(prefix="/projects/{project_id}/datasets", tags=["datasets"])
_dataset_write_roles = {Role.OWNER, Role.ADMIN}
_dataset_read_roles = {Role.OWNER, Role.ADMIN, Role.ANNOTATOR, Role.REVIEWER, Role.VIEWER}


@router.post("", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    project_id: UUID, payload: DatasetCreate, current_user: CurrentUser, session: SessionDep
) -> Dataset:
    await get_project_for_member(
        session=session,
        user_id=current_user.id,
        project_id=project_id,
        allowed_roles=_dataset_write_roles,
    )
    dataset = Dataset(
        project_id=project_id,
        slug=payload.slug,
        name=payload.name.strip(),
        description=payload.description,
    )
    session.add(dataset)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflict("A dataset with this slug already exists in this project") from exc
    await session.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetRead])
async def list_datasets(
    project_id: UUID, current_user: CurrentUser, session: SessionDep
) -> list[Dataset]:
    await get_project_for_member(
        session=session,
        user_id=current_user.id,
        project_id=project_id,
        allowed_roles=_dataset_read_roles,
    )
    return list(
        await session.scalars(
            select(Dataset)
            .where(Dataset.project_id == project_id)
            .order_by(Dataset.created_at.desc())
        )
    )
