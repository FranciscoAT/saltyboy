from dataclasses import dataclass
from typing import Dict


@dataclass
class DatabaseStatsBreakdown:
    breakdown: Dict[str, int]
    total: int


@dataclass
class DatabaseStatsSchema:
    matches: DatabaseStatsBreakdown
    fighters: DatabaseStatsBreakdown
