from currency_converter import CurrencyConverter

# Tool description to pass the LLM to learn about which tool he may use each turn
currency_converter_tool_description = {
    "toolSpec": {
        "name": "convert_currency",
        "description": "Converts a given amount from one currency to another. The user should provide the amount, the source currency, and the target currency. The tool will return the converted amount in the target currency. It should be used when the user needs to convert one currency to another, such as when purchasing a currency pair or converting cash into a different currency.",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The amount of the source currency to be converted.",
                    },
                    "source_currency": {
                        "type": "string",
                        "description": "The currency of the amount provided. e.g USD for US Dollars.",
                    },
                    "target_currency": {
                        "type": "string",
                        "description": "The currency to convert the amount to. e.g EUR for Euros.",
                    },
                },
                "required": ["amount", "source_currency", "target_currency"],
            },
        },
    }
}


def parse_and_run_convert_currency(tool_use_id, input):
    """
    Parses the given tool inputs, to pass to the tool, and return the tool result formatted for Bedrock Converse API
    :param tool_use_id: The tool use id to uniquely identify the tool use
    :param input: The tool inputs, {amount: float, source_currency: str, target_currency: str}
    :return: The tool result formatted for Bedrock Converse API
    """
    amount = input.get("amount", {})
    source_currency = input.get("source_currency", {})
    target_currency = input.get("target_currency", {})
    converted_currency = convert_currency(amount, source_currency, target_currency)
    tool_result = {
        "toolUseId": tool_use_id,
        "content": [
            {
                "json": {
                    "converted_currency": converted_currency
                }
            }
        ]
    }
    tool_result_message = {
        "role": "user",
        "content": [{"toolResult": tool_result}],
    }
    return tool_result_message



def convert_currency(amount: float, source_currency: str, target_currency: str) -> float:
    """
    Convert the given amount from the source currency to the target currency.
    :param amount: The amount of the source currency.
    :param source_currency: The currency of the amount provided.
    :param target_currency: The currency to convert the amount to.
    :return: The converted amount in the target currency.
    """
    c = CurrencyConverter()
    converted_amount = c.convert(amount, source_currency, target_currency)
    return float(converted_amount)