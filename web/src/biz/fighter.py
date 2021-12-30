from typing import Optional

from src.database import Database
from src.schemas.fighters import FighterInfoSchema, FighterStatsSchema, MatchSchema
from src.utils import row_to_dataclass


def get_fighter(**kwargs) -> Optional[FighterInfoSchema]:
    db = Database()
    fighter = db.get_fighter(**kwargs)
    if not fighter:
        return None
    db_matches = db.get_matches(fighter["id"])
    matches = [row_to_dataclass(x, MatchSchema) for x in db_matches]

    total_matches = len(matches)
    total_wins = 0
    total_bet = 0
    for match in matches:
        if match.winner == fighter["id"]:
            total_wins += 1
        if match.fighter_blue == fighter["id"]:
            total_bet += match.bet_blue
        else:
            total_bet += match.bet_red

    win_rate = 0.0 if total_matches == 0 else round(total_wins / total_matches, 2)
    average_bet = 0.0 if total_matches == 0 else round(total_bet / total_matches, 2)

    fighter_stats = FighterStatsSchema(
        win_rate=win_rate,
        average_bet=average_bet,
        total_matches=total_matches,
    )

    return row_to_dataclass(
        fighter,
        FighterInfoSchema,
        overwrite_fields={"stats": fighter_stats, "matches": matches},
    )
