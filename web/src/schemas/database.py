from dataclasses import dataclass
from typing import Dict

from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class DatabaseStatsBreakdown(JsonSchemaMixin):
    breakdown: Dict[str, int]
    total: int


@dataclass
class DatabaseStatsSchema(JsonSchemaMixin):
    matches: DatabaseStatsBreakdown
    fighters: DatabaseStatsBreakdown
