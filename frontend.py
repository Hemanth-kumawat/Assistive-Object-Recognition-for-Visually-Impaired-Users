import streamlit as st
import threading
import queue
import time
import sys


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ULTRON AI",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# GLOBAL STATE
# ============================================================

if "running" not in st.session_state:
    st.session_state.running = False

if "status" not in st.session_state:
    st.session_state.status = "OFFLINE"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "bot_thread" not in st.session_state:
    st.session_state.bot_thread = None


# ============================================================
# OUTPUT QUEUE
# ============================================================

output_queue = queue.Queue()


# ============================================================
# OUTPUT CAPTURE
# ============================================================

class OutputCapturer:

    def __init__(self, output_queue):
        self.output_queue = output_queue

    def write(self, text):

        if text and text.strip():
            self.output_queue.put(text)

    def flush(self):
        pass


# ============================================================
# ULTRON COMMAND PROCESSOR
# ============================================================

def process_command(user_text):

    import gemini

    if not user_text:
        return None

    # Add user message
    output_queue.put(
        f"USER|{user_text}"
    )

    try:

        response = gemini.ask_gemini(user_text)

        if response:

            output_queue.put(
                f"ULTRON|{response}"
            )

            return response

        return "I did not receive a response."

    except Exception as error:

        print(f"Gemini error: {error}")

        response = (
            "I'm having trouble connecting "
            "to my AI system."
        )

        output_queue.put(
            f"ULTRON|{response}"
        )

        return response


# ============================================================
# RUN ULTRON
# ============================================================

def run_ultron():

    import speech

    try:

        output_queue.put(
            "SYSTEM|Initializing ULTRON..."
        )

        audio = speech.create_audio_core()

        output_queue.put(
            "SYSTEM|Voice system initialized."
        )

        output_queue.put(
            "STATUS|LISTENING"
        )

        audio.speak(
            "Hello. I am Ultron. "
            "I am online and ready to assist you."
        )

        audio.start_listening(
            process_command
        )

        output_queue.put(
            "STATUS|OFFLINE"
        )

    except Exception as error:

        output_queue.put(
            f"SYSTEM|ERROR: {error}"
        )

        output_queue.put(
            "STATUS|ERROR"
        )


# ============================================================
# START ULTRON
# ============================================================

def start_ultron():

    if st.session_state.running:
        return

    st.session_state.running = True
    st.session_state.status = "STARTING"

    thread = threading.Thread(
        target=run_ultron,
        daemon=True
    )

    st.session_state.bot_thread = thread

    thread.start()


# ============================================================
# STOP ULTRON
# ============================================================

def stop_ultron():

    st.session_state.running = False
    st.session_state.status = "OFFLINE"

    output_queue.put(
        "STATUS|OFFLINE"
    )

    try:

        import speech

        # Stop current AudioCore if available
        if hasattr(speech, "audio_core"):
            speech.audio_core.stop()

    except Exception:
        pass


# ============================================================
# PROCESS QUEUE
# ============================================================

def process_queue():

    while True:

        try:

            message = output_queue.get_nowait()

        except queue.Empty:

            break

        if "|" not in message:
            continue

        message_type, message_text = message.split(
            "|",
            1
        )

        if message_type == "STATUS":

            st.session_state.status = (
                message_text
            )

        elif message_type == "USER":

            st.session_state.messages.append(
                {
                    "type": "user",
                    "text": message_text
                }
            )

        elif message_type == "ULTRON":

            st.session_state.messages.append(
                {
                    "type": "ultron",
                    "text": message_text
                }
            )

        elif message_type == "SYSTEM":

            st.session_state.messages.append(
                {
                    "type": "system",
                    "text": message_text
                }
            )


# ============================================================
# UPDATE QUEUE
# ============================================================

process_queue()


# ============================================================
# FUTURISTIC UI
# ============================================================

st.markdown(
    """
    <style>

    /* ------------------------------------------------
       GLOBAL
    ------------------------------------------------ */

    .stApp {

        background:
            radial-gradient(
                circle at 50% 30%,
                #18202c 0%,
                #080b10 40%,
                #020305 100%
            );

        color: #e8edf2;
    }


    /* ------------------------------------------------
       HIDE STREAMLIT ELEMENTS
    ------------------------------------------------ */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }


    /* ------------------------------------------------
       MAIN CONTAINER
    ------------------------------------------------ */

    .block-container {

        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }


    /* ------------------------------------------------
       HEADER
    ------------------------------------------------ */

    .ultron-header {

        text-align: center;

        padding: 10px;

        margin-bottom: 20px;
    }


    .ultron-title {

        font-size: 48px;

        font-weight: 700;

        letter-spacing: 12px;

        margin: 0;

        color: #e9eef3;

        text-shadow:
            0 0 10px rgba(150, 180, 210, 0.6),
            0 0 30px rgba(80, 120, 160, 0.3);
    }


    .ultron-subtitle {

        font-size: 13px;

        letter-spacing: 5px;

        color: #8995a2;

        margin-top: 5px;
    }


    /* ------------------------------------------------
       CORE
    ------------------------------------------------ */

    .core-container {

        display: flex;

        justify-content: center;

        align-items: center;

        height: 390px;

        margin-top: 5px;
    }


    .core {

        width: 250px;

        height: 250px;

        border-radius: 50%;

        position: relative;

        display: flex;

        justify-content: center;

        align-items: center;

        background:

            radial-gradient(
                circle,
                #dce5ec 0%,
                #9daab5 5%,
                #34414d 15%,
                #121820 38%,
                #06080c 70%
            );

        box-shadow:

            0 0 20px rgba(180, 210, 235, 0.4),

            0 0 60px rgba(100, 140, 180, 0.25),

            inset 0 0 40px rgba(220, 235, 245, 0.15);

        animation: pulse 3s infinite ease-in-out;
    }


    .core::before {

        content: "";

        position: absolute;

        width: 190px;

        height: 190px;

        border-radius: 50%;

        border: 2px solid rgba(180, 205, 225, 0.35);

        box-shadow:

            0 0 20px rgba(180, 205, 225, 0.25),

            inset 0 0 20px rgba(180, 205, 225, 0.1);
    }


    .core::after {

        content: "";

        position: absolute;

        width: 120px;

        height: 120px;

        border-radius: 50%;

        border: 1px solid rgba(220, 235, 245, 0.3);

        animation: rotate 8s linear infinite;
    }


    .core-center {

        width: 75px;

        height: 75px;

        border-radius: 50%;

        background:

            radial-gradient(
                circle,
                #ffffff 0%,
                #cbd6df 15%,
                #6c7b88 40%,
                #202933 75%
            );

        box-shadow:

            0 0 20px rgba(220, 235, 245, 0.9),

            0 0 50px rgba(150, 190, 220, 0.6);

        z-index: 5;
    }


    @keyframes pulse {

        0% {
            transform: scale(1);
        }

        50% {
            transform: scale(1.04);
        }

        100% {
            transform: scale(1);
        }
    }


    @keyframes rotate {

        from {
            transform: rotate(0deg);
        }

        to {
            transform: rotate(360deg);
        }
    }


    /* ------------------------------------------------
       STATUS
    ------------------------------------------------ */

    .status-panel {

        text-align: center;

        margin-top: -20px;

        margin-bottom: 20px;
    }


    .status-label {

        font-size: 12px;

        letter-spacing: 4px;

        color: #7f8b97;
    }


    .status-value {

        font-size: 18px;

        letter-spacing: 3px;

        margin-top: 8px;

        font-weight: 600;

        color: #dce5ec;
    }


    /* ------------------------------------------------
       CHAT
    ------------------------------------------------ */

    .chat-panel {

        background:

            rgba(10, 14, 19, 0.72);

        border:

            1px solid rgba(160, 180, 200, 0.12);

        border-radius: 18px;

        padding: 20px;

        min-height: 260px;

        max-height: 400px;

        overflow-y: auto;

        box-shadow:

            0 15px 50px rgba(0, 0, 0, 0.35);
    }


    .chat-user {

        text-align: right;

        margin-bottom: 15px;

        color: #c4d0da;
    }


    .chat-ultron {

        text-align: left;

        margin-bottom: 15px;

        color: #e8edf2;
    }


    .chat-system {

        text-align: center;

        margin-bottom: 15px;

        color: #697582;

        font-size: 12px;
    }


    .chat-name {

        font-size: 10px;

        letter-spacing: 3px;

        color: #697783;

        margin-bottom: 4px;
    }


    /* ------------------------------------------------
       BUTTONS
    ------------------------------------------------ */

    div.stButton > button {

        width: 100%;

        height: 48px;

        border-radius: 12px;

        border: 1px solid rgba(180, 200, 220, 0.2);

        background: rgba(30, 38, 48, 0.8);

        color: #e5ebf0;

        font-size: 14px;

        letter-spacing: 2px;

        transition: all 0.2s ease;
    }


    div.stButton > button:hover {

        border-color: rgba(210, 225, 240, 0.5);

        background: rgba(55, 65, 78, 0.9);

        box-shadow:

            0 0 20px rgba(170, 200, 225, 0.15);
    }


    /* ------------------------------------------------
       FOOTER
    ------------------------------------------------ */

    .footer {

        text-align: center;

        color: #4e5964;

        font-size: 10px;

        letter-spacing: 3px;

        margin-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="ultron-header">

        <div class="ultron-title">
            ULTRON
        </div>

        <div class="ultron-subtitle">
            ARTIFICIAL INTELLIGENCE SYSTEM
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CORE DISPLAY
# ============================================================

st.markdown(
    """
    <div class="core-container">

        <div class="core">

            <div class="core-center"></div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STATUS
# ============================================================

status = st.session_state.status

st.markdown(
    f"""
    <div class="status-panel">

        <div class="status-label">
            SYSTEM STATUS
        </div>

        <div class="status-value">
            {status}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONTROL BUTTONS
# ============================================================

col1, col2, col3 = st.columns(
    [1, 1, 1]
)

with col1:

    if st.button(
        "▶  START ULTRON",
        disabled=st.session_state.running
    ):

        start_ultron()

        st.rerun()


with col2:

    if st.button(
        "■  STOP ULTRON",
        disabled=not st.session_state.running
    ):

        stop_ultron()

        st.rerun()


with col3:

    if st.button(
        "↻  CLEAR CHAT"
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# CONVERSATION DISPLAY
# ============================================================

st.markdown(
    "### CONVERSATION"
)


chat_html = """
<div class="chat-panel">
"""


if not st.session_state.messages:

    chat_html += """
    <div class="chat-system">
        ULTRON SYSTEM READY
    </div>
    """

else:

    for message in st.session_state.messages:

        message_type = message["type"]
        message_text = message["text"]

        if message_type == "user":

            chat_html += f"""
            <div class="chat-user">

                <div class="chat-name">
                    USER
                </div>

                {message_text}

            </div>
            """

        elif message_type == "ultron":

            chat_html += f"""
            <div class="chat-ultron">

                <div class="chat-name">
                    ULTRON
                </div>

                {message_text}

            </div>
            """

        else:

            chat_html += f"""
            <div class="chat-system">
                {message_text}
            </div>
            """


chat_html += "</div>"


st.markdown(
    chat_html,
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        ULTRON AI • VOICE INTELLIGENCE • ASSISTIVE TECHNOLOGY
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# AUTO REFRESH WHILE RUNNING
# ============================================================

if st.session_state.running:

    time.sleep(0.5)

    st.rerun()