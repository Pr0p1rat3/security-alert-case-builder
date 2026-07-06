"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-02
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The declarative models are the source of truth for this MVP. This
    # migration creates all tables in metadata to keep the migration concise.
    from app.models import *  # noqa: F403
    from app.models.base import Base

    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    from app.models import *  # noqa: F403
    from app.models.base import Base

    Base.metadata.drop_all(bind=op.get_bind())

