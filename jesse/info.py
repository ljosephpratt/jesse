from jesse.enums import exchanges as exchanges_enums, timeframes

JESSE_API_URL = "https://api1.jesse.trade/api"
# JESSE_API_URL = 'http://localhost:8040/api'
JESSE_WEBSITE_URL = "https://jesse.trade"
# JESSE_WEBSITE_URL = 'http://localhost:8040'

ALPACA_TIMEFRAMES = [
    timeframes.MINUTE_1,
    timeframes.MINUTE_3,
    timeframes.MINUTE_5,
    timeframes.MINUTE_15,
    timeframes.MINUTE_30,
    timeframes.HOUR_1,
    timeframes.HOUR_2,
    timeframes.HOUR_4,
    timeframes.HOUR_6,
    timeframes.HOUR_8,
    timeframes.HOUR_12,
    timeframes.DAY_1,
    timeframes.WEEK_1,
    timeframes.MONTH_1,
]


exchange_info = {
    # Alpaca
    exchanges_enums.ALPACA: {
        "name": exchanges_enums.ALPACA,
        "url": "https://alpaca.markets",
        "fee": 0.0,  # Alpaca typically has zero commission
        "type": "spot",  # or "futures" depending on what you're implementing
        "settlement_currency": "USD",
        "supported_leverage_modes": ["cross", "isolated"],
        "supported_timeframes": ALPACA_TIMEFRAMES,
        "modes": {
            "backtesting": True,
            "live_trading": True,
        },
        "required_live_plan": "free",
    },
}

# list of supported exchanges for backtesting
backtesting_exchanges = [
    k for k, v in exchange_info.items() if v["modes"]["backtesting"] is True
]
backtesting_exchanges = list(sorted(backtesting_exchanges))

# list of supported exchanges for live trading
live_trading_exchanges = [
    k for k, v in exchange_info.items() if v["modes"]["live_trading"] is True
]
live_trading_exchanges = list(sorted(live_trading_exchanges))

# used for backtesting, and live trading when local candle generation is enabled:
jesse_supported_timeframes = [
    timeframes.MINUTE_1,
    timeframes.MINUTE_3,
    timeframes.MINUTE_5,
    timeframes.MINUTE_15,
    timeframes.MINUTE_30,
    timeframes.MINUTE_45,
    timeframes.HOUR_1,
    timeframes.HOUR_2,
    timeframes.HOUR_3,
    timeframes.HOUR_4,
    timeframes.HOUR_6,
    timeframes.HOUR_8,
    timeframes.HOUR_12,
    timeframes.DAY_1,
]
