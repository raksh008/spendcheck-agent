"""Budget tools for the Spend Check agent.

All the maths is plain, deterministic Python. The LLM never does the arithmetic:
it only decides WHEN to call these tools and explains the result in friendly words.

The data comes from data/sample_budget.json (a student with Rs 5,000 monthly pocket money).
"""

import json
from pathlib import Path
from typing import Any, Dict


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_budget.json"


def _load() -> Dict[str, Any]:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def _find_category(data: Dict[str, Any], category: str) -> str:
    """Match a category name case-insensitively, or raise a helpful error"""
    wanted = category.strip().lower()
    for name in data["categories"]:
        if name.lower() == wanted:
            return name
    raise ValueError(f"Unknown category '{category}'. Available: {', '.join(data['categories'])}")


def get_budget_summary() -> Dict[str, Any]:
    """Return the monthly income, savings target and every category's limit, spent and remaining amount in rupees"""
    data = _load()
    categories = {}
    for name, c in data["categories"].items():
        categories[name] = {"limit": c["limit"], "spent": c["spent"], "remaining": c["limit"] - c["spent"]}
    return {
        "monthly_income": data["monthly_income"],
        "savings_target": data["savings_target"],
        "total_remaining": sum(c["remaining"] for c in categories.values()),
        "categories": categories,
    }


def get_category_status(category: str) -> Dict[str, Any]:
    """Return the limit, spent and remaining rupees for one spending category such as food, transport, fun or other"""
    data = _load()
    name = _find_category(data, category)
    c = data["categories"][name]
    return {"category": name, "limit": c["limit"], "spent": c["spent"], "remaining": c["limit"] - c["spent"]}


def can_i_afford(amount: float, category: str) -> Dict[str, Any]:
    """Check whether a purchase of the given rupee amount fits in the remaining budget of a category"""
    if amount <= 0:
        raise ValueError("Amount must be more than 0")
    data = _load()
    name = _find_category(data, category)
    c = data["categories"][name]
    remaining = c["limit"] - c["spent"]
    after = remaining - amount
    if after >= 0:
        message = f"Yes, Rs {amount:g} fits in {name}. You would have Rs {after:g} left for the rest of the month."
    else:
        message = (
            f"Rs {amount:g} is Rs {-after:g} more than the Rs {remaining:g} left in {name}. "
            "You could move money from another category or plan it for next month."
        )
    return {"affordable": after >= 0, "category": name, "amount": amount, "remaining_before": remaining, "remaining_after": after, "message": message}
