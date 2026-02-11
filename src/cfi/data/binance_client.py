import requests
from typing import List, Dict

BASE = "https://fapi.binance.com"

def _get(path: str, params: dict) -> list:
    r = requests.get(BASE + path, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def klines(symbol: str, interval: str, limit: int = 500) -> list:
    # interval: "5m","15m","1h","4h","1d"
    return _get("/fapi/v1/klines", {"symbol": symbol, "interval": interval, "limit": limit})

def funding_rate(symbol: str, limit: int = 1) -> list:
    return _get("/fapi/v1/fundingRate", {"symbol": symbol, "limit": limit})

def open_interest(symbol: str) -> dict:
    return requests.get(BASE + "/fapi/v1/openInterest", params={"symbol": symbol}, timeout=15).json()
