from typing import Optional

from src.biz.fighter import get_fighter
from src.database import Database
from src.schemas.fighters import MinimalFighterInfoSchema
from src.schemas.match import CurrentMatchSchema, EnhancedMatchSchema
from src.utils import row_to_dataclass


def get_current_match() -> Optional[CurrentMatchSchema]:
    db = Database()
    current_match = db.get_current_match()
    if not current_match:
        return None

    fighter_red_info = None
    fighter_blue_info = None
    if current_match["match_format"] != "exhibition":
        fighter_red_info = get_fighter(fighter_name=current_match["fighter_red"])
        fighter_blue_info = get_fighter(fighter_name=current_match["fighter_blue"])

    return row_to_dataclass(
        current_match,
        CurrentMatchSchema,
        overwrite_fields={
            "fighter_red_info": fighter_red_info,
            "fighter_blue_info": fighter_blue_info,
        },
    )


def get_last_match() -> Optional[EnhancedMatchSchema]:
    db = Database()
    last_match = db.get_last_match()
    if not last_match:
        return None

    fighter_red_info = db.get_fighter(fighter_id=last_match["fighter_red"])
    fighter_blue_info = db.get_fighter(fighter_id=last_match["fighter_blue"])

    dc_fighter_red_info = row_to_dataclass(fighter_red_info, MinimalFighterInfoSchema)  # type: ignore
    dc_fighter_blue_info = row_to_dataclass(fighter_blue_info, MinimalFighterInfoSchema)  # type: ignore

    return row_to_dataclass(
        last_match,
        EnhancedMatchSchema,
        overwrite_fields={
            "fighter_red_info": dc_fighter_red_info,
            "fighter_blue_info": dc_fighter_blue_info,
        },
    )
