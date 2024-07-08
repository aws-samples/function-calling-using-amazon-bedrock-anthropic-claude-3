import yfinance as yf
from typing import Union


ticker_tool_description = {
    "toolSpec": {
        "name": "get_stock_price",
        "description": "Retrieves the current stock price for a given ticker symbol, and the currency that its being traded. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company.",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The ticker symbol of the company. e.g AAPL for Apple Inc.",
                    }
                },
                "required": ["ticker"],
            },
        },
    }
}


def parse_and_run_get_stock_price(tool_use_id, input):
    """
    Parses the given tool inputs, to pass to the tool, and return the tool result formatted for Bedrock Converse API
    :param tool_use_id: the id of the tool use
    :param input: the tool input { ticker: str }
    :return: The tool result formatted for Bedrock Converse API
    """
    ticker = input.get("ticker", {})
    if ticker:
        price, currency = get_stock_price(ticker)
        tool_result = {
            "toolUseId": tool_use_id,
            "content": [
                {
                    "json": {
                        "ticker": ticker,
                        "price": price,
                        "currency": currency,
                    }
                }
            ],
        }
        tool_result_message = {"role": "user", "content": [{"toolResult": tool_result}]}

    return tool_result_message


def get_stock_price(ticker: str) -> Union[float, str]:
    """
    Retrieves the current stock price for the given ticker symbol.
    :param ticker: The ticker symbol of the company.
    :return: A tuple containing the current stock price and the currency code.
    """    
    stock = yf.Ticker(ticker)
    info = stock.basic_info
    hist = stock.history(period="1d")
    current_price = hist["Close"].iloc[0]
    return float(current_price), info["currency"]
