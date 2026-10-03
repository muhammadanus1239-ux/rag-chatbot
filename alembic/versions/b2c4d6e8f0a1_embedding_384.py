"""embedding 384

Revision ID: b2c4d6e8f0a1
Revises: adfe1be678e0
Create Date: 2026-10-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy

revision: str = 'b2c4d6e8f0a1'
down_revision: Union[str, Sequence[str], None] = 'adfe1be678e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('chunks', 'embedding')
    op.add_column(
        'chunks',
        sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=384), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('chunks', 'embedding')
    op.add_column(
        'chunks',
        sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=True),
    )