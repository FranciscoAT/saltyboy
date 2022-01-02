from dataclasses import dataclass
from typing import Dict

from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class DatabaseStatsBreakdown(JsonSchemaMixin):
    """Database stats broken down by tier"""
    breakdown: Dict[str, int]
    total: int


@dataclass
class DatabaseStatsSchema(JsonSchemaMixin):
    """All database stats"""
    matches: DatabaseStatsBreakdown
    fighters: DatabaseStatsBreakdown
