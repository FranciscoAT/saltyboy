"""Nullable tier

Revision ID: 8bb9adee6434
Revises: 65deecb0c4f0
Create Date: 2021-12-31 20:40:12.966190

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8bb9adee6434"
down_revision = "65deecb0c4f0"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("current_match")
    op.create_table(
        "current_match",
        sa.Column("tier", sa.String(1), nullable=True),
        sa.Column("fighter_red", sa.String(), nullable=False),
        sa.Column("fighter_blue", sa.String(), nullable=False),
        sa.Column("match_format", sa.String(16), nullable=False),
    )


def downgrade():
    op.drop_table("current_match")
    op.create_table(
        "current_match",
        sa.Column("tier", sa.String(1), nullable=False),
        sa.Column("fighter_red", sa.String(), nullable=False),
        sa.Column("fighter_blue", sa.String(), nullable=False),
        sa.Column("match_format", sa.String(16), nullable=False),
    )
