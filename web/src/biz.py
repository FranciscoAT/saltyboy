from dataclasses import asdict, dataclass
from sqlite3 import Row
from typing import Dict, List, Optional, Tuple

from werkzeug.exceptions import BadRequest

from src.database import Database


@dataclass
class FighterStats:
    win_rate: float
    average_bet: float
    total_matches: int


@dataclass
class FighterStatsVs:
    win_rate_vs: float
    average_bet_vs: float
    total_matches_vs: float


@dataclass
class FighterInfo:
    fighter: Dict
    stats: FighterStats


@dataclass
class FighterInfoVs(FighterInfo):
    stats_vs: FighterStatsVs


@dataclass
class Analysis:
    red: FighterInfoVs
    blue: FighterInfoVs
    suggested_bet: str
    confidence: float


def get_fighter(
    fighter_name: Optional[str] = None,
    fighter_id: Optional[int] = None,
    db: Optional[Database] = None,
) -> Optional[Dict]:
    db = db if db else Database()
    fighter = db.get_fighter(fighter_name, fighter_id)
    if not fighter:
        return None
    fighter_stats = db.get_matches(fighter["id"])
    return asdict(_analyze_matches(fighter_stats, fighter))


def analyze_match(fighter_red: Dict, fighter_blue: Dict) -> Dict:
    db = Database()
    fighter_red_obj = _get_fighter_throw_none(db, **fighter_red)
    fighter_blue_obj = _get_fighter_throw_none(db, **fighter_blue)

    if fighter_red_obj["id"] == fighter_blue_obj["id"]:
        raise BadRequest("Cannot compare the same fighter to itself.")

    red_matches = db.get_matches(fighter_red_obj["id"])
    blue_matches = db.get_matches(fighter_blue_obj["id"])

    red_info = _analyze_matches_vs(red_matches, fighter_red_obj, fighter_blue_obj)
    blue_info = _analyze_matches_vs(blue_matches, fighter_blue_obj, fighter_red_obj)
    suggested_bet, confidence = _determine_winner(red_info, blue_info)

    return asdict(
        Analysis(
            red=red_info,
            blue=blue_info,
            suggested_bet=suggested_bet,
            confidence=confidence,
        )
    )


def _determine_winner(
    red_info: FighterInfoVs, blue_info: FighterInfoVs
) -> Tuple[str, float]:
    # TODO: this logic needs to be improved
    if red_info.stats_vs.total_matches_vs != 0:
        if red_info.stats_vs.win_rate_vs > blue_info.stats_vs.win_rate_vs:
            suggested_bet = "red"
            confidence = red_info.stats_vs.win_rate_vs
        else:
            suggested_bet = "blue"
            confidence = blue_info.stats_vs.win_rate_vs
    else:
        if red_info.stats.win_rate > blue_info.stats.win_rate:
            suggested_bet = "red"
            confidence = red_info.stats.win_rate
        else:
            suggested_bet = "blue"
            confidence = blue_info.stats.win_rate

    return suggested_bet, confidence


def _analyze_matches(matches: List[Row], fighter: Row) -> FighterInfo:
    num_wins = 0
    total_bet = 0

    for match in matches:
        if match["winner"] == fighter["id"]:
            num_wins += 1
        if match["fighter_red"] == fighter["id"]:
            total_bet += match["bet_red"]
        else:
            total_bet += match["bet_blue"]

    total_matches = len(matches)
    win_rate = 0
    average_bet = 0
    if total_matches > 0:
        win_rate = num_wins / total_matches
        average_bet = total_bet / total_matches

    stats = FighterStats(
        win_rate=win_rate, average_bet=average_bet, total_matches=total_matches
    )

    return FighterInfo(fighter=dict(fighter), stats=stats)


def _analyze_matches_vs(
    matches: List[Row], fighter: Row, opponent: Row
) -> FighterInfoVs:
    num_wins = 0
    total_bet = 0
    num_wins_vs = 0
    total_bet_vs = 0
    total_matches_vs = 0

    for match in matches:
        is_red = match["fighter_red"] == fighter["id"]

        if opponent["id"] in [match["fighter_red"], match["fighter_blue"]]:
            if match["winner"] == fighter["id"]:
                num_wins_vs += 1
            total_matches_vs += 1
            if is_red:
                total_bet_vs += match["bet_red"]
            else:
                total_bet_vs += match["bet_blue"]

        if match["winner"] == fighter["id"]:
            num_wins += 1

        if is_red:
            total_bet += match["bet_red"]
        else:
            total_bet += match["bet_blue"]

    total_matches = len(matches)
    win_rate = 0.0
    average_bet = 0.0
    if total_matches:
        win_rate = num_wins / total_matches
        average_bet = total_bet / total_matches

    win_rate_vs = 0.0
    average_bet_vs = 0.0
    if total_matches_vs:
        win_rate_vs = num_wins_vs / total_matches_vs
        average_bet_vs = total_bet_vs / total_matches_vs

    stats = FighterStats(
        win_rate=win_rate, average_bet=average_bet, total_matches=total_matches
    )
    stats_vs = FighterStatsVs(
        win_rate_vs=win_rate_vs,
        average_bet_vs=average_bet_vs,
        total_matches_vs=total_matches_vs,
    )

    return FighterInfoVs(fighter=dict(fighter), stats=stats, stats_vs=stats_vs)


def _get_fighter_throw_none(
    db: Database, fighter_name: Optional[str] = None, fighter_id: Optional[int] = None
) -> Row:
    fighter = db.get_fighter(fighter_name, fighter_id)
    if fighter is None:
        raise BadRequest(
            f"Fighter with either id: {fighter_id} or name: {fighter_name} was not found."
        )
    return fighter
