"""Heartbeat table

Revision ID: 248ad8274833
Revises: fd36e6c00794
Create Date: 2024-02-29 10:03:57.263989

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "248ad8274833"
down_revision = "fd36e6c00794"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bot_heartbeat", sa.Column("heartbeat_time", sa.DateTime(), nullable=False)
    )


def downgrade():
    op.drop_table("bot_heartbeat")
