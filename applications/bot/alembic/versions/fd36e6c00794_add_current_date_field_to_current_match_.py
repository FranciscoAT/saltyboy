"""Add current date field to current match table

Revision ID: fd36e6c00794
Revises: beb40ff88475
Create Date: 2024-02-27 21:12:24.717300

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "fd36e6c00794"
down_revision = "beb40ff88475"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "current_match", sa.Column("updated_at", sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column("current_match", "updated_at")
