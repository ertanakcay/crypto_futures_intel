from ..types import Direction, SetupType, Trigger

def build_pullback_trigger(direction: Direction) -> Trigger:
    if direction == Direction.SHORT:
        return Trigger(
            tfs=["15m", "5m"],
            conditions=[
                "15m lower-high formed",
                "15m close < EMA20",
                "5m breakdown & retest fails (body rejection)",
            ],
        )
    return Trigger(
        tfs=["15m", "5m"],
        conditions=[
            "15m higher-low formed",
            "15m close > EMA20",
            "5m break & retest holds (body acceptance)",
        ],
    )

def build_breakout_trigger(direction: Direction) -> Trigger:
    if direction == Direction.SHORT:
        return Trigger(
            tfs=["15m", "5m"],
            conditions=[
                "15m close below 1h swing_low",
                "15m volume z-score >= 1.0",
                "5m retest fails below breakdown level",
            ],
        )
    return Trigger(
        tfs=["15m", "5m"],
        conditions=[
            "15m close above 1h swing_high",
            "15m volume z-score >= 1.0",
            "5m retest holds above breakout level",
        ],
    )

def choose_setup(regime_label: str) -> SetupType:
    if regime_label == "TREND":
        return SetupType.PULLBACK
    if regime_label == "BREAKOUT":
        return SetupType.BREAKOUT
    return SetupType.MEAN_REVERT
