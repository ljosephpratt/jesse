import requests
import jesse.helpers as jh
from jesse.modes.import_candles_mode.drivers.interface import CandleExchange
from typing import Union, List
from jesse.services.env import ENV_VALUES
from jesse.enums import exchanges
from datetime import datetime, timedelta


class Alpaca(CandleExchange):
    def __init__(self) -> None:
        super().__init__(
            name=exchanges.ALPACA,
            count=200,
            rate_limit_per_second=5,
            backup_exchange_class=None,
        )

        self.endpoint = "https://data.alpaca.markets/v2"

        # Get API credentials from environment
        self.api_key = ENV_VALUES.get("ALPACA_API_KEY", "")
        self.api_secret = ENV_VALUES.get("ALPACA_API_SECRET", "")

        # Setup headers for API requests
        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
        }

    def get_starting_time(self, symbol: str) -> int:
        """
        Get the earliest timestamp available for the symbol
        """
        # Extract stock symbol from Jesse's format
        stock_symbol = symbol.split("-")[0]

        # For common stocks, we know approximate start dates
        if stock_symbol in ["AAPL", "MSFT", "IBM", "GE"]:
            # These stocks have been around for decades, use a conservative start date
            return int(datetime(2000, 1, 1).timestamp() * 1000)

        # For most other stocks, Alpaca generally has data back to around 2015
        return int(datetime(2015, 1, 1).timestamp() * 1000)

    def fetch(
        self, symbol: str, start_timestamp: int, timeframe: str = "1m"
    ) -> Union[list, None]:
        """
        Fetch candles from Alpaca API
        """
        # Convert symbol format (BTC-USD -> BTC)
        stock_symbol = symbol.split("-")[0]

        # Convert start_timestamp to datetime
        start_date = datetime.fromtimestamp(start_timestamp / 1000)
        end_date = start_date + timedelta(days=1)  # Get 1 day's worth of data

        # Map Jesse timeframes to Alpaca timeframes
        timeframe_map = {
            "1m": "1Min",
            "5m": "5Min",
            "15m": "15Min",
            "30m": "30Min",
            "1h": "1Hour",
            "1D": "1Day",
        }
        alpaca_timeframe = timeframe_map.get(timeframe, "1Min")

        # Build request URL and parameters
        url = f"{self.endpoint}/stocks/{stock_symbol}/bars"
        params = {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "timeframe": alpaca_timeframe,
            "limit": self.count,
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            self.validate_response(response)

            data = response.json()

            if "bars" not in data or not data["bars"]:
                return []

            result = []
            for bar in data["bars"]:
                timestamp = int(
                    datetime.fromisoformat(bar["t"].replace("Z", "")).timestamp() * 1000
                )
                result.append(
                    {
                        "id": jh.generate_unique_id(),
                        "exchange": self.name,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "timestamp": timestamp,
                        "open": float(bar["o"]),
                        "close": float(bar["c"]),
                        "high": float(bar["h"]),
                        "low": float(bar["l"]),
                        "volume": float(bar["v"]),
                    }
                )

            return result

        except Exception as e:
            from jesse.services import logger

            logger.error(f"Error fetching candles from Alpaca: {e}")
            return []

    def get_available_symbols(self) -> list:
        """
        Returns a list of available symbols from Alpaca
        """
        try:
            # Request active assets from Alpaca
            url = f"{self.endpoint}/assets"
            response = requests.get(
                url,
                headers=self.headers,
                params={"status": "active", "asset_class": "us_equity"},
            )

            self.validate_response(response)
            assets = response.json()

            # Return a limited list of popular symbols for better usability
            popular_symbols = [
                "AAPL-USD",
                "MSFT-USD",
                "AMZN-USD",
                "TSLA-USD",
                "GOOGL-USD",
                "META-USD",
                "NVDA-USD",
                "JPM-USD",
                "V-USD",
                "MA-USD",
                "JNJ-USD",
                "WMT-USD",
                "PG-USD",
                "UNH-USD",
                "HD-USD",
                "SPY-USD",
                "QQQ-USD",
                "IWM-USD",
                "DIA-USD",
                "VTI-USD",
            ]

            return popular_symbols

        except Exception as e:
            from jesse.services import logger

            logger.error(f"Error getting available symbols from Alpaca: {e}")
            return [
                "AAPL-USD",
                "MSFT-USD",
                "AMZN-USD",
                "TSLA-USD",
                "GOOGL-USD",
                "META-USD",
                "NVDA-USD",
                "SPY-USD",
                "QQQ-USD",
            ]
