from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List

class RegimeLabel(str, Enum):
    TREND = "TREND"
    RANGE = "RANGE"
    BREAKOUT = "BREAKOUT"
    VOL_SPIKE = "VOL_SPIKE"

class Status(str, Enum):
    TRADEABLE = "TRADEABLE"
    CAUTION = "CAUTION"
    NO_TRADE = "NO_TRADE"

class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"

class SetupType(str, Enum):
    PULLBACK = "PULLBACK"
    BREAKOUT = "BREAKOUT"
    MEAN_REVERT = "MEAN_REVERT"

class RedFlag(str, Enum):
    FUNDING_EXTREME = "FUNDING_EXTREME"
    OI_DIVERGENCE = "OI_DIVERGENCE"
    VOL_SPIKE = "VOL_SPIKE"
    WICK_MARKET = "WICK_MARKET"

@dataclass
class Regime:
    label: RegimeLabel
    confidence: int  # 0-100

@dataclass
class Trigger:
    tfs: List[str]
    conditions: List[str]

@dataclass
class StopModel:
    tf: str
    method: str
    multiple: float

@dataclass
class RiskBox:
    leverage_cap: int
    stop_model: StopModel
    red_flags: List[RedFlag] = field(default_factory=list)

@dataclass
class DecisionCard:
    symbol: str
    regime: Regime
    status: Status
    bias: Direction
    setup: SetupType
    trigger: Trigger
    risk: RiskBox
    action: str
    invalidation: str
    ts_iso: str
