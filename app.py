import random
import time
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent

st.set_page_config(
    page_title="Mind Guess | Number Mystery Game",
    page_icon="🧠",
    layout="centered"
)

# Friendly checks so a setup problem shows a message instead of a blank page
_needed = ["styles.css", "templates/welcome.html", "templates/badge.html"]
_missing = [f for f in _needed if not (BASE / f).exists()]
if _missing:
    st.error(f"Missing files next to app.py: {', '.join(_missing)}. Keep the folder structure as sent.")
    st.stop()
if not hasattr(st, "fragment"):
    st.error(f"Streamlit {st.__version__} is too old for the live timer. Run: pip install --upgrade streamlit")
    st.stop()


def render(name, **ctx):
    """Load templates/<name>.html and fill {{placeholders}}."""
    html = (BASE / "templates" / f"{name}.html").read_text(encoding="utf-8")
    for key, value in ctx.items():
        html = html.replace("{{" + key + "}}", str(value))
    return "".join(line.strip() + " " for line in html.splitlines())


# Custom Styling for Mind Game Aesthetic (styles.css)
css = (BASE / "styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

#  SESSION STATE 
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "username" not in st.session_state:
    st.session_state.username = "Player"
if "secret_number" not in st.session_state:
    st.session_state.secret_number = random.randint(1, 100)
if "attempts_left" not in st.session_state:
    st.session_state.attempts_left = 10
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "game_status" not in st.session_state:
    st.session_state.game_status = "playing"  # playing, won, lost
if "history" not in st.session_state:
    st.session_state.history = []
if "feedback_msg" not in st.session_state:
    st.session_state.feedback_msg = None


def start_new_game():
    st.session_state.secret_number = random.randint(1, 100)
    st.session_state.attempts_left = 10
    st.session_state.start_time = time.time()
    st.session_state.end_time = None
    st.session_state.game_status = "playing"
    st.session_state.history = []
    st.session_state.feedback_msg = None


def get_elapsed():
    # Stops counting once the game has ended
    end = st.session_state.end_time or time.time()
    return int(end - st.session_state.start_time)


def get_time_left():
    return max(0, 60 - get_elapsed())


def end_game(status):
    st.session_state.game_status = status
    st.session_state.end_time = time.time()


# LIVE TIMER: this block re-runs by itself every second while playing
def timer_panel():
    time_left = get_time_left()

    # Time ran out: end the game and refresh the whole page
    if time_left == 0 and st.session_state.game_status == "playing":
        end_game("lost")
        st.rerun()

    # Status Dashboard
    col_t1, col_t2 = st.columns(2)
    col_t1.metric("⏳ Time Remaining", f"{time_left}s")
    col_t2.metric("🎯 Attempts Left", f"{st.session_state.attempts_left} / 10")

    # Time Progress Bar
    st.progress(time_left / 60)


#  PAGE 1: WELCOME SCREEN 
if st.session_state.page == "welcome":
    st.markdown(render("welcome"), unsafe_allow_html=True)

    with st.container():
        user_name_input = st.text_input("Enter your Player Nickname to begin:", placeholder="e.g. MasterMind")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Game", use_container_width=True):
                if user_name_input.strip():
                    st.session_state.username = user_name_input.strip()
                start_new_game()
                st.session_state.page = "game"
                st.rerun()

#  PAGE 2: GAME SCREEN 
elif st.session_state.page == "game":
    st.markdown(f"### 🎮 Player: **{st.session_state.username}**")

    # Check timeout condition (covers the case where the page was idle)
    if get_time_left() == 0 and st.session_state.game_status == "playing":
        end_game("lost")

    # Live countdown: ticks every second only while the game is being played
    is_playing = st.session_state.game_status == "playing"
    st.fragment(timer_panel, run_every=1 if is_playing else None)()

    elapsed = get_elapsed()
    time_left = get_time_left()

    #  Active Game Play Form 
    if st.session_state.game_status == "playing":
        with st.form("guess_form", clear_on_submit=True):
            # value=None keeps the input blank on every submission
            user_guess = st.number_input(
                "Enter your guess (1 - 100):",
                min_value=1,
                max_value=100,
                step=1,
                value=None,
                placeholder="Type a number..."
            )
            submit = st.form_submit_button("Submit Guess", use_container_width=True)

        if submit:
            if user_guess is None:
                st.session_state.feedback_msg = ("warning", "⚠️ Please enter a number before submitting!")
            else:
                st.session_state.attempts_left -= 1
                st.session_state.history.append(user_guess)

                if user_guess == st.session_state.secret_number:
                    end_game("won")
                    st.session_state.feedback_msg = None
                    st.rerun()
                elif st.session_state.attempts_left == 0:
                    end_game("lost")
                    st.session_state.feedback_msg = None
                    st.rerun()
                else:
                    if user_guess < st.session_state.secret_number:
                        st.session_state.feedback_msg = ("warning", f"📉 Too low! The mystery number is higher than **{user_guess}**.")
                    else:
                        st.session_state.feedback_msg = ("warning", f"📈 Too high! The mystery number is lower than **{user_guess}**.")
            st.rerun()

        # Display the persistent hint banner after rerun
        if st.session_state.feedback_msg:
            msg_type, msg_text = st.session_state.feedback_msg
            if msg_type == "warning":
                st.warning(msg_text)

    # Won State: 
    elif st.session_state.game_status == "won":
        st.balloons()
        st.snow()
        st.success(f"""
        ### 🌸 🌺 💐 CONGRATULATIONS, {st.session_state.username}! 💐 🌺 🌸
        **Brilliant mind!** You uncovered the secret number **{st.session_state.secret_number}**!
        * Total Guesses: **{10 - st.session_state.attempts_left}**
        * Time Taken: **{elapsed}s**
        """)

    # --- Lost State (Attempts Out or Timeout) ---
    elif st.session_state.game_status == "lost":
        if time_left == 0:
            st.error("⏰ **Time's up!** The 60-second timer ran out.")
        else:
            st.error("💀 **Game Over!** You used all 10 attempts.")
        st.info(f"The mystery number was: **{st.session_state.secret_number}**")

    # Display Guess History
    if st.session_state.history:
        st.write("##### Guess Trail:")
        trail_html = " ".join([render("badge", guess=g) for g in st.session_state.history])
        st.markdown(trail_html, unsafe_allow_html=True)

    st.write("---")

    # Bottom Actions: Play Again / Exit
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Play Again (New Game)", use_container_width=True):
            start_new_game()
            st.rerun()
    with col_btn2:
        if st.button("🏠 Exit to Menu", use_container_width=True):
            st.session_state.page = "welcome"
            st.rerun()