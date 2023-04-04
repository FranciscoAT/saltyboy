from src.biz.fighter import get_fighter
from src.database import Database
from src.schemas.fighters import MinimalFighterInfoSchema
from src.schemas.match import CurrentMatchSchema, EnhancedMatchSchema
from src.utils import row_to_dataclass


def get_current_match() -> CurrentMatchSchema | None:
    database_ = Database()
    current_match = database_.get_current_match()
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


def get_last_match() -> EnhancedMatchSchema | None:
    database_ = Database()
    last_match = database_.get_last_match()
    if not last_match:
        return None

    fighter_red_info = database_.get_fighter(fighter_id=last_match["fighter_red"])
    fighter_blue_info = database_.get_fighter(fighter_id=last_match["fighter_blue"])

    if fighter_red_info is None:
        return None

    if fighter_blue_info is None:
        return None

    dc_fighter_red_info = row_to_dataclass(fighter_red_info, MinimalFighterInfoSchema)
    dc_fighter_blue_info = row_to_dataclass(fighter_blue_info, MinimalFighterInfoSchema)

    return row_to_dataclass(
        last_match,
        EnhancedMatchSchema,
        overwrite_fields={
            "fighter_red_info": dc_fighter_red_info,
            "fighter_blue_info": dc_fighter_blue_info,
        },
    )
