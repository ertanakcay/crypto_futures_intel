import numpy as np
import pandas as pd
from ..types import Direction

def compute_bias(df_4h: pd.DataFrame, ema20_4h: pd.Series, ema50_4h: pd.Series) -> Direction:
    c = df_4h["close"].iloc[-1]
    if ema20_4h.iloc[-1] > ema50_4h.iloc[-1] and c > ema50_4h.iloc[-1]:
        return Direction.LONG
    if ema20_4h.iloc[-1] < ema50_4h.iloc[-1] and c < ema50_4h.iloc[-1]:
        return Direction.SHORT
    return Direction.NEUTRAL

def classify_regime(*, ema20: float, ema50: float, ema200: float, adx_val: float, atr_z: float, bbw: float, cfg: dict) -> str:
    if np.isfinite(atr_z) and atr_z >= cfg["regime"]["atr_z_vol_spike"]:
        return "VOL_SPIKE"

    # Trend: ADX güçlü + EMA hizalı
    if adx_val >= cfg["regime"]["adx_trend_min"] and ((ema20 > ema50 > ema200) or (ema20 < ema50 < ema200)):
        return "TREND"

    # Range: ADX zayıf
    if adx_val <= cfg["regime"]["adx_range_max"]:
        return "RANGE"

    # Breakout sadece squeeze varken
    if np.isfinite(bbw) and bbw <= cfg["regime"]["bbw_squeeze_max"]:
        return "BREAKOUT"

    # Arada kalan bölge = chop → range gibi yönet
    return "RANGE"

def regime_confidence(regime_label: str, *, adx_val: float, tf_agree: float, penalties: int) -> int:
    score = 50
    if np.isfinite(adx_val):
        score += int(min(20, max(0, (adx_val - 10) * 1.2)))
    score += int(20 * tf_agree)

    if regime_label == "TREND":
        score += 10
    elif regime_label == "BREAKOUT":
        score += 5
    elif regime_label == "VOL_SPIKE":
        score -= 10

    score -= penalties
    return int(max(0, min(100, score)))
