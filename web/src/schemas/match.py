from src.schemas.fighters import FighterInfoSchema
from dataclasses import dataclass

from src.schemas.fighters import FighterInfoSchema
@dataclass
class CurrentMatchSchema:
    fighter_blue: str
    fighter_red: str
    match_format: str
    tier: str
    fighter_red_info: FighterInfoSchema
    fighter_blue_info: FighterInfoSchema
