import jesse.helpers as jh
from fastapi.responses import JSONResponse
from jesse.info import exchange_info, live_trading_exchanges, backtesting_exchanges


def get_exchange_supported_symbols(exchange: str) -> JSONResponse:
    """
    Returns a list of supported symbols for the given exchange
    """
    try:
        from jesse.services.db import database

        database.open_connection()

        # Just return a list of common cryptocurrencies for now
        # This could be expanded to pull actual data from exchanges
        if exchange in exchange_info:
            # Return a basic set of symbols that work with most exchanges
            symbols = [
                "BTC-USDT",
                "ETH-USDT",
                "BNB-USDT",
                "SOL-USDT",
                "XRP-USDT",
                "ADA-USDT",
                "AVAX-USDT",
                "DOT-USDT",
                "MATIC-USDT",
                "LTC-USDT",
            ]

            # Format the response as needed by the frontend
            return JSONResponse(
                {
                    "status": "success",
                    "message": f"Supported symbols for {exchange}",
                    "data": symbols,
                },
                status_code=200,
            )
        else:
            return JSONResponse(
                {"status": "error", "message": f"Exchange {exchange} is not supported"},
                status_code=400,
            )

    except Exception as e:
        # Log the error for debugging
        jh.error(f"Error in get_exchange_supported_symbols: {str(e)}")

        # Return a user-friendly error
        return JSONResponse(
            {
                "status": "error",
                "message": "An error occurred while fetching supported symbols",
                "error": str(e),
            },
            status_code=500,
        )


# from starlette.responses import JSONResponse

# from jesse.modes.import_candles_mode import CandleExchange
# from jesse.modes.import_candles_mode.drivers import drivers, driver_names
# from jesse.services.redis import sync_redis


# def get_exchange_supported_symbols(exchange: str) -> JSONResponse:
#     # first try to get from cache
#     cache_key = f'exchange-symbols:{exchange}'
#     cached_result = sync_redis.get(cache_key)
#     if cached_result is not None:
#         return JSONResponse({
#             'data': eval(cached_result)
#         }, status_code=200)

#     arr = []

#     try:
#         driver: CandleExchange = drivers[exchange]()
#     except KeyError:
#         raise ValueError(f'{exchange} is not a supported exchange. Supported exchanges are: {driver_names}')

#     try:
#         arr = driver.get_available_symbols()
#         # cache successful result for 5 minutes
#         sync_redis.setex(cache_key, 300, str(arr))
#     except Exception as e:
#         return JSONResponse({
#             'error': str(e)
#         }, status_code=500)

#     return JSONResponse({
#         'data': arr
#     }, status_code=200)
