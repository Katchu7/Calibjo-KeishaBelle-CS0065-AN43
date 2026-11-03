"""TA 4: Knowledge Representation, Rule-Based Reasoning, and Case-Based Reasoning.

Scenario: simple indoor comfort and rainy-day advice for one room.
Run normally to enter current room facts and revise the retrieved CBR solution.
Run with --demo to reproduce the example output included in the report.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from typing import Any


# Knowledge representation: five facts, grouped into three knowledge categories.
KNOWLEDGE_CATEGORIES = {
    "ambient_conditions": ("temperature_c", "is_raining", "humidity_pct"),
    "occupancy": ("room_occupied",),
    "ventilation": ("window_open",),
}

DEFAULT_FACTS: dict[str, Any] = {
    "temperature_c": 32,
    "is_raining": True,
    "humidity_pct": 85,
    "room_occupied": True,
    "window_open": False,
}


# Rule functions return one action when their IF condition matches, else None.
def rule_hot_room(facts: dict[str, Any]) -> str | None:
    """IF the room is hot and occupied, THEN turn on the air conditioner."""
    if facts["temperature_c"] >= 30 and facts["room_occupied"]:
        return "Turn on the air conditioner"
    return None

def rule_rain(facts: dict[str, Any]) -> str | None:
    """IF it is raining, THEN bring an umbrella."""
    if facts["is_raining"]:
        return "Bring an umbrella"
    return None


def rule_humid_room(facts: dict[str, Any]) -> str | None:
    """IF humidity is high and the window is closed, THEN use a dehumidifier."""
    if facts["humidity_pct"] >= 70 and not facts["window_open"]:
        return "Use a dehumidifier"
    return None


RULES = (rule_hot_room, rule_rain, rule_humid_room)


def infer_actions(facts: dict[str, Any]) -> list[str]:
    """Inference engine: check every rule against working-memory facts."""
    actions: list[str] = []
    for rule in RULES:
        action = rule(facts)
        if action is not None:
            actions.append(action)
    return actions

# Three retained past cases. Each case maps a problem profile to a solution.
CASE_BASE: list[dict[str, Any]] = [
    {
        "id": "case_1_hot_and_rainy",
        "problem": {"hot": True, "raining": True, "humid": False},
        "solution": "Bring an umbrella and use the air conditioner",
    },
    {
        "id": "case_2_hot_and_dry",
        "problem": {"hot": True, "raining": False, "humid": False},
        "solution": "Use a fan and drink water",
    },
    {
        "id": "case_3_cool_rainy_and_humid",
        "problem": {"hot": False, "raining": True, "humid": True},
        "solution": "Bring an umbrella and use a dehumidifier",
    },
]

def problem_profile(facts: dict[str, Any]) -> dict[str, bool]:
    """Convert detailed facts to comparable case features."""
    return {
        "hot": facts["temperature_c"] >= 30,
        "raining": facts["is_raining"],
        "humid": facts["humidity_pct"] >= 70,
    }


def similarity(query: dict[str, bool], past: dict[str, bool]) -> float:
    """Return the proportion of matching Boolean features (0.0 to 1.0)."""
    matches = sum(query[key] == past[key] for key in query)
    return matches / len(query)

def retrieve_case(
    facts: dict[str, Any], cases: list[dict[str, Any]]
) -> tuple[dict[str, Any], float]:
    """Retrieve the most similar case; stable ordering resolves ties."""
    if not cases:
        raise ValueError("The case base is empty; add a past case before retrieval.")
    query = problem_profile(facts)
    best_case = max(cases, key=lambda case: similarity(query, case["problem"]))
    score = similarity(query, best_case["problem"])
    return best_case, score

def get_facts(interactive: bool) -> dict[str, Any]:
    """Read a new situation, using the documented sample as each default."""
    facts = deepcopy(DEFAULT_FACTS)
    if not interactive:
        return facts
    print("Enter current facts (press Enter to use the sample value).")
    raw = input(f"Temperature in C [{facts['temperature_c']}]: ").strip()
    if raw:
        facts["temperature_c"] = float(raw)
    raw = input(f"Is it raining? y/n [{'y' if facts['is_raining'] else 'n'}]: ").strip().lower()
    if raw:
        if raw not in {"y", "n"}:
            raise ValueError("Please enter y or n for raining.")
        facts["is_raining"] = raw == "y"
    raw = input(f"Humidity percent [{facts['humidity_pct']}]: ").strip()
    if raw:
        facts["humidity_pct"] = int(raw)
    raw = input(f"Is the room occupied? y/n [{'y' if facts['room_occupied'] else 'n'}]: ").strip().lower()
    if raw:
        if raw not in {"y", "n"}:
            raise ValueError("Please enter y or n for room occupied.")
        facts["room_occupied"] = raw == "y"
    raw = input(f"Is a window open? y/n [{'y' if facts['window_open'] else 'n'}]: ").strip().lower()
    if raw:
        if raw not in {"y", "n"}:
            raise ValueError("Please enter y or n for window open.")
        facts["window_open"] = raw == "y"
    if not 0 <= facts["humidity_pct"] <= 100:
        raise ValueError("Humidity must be between 0 and 100 percent.")
    return facts

def cbr_cycle(
    facts: dict[str, Any], cases: list[dict[str, Any]], interactive: bool
) -> tuple[str, float, dict[str, Any]]:
    """Perform Retrieve, Reuse, Revise, Retain and return the retained case."""
    selected, score = retrieve_case(facts, cases)  # Retrieve
    solution = selected["solution"]  # Reuse
    print(f"Retrieved: {selected['id']} (similarity {score:.0%})")
    print(f"Reused solution: {solution}")
    if interactive and input("Revise this solution? y/n [n]: ").strip().lower() == "y":
        revised = input("Enter the revised solution: ").strip()
        if revised:
            solution = revised  # Revise
    retained = {
        "id": f"case_{len(cases) + 1}_new_situation",
        "problem": problem_profile(facts),
        "solution": solution,
    }
    cases.append(retained)  # Retain
    print(f"Retained new case: {retained['id']}")
    return solution, score, retained

def print_knowledge_base(facts: dict[str, Any]) -> None:
    print("Knowledge Base (working memory):")
    for category, keys in KNOWLEDGE_CATEGORIES.items():
        values = ", ".join(f"{key}={facts[key]}" for key in keys)
        print(f"  {category}: {values}")
        
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="run the fixed sample without prompts")
    args = parser.parse_args()
    facts = get_facts(interactive=not args.demo)

    print("\nTA 4: KR, RBR, and CBR")
    print_knowledge_base(facts)
    print("\nRule-Based Reasoning Actions:")
    actions = infer_actions(facts)
    if actions:
        for action in actions:
            print(f"- {action}")
    else:
        print("- No rule fired; no action inferred")

    print("\nCase-Based Reasoning (4R Cycle):")
    solution, _, _ = cbr_cycle(facts, CASE_BASE, interactive=not args.demo)
    print(f"Final CBR solution: {solution}")
    print(f"Case base size after retain: {len(CASE_BASE)}")


if __name__ == "__main__":
    main()
