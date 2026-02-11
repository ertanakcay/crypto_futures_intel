from datetime import datetime, timezone

from ..types import (
    DecisionCard,
    Direction,
    Regime,
    RegimeLabel,
    RiskBox,
    SetupType,
    StopModel,
)
from ..futures.risk_governor import apply_veto_and_caps
from .playbook import build_breakout_trigger, build_pullback_trigger, choose_setup


def compose_card(
    *,
    symbol: str,
    regime_label: str,
    confidence: int,
    bias: Direction,
    funding_abs: float,
    oi_divergence: bool,
    vol_spike: bool,
    wick_market: bool,
    base_cap: int,
    cfg: dict,
    breakout_dir: Direction | None = None,   # ✅ yeni: breakout yönü
) -> DecisionCard:

    status, cap, flags, a_plus = apply_veto_and_caps(
        base_cap=base_cap,
        regime_label=regime_label,
        confidence=confidence,
        funding_abs=funding_abs,
        oi_divergence=oi_divergence,
        vol_spike=vol_spike,
        wick_market=wick_market,
        cfg=cfg,
    )

    setup: SetupType = choose_setup(regime_label)

    # ✅ BREAKOUT modunda yön: breakout_dir
    # ✅ Trend/pullback modunda yön: bias
    if regime_label == "BREAKOUT" and breakout_dir is not None and breakout_dir != Direction.NEUTRAL:
        use_dir = breakout_dir
    else:
        use_dir = bias if bias != Direction.NEUTRAL else Direction.LONG
     # 🚫 BREAKOUT var ama kırılım yoksa → trade yok
    if regime_label == "BREAKOUT" and (breakout_dir is None or breakout_dir == Direction.NEUTRAL):
      status = status.NO_TRADE

    # Trigger seçimi
    if setup == SetupType.BREAKOUT:
        trig = build_breakout_trigger(use_dir)
    else:
        trig = build_pullback_trigger(use_dir)

    # Action kararı
    if status == status.NO_TRADE:
        action = "NO-TRADE"
        invalidation = "N/A"
    else:
        if regime_label == "BREAKOUT" and breakout_dir is not None and breakout_dir != Direction.NEUTRAL:
            action = breakout_dir.value
        else:
            action = bias.value

        invalidation = "1H structure break / level reclaim"

    stop_model = StopModel(tf="15m", method="ATR", multiple=1.2)

    if a_plus:
        cap = min(cfg["risk"]["max_a_plus_leverage"], max(cap, cfg["risk"]["max_default_leverage"]))

    return DecisionCard(
        symbol=symbol,
        regime=Regime(label=RegimeLabel(regime_label), confidence=int(confidence)),
        status=status,
        bias=bias,
        setup=setup,
        trigger=trig,
        risk=RiskBox(leverage_cap=int(cap), stop_model=stop_model, red_flags=flags),
        action=action,
        invalidation=invalidation,
        ts_iso=datetime.now(timezone.utc).astimezone().isoformat(),
    )
