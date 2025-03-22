import requests
import pandas as pd
from typing import Union
import arrow
import time
from jesse.modes.import_candles_mode.drivers.interface import CandleExchange
from jesse.config import config
from jesse.exceptions import InvalidConfig
from jesse.models import Candle
from jesse.enums import exchanges


class AlphaVantage(CandleExchange):
    def __init__(self) -> None:
        super().__init__(
            name=exchanges.ALPHA_VANTAGE,
            count=200,
            rate_limit_per_second=5,
            backup_exchange_class=None,
        )
        self.name = exchanges.ALPHA_VANTAGE
        self.api_key = config["exchanges"]["alpha_vantage"]["api_key"]

        if not self.api_key:
            raise InvalidConfig("Alpha Vantage API key is required")

        self.base_url = "https://www.alphavantage.co/query"

    def get_starting_time(self, symbol: str) -> int:
        """
        Returns the starting time for the given symbol. Useful for backtesting.
        """
        # Alpha Vantage doesn't have a specific API for getting the earliest time
        # Use a small request to get the earliest available time
        try:
            url = f"{self.base_url}?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Get the earliest date in the response
            time_series = data.get("Time Series (Daily)", {})
            if time_series:
                earliest_date = sorted(time_series.keys())[0]
                timestamp = arrow.get(earliest_date).int_timestamp * 1000
                return timestamp
            else:
                return None
        except Exception as e:
            raise Exception(f"Error getting starting time for {symbol}: {e}")

    def fetch(
        self, symbol: str, start_timestamp: int, timeframe: str = "1D"
    ) -> Union[list, None]:
        """
        Fetches candles from the API
        """
        start_date = arrow.get(start_timestamp / 1000).format("YYYY-MM-DD")

        # Mapping Jesse timeframes to Alpha Vantage intervals
        timeframe_map = {
            "1m": "TIME_SERIES_INTRADAY&interval=1min",
            "5m": "TIME_SERIES_INTRADAY&interval=5min",
            "15m": "TIME_SERIES_INTRADAY&interval=15min",
            "30m": "TIME_SERIES_INTRADAY&interval=30min",
            "1h": "TIME_SERIES_INTRADAY&interval=60min",
            "1D": "TIME_SERIES_DAILY",
            "1W": "TIME_SERIES_WEEKLY",
            "1M": "TIME_SERIES_MONTHLY",
        }

        if timeframe not in timeframe_map:
            raise ValueError(
                f"Timeframe {timeframe} not supported by Alpha Vantage driver"
            )

        function = timeframe_map[timeframe]

        # Build URL
        url = f"{self.base_url}?function={function}&symbol={symbol}&outputsize=full&apikey={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Check for error messages
            if "Error Message" in data:
                print(f"Alpha Vantage API error: {data['Error Message']}")
                return None

            # Determine the key for time series data based on the timeframe
            time_series_key = None
            if "INTRADAY" in function:
                interval = function.split("=")[1]
                time_series_key = f"Time Series ({interval})"
            elif function == "TIME_SERIES_DAILY":
                time_series_key = "Time Series (Daily)"
            elif function == "TIME_SERIES_WEEKLY":
                time_series_key = "Weekly Time Series"
            elif function == "TIME_SERIES_MONTHLY":
                time_series_key = "Monthly Time Series"

            if not time_series_key or time_series_key not in data:
                print(f"No data found for {symbol} with timeframe {timeframe}")
                return None

            # Parse the data into a list of candles
            time_series = data[time_series_key]
            candles = []

            for date, values in time_series.items():
                # Skip candles earlier than the start date
                if arrow.get(date).int_timestamp * 1000 < start_timestamp:
                    continue

                candle = {
                    "id": arrow.get(date).int_timestamp,
                    "exchange": self.name,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "timestamp": arrow.get(date).int_timestamp * 1000,
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": float(values["5. volume"]),
                }
                candles.append(candle)

            # Sort by timestamp in ascending order
            candles.sort(key=lambda x: x["timestamp"])

            if len(candles) == 0:
                return None

            return candles
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {symbol}: {e}")
            # Rate limit handling - Alpha Vantage allows 5 API calls per minute
            if hasattr(e, "response") and e.response and e.response.status_code == 429:
                print("Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
            return None

    def get_available_symbols(self) -> list:
        """
        Returns a list of available trading symbols in Alpha Vantage
        """
        url = f"{self.base_url}?function=LISTING_STATUS&apikey={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            # The response is a CSV file
            import csv
            from io import StringIO

            symbols = []
            csv_reader = csv.reader(StringIO(response.text))

            # Skip header row
            next(csv_reader)

            # Extract symbols from CSV
            for row in csv_reader:
                if len(row) > 0 and row[0]:  # Symbol is in the first column
                    symbols.append(row[0])

                    # Limit to first 100 symbols to avoid overwhelming the user
                    if len(symbols) >= 100:
                        break

            return symbols
        except Exception as e:
            print(f"Error getting available symbols: {e}")
            # Return a small set of common stocks if we can't get the full list
            return [
                "AAPL",
                "MSFT",
                "AMZN",
                "GOOGL",
                "META",
                "TSLA",
                "NVDA",
                "JPM",
                "V",
                "JNJ",
            ]
