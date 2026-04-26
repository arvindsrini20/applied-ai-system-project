import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score
from ai_coach import get_coaching_hint

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIXME: Logic breaks here — initializing attempts to 1 instead of 0 causes the
# display (attempt_limit - attempts) to start one short and never reach 0.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0  # FIX: Corrected initial value from 1 to 0 using Claude Code; off-by-one caused the attempt counter to start short.

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "current_low" not in st.session_state:
    st.session_state.current_low = low
if "current_high" not in st.session_state:
    st.session_state.current_high = high

st.subheader("Make a guess")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIXME: Logic breaks here — placing this display before the buttons means
# `submit` is unknown and `attempts` hasn't been incremented yet, so the
# counter always shows a stale value (1 instead of 0 on the final guess).
st.info(
    f"Guess a number between 1 and 100. "
    f"Attempts left: {attempt_limit - st.session_state.attempts - (1 if submit else 0)}"  # FIX: Added `- (1 if submit else 0)` with Claude Code to account for the pending increment before rerun, fixing the stale counter display.
)

if new_game:
    st.session_state.attempts = 0
    st.session_state.status = "playing"  # FIX: Added status reset with Claude Code; without it, post-win/loss status caused st.stop() to fire immediately and the new game never rendered.
    st.session_state.secret = random.randint(low, high)
    st.session_state.history = []
    st.session_state.current_low = low
    st.session_state.current_high = high
    st.success("New game started.")
    st.rerun()

    # FIXME: Logic breaks here - st.session_state.status is never reset to "playing",
    # so after a win/loss the status check at line 140 immediately calls st.stop()
    # and the new game is never rendered.

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        if show_hint:
            if outcome != "Win":
                ai_hint = get_coaching_hint(
                    guess=guess_int,
                    outcome=outcome,
                    history=st.session_state.history,
                    current_low=st.session_state.current_low,
                    current_high=st.session_state.current_high,
                    attempts_left=attempt_limit - st.session_state.attempts,
                )
                st.warning(ai_hint if ai_hint else message)
            else:
                st.warning(message)

        if outcome == "Too High":
            st.session_state.current_high = min(st.session_state.current_high, guess_int - 1)
        elif outcome == "Too Low":
            st.session_state.current_low = max(st.session_state.current_low, guess_int + 1)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
