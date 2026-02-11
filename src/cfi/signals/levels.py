import pandas as pd

def pivot_levels(df_1h: pd.DataFrame, n: int = 20) -> dict:
    """
    Basit pivot: son n bar içindeki swing_high / swing_low.
    df_1h index: time, columns: open/high/low/close/volume
    """
    swing_high = df_1h["high"].rolling(n).max().iloc[-1]
    swing_low = df_1h["low"].rolling(n).min().iloc[-1]
    return {"swing_high": float(swing_high), "swing_low": float(swing_low)}
def retest_pass_5m(df_5m: pd.DataFrame, level: float, direction: str, lookback: int = 12) -> bool:
    """
    direction: "LONG" => level üstünde tutunma
               "SHORT" => level altında tutunma
    lookback: son kaç adet 5m bar (12 => ~1 saat)
    Basit kural: son lookback içinde level'a temas + son kapanış doğru tarafta.
    """
    d = df_5m.tail(lookback)
    last_close = float(d["close"].iloc[-1])

    touched = (d["low"] <= level <= d["high"]).any()

    if direction == "LONG":
        return touched and (last_close > level)
    if direction == "SHORT":
        return touched and (last_close < level)
    return False
