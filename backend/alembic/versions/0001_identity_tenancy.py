"""Create identity, tenancy, project, and dataset foundations.

Revision ID: 0001_identity_tenancy
Revises:
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_identity_tenancy"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column[object]]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    role = sa.Enum("owner", "admin", "annotator", "reviewer", "viewer", name="membership_role")
    role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("name", sa.String(160), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "memberships",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.Uuid(),
            sa.ForeignKey("organizations.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("role", role, nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_memberships_organization_user"),
    )
    op.create_index(
        "ix_memberships_user_organization", "memberships", ["user_id", "organization_id"]
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.Uuid(),
            sa.ForeignKey("organizations.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        *_timestamps(),
        sa.UniqueConstraint("organization_id", "slug", name="uq_projects_organization_slug"),
    )
    op.create_index(
        "ix_projects_organization_created_at", "projects", ["organization_id", "created_at"]
    )
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        *_timestamps(),
        sa.UniqueConstraint("project_id", "slug", name="uq_datasets_project_slug"),
    )
    op.create_index("ix_datasets_project_created_at", "datasets", ["project_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_datasets_project_created_at", table_name="datasets")
    op.drop_table("datasets")
    op.drop_index("ix_projects_organization_created_at", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_memberships_user_organization", table_name="memberships")
    op.drop_table("memberships")
    op.drop_table("organizations")
    op.drop_table("users")
    sa.Enum(name="membership_role").drop(op.get_bind(), checkfirst=True)
