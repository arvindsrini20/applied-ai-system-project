# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

The game looked like a standard, low-effort web game. It had settings to the left with a difficulty adjuster, the main page with the guess box, submit guess button, and new game button. There was also a checkbox for a hint. There was also a bar to show how many attempts left. 


- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

  The New Game button doesn't work
  The Higher and Lower options are mixed up
  The attempts stops you at 1 attempt left instead of 0 attempts left.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

I used Claude Code as my AI teammate throughout this project.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

**Correct suggestion — fixing the New Game button (status never reset):**
Claude Code identified that after a win or loss, `st.session_state.status` was never reset to `"playing"` inside the New Game block. Because the status check (`if st.session_state.status != "playing": st.stop()`) runs before any game logic, the app would immediately halt and the new game was never rendered. The AI suggested adding `st.session_state.status = "playing"` inside the `if new_game:` block. I verified this by winning a game, clicking New Game, and confirming that a fresh round started instead of the screen staying frozen on the win message.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

**Incorrect/misleading suggestion — fixing the attempts counter display:**
When I asked about the counter showing "1 attempt left" instead of "0 attempts left," Claude Code first suggested moving the `st.info(...)` display block to after the submit logic so the incremented value would already be in session state. That advice was misleading — in Streamlit, a rerun is triggered after the button press, so rearranging the display line doesn't actually change which value is read during the current render pass. I verified this by moving the block and seeing the counter still show stale values. The correct fix turned out to be keeping the display where it was and subtracting an extra `1 if submit else 0` to compensate for the pending increment, which I confirmed by testing all the way from the maximum attempts down to 0.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

A bug was only considered fixed when it passed both layers of verification: automated pytest tests for the pure logic functions, and manual playtesting in the live Streamlit app for anything involving UI state or button behavior. Passing one without the other wasn't enough — the pytest suite can't catch Streamlit rendering issues, and manual testing alone is too easy to fool yourself.

- Describe at least one test you ran (manual or using pytest)
  and what it showed you about your code.

**pytest — verifying the hint direction fix in `check_guess`:**
In `tests/test_game_logic.py` I ran tests like `test_too_high_returns_correct_status` and `test_too_low_returns_correct_status`, which call `check_guess(80, 50)` and `check_guess(20, 50)` and assert the correct `"Too High"` / `"Too Low"` outcomes. Before the fix the hints were swapped, so these tests failed. After correcting the comparison logic in `logic_utils.py`, all five tests passed, confirming the hint direction was repaired.

**Manual Streamlit testing — verifying the New Game button and attempt counter:**
I ran the app with `streamlit run app.py`, played a game to completion (both win and loss), then clicked New Game to confirm a fresh round started instead of freezing on the end screen. I also counted down attempts on each difficulty and watched the "Attempts left" counter to confirm it reached 0 on the final guess instead of stopping at 1.

- Did AI help you design or understand any tests? How?

Yes — Claude Code pointed out that the existing pytest tests only called `check_guess` with two integer arguments, which wouldn't catch the type-mismatch bug where the app sometimes passes `secret` as a string. It suggested adding a test case like `check_guess(50, "50")` to cover that path. That helped me understand the difference between testing the happy path and testing the actual conditions the code runs under in the app.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.

Every time you clicked Submit, Streamlit re-ran the entire `app.py` script from top to bottom. The original code had `st.session_state.secret = random.randint(low, high)` without checking whether a secret already existed, so a brand new random number was generated on every single rerun. This made it impossible to win because the target kept moving.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Imagine every button click causes the entire program to restart from line one — that's a Streamlit rerun. Normally that would wipe out everything, like a whiteboard being erased. Session state is like a sticky note you put on the whiteboard before it gets erased — values stored there survive the rerun so the game can remember things like your score or the secret number between clicks.

- What change did you make that finally gave the game a stable secret number?

I wrapped the secret number generation in a guard: `if "secret" not in st.session_state:` before assigning it. This means the random number is only picked once — on the very first run — and every subsequent rerun skips that line and keeps the same secret.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

Always verify fixes at two levels: a fast automated test for the logic, and a manual run of the actual app for the UI behavior. Pytest caught the swapped hint direction instantly, but only playing the game revealed that the New Game button was still broken. Using both together meant I didn't ship a fix that only worked in one context.

- What is one thing you would do differently next time you work with AI on a coding task?

I would ask the AI to explain *why* a fix works before applying it, not just accept the suggestion and move on. When Claude Code first suggested rearranging the display block to fix the counter, I applied it without fully understanding Streamlit's render model — which wasted time. Asking "why does this fix it?" upfront would have caught the flawed reasoning immediately.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

I used to assume AI-generated code was either right or wrong in an obvious way — but this project showed it can be subtly wrong in ways that look reasonable at first glance. Now I treat AI output as a starting point that needs to be read critically and tested, not a finished answer.
