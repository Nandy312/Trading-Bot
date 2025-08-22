def find_solid_zones(zones):
    """Return supports/resistances from any timeframe where first 4 digits match in at least 2 timeframes."""
    tf_keys = ['60', '300', '900', '1800']
    all_supports = []
    all_resistances = []
    # Collect all supports and resistances with their first4 digit and source tf
    for tf in tf_keys:
        for s in zones.get(tf, {}).get('supports', []):
            all_supports.append((s, tf, str(int(s))[:4]))
        for r in zones.get(tf, {}).get('resistances', []):
            all_resistances.append((r, tf, str(int(r))[:4]))
    # Find all unique first4s
    support_first4s = set(x[2] for x in all_supports)
    resistance_first4s = set(x[2] for x in all_resistances)
    # For each first4, count how many tfs it appears in
    solid_supports = []
    for f4 in support_first4s:
        tfs = set(x[1] for x in all_supports if x[2] == f4)
        if len(tfs) >= 2:
            # Add all levels with this first4
            solid_supports.extend([x[0] for x in all_supports if x[2] == f4])
    solid_resistances = []
    for f4 in resistance_first4s:
        tfs = set(x[1] for x in all_resistances if x[2] == f4)
        if len(tfs) >= 2:
            solid_resistances.extend([x[0] for x in all_resistances if x[2] == f4])
    # Remove duplicates and sort
    solid_supports = sorted(list(set(solid_supports)))
    solid_resistances = sorted(list(set(solid_resistances)))
    return {'supports': solid_supports, 'resistances': solid_resistances}
# --- Indicator Calculation Functions ---
# Each function returns 'BUY', 'SELL', or 'NEUTRAL' for the latest candle
# Settings for 1-min trading are documented in comments
def indicator_ema(close, period=10):
    ema = close.ewm(span=period, adjust=False).mean()
    if close.iloc[-1] > ema.iloc[-1]:
        return 'BUY'
    elif close.iloc[-1] < ema.iloc[-1]:
        return 'SELL'
    return 'NEUTRAL'

def indicator_sma(close, period=10):
    sma = close.rolling(window=period).mean()
    if close.iloc[-1] > sma.iloc[-1]:
        return 'BUY'
    elif close.iloc[-1] < sma.iloc[-1]:
        return 'SELL'
    return 'NEUTRAL'

def indicator_rsi(close, period=7, overbought=70, oversold=30):
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    if val < oversold:
        return 'BUY'
    elif val > overbought:
        return 'SELL'
    return 'NEUTRAL'

# ...existing code...
# Add 23 more indicator functions (MACD, Bollinger Bands, Stochastic, ATR, ADX, CCI, Parabolic SAR, Williams %R, ROC, Momentum, OBV, MFI, VWAP, Ichimoku, Donchian, Keltner, Envelope, DMI, Chaikin, Elder Ray, TSI, Ultimate Oscillator, Force Index)
# For brevity, these will be stubbed as NEUTRAL, but you can fill in the logic as needed
def indicator_macd(close): return 'NEUTRAL'
def indicator_bollinger(close): return 'NEUTRAL'
def indicator_stochastic(close): return 'NEUTRAL'
def indicator_atr(close): return 'NEUTRAL'
def indicator_adx(close): return 'NEUTRAL'
def indicator_cci(close): return 'NEUTRAL'
def indicator_sar(close): return 'NEUTRAL'
def indicator_williams(close): return 'NEUTRAL'
def indicator_roc(close): return 'NEUTRAL'
def indicator_momentum(close): return 'NEUTRAL'
def indicator_obv(close): return 'NEUTRAL'
def indicator_mfi(close): return 'NEUTRAL'
def indicator_vwap(close): return 'NEUTRAL'
def indicator_ichimoku(close): return 'NEUTRAL'
def indicator_donchian(close): return 'NEUTRAL'
def indicator_keltner(close): return 'NEUTRAL'
def indicator_envelope(close): return 'NEUTRAL'
def indicator_dmi(close): return 'NEUTRAL'
def indicator_chaikin(close): return 'NEUTRAL'
def indicator_elder(close): return 'NEUTRAL'
def indicator_tsi(close): return 'NEUTRAL'
def indicator_ultimate(close): return 'NEUTRAL'
def indicator_force(close): return 'NEUTRAL'

INDICATOR_FUNCS = [
    indicator_ema, indicator_sma, indicator_rsi, indicator_macd, indicator_bollinger,
    indicator_stochastic, indicator_atr, indicator_adx, indicator_cci, indicator_sar,
    indicator_williams, indicator_roc, indicator_momentum, indicator_obv, indicator_mfi,
    indicator_vwap, indicator_ichimoku, indicator_donchian, indicator_keltner, indicator_envelope,
    indicator_dmi, indicator_chaikin, indicator_elder, indicator_tsi, indicator_ultimate, indicator_force
]

INDICATOR_NAMES = [
    'EMA', 'SMA', 'RSI', 'MACD', 'Bollinger Bands', 'Stochastic', 'ATR', 'ADX', 'CCI', 'Parabolic SAR',
    'Williams %R', 'ROC', 'Momentum', 'OBV', 'MFI', 'VWAP', 'Ichimoku', 'Donchian', 'Keltner', 'Envelope',
    'DMI', 'Chaikin', 'Elder Ray', 'TSI', 'Ultimate Oscillator', 'Force Index'
]



import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import yfinance as yf
import websocket
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Assets supporting 1-min expiry (forex, synthetic indices, commodities, crypto)
ONE_MIN_SYMBOLS = [
    # Major/minor forex pairs
    {"symbol": "frxEURUSD", "name": "EUR/USD", "yahoo": "EURUSD=X", "deriv": None},
    {"symbol": "frxGBPUSD", "name": "GBP/USD", "yahoo": "GBPUSD=X", "deriv": None},
    {"symbol": "frxUSDJPY", "name": "USD/JPY", "yahoo": "USDJPY=X", "deriv": None},
    {"symbol": "frxAUDUSD", "name": "AUD/USD", "yahoo": "AUDUSD=X", "deriv": None},
    {"symbol": "frxUSDCHF", "name": "USD/CHF", "yahoo": "USDCHF=X", "deriv": None},
    {"symbol": "frxUSDCAD", "name": "USD/CAD", "yahoo": "USDCAD=X", "deriv": None},
    {"symbol": "frxNZDUSD", "name": "NZD/USD", "yahoo": "NZDUSD=X", "deriv": None},
    {"symbol": "frxEURGBP", "name": "EUR/GBP", "yahoo": "EURGBP=X", "deriv": None},
    {"symbol": "frxEURJPY", "name": "EUR/JPY", "yahoo": "EURJPY=X", "deriv": None},
    {"symbol": "frxGBPJPY", "name": "GBP/JPY", "yahoo": "GBPJPY=X", "deriv": None},
    # Synthetic Indices (Deriv API code)
    {"symbol": "R_10", "name": "Volatility 10 Index", "yahoo": None, "deriv": "R_10"},
    {"symbol": "R_25", "name": "Volatility 25 Index", "yahoo": None, "deriv": "R_25"},
    {"symbol": "R_50", "name": "Volatility 50 Index", "yahoo": None, "deriv": "R_50"},
    {"symbol": "R_75", "name": "Volatility 75 Index", "yahoo": None, "deriv": "R_75"},
    {"symbol": "R_100", "name": "Volatility 100 Index", "yahoo": None, "deriv": "R_100"},
    {"symbol": "BOOM1000", "name": "Boom 1000 Index", "yahoo": None, "deriv": "BOOM1000"},
    {"symbol": "CRASH1000", "name": "Crash 1000 Index", "yahoo": None, "deriv": "CRASH1000"},
    # Commodities
    {"symbol": "XAUUSD", "name": "Gold/USD", "yahoo": "GC=F", "deriv": None},
    {"symbol": "XAGUSD", "name": "Silver/USD", "yahoo": "SI=F", "deriv": None},
    # Crypto
    {"symbol": "BTCUSD", "name": "Bitcoin/USD", "yahoo": "BTC-USD", "deriv": None},
    {"symbol": "ETHUSD", "name": "Ethereum/USD", "yahoo": "ETH-USD", "deriv": None},
]


def get_asset_info(symbol):
    for s in ONE_MIN_SYMBOLS:
        if s["symbol"] == symbol:
            return s
    return None

def calculate_ema(series, period=10):
    return series.ewm(span=period, adjust=False).mean()

def calculate_rsi(series, period=7):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@app.get("/assets")
def get_assets():
    return {
        "symbols": [{"symbol": s["symbol"], "name": s["name"]} for s in ONE_MIN_SYMBOLS]
    }


def consensus_signal(close):
    signals = {}
    buy_count = 0
    sell_count = 0
    for func, name in zip(INDICATOR_FUNCS, INDICATOR_NAMES):
        try:
            sig = func(close)
        except Exception:
            sig = 'NEUTRAL'
        signals[name] = sig
        if sig == 'BUY':
            buy_count += 1
        elif sig == 'SELL':
            sell_count += 1
    total = buy_count + sell_count
    # Only generate signal if 70%+ agree
    if total > 0:
        if buy_count / len(INDICATOR_FUNCS) >= 0.7:
            return 'BUY', signals
        elif sell_count / len(INDICATOR_FUNCS) >= 0.7:
            return 'SELL', signals
    return 'NO SIGNAL', signals

@app.get("/signal")
def get_signal(symbol: str):
    asset = get_asset_info(symbol)
    if not asset:
        return {"error": "Symbol not supported"}
    # Yahoo Finance source
    if asset["yahoo"]:
        try:
            df = yf.download(asset["yahoo"], interval="1m", period="30m")
            if df.empty or len(df) < 15:
                return {"error": "Not enough data"}
            close = df["Close"]
            signal, breakdown = consensus_signal(close)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            return {"symbol": symbol, "signal": signal, "timestamp": timestamp, "breakdown": breakdown}
        except Exception as e:
            return {"error": str(e)}
    # Deriv synthetic indices
    elif asset["deriv"]:
        try:
            ws = websocket.create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089")
            req = {
                "ticks_history": asset["deriv"],
                "count": 30,
                "end": "latest",
                "style": "candles",
                "granularity": 60
            }
            ws.send(json.dumps(req))
            result = json.loads(ws.recv())
            ws.close()
            candles = result.get("candles", [])
            if not candles or len(candles) < 15:
                return {"error": "Not enough data"}
            close = pd.Series([c["close"] for c in candles])
            signal, breakdown = consensus_signal(close)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            return {"symbol": symbol, "signal": signal, "timestamp": timestamp, "breakdown": breakdown}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "No data source for this asset"}


# -------------------- Multi-timeframe Analysis --------------------
def _yf_interval_for_seconds(seconds: int) -> str:
    return {60: '1m', 300: '5m', 900: '15m', 1800: '30m'}.get(seconds, '1m')

def _yf_period_for_interval(interval: str) -> str:
    # Use safe periods accepted by yfinance; we'll filter to last 10h later
    if interval == '1m':
        return '1d'
    else:
        return '5d'

def fetch_candles(asset: dict, timeframe_sec: int, hours: int = 10) -> pd.DataFrame:
    """Return OHLC dataframe for given timeframe seconds covering ~last hours."""
    if asset.get('yahoo'):
        interval = _yf_interval_for_seconds(timeframe_sec)
        period = _yf_period_for_interval(interval)
        df = yf.download(asset['yahoo'], interval=interval, period=period, progress=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.tail(int((hours * 3600) / timeframe_sec) + 10)
        df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
        df = df[['open', 'high', 'low', 'close']].dropna()
        return df
    elif asset.get('deriv'):
        count = int((hours * 3600) / timeframe_sec) + 10
        ws = websocket.create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089")
        req = {
            "ticks_history": asset['deriv'],
            "count": count,
            "end": "latest",
            "style": "candles",
            "granularity": timeframe_sec
        }
        ws.send(json.dumps(req))
        result = json.loads(ws.recv())
        ws.close()
        candles = result.get('candles', [])
        if not candles:
            return pd.DataFrame()
        o = [c['open'] for c in candles]
        h = [c['high'] for c in candles]
        l = [c['low'] for c in candles]
        c_ = [c['close'] for c in candles]
        df = pd.DataFrame({'open': o, 'high': h, 'low': l, 'close': c_})
        return df
    else:
        return pd.DataFrame()

def compute_atr(df: pd.DataFrame, period: int = 14) -> float:
    if df.empty or len(df) < period + 1:
        return 0.0
    prev_close = df['close'].shift(1)
    tr = pd.concat([
        (df['high'] - df['low']).abs(),
        (df['high'] - prev_close).abs(),
        (df['low'] - prev_close).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean().iloc[-1]
    return float(atr) if pd.notna(atr) else 0.0

def detect_zones(df: pd.DataFrame, window: int = 5, merge_threshold: float = None):
    """Return dict with 'supports' and 'resistances' lists of price levels."""
    if df.empty:
        return {'supports': [], 'resistances': []}
    highs = df['high']
    lows = df['low']
    res_levels = []
    sup_levels = []
    for i in range(window, len(df) - window):
        seg = slice(i - window, i + window + 1)
        if highs.iloc[i] == highs.iloc[seg].max():
            res_levels.append(highs.iloc[i])
        if lows.iloc[i] == lows.iloc[seg].min():
            sup_levels.append(lows.iloc[i])
    # Merge nearby levels
    def merge_levels(levels, thr):
        if not levels:
            return []
        levels = sorted(levels)
        merged = [levels[0]]
        for lv in levels[1:]:
            if abs(lv - merged[-1]) <= thr:
                merged[-1] = (merged[-1] + lv) / 2.0
            else:
                merged.append(lv)
        return merged
    atr = compute_atr(df)
    thr = merge_threshold if merge_threshold is not None else max(atr * 0.5, (df['close'].iloc[-1] * 0.0005))
    return {
        'supports': merge_levels(sup_levels, thr)[:5],
        'resistances': merge_levels(res_levels, thr)[:5]
    }

def ema_trend(close: pd.Series, short_p: int, long_p: int) -> str:
    if len(close) < long_p + 2:
        return 'FLAT'
    e1 = close.ewm(span=short_p, adjust=False).mean()
    e2 = close.ewm(span=long_p, adjust=False).mean()
    if e1.iloc[-1] > e2.iloc[-1] and e1.iloc[-2] <= e2.iloc[-2]:
        return 'UP'
    if e1.iloc[-1] < e2.iloc[-1] and e1.iloc[-2] >= e2.iloc[-2]:
        return 'DOWN'
    # If no recent cross, use distance
    diff = e1.iloc[-1] - e2.iloc[-1]
    if diff > 0:
        return 'UP'
    if diff < 0:
        return 'DOWN'
    return 'FLAT'

def weakness_at_zone(df1m: pd.DataFrame, zones: dict):
    if df1m.empty:
        return {'at': 'none', 'zone': None, 'weak': False}
    atr1 = compute_atr(df1m, period=14)
    if atr1 == 0:
        return {'at': 'none', 'zone': None, 'weak': False}
    last_close = df1m['close'].iloc[-1]
    zone_width = max(atr1 * 0.25, last_close * 0.0003)
    nearest_res = min(zones.get('resistances', []), key=lambda z: abs(z - last_close), default=None)
    nearest_sup = min(zones.get('supports', []), key=lambda z: abs(z - last_close), default=None)
    at = 'none'
    ref_zone = None
    if nearest_res is not None and abs(last_close - nearest_res) <= zone_width:
        at = 'resistance'; ref_zone = nearest_res
    elif nearest_sup is not None and abs(last_close - nearest_sup) <= zone_width:
        at = 'support'; ref_zone = nearest_sup
    if at == 'none':
        return {'at': 'none', 'zone': None, 'weak': False}
    # Weakness: 3 small-bodied candles and rejection wicks
    recent = df1m.tail(3)
    bodies = (recent['close'] - recent['open']).abs()
    small = bodies.mean() < atr1 * 0.3
    if at == 'resistance':
        rejection = (recent['close'] < ref_zone).all()
        weak = bool(small and rejection)
    else:
        rejection = (recent['close'] > ref_zone).all()
        weak = bool(small and rejection)
    return {'at': at, 'zone': float(ref_zone) if ref_zone is not None else None, 'weak': weak}


@app.get('/analysis')
def analysis(symbol: str):
    asset = get_asset_info(symbol)
    if not asset:
        return {"error": "Symbol not supported"}
    tf_secs = [60, 300, 900, 1800]
    frames = {}
    for s in tf_secs:
        df = fetch_candles(asset, s, hours=10)
        frames[s] = df
    # Zones per TF
    zones = {str(s): detect_zones(frames[s]) for s in tf_secs}
    # Trends
    short_term = ema_trend(frames[60]['close'] if not frames[60].empty else pd.Series(dtype=float), 10, 20)
    long_term = ema_trend(frames[1800]['close'] if not frames[1800].empty else pd.Series(dtype=float), 50, 100)
    # Weakness near nearest zone using 1m zones (fallback to 5m)
    zref = zones.get('60') if zones.get('60') else zones.get('300', {'supports': [], 'resistances': []})
    weak_info = weakness_at_zone(frames[60], zref)
    # Entry suggestion
    entry = {"direction": "NONE", "zone": weak_info.get('zone'), "reason": "No weakness at key zone"}
    if weak_info['weak']:
        if weak_info['at'] == 'resistance' and short_term != 'UP':
            entry = {"direction": "SELL", "zone": weak_info['zone'], "reason": "Weak at resistance with non-up short-term trend"}
        elif weak_info['at'] == 'support' and short_term != 'DOWN':
            entry = {"direction": "BUY", "zone": weak_info['zone'], "reason": "Weak at support with non-down short-term trend"}
    solid_zones = find_solid_zones(zones)
    return {
        "symbol": symbol,
        "zones": zones,
        "trends": {"short_term": short_term, "long_term": long_term},
        "weakness": weak_info,
    "entry_suggestion": entry,
    "solid_zones": solid_zones
    }
