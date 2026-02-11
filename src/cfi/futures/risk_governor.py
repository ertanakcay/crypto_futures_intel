from ..types import RedFlag, Status

def apply_veto_and_caps(
    *,
    base_cap: int,
    regime_label: str,
    confidence: int,
    funding_abs: float,
    oi_divergence: bool,
    vol_spike: bool,
    wick_market: bool,
    cfg: dict,
):
    flags = []
    cap = base_cap
    a_plus = False

    # Volatility / microstructure
    if vol_spike:
        flags.append(RedFlag.VOL_SPIKE)
        cap = min(cap, cfg["caps_rules"]["vol_spike_cap"])
    if oi_divergence:
        flags.append(RedFlag.OI_DIVERGENCE)
        cap = min(cap, cfg["caps_rules"]["oi_divergence_cap"])
    if wick_market:
        flags.append(RedFlag.WICK_MARKET)
        cap = min(cap, 10)

    # Funding
    if funding_abs >= cfg["futures"]["funding_veto"]:
        flags.append(RedFlag.FUNDING_EXTREME)
        return Status.NO_TRADE, cap, flags, False
    if funding_abs >= cfg["futures"]["funding_warn"]:
        cap = min(cap, cfg["caps_rules"]["funding_warn_cap"])

    # Regime caps
    if regime_label == "RANGE":
        cap = min(cap, cfg["caps_rules"]["range_cap"])

    # Status by confidence
    if confidence >= cfg["risk"]["confidence_tradeable"] and len(flags) == 0:
        status = Status.TRADEABLE
    elif confidence >= 60:
        status = Status.CAUTION
    else:
        status = Status.NO_TRADE

    # A+ gate
    if (
        confidence >= cfg["risk"]["confidence_a_plus"]
        and len(flags) == 0
        and regime_label in ("TREND", "BREAKOUT")
        and funding_abs < cfg["futures"]["funding_warn"]
    ):
        a_plus = True

    return status, int(cap), flags, a_plus
