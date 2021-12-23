"""Current Match

Revision ID: 65deecb0c4f0
Revises: 908066480906
Create Date: 2021-12-22 23:31:18.967672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "65deecb0c4f0"
down_revision = "908066480906"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "current_match",
        sa.Column("tier", sa.String(1), nullable=False),
        sa.Column("fighter_red", sa.String(), nullable=False),
        sa.Column("fighter_blue", sa.String(), nullable=False),
        sa.Column("match_format", sa.String(16), nullable=False),
    )


def downgrade():
    op.drop_table("current_match")
