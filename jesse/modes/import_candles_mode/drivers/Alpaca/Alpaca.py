import requests
import jesse.helpers as jh
from jesse.modes.import_candles_mode.drivers.interface import CandleExchange
from typing import Union, List
from jesse.services.env import ENV_VALUES
from jesse.enums import exchanges
from datetime import datetime, timedelta, timezone
from .alpaca_utils import timeframe_to_interval


class Alpaca(CandleExchange):
    def __init__(self) -> None:
        super().__init__(
            name=exchanges.ALPACA,
            count=1000,
            rate_limit_per_second=5,
            backup_exchange_class=None,
        )

        self.endpoint = "https://data.alpaca.markets/v2"

        # Get API credentials from environment
        # Match the env var names with what's in the .env file
        self.api_key = ENV_VALUES.get("APCA_API_KEYID", "")
        self.api_secret = ENV_VALUES.get("APCA_API_SECRET_KEY", "")

        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
        }

    def _convert_to_unix_timestamp(self, timestamp_str: str) -> int:
        """
        Convert RFC 3339 timestamp (e.g., '2024-01-03T00:00:00Z') to Unix timestamp in milliseconds
        """

        dt = datetime.fromisoformat(timestamp_str).astimezone(timezone.utc)

        return dt.timestamp()

    def get_starting_time(self, symbol: str) -> int:
        """
        Get the timestamp of the oldest available candle for the symbol
        """
        try:
            from alpaca.data import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame

            stock_symbol = symbol.split("-")[0] if "-" in symbol else symbol

            client = StockHistoricalDataClient(
                api_key=self.api_key, secret_key=self.api_secret
            )

            far_past_date = datetime(1970, 1, 1, tzinfo=timezone.utc)

            request_params = StockBarsRequest(
                symbol_or_symbols=stock_symbol,
                timeframe=TimeFrame.Day,
                start=far_past_date,
                limit=1,
            )

            bars_df = client.get_stock_bars(request_params).df

            if bars_df.empty:
                return 0

            oldest_timestamp = bars_df.index[0][1]

            unix_timestamp = self._convert_to_unix_timestamp(oldest_timestamp)

            return unix_timestamp

        except Exception as e:
            from jesse.services import logger

            logger.error(f"Error fetching oldest candle timestamp from Alpaca: {e}")
            return 0

    def fetch(
        self, symbol: str, start_timestamp: int, timeframe: str = "1m"
    ) -> Union[list, None]:
        try:
            from alpaca.data import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest

            start_time = datetime.fromtimestamp(start_timestamp / 1000, tz=timezone.utc)

            stock_symbol = symbol.split("-")[0] if "-" in symbol else symbol

            client = StockHistoricalDataClient(
                api_key=self.api_key, secret_key=self.api_secret
            )

            interval = timeframe_to_interval(timeframe)

            request_params = StockBarsRequest(
                symbol_or_symbols=stock_symbol,
                timeframe=interval,
                start=start_time,
                # end=end_time,
                limit=self.count,
            )

            data = []

            bars_response = client.get_stock_bars(request_params)

            while True:
                if not bars_response.df.empty:
                    bars_df = bars_response.df
                    for index, row in bars_df.iterrows():
                        timestamp = int(
                            self._convert_to_unix_timestamp(str(index[1])) * 1000
                        )
                        data.append(
                            [
                                timestamp,
                                row["open"],
                                row["high"],
                                row["low"],
                                row["close"],
                                row["volume"],
                            ]
                        )
                if (
                    hasattr(bars_response, "next_page_token")
                    and bars_response.next_page_token
                ):
                    request_params.page_token = bars_response.next_page_token
                    bars_response = client.get_stock_bars(request_params)
                else:
                    break

        except Exception as e:
            from jesse.services import logger

            logger.error(f"Error fetching candles from Alpaca: {e}")
            return None

        return [
            {
                "id": jh.generate_unique_id(),
                "exchange": self.name,
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": int(d[0]),
                "open": float(d[1]),
                "close": float(d[4]),
                "high": float(d[2]),
                "low": float(d[3]),
                "volume": float(d[5]),
            }
            for d in data
        ]

    def get_available_symbols(self) -> list:
        """
        Returns a list of available symbols from Alpaca
        """

        popular_symbols = [
            "AAPL-USD",
            "AMCR-USD",
            "AMZN-USD",
            "CSCO-USD",
            "DIA-USD",
            "F-USD",
            "GOOGL-USD",
            "HD-USD",
            "INTC-USD",
            "IWM-USD",
            "JNJ-USD",
            "JPM-USD",
            "LCID-USD",
            "MA-USD",
            "META-USD",
            "MSFT-USD",
            "NIO-USD",
            "NKE-USD",
            "NU-USD",
            "NVDA-USD",
            "PFE-USD",
            "PG-USD",
            "PLTR-USD",
            "QQQ-USD",
            "SPY-USD",
            "TSLA-USD",
            "UNH-USD",
            "USB-USD",
            "V-USD",
            "VFC-USD",
            "VTI-USD",
            "VTRS-USD",
            "WMT-USD",
        ]

        return popular_symbols
