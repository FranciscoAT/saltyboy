"""ELO Tables

Revision ID: eac8dd9395bd
Revises: 8bb9adee6434
Create Date: 2022-01-04 14:47:10.202793

"""
import math

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eac8dd9395bd"
down_revision = "8bb9adee6434"
branch_labels = None
depends_on = None


class Fighter:
    def __init__(self, tier: str) -> None:
        self.tier = tier
        self.prev_tier = tier
        self.elo = 1500
        self.tier_elo = 1500

    def fight(
        self, opponent_elo: int, opponent_tier_elo: int, tier: str, won: bool
    ) -> None:
        if self.tier != tier:
            self.prev_tier = self.tier
            self.tier = tier
            self.tier_elo = 1500

        self.elo = self.calculate_elo(self.elo, opponent_elo, won)
        self.tier_elo = self.calculate_elo(self.tier_elo, opponent_tier_elo, won)

    @classmethod
    def calculate_elo(cls, elo: int, opponent_elo: int, won: bool) -> int:
        # Calculate transformed ratings
        tr_alpha = math.pow(10, elo / 400)
        tr_beta = math.pow(10, opponent_elo / 400)

        # Calculate expected score
        es_alpha = tr_alpha / (tr_alpha + tr_beta)

        # Score
        score_alpha = 1 if won is True else 0

        # Calculate updated ELO
        return int(elo + (32 * (score_alpha - es_alpha)))


def upgrade():
    op.add_column("fighter", sa.Column("elo", sa.Integer(), nullable=True))
    op.add_column("fighter", sa.Column("tier_elo", sa.Integer(), nullable=True))
    op.add_column("fighter", sa.Column("prev_tier", sa.String(1), nullable=True))

    fighters = {}
    conn = op.get_bind()
    fighter_ids = conn.execute("SELECT id, tier FROM fighter").fetchall()
    for fighter in fighter_ids:
        fighters[fighter[0]] = Fighter(tier=fighter[1])

    matches = conn.execute(
        "SELECT fighter_red, fighter_blue, winner, tier FROM match ORDER BY date ASC"
    ).fetchall()

    for match in matches:
        fighter_a = fighters[match[0]]
        fighter_b = fighters[match[1]]

        fighter_a_elo = fighter_a.elo
        fighter_a_tier_elo = fighter_a.tier_elo

        fighter_b_elo = fighter_b.elo
        fighter_b_tier_elo = fighter_b.tier_elo

        fighter_a.fight(
            fighter_b_elo, fighter_b_tier_elo, match[3], match[0] == match[2]
        )
        fighter_b.fight(
            fighter_a_elo, fighter_a_tier_elo, match[3], match[1] == match[2]
        )

    for fighter_id, fighter in fighters.items():
        conn.execute(
            sa.text(
                "UPDATE fighter SET elo = :elo, tier_elo = :tier_elo, prev_tier = :prev_tier WHERE id = :id"
            ),
            elo=fighter.elo,
            tier_elo=fighter.tier_elo,
            prev_tier=fighter.prev_tier,
            id=fighter_id,
        )

    op.create_table(
        "fighter_tmp",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("tier", sa.String(1), nullable=False),
        sa.Column("created_time", sa.DateTime(), nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.Column("best_streak", sa.Integer(), nullable=False),
        sa.Column("elo", sa.Integer(), nullable=False),
        sa.Column("tier_elo", sa.Integer(), nullable=False),
        sa.Column("prev_tier", sa.String(1), nullable=False),
    )

    conn.execute("INSERT INTO fighter_tmp SELECT id,name,tier,created_time,last_updated,best_streak,elo,tier_elo,prev_tier FROM fighter")
    op.drop_table("fighter")
    op.rename_table("fighter_tmp", "fighter")


def downgrade():
    op.create_table(
        "fighter_tmp",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("tier", sa.String(1), nullable=False),
        sa.Column("created_time", sa.DateTime(), nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.Column("best_streak", sa.Integer(), nullable=False),
    )

    conn = op.get_bind()
    conn.execute(
        "INSERT INTO fighter_tmp SELECT id,name,tier,created_time,best_streak,last_updated FROM fighter"
    )
    op.drop_table("fighter")
    op.rename_table("fighter_tmp", "fighter")
