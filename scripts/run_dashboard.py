import json
from pathlib import Path

import yaml
import numpy as np

from cfi.data.binance_client import klines, funding_rate
from cfi.data.store import klines_to_df

from cfi.features.indicators import ema, adx, atr, zscore, bb_width
from cfi.regime.regime_engine import compute_bias, classify_regime, regime_confidence

from cfi.signals.levels import pivot_levels
from cfi.types import Direction
from cfi.signals.decision import compose_card
from cfi.reporting.dashboard import to_dashboard_dict


def load_cfg() -> dict:
    cfg_path = Path("config/default.yaml")
    if not cfg_path.exists():
        raise FileNotFoundError("config/default.yaml bulunamadı.")
    text = cfg_path.read_text(encoding="utf-8-sig").strip()
    return yaml.safe_load(text) if text else {}


def main():
    cfg = load_cfg()

    # defaults (yoksa ekle)
    cfg.setdefault("exchange", "binance_usdtm")
    cfg.setdefault("futures", {"funding_warn": 0.0005, "funding_veto": 0.0010})
    cfg.setdefault(
        "risk",
        {
            "max_default_leverage": 25,
            "max_a_plus_leverage": 50,
            "confidence_tradeable": 75,
            "confidence_a_plus": 82,
        },
    )
    cfg.setdefault(
        "caps_rules",
        {
            "range_cap": 8,
            "vol_spike_cap": 12,
            "oi_divergence_cap": 10,
            "funding_warn_cap": 15,
        },
    )
    cfg.setdefault(
        "regime",
        {
            "adx_trend_min": 20,
            "adx_range_max": 15,
            "atr_z_vol_spike": 2.0,
            "bbw_squeeze_max": 0.06,
        },
    )

    symbols = ["BTCUSDT", "ADAUSDT", "SOLUSDT"]
    tfs = ["5m", "15m", "1h", "4h", "1d"]

    assets = []

    for sym in symbols:
        # --- OHLCV fetch ---
        dfs = {}
        for tf in tfs:
            raw = klines(sym, tf, limit=500)
            dfs[tf] = klines_to_df(raw)

        # --- bias (4h) ---
        c4h = dfs["4h"]["close"]
        ema20_4h = ema(c4h, 20)
        ema50_4h = ema(c4h, 50)
        bias = compute_bias(dfs["4h"], ema20_4h, ema50_4h)

        # --- regime baseline (1h) ---
        c1h = dfs["1h"]["close"]
        ema20_1h = ema(c1h, 20)
        ema50_1h = ema(c1h, 50)
        ema200_1h = ema(c1h, 200)
        adx_1h = float(adx(dfs["1h"], 14).iloc[-1])
        bbw_1h = float(bb_width(c1h, 20, 2).iloc[-1])

        # --- volatility proxy (15m ATR zscore) ---
        atr_15m = atr(dfs["15m"], 14)
        atr_z_15m = float(zscore(atr_15m, 96).iloc[-1]) if len(atr_15m) >= 96 else 0.0
        vol_z_15m = float(zscore(dfs["15m"]["volume"], 96).iloc[-1]) if len(dfs["15m"]) >= 96 else 0.0


        # --- futures stress: funding ---
        fr = funding_rate(sym, limit=1)
        funding = float(fr[-1]["fundingRate"]) if fr else 0.0

        penalties = 0
        if abs(funding) >= cfg["futures"]["funding_warn"]:
            penalties += 10
        if np.isfinite(atr_z_15m) and atr_z_15m >= cfg["regime"]["atr_z_vol_spike"]:
            penalties += 10

        regime = classify_regime(
            ema20=float(ema20_1h.iloc[-1]),
            ema50=float(ema50_1h.iloc[-1]),
            ema200=float(ema200_1h.iloc[-1]),
            adx_val=adx_1h,
            atr_z=atr_z_15m,
            bbw=bbw_1h,
            cfg=cfg,
        )

        tf_agree = (
            1.0
            if ((ema20_1h.iloc[-1] > ema50_1h.iloc[-1]) == (ema20_4h.iloc[-1] > ema50_4h.iloc[-1]))
            else 0.5
        )
        conf = regime_confidence(regime, adx_val=adx_1h, tf_agree=tf_agree, penalties=penalties)

        # --- BREAKOUT yönü: 1H pivot + 15m close ---
        levels = pivot_levels(dfs["1h"], n=20)
        swing_high = levels["swing_high"]
        swing_low = levels["swing_low"]
        c15 = float(dfs["15m"]["close"].iloc[-1])

        if c15 > swing_high:
            breakout_dir = Direction.LONG
        elif c15 < swing_low:
            breakout_dir = Direction.SHORT
        else:
            breakout_dir = Direction.NEUTRAL
         # Breakout teyidi: pivot break + volume + retest
   	        # Breakout teyidi: pivot break + volume + retest
        if breakout_dir == Direction.LONG:
            retest_ok = retest_pass_5m(dfs["5m"], swing_high, "LONG", lookback=12)
            breakout_confirmed = (c15 > swing_high) and (vol_z_15m >= 1.0) and retest_ok
        elif breakout_dir == Direction.SHORT:
            retest_ok = retest_pass_5m(dfs["5m"], swing_low, "SHORT", lookback=12)
            breakout_confirmed = (c15 < swing_low) and (vol_z_15m >= 1.0) and retest_ok
        else:
            breakout_confirmed = False
        if regime == "BREAKOUT" and not breakout_confirmed:
            breakout_dir = Direction.NEUTRAL


        # base cap per symbol
        base_cap = 25 if sym == "BTCUSDT" else (20 if sym == "SOLUSDT" else 18)

        card = compose_card(
            symbol=sym,
            regime_label=regime,
            confidence=conf,
            bias=bias,
            funding_abs=abs(funding),
            oi_divergence=False,  # sonraki sprint
            vol_spike=(regime == "VOL_SPIKE"),
            wick_market=False,  # sonraki sprint
            base_cap=base_cap,
            cfg=cfg,
            breakout_dir=breakout_dir,
        )

        assets.append(to_dashboard_dict(card))

    out = {"exchange": cfg.get("exchange"), "assets": assets}
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
