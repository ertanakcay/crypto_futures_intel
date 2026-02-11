import pandas as pd

KLINE_COLS = ["open_time","open","high","low","close","volume",
              "close_time","quote_asset_volume","num_trades",
              "taker_buy_base","taker_buy_quote","ignore"]

def klines_to_df(klines: list) -> pd.DataFrame:
    df = pd.DataFrame(klines, columns=KLINE_COLS)
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df.set_index("open_time", inplace=True)
    return df[["open","high","low","close","volume"]]
