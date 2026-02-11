from ..types import DecisionCard

def to_dashboard_dict(card: DecisionCard) -> dict:
    why = []
    if card.status.value == "NO_TRADE":
        if card.regime.label.value == "BREAKOUT":
            why.append("Breakout teyidi yok (15m close pivot dışına taşmadı).")
        if len(card.risk.red_flags) > 0:
            why.append("Risk veto / kırmızı bayrak var.")
        if not why:
            why.append("Confidence / risk filtreleri nedeniyle trade dışı.")

    return {
        "symbol": card.symbol,
        "regime": {"label": card.regime.label.value, "confidence": card.regime.confidence},
        "status": card.status.value,
        "bias": card.bias.value,
        "setup": card.setup.value,
        "trigger": {"tfs": card.trigger.tfs, "conditions": card.trigger.conditions[:3]},
        "risk": {
            "leverage_cap": card.risk.leverage_cap,
            "stop": f"{card.risk.stop_model.multiple}x {card.risk.stop_model.method}({card.risk.stop_model.tf})",
            "red_flags": [f.value for f in card.risk.red_flags][:3],
        },
        "action": card.action,
        "invalidation": card.invalidation,
        "why": why,   # ✅ yeni
        "ts": card.ts_iso,
    }
