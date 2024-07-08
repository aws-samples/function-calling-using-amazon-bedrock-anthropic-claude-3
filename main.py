from pkg.ask import generate_text
from loguru import logger
from tools.ticker import parse_and_run_get_stock_price
from tools.currency import parse_and_run_convert_currency
import argparse
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=False, help='Input text for the LLM', default="What is the current stock price of amazon stock in pounds?")
    return parser.parse_known_args()


def build_message(input_text:str) -> list[dict]:
    """
    Build the message to send to the LLM from the input test
    :param input_text: the input text to send to the LLM
    :return: a list containing containing the role, content and user input as text
    """
    return [{"role": "user", "content": [{"text": input_text}]}]


def main():
    logger.info("Starting")
    args, _ = parse_args()
    input_text = args.input
    msg = build_message(input_text)
    logger.info(f"input text: {input_text}")
    
    stop_reason: str = None
    answer: str = None

    # Run until the model end_turn
    while stop_reason != 'end_turn':
        stop_reason, tools_requested, messages = generate_text(msg)
        logger.debug(f"stop reason is {stop_reason}, continue work till final answer")
        
        # Amazon Bedrock LLM ended turn and responded the final answer
        if stop_reason == 'end_turn':
            logger.info("The question asked the LLM ended turn and this is the answer")
            answers = messages.get("content", {})
            # itterate over the returned answers from Amazon Bedrock LLM
            answers_text = [a.get('text', '\n') for a in answers]
            answer = ''.join(answers_text)
            break
        
        if stop_reason == 'tool_use':
            # find from the content returned form tools_requested the tool to use
            for content in tools_requested:
                if 'toolUse' in content:
                    tool_use_id = content.get('toolUse', {}).get('toolUseId')
                    tool_use_name = content.get('toolUse', {}).get('name')
                    tool_use_input = content.get('toolUse', {}).get('input')
                    logger.info(f"tool use id is {tool_use_id}, tool use name is {tool_use_name}")
                    # stock price tool
                    if tool_use_name == 'get_stock_price':
                        message = parse_and_run_get_stock_price(tool_use_id, tool_use_input)
                        messages.append(message)
                    
                    # currency conversion tool
                    if tool_use_name == 'convert_currency':
                        message = parse_and_run_convert_currency(tool_use_id, tool_use_input)
                        messages.append(message)
                
                # See the messages appended that are being built for the LLM, this will allow the Bedrock LLM to provide the final answer.
                logger.debug(f"messages is now:\n{json.dumps(messages)}")

        else:
            # Stop reasons can be: 'end_turn'|'tool_use'|'max_tokens'|'stop_sequence'|'guardrail_intervened'|'content_filtered'
            # This code sample only covers end_turn, and tool_use, you may need to implement additional code to cover all the rest of the responses.
            logger.warning(f"llm didn't end_turn, or asked to use a tool, he asked to {stop_reason}")
            return
        
    # Printing the final reponse from the model
    logger.info(answer)
        

if __name__ == "__main__":
    main()

