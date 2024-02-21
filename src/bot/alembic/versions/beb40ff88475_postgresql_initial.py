"""Postgresql Initial

Revision ID: beb40ff88475
Revises: 
Create Date: 2024-02-21 13:27:50.644311

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "beb40ff88475"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "fighter",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("tier", sa.String(1), nullable=False),
        sa.Column("prev_tier", sa.String(1), nullable=False),
        sa.Column("elo", sa.Integer(), nullable=False),
        sa.Column("tier_elo", sa.Integer(), nullable=False),
        sa.Column("best_streak", sa.Integer(), nullable=False),
        sa.Column("created_time", sa.DateTime(), nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "match",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column(
            "fighter_red",
            sa.Integer(),
            sa.ForeignKey("fighter.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "fighter_blue",
            sa.Integer(),
            sa.ForeignKey("fighter.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "winner",
            sa.Integer(),
            sa.ForeignKey("fighter.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("bet_red", sa.Integer(), nullable=False),
        sa.Column("bet_blue", sa.Integer(), nullable=False),
        sa.Column("tier", sa.String(1), nullable=False),
        sa.Column("match_format", sa.String(16), nullable=False),
        sa.Column("colour", sa.String(8), nullable=False),
        sa.Column("streak_red", sa.Integer(), nullable=False),
        sa.Column("streak_blue", sa.Integer(), nullable=False),
    )

    op.create_table(
        "current_match",
        sa.Column("tier", sa.String(1), nullable=True),
        sa.Column("fighter_red", sa.String(), nullable=False),
        sa.Column("fighter_blue", sa.String(), nullable=False),
        sa.Column("match_format", sa.String(16), nullable=False),
    )


def downgrade():
    op.drop_table("current_match")
    op.drop_table("match")
    op.drop_table("fighter")
