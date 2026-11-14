"""Offline tests: no API key needed. The LLM is replaced by a fake that asks for one tool call."""

import json
import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))

from mincore import MinCore  # noqa: E402
from spendcheck_tools import can_i_afford, get_budget_summary, get_category_status  # noqa: E402


class TestTools(unittest.TestCase):
    def test_summary_adds_up(self):
        s = get_budget_summary()
        self.assertEqual(s["categories"]["food"]["remaining"], 600)
        self.assertEqual(s["total_remaining"], 600 + 250 + 150 + 900)

    def test_category_is_case_insensitive(self):
        self.assertEqual(get_category_status("FOOD")["remaining"], 600)

    def test_affordable(self):
        r = can_i_afford(500, "food")
        self.assertTrue(r["affordable"])
        self.assertEqual(r["remaining_after"], 100)

    def test_not_affordable(self):
        r = can_i_afford(800, "food")
        self.assertFalse(r["affordable"])
        self.assertEqual(r["remaining_after"], -200)

    def test_unknown_category_and_bad_amount(self):
        with self.assertRaises(ValueError):
            can_i_afford(100, "rent")
        with self.assertRaises(ValueError):
            can_i_afford(0, "food")


class FakeResponses:
    """First call bootstraps, second asks for a tool call, third gives the final answer"""

    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        n = len(self.calls)
        if n == 2:
            call = SimpleNamespace(name="can_i_afford", arguments=json.dumps({"amount": 800, "category": "food"}), call_id="c1")
            return SimpleNamespace(id="r2", output=[call], output_text="")
        return SimpleNamespace(id=f"r{n}", output=[], output_text="final answer" if n == 3 else "")


class TestAgentLoop(unittest.TestCase):
    def test_loop_runs_tool_and_returns_result_to_model(self):
        llm = MinCore(api_key="test-key")
        fake = FakeResponses()
        llm.client = SimpleNamespace(responses=fake)
        _, text = llm.send_message("Can I afford 800 on food?", functions=(can_i_afford,))
        self.assertEqual(text, "final answer")
        tool_output = fake.calls[2]["input"][0]
        self.assertEqual(tool_output["type"], "function_call_output")
        self.assertFalse(json.loads(tool_output["output"])["affordable"])


if __name__ == "__main__":
    unittest.main()
