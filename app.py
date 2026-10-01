import streamlit as st
from ultron_core import UltronCore


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="ULTRON Assistive AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS ONLY
# NO HTML DIVS
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&display=swap'
    );

    .stApp {
        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(0, 220, 255, 0.12),
                transparent 35%
            ),
            #02060b;
        color: #dffaff;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
    }

    .stButton button {
        border-radius: 10px;
        min-height: 45px;
        background: rgba(0, 150, 210, 0.12);
        border: 1px solid rgba(0, 220, 255, 0.35);
        color: #dffaff;
        font-weight: 600;
    }

    .stButton button:hover {
        border: 1px solid #00dcff;
        box-shadow: 0 0 18px rgba(0, 220, 255, 0.25);
    }

    .stTextInput input {
        background: #061019;
        border: 1px solid rgba(0, 220, 255, 0.25);
        color: white;
        border-radius: 10px;
    }

    [data-testid="stCameraInput"] {
        border: 1px solid rgba(0, 220, 255, 0.3);
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: rgba(0, 220, 255, 0.15);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "ultron" not in st.session_state:
    st.session_state.ultron = UltronCore()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_response" not in st.session_state:
    st.session_state.last_response = ""


# ============================================================
# HEADER
# ============================================================

st.title("🤖 ULTRON")

st.caption(
    "ADVANCED ASSISTIVE INTELLIGENCE  //  CONTROL CENTER"
)

st.success("● SYSTEM ONLINE")


# ============================================================
# CORE
# ============================================================

core_col, system_col = st.columns([1, 2])


with core_col:

    st.subheader("◉ ULTRON CORE")

    st.metric(
        "CORE STATUS",
        "ONLINE"
    )


with system_col:

    st.subheader("SYSTEM DIAGNOSTICS")

    status = st.session_state.ultron.get_status()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "CORE",
            "ONLINE"
        )

    with c2:
        st.metric(
            "VOICE",
            str(status.get("voice", "READY"))
        )

    with c3:
        st.metric(
            "NAVIGATION",
            str(status.get("navigation", "READY"))
        )

    with c4:
        st.metric(
            "AUDIO",
            str(status.get("navigation_voice", "READY"))
        )


# ============================================================
# MAIN
# ============================================================

st.divider()

left, right = st.columns([1.05, 1])


# ============================================================
# VOICE
# ============================================================

with left:

    st.subheader("🎤 VOICE COMMAND CENTER")

    st.caption(
        "Voice-first interaction with ULTRON"
    )

    v1, v2 = st.columns(2)

    with v1:

        if st.button(
            "🎤 ACTIVATE VOICE",
            use_container_width=True
        ):

            st.session_state.ultron.start_continuous_voice()

            st.success(
                "VOICE SYSTEM ACTIVE"
            )

    with v2:

        if st.button(
            "🔇 STOP VOICE",
            use_container_width=True
        ):

            st.session_state.ultron.stop_continuous_voice()

            st.info(
                "VOICE SYSTEM STOPPED"
            )


    st.divider()

    st.write(
        "Manual command — optional"
    )

    command = st.text_input(
        "Command",
        placeholder=(
            "hello / what do you see / "
            "navigate to JBIT"
        )
    )

    if st.button(
        "▶ EXECUTE COMMAND",
        use_container_width=True
    ):

        if command.strip():

            response = (
                st.session_state
                .ultron
                .process_text_command(
                    command
                )
            )

            st.session_state.last_response = response

            st.session_state.messages.append(
                {
                    "user": command,
                    "assistant": response
                }
            )

            st.session_state.ultron.audio.speak_async(
                response
            )

    if st.session_state.last_response:

        st.subheader(
            "ULTRON RESPONSE"
        )

        st.info(
            st.session_state.last_response
        )


# ============================================================
# VISION
# ============================================================

with right:

    st.subheader("👁️ VISION ENGINE")

    st.caption(
        "Object detection • Scene understanding • OCR"
    )

    camera_image = st.camera_input(
        "Camera"
    )

    if camera_image:

        st.image(
            camera_image,
            use_container_width=True
        )

        b1, b2 = st.columns(2)

        with b1:

            if st.button(
                "👁 DETECT OBJECTS",
                use_container_width=True
            ):

                with st.spinner(
                    "VISION PROCESSING..."
                ):

                    objects = (
                        st.session_state
                        .ultron
                        .detect_objects(
                            camera_image
                        )
                    )

                if objects:

                    st.success(
                        f"{len(objects)} object(s) detected"
                    )

                    for obj in objects:

                        name = obj.get(
                            "class",
                            "object"
                        )

                        confidence = obj.get(
                            "confidence",
                            0
                        )

                        st.write(
                            f"**{name}** — "
                            f"{confidence:.0%}"
                        )

                else:

                    st.warning(
                        "No objects detected"
                    )


        with b2:

            if st.button(
                "🌎 DESCRIBE SCENE",
                use_container_width=True
            ):

                with st.spinner(
                    "ANALYZING SCENE..."
                ):

                    description = (
                        st.session_state
                        .ultron
                        .describe_scene(
                            camera_image
                        )
                    )

                st.info(
                    description
                )

                st.session_state.ultron.audio.speak_async(
                    description
                )


        if st.button(
            "📖 READ TEXT",
            use_container_width=True
        ):

            with st.spinner(
                "OCR PROCESSING..."
            ):

                text = (
                    st.session_state
                    .ultron
                    .read_text(
                        camera_image
                    )
                )

            st.info(
                text
            )

            st.session_state.ultron.audio.speak_async(
                text
            )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

st.subheader("🧭 NAVIGATION ENGINE")

st.caption(
    "Pedestrian navigation with voice guidance"
)

n1, n2, n3 = st.columns(
    [2.5, 1, 1]
)


with n1:

    destination = st.text_input(
        "Destination",
        placeholder=(
            "JBIT / KG Reddy College"
        )
    )


with n2:

    if st.button(
        "🧭 NAVIGATE",
        use_container_width=True
    ):

        if destination.strip():

            response = (
                st.session_state
                .ultron
                .handle_navigation(
                    destination
                )
            )

            st.success(
                response
            )

            st.session_state.ultron.audio.speak_async(
                response
            )

        else:

            st.warning(
                "Enter destination"
            )


with n3:

    if st.button(
        "🛑 STOP",
        use_container_width=True
    ):

        response = (
            st.session_state
            .ultron
            .stop_navigation()
        )

        st.info(
            response
        )

        st.session_state.ultron.audio.speak_async(
            response
        )


if st.button(
    "📍 CHECK NAVIGATION STATUS"
):

    response = (
        st.session_state
        .ultron
        .navigation_status()
    )

    st.info(
        response
    )


# ============================================================
# SYSTEM CONTROLS
# ============================================================

st.divider()

st.subheader("⚙️ SYSTEM CONTROLS")

s1, s2, s3, s4 = st.columns(4)


with s1:

    if st.button(
        "🔊 SPEAKER TEST",
        use_container_width=True
    ):

        st.session_state.ultron.audio.speak_async(
            "Hello. ULTRON audio system is operational."
        )


with s2:

    if st.button(
        "🎤 VOICE TEST",
        use_container_width=True
    ):

        st.session_state.ultron.audio.speak_async(
            "Voice communication system is operational."
        )


with s3:

    if st.button(
        "🔄 REFRESH",
        use_container_width=True
    ):

        st.rerun()


with s4:

    if st.button(
        "🛑 SHUTDOWN",
        use_container_width=True
    ):

        st.session_state.ultron.shutdown()

        st.warning(
            "ULTRON CORE SHUTDOWN"
        )


# ============================================================
# HISTORY
# ============================================================

if st.session_state.messages:

    st.divider()

    st.subheader("💬 COMMAND HISTORY")

    for item in reversed(
        st.session_state.messages
    ):

        st.write(
            "YOU:",
            item["user"]
        )

        st.write(
            "ULTRON:",
            item["assistant"]
        )

        st.divider()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "ULTRON ASSISTIVE INTELLIGENCE  •  "
    "VOICE  •  VISION  •  OCR  •  NAVIGATION"
)