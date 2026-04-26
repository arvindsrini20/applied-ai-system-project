import json
import time
import logging

logging.basicConfig(
    filename="coach.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def _log(step: str, payload: dict):
    entry = {"time": time.time(), "step": step, **payload}
    with open("game_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
    logging.info(f"step={step} {payload}")


def _plan(guess: int, outcome: str, current_low: int, current_high: int) -> dict:
    """
    Step 1 — Plan: Apply the current guess outcome to narrow the search range.
    Returns a dict with the updated range and the optimal next guess (midpoint).
    """
    if outcome == "Too High":
        new_high = min(current_high, guess - 1)
        new_low = current_low
    else:
        new_low = max(current_low, guess + 1)
        new_high = current_high

    range_size = max(new_high - new_low + 1, 0)
    midpoint = (new_low + new_high) // 2
    original_size = current_high - current_low + 1
    pct_eliminated = round((1 - range_size / original_size) * 100) if original_size > 0 else 100

    return {
        "new_low": new_low,
        "new_high": new_high,
        "range_size": range_size,
        "midpoint": midpoint,
        "pct_eliminated": pct_eliminated,
    }


def _act(guess: int, outcome: str, plan: dict, attempts_left: int) -> str:
    """
    Step 2 — Act: Generate a strategic coaching hint using the plan output.
    Adapts message based on range size and urgency (attempts remaining).
    """
    new_low = plan["new_low"]
    new_high = plan["new_high"]
    range_size = plan["range_size"]
    midpoint = plan["midpoint"]
    pct_eliminated = plan["pct_eliminated"]
    label = "Too high!" if outcome == "Too High" else "Too low!"

    if range_size <= 1:
        return f"{label} Only one number left — go {'lower' if outcome == 'Too High' else 'higher'}!"

    if range_size <= 5:
        options = list(range(new_low, new_high + 1))
        return (
            f"{label} You've narrowed it to just {range_size} possibilities: {options}. "
            f"You're almost there!"
        )

    if attempts_left <= 2:
        return (
            f"{label} Running out of attempts — the number is between {new_low} and {new_high}. "
            f"Try {midpoint} now to split the remaining {range_size} options."
        )

    if attempts_left <= 4:
        return (
            f"{label} You've eliminated {pct_eliminated}% of the range. "
            f"The number is between {new_low} and {new_high} — try {midpoint} next."
        )

    return (
        f"{label} The number must be between {new_low} and {new_high} ({range_size} possibilities). "
        f"Try {midpoint} to cut the remaining range in half."
    )


def _check(hint: str, outcome: str) -> bool:
    """
    Step 3 — Check: Verify the hint is directionally consistent with the outcome.
    Returns False if the hint could mislead the player.
    """
    h = hint.lower()
    if outcome == "Too High":
        return any(w in h for w in ["high", "lower", "down", "below", "less", "smaller"])
    else:
        return any(w in h for w in ["low", "higher", "up", "above", "more", "larger"])


def get_coaching_hint(
    guess: int,
    outcome: str,
    history: list,
    current_low: int,
    current_high: int,
    attempts_left: int,
) -> str | None:
    """
    Agentic 3-step loop:
      1. Plan  — narrow the search range using the current guess outcome
      2. Act   — generate a strategic coaching hint based on the narrowed range
      3. Check — verify the hint is directionally correct; fall back if not

    Returns the hint string, or None on unexpected error (caller uses basic hint).
    """
    try:
        plan = _plan(guess, outcome, current_low, current_high)
        _log("plan", {"guess": guess, "outcome": outcome, "plan": plan})

        hint = _act(guess, outcome, plan, attempts_left)
        _log("act", {"hint": hint})

        if not _check(hint, outcome):
            fallback = (
                f"Too high — the number is lower than {guess}. Focus on the range below."
                if outcome == "Too High"
                else f"Too low — the number is higher than {guess}. Focus on the range above."
            )
            _log("check", {"valid": False, "action": "fallback", "fallback": fallback})
            return fallback

        _log("check", {"valid": True})
        return hint

    except Exception as e:
        logging.error(f"Coach error: {e}")
        _log("error", {"error": str(e)})
        return None
