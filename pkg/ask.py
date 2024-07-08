import boto3
from tools.ticker import ticker_tool_description
from tools.currency import currency_converter_tool_description
from typing import Union


bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")

# Bedrock model selected
# See supported models:
# https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html#conversation-inference-supported-models-features
modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

# Converse API inferense parameters
kwargs = {
    "temperature": 0,
    "maxTokens": 300,
    "topP": 0,
}


system_text_promot = """you are a stock market bot, that provides accurate ticker prices at any currency.
use your tools to get stock price, and covert to another currency when asked.
"""


def generate_text(messages) -> Union[str, list[str], list[dict[str, any]]]:
    """
    Generate the Amazon Bedrock model response for a given input text, and return the response of each turn
    :param messages: list of message dicts from the user
    :return: stop reason, list of the tools requested, and the output messages from the model
    """
    
    system_prompt = [{"text": system_text_promot}]

    # Using Amazon Bedrock converse API
    # https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
    response = bedrock_client.converse(
        modelId=modelId,
        messages=messages,
        system=system_prompt,
        toolConfig={
            "tools": [ticker_tool_description, currency_converter_tool_description]
        },
        inferenceConfig=kwargs,
    )

    output_message = response.get("output", {}).get("message", {})
    stop_reason = response.get("stopReason")
    tools_requested = []
    # Only if a tools should be used, send the tool to use, and append the messages for the user and assistant to build a conversation
    if stop_reason == "tool_use":
        tools_requested = (
            response.get("output", {}).get("message", {}).get("content", {})
        )
        messages.append(output_message)
        return stop_reason, tools_requested, messages

    return stop_reason, tools_requested, output_message
