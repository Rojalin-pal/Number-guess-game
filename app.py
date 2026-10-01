import streamlit as st
import random
import time

st.set_page_config(
    page_title="Mind Guess | Number Mystery Game",
    page_icon="🧠",
    layout="centered"
)

# Custom Styling for Mind Game Aesthetic
st.markdown("""
<style>
    .main {
        background: radial-gradient(circle, #0f172a 0%, #020617 100%);
    }
    .game-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
    }
    .neon-title {
        color: #a855f7;
        text-shadow: 0 0 10px #9333ea, 0 0 20px #6366f1;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .badge-history {
        display: inline-block;
        background-color: #334155;
        color: #f8fafc;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE -----------------
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
    st.session_state.game_status = "playing"
    st.session_state.history = []
    st.session_state.feedback_msg = None

# ================= PAGE 1: WELCOME SCREEN =================
if st.session_state.page == "welcome":
    st.markdown("""
        <div class="game-card">
            <h1 class="neon-title">🧠 THE MIND GUESS</h1>
            <p style="color: #cbd5e1; font-size: 1.15rem;">Can you read the machine's mind?</p>
            <p style="color: #94a3b8; font-size: 0.95rem;">
                A secret number between <b>1 and 100</b> has been chosen.<br>
                You have <b>10 attempts</b> and exactly <b>60 seconds</b> on the clock.
            </p>
        </div>
    """, unsafe_allow_html=True)

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

# ================= PAGE 2: GAME SCREEN =================
elif st.session_state.page == "game":
    st.markdown(f"### 🎮 Player: **{st.session_state.username}**")
    
    # Timer Calculation (60 seconds)
    elapsed = int(time.time() - st.session_state.start_time)
    time_left = max(0, 60 - elapsed)

    # Check timeout condition
    if time_left == 0 and st.session_state.game_status == "playing":
        st.session_state.game_status = "lost"

    # Status Dashboard
    col_t1, col_t2 = st.columns(2)
    col_t1.metric("⏳ Time Remaining", f"{time_left}s")
    col_t2.metric("🎯 Attempts Left", f"{st.session_state.attempts_left} / 10")

    # Time Progress Bar
    st.progress(time_left / 60)

    # --- Active Game Play Form ---
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
                    st.session_state.game_status = "won"
                    st.session_state.feedback_msg = None
                    st.rerun()
                elif st.session_state.attempts_left == 0:
                    st.session_state.game_status = "lost"
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

    # --- Won State: Flowers & Celebrations ---
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
        trail_html = " ".join([f"<span class='badge-history'>{g}</span>" for g in st.session_state.history])
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