#!/usr/bin/env python
"""Spend Check agent: "Can I afford this?"

A personalised version of codycollier/minimal-agent-core (MIT). The agent loop in
mincore.py is the original author's; the tools, data and system prompt here are new.
"""

import logging
import os

from dotenv import load_dotenv

from mincore import MinCore
from spendcheck_tools import can_i_afford, get_budget_summary, get_category_status


SYSTEM_PROMPT = """
You are Spend Check, a friendly money helper for students on a small monthly budget.
You have three tools: get_budget_summary, get_category_status and can_i_afford.
Always use a tool to get numbers. Never do the arithmetic or guess the numbers yourself.
Keep a warm, encouraging tone and never scold the user about their spending.
All amounts are in rupees. Only talk about the user's budget, or make polite conversation.
"""


def agent_loop():
    """Main loop for the agent"""
    logging.basicConfig(level=logging.INFO)

    load_dotenv(dotenv_path=".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found. Copy .env.example to .env and add your key")

    llm = MinCore(api_key=api_key, system_prompt=SYSTEM_PROMPT)

    response_id = None
    funcs = (get_budget_summary, get_category_status, can_i_afford)
    print("Spend Check: ask me things like 'Can I afford Rs 800 on food?' (Ctrl+C to quit)")
    while True:
        user_input = input("\n>>> You: ")
        response_id, response_text = llm.send_message(user_input, previous_response_id=response_id, functions=funcs)
        print("\n>>> Agent: ", response_text)


if __name__ == "__main__":
    agent_loop()
