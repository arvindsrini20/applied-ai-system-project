# Model Card: AI-Powered Number Guessing Coach

## AI Collaboration

**Helpful suggestion:**
Claude suggested storing the narrowed range in session state (`current_low`/`current_high`) and updating it after each guess, rather than passing the original difficulty range every time. That single change is what made the coach actually useful — before it, the Plan step had no accumulated knowledge to work with, just the current guess and the full original range.

**Flawed suggestion:**
Claude's first version of the coach was built around the Anthropic API, which required a paid API key I didn't have. The whole design had to be rebuilt from scratch as a rule-based system. It also left in a `with st.spinner("Coach is thinking...")` block that made sense for an API call but just flashed for a millisecond in the rule-based version and looked like a bug. I had to catch and remove it — same lesson as before: accept AI suggestions as a starting point, not a finished answer.

---

## Biases and Limitations

The coach's advice assumes optimal binary-search play — it always suggests the midpoint of the remaining range. This is mathematically correct but might feel robotic. A human coach might consider the psychological tendency to guess round numbers and account for that. The system also has no memory across games; it cannot learn that a particular player tends to guess too high and adjust accordingly.

The coach's quality also depends on accumulated range data. On the first guess with no history, the hint is generic. The model has no way to reason about player intent or strategy — only the numbers it has been given.

---

## Testing Results

**Automated tests:** 5 out of 5 pytest tests pass. Tests cover win detection, Too High, and Too Low outcomes for `check_guess`. A pre-existing bug was found and fixed — the original tests compared `check_guess` output against a plain string, but the function returns a `(outcome, message)` tuple. Tests were updated to unpack correctly.

**Logging:** Every step of the agentic loop (plan, act, check, errors) is recorded in `game_log.jsonl` with timestamps, inputs, and outputs. This makes every decision the agent made traceable after the fact.

**Check step (self-verification):** The `_check` function scans the generated hint for directional keywords consistent with the outcome. During development this caught edge cases where the Act step produced an ambiguous message that didn't clearly tell the player which direction to move.

**What didn't work initially:** The first version computed the narrowed range only from the current guess, without carrying forward previous guesses. Hints after guess 5 were no better than after guess 1. Adding `current_low`/`current_high` to session state fixed this.

**What surprised me:** The biggest surprise was how useless the hints were before accumulated range tracking was added. In the first version, the coach said something like "the number must be between 1 and 100" on guess 6 — the same thing it said on guess 1. Once session state was tracking the narrowed range, the hints became specific and genuinely useful within a few guesses.
