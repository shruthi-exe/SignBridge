import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import math
import random
import hashlib

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="SignBridge",
    page_icon="🖐️",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "page": "HOME",
    "score": 0,
    "attempts": 0,
    "correct": 0,
    "streak": 0,
    "best_streak": 0,
    "challenge": "✋ STOP",
    "last_image_hash": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# SIGNS
# =========================================================

AI_SIGNS = {
    "✋ STOP": "Open palm with all four fingers extended.",
    "👍 YES": "Thumb pointing upward while the other fingers are curled.",
    "👎 NO": "Thumb pointing downward while the other fingers are curled.",
    "✌️ PEACE": "Index and middle fingers extended in a V shape.",
    "👈 POINTING": "Index finger extended while the other fingers are curled.",
    "👊 FIST BUMP": "All four fingers curled into a fist with the thumb across them.",
    "🤙 CALL": "Thumb and pinky extended while the other fingers are curled.",
    "🤟 LOVE": "Thumb, index finger and pinky extended.",
    "👌 OK": "Thumb and index finger form a circle.",
    "🤘 ROCK": "Index and pinky extended while the thumb stays curled.",
}

LEARN_SIGNS = [
    ("👋", "HELLO", "A friendly greeting.", "Raise an open hand and wave."),
    ("🌅", "GOOD MORNING", "A morning greeting.", "Practise the appropriate greeting sequence."),
    ("🤟", "LOVE", "A commonly recognised gesture.", "Extend your thumb, index finger and pinky."),
    ("🤙", "CALL", "Represents calling or using a phone.", "Extend your thumb and pinky."),
    ("👊", "FIST BUMP", "A friendly greeting or celebration.", "Make a closed fist."),
    ("✌️", "PEACE", "Represents peace.", "Extend your index and middle fingers in a V."),
    ("👍", "YES", "Shows agreement.", "Make a thumbs-up gesture."),
    ("👎", "NO", "Shows disagreement.", "Make a thumbs-down gesture."),
    ("👌", "OK", "Shows that something is okay.", "Touch your thumb and index finger together."),
    ("🤘", "ROCK", "A gesture associated with rock music.", "Extend your index and pinky fingers."),
    ("👈", "POINTING", "Indicates an object or direction.", "Extend your index finger."),
    ("🙏", "THANK YOU", "Expresses gratitude.", "Practise the appropriate sign-language movement."),
    ("😔", "SORRY", "Used when apologising.", "Practise the appropriate sign-language movement."),
    ("🤲", "HELP", "Used to ask for or offer assistance.", "Practise the appropriate sign-language movement."),
]

# =========================================================
# UI STYLE
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 10% 5%, rgba(139,92,246,0.20), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(6,182,212,0.14), transparent 25%),
        #080914;
    color: #f5f3ff;
}

.block-container {
    max-width: 1250px;
    padding-top: 28px;
    padding-bottom: 50px;
}

/* ---------------------------------------------------------
   HERO / BANNER
--------------------------------------------------------- */

.hero {
    padding: 32px;
    border-radius: 28px;
    background: linear-gradient(
        135deg,
        rgba(139,92,246,0.20),
        rgba(6,182,212,0.07)
    );
    border: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 24px;
}

.logo {
    font-size: 46px;
    font-weight: 900;
    letter-spacing: -2px;
}

.tagline {
    font-size: 18px;
    opacity: 0.65;
}

.small-label {
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 800;
    opacity: 0.5;
}

.card,
.sign-card,
.target,
.result,
.info-box {
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.045);
}

.card {
    padding: 25px;
    border-radius: 24px;
    min-height: 190px;
}

.card p,
.sign-card p {
    opacity: 0.65;
    line-height: 1.7;
}

.sign-card {
    padding: 28px;
    border-radius: 24px;
    margin-bottom: 18px;
    min-height: 300px;
}

.sign-emoji {
    font-size: 65px;
}

.sign-name {
    font-size: 23px;
    font-weight: 900;
}

.target {
    padding: 35px;
    border-radius: 28px;
    text-align: center;
    background: linear-gradient(
        135deg,
        rgba(139,92,246,0.18),
        rgba(6,182,212,0.07)
    );
}

.target-sign {
    font-size: 85px;
    line-height: 1.1;
    margin: 15px;
}

.result {
    padding: 35px;
    border-radius: 26px;
    text-align: center;
    margin-top: 25px;
}

.result-sign {
    font-size: 55px;
    font-weight: 900;
}

.info-box {
    padding: 24px;
    border-radius: 22px;
    line-height: 1.7;
}

.footer {
    text-align: center;
    opacity: 0.35;
    padding-top: 45px;
    font-size: 13px;
    letter-spacing: 1px;
}

/* ---------------------------------------------------------
   MOBILE RESPONSIVENESS
--------------------------------------------------------- */

@media (max-width: 768px) {

    .block-container {
        padding-left: 12px;
        padding-right: 12px;
        padding-top: 18px;
    }

    .hero {
        padding: 24px 20px;
        border-radius: 22px;
        margin-bottom: 18px;
    }

    .logo {
        font-size: 34px;
        letter-spacing: -1.5px;
    }

    .tagline {
        font-size: 15px;
    }

    .hero p {
        font-size: 14px;
        line-height: 1.55;
    }

    /* Keep the four progress metrics in one horizontal row */
    div[data-testid="stHorizontalBlock"] {
        gap: 6px;
    }

    div[data-testid="stHorizontalBlock"] > div {
        min-width: 0 !important;
    }

    div[data-testid="stMetric"] {
        padding: 4px 2px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 9px !important;
        white-space: nowrap;
    }

    div[data-testid="stMetricValue"] {
        font-size: 18px !important;
    }

    .card {
        padding: 20px;
        min-height: 160px;
    }

    .card h2 {
        font-size: 20px;
    }

    .card p {
        font-size: 14px;
    }

    .info-box {
        padding: 18px;
        font-size: 14px;
    }

    .info-box h3 {
        font-size: 17px;
    }

    .sign-card {
        padding: 22px;
    }

    .target {
        padding: 25px 15px;
    }

    .target-sign {
        font-size: 65px;
    }

    .result {
        padding: 25px 15px;
    }

    .result-sign {
        font-size: 42px;
    }

}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HAND GEOMETRY
# =========================================================

def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def angle(a, b, c):
    ba = np.array([a.x - b.x, a.y - b.y])
    bc = np.array([c.x - b.x, c.y - b.y])

    denom = np.linalg.norm(ba) * np.linalg.norm(bc)

    if denom == 0:
        return 180.0

    cosine = np.clip(
        np.dot(ba, bc) / denom,
        -1,
        1
    )

    return math.degrees(math.acos(cosine))


def finger_extended(lm, mcp, pip, tip):
    joint_angle = angle(
        lm[mcp],
        lm[pip],
        lm[tip]
    )

    tip_distance = distance(lm[tip], lm[0])
    pip_distance = distance(lm[pip], lm[0])

    return (
        joint_angle > 150
        and tip_distance > pip_distance * 1.06
    )


# =========================================================
# BETTER THUMB DETECTION
# =========================================================

def thumb_is_open(lm):

    thumb_angle = angle(
        lm[2],
        lm[3],
        lm[4]
    )

    palm_size = max(
        distance(lm[0], lm[9]),
        0.001
    )

    thumb_tip_from_palm = distance(
        lm[4],
        lm[9]
    )

    return (
        thumb_angle > 145
        and thumb_tip_from_palm > palm_size * 0.50
    )


# =========================================================
# GESTURE CLASSIFIER
# =========================================================

def classify_gesture(landmarks):

    lm = landmarks

    index = finger_extended(lm, 5, 6, 8)
    middle = finger_extended(lm, 9, 10, 12)
    ring = finger_extended(lm, 13, 14, 16)
    pinky = finger_extended(lm, 17, 18, 20)

    fingers = sum([
        index,
        middle,
        ring,
        pinky
    ])

    thumb_open = thumb_is_open(lm)

    palm_size = max(
        distance(lm[0], lm[9]),
        0.001
    )

    thumb_index_gap = distance(
        lm[4],
        lm[8]
    )

    # =====================================================
    # OK
    # =====================================================

    if (
        thumb_index_gap < palm_size * 0.32
        and middle
        and ring
        and pinky
    ):
        return "👌 OK"

    # =====================================================
    # LOVE
    # INDEX + PINKY + THUMB
    # =====================================================

    if (
        index
        and pinky
        and thumb_open
        and not middle
        and not ring
    ):
        return "🤟 LOVE"

    # =====================================================
    # ROCK
    # INDEX + PINKY
    # THUMB MUST BE CLOSED
    # =====================================================

    if (
        index
        and pinky
        and not middle
        and not ring
        and not thumb_open
    ):
        return "🤘 ROCK"

    # =====================================================
    # CALL
    # THUMB + PINKY
    # =====================================================

    if (
        thumb_open
        and pinky
        and not index
        and not middle
        and not ring
    ):
        return "🤙 CALL"

    # =====================================================
    # PEACE
    # =====================================================

    if (
        index
        and middle
        and not ring
        and not pinky
    ):
        return "✌️ PEACE"

    # =====================================================
    # POINTING
    # =====================================================

    if (
        index
        and not middle
        and not ring
        and not pinky
    ):
        return "👈 POINTING"

    # =====================================================
    # THUMBS UP / DOWN
    # =====================================================

    if (
        thumb_open
        and not index
        and not middle
        and not ring
        and not pinky
    ):

        if lm[4].y < lm[3].y - 0.025:
            return "👍 YES"

        if lm[4].y > lm[3].y + 0.025:
            return "👎 NO"

    # =====================================================
    # FIST BUMP
    # =====================================================

    if (
        fingers == 0
        and not thumb_open
    ):
        return "👊 FIST BUMP"

    # =====================================================
    # STOP
    # =====================================================

    if (
        fingers == 4
        and thumb_open
    ):
        return "✋ STOP"

    return "🖐️ UNKNOWN"


# =========================================================
# HAND DETECTION
# =========================================================

def detect_hand(image):

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    with mp.solutions.hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.60,
        min_tracking_confidence=0.60
    ) as hands:

        results = hands.process(rgb)

    return rgb, results


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

<div class="small-label">
AI • COMPUTER VISION • SIGN LANGUAGE
</div>

<div class="logo">
🖐️ SIGNBRIDGE
</div>

<div class="tagline">
Turning gestures into understanding.
</div>

<p>
Learn signs, practise with AI and build your confidence
through interactive challenges.
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# STATS
# =========================================================

accuracy = (
    st.session_state.correct /
    st.session_state.attempts *
    100
    if st.session_state.attempts > 0
    else 0
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "⭐ XP",
        st.session_state.score
    )

with c2:
    st.metric(
        "🎯 ATTEMPTS",
        st.session_state.attempts
    )

with c3:
    st.metric(
        "📊 ACCURACY",
        f"{accuracy:.0f}%"
    )

with c4:
    st.metric(
        "🔥 BEST STREAK",
        st.session_state.best_streak
    )

st.write("")

# =========================================================
# NAVIGATION
# =========================================================

st.markdown(
    """
    <div class="small-label" style="text-align:center;">
    EXPLORE SIGNBRIDGE
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

nav1, nav2, nav3 = st.columns(3)

with nav1:
    if st.button(
        "🏠 HOME",
        use_container_width=True
    ):
        st.session_state.page = "HOME"
        st.rerun()

with nav2:
    if st.button(
        "📚 LEARN",
        use_container_width=True
    ):
        st.session_state.page = "LEARN"
        st.rerun()

with nav3:
    if st.button(
        "🎯 PRACTICE",
        use_container_width=True
    ):
        st.session_state.page = "PRACTICE"
        st.rerun()

st.write("")

# =========================================================
# HOME
# =========================================================

if st.session_state.page == "HOME":

    # =====================================================
    # WELCOME FIRST
    # =====================================================

    st.header("Welcome to SignBridge 👋")

    st.write(
        "An interactive AI-powered platform for learning "
        "and practising basic gestures."
    )

    st.write("")

    # =====================================================
    # SIGNBRIDGE INTRO
    # =====================================================

    st.markdown("""
    <div class="hero">

    <div class="small-label">
    AI • COMPUTER VISION • SIGN LANGUAGE
    </div>

    <h2>
    🖐️ SIGNBRIDGE
    </h2>

    <div class="tagline">
    Turning gestures into understanding.
    </div>

    <p>
    Learn signs, practise with AI and build your confidence
    through interactive challenges.
    </p>

    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # =====================================================
    # HOME PROGRESS STATS
    # =====================================================

    st.header("🏆 Your Progress")

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.metric(
            "⭐ XP",
            st.session_state.score
        )

    with p2:
        st.metric(
            "🎯 TARGET",
            st.session_state.attempts
        )

    with p3:
        st.metric(
            "📊 ACCURACY",
            f"{accuracy:.0f}%"
        )

    with p4:
        st.metric(
            "🔥 BEST STREAK",
            st.session_state.best_streak
        )

    st.write("")

    # =====================================================
    # THREE MAIN CARDS
    # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">

        <div class="small-label">
        01 • LEARN
        </div>

        <h2>
        📚 Sign Academy
        </h2>

        <p>
        Explore useful signs with meanings,
        instructions and practice tips.
        </p>

        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">

        <div class="small-label">
        02 • AI
        </div>

        <h2>
        🤖 Gesture Vision
        </h2>

        <p>
        MediaPipe tracks hand landmarks to
        analyse supported gestures.
        </p>

        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">

        <div class="small-label">
        03 • PROGRESS
        </div>

        <h2>
        🏆 Level Up
        </h2>

        <p>
        Earn XP, build streaks and improve
        your recognition accuracy.
        </p>

        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # =====================================================
    # HOW SIGNBRIDGE WORKS
    # =====================================================

    st.header("🧠 How SignBridge Works")

    a, b, c = st.columns(3)

    with a:
        st.markdown("""
        <div class="info-box">

        <div class="small-label">
        STEP 01
        </div>

        <h3>📷 CAPTURE</h3>

        <p>
        Your camera captures the hand gesture clearly
        so SignBridge can begin analysing it.
        </p>

        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown("""
        <div class="info-box">

        <div class="small-label">
        STEP 02
        </div>

        <h3>🔬 TRACK</h3>

        <p>
        MediaPipe tracks 21 hand landmarks and
        maps the position of each point.
        </p>

        </div>
        """, unsafe_allow_html=True)

    with c:
        st.markdown("""
        <div class="info-box">

        <div class="small-label">
        STEP 03
        </div>

        <h3>🤖 RECOGNISE</h3>

        <p>
        Landmark positions are analysed using
        classification rules to identify the gesture.
        </p>

        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # =====================================================
    # PROGRESS
    # =====================================================

    st.header("📈 Progress Level")

    st.progress(
        min(st.session_state.score / 100, 1.0)
    )

    if st.session_state.score < 20:
        st.write(
            "🌱 **FIRST STEPS** — Start practising!"
        )

    elif st.session_state.score < 50:
        st.write(
            "🥉 **SIGN STARTER** — You're improving!"
        )

    elif st.session_state.score < 100:
        st.write(
            "🥈 **SIGN EXPLORER** — Keep going!"
        )

    else:
        st.write(
            "🏆 **SIGN MASTER** — Achievement unlocked!"
        )

    st.write("")

    # =====================================================
    # FEATURED SIGN
    # =====================================================

    st.markdown("""
    <div class="hero">

    <div class="small-label">
    ✨ FEATURED SIGN
    </div>

    <h2>
    🤟 LOVE
    </h2>

    <p>
    Head to Practice Arena and try it with the AI.
    </p>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# LEARN
# =========================================================

elif st.session_state.page == "LEARN":

    st.header("📚 Sign Academy")

    st.write(
        "Learn the meaning, hand position and practice tips "
        "before testing yourself."
    )

    st.write("")

    search = st.text_input(
        "🔎 SEARCH SIGNS",
        placeholder="Search for love, help, morning..."
    )

    if search.strip():

        query = search.lower()

        signs = [
            sign
            for sign in LEARN_SIGNS
            if query in sign[1].lower()
            or query in sign[2].lower()
        ]

    else:

        signs = LEARN_SIGNS

    if not signs:

        st.warning(
            "🔎 No signs found. Try another search."
        )

    else:

        for i in range(0, len(signs), 2):

            col1, col2 = st.columns(2)

            for col, idx in [
                (col1, i),
                (col2, i + 1)
            ]:

                if idx >= len(signs):
                    continue

                emoji, name, meaning, how = signs[idx]

                with col:

                    st.markdown(
                        f"""
                        <div class="sign-card">

                        <div class="sign-emoji">
                        {emoji}
                        </div>

                        <div class="sign-name">
                        {name}
                        </div>

                        <br>

                        <div class="small-label">
                        MEANING
                        </div>

                        <p>
                        {meaning}
                        </p>

                        <div class="small-label">
                        HOW TO PRACTISE
                        </div>

                        <p>
                        {how}
                        </p>

                        <div class="small-label">
                        💡 PRACTICE TIP
                        </div>

                        <p>
                        Keep the movement clear and controlled.
                        </p>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    st.write("")

    st.markdown("""
    <div class="hero">

    <div class="small-label">
    🧠 LEARNING FORMULA
    </div>

    <h2>
    Shape → Position → Movement → Practice
    </h2>

    <p>
    First understand the handshape. Then observe
    the position and movement. Finally practise it yourself.
    </p>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PRACTICE
# =========================================================

elif st.session_state.page == "PRACTICE":

    st.header("🎯 Practice Arena")

    st.write(
        "Test your gesture recognition skills."
    )

    st.write("")

    control1, control2 = st.columns(2)

    with control1:

        if st.button(
            "🎲 NEW RANDOM CHALLENGE",
            use_container_width=True
        ):

            choices = [
                sign
                for sign in AI_SIGNS.keys()
                if sign != st.session_state.challenge
            ]

            st.session_state.challenge = random.choice(
                choices
            )

            st.session_state.last_image_hash = None

            st.rerun()

    with control2:

        selected = st.selectbox(
            "CHOOSE YOUR SIGN",
            list(AI_SIGNS.keys()),
            index=list(AI_SIGNS.keys()).index(
                st.session_state.challenge
            )
        )

        if selected != st.session_state.challenge:

            st.session_state.challenge = selected
            st.session_state.last_image_hash = None

    st.write("")

    target = st.session_state.challenge

    st.markdown(
        f"""
        <div class="target">

        <div class="small-label">
        🎯 CURRENT CHALLENGE
        </div>

        <div class="target-sign">
        {target}
        </div>

        <p>
        Show the target gesture clearly to the camera.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    st.info(
        f"💡 **Tip:** {AI_SIGNS[target]}"
    )

    st.write("")

    camera = st.camera_input(
        "📷 SHOW YOUR GESTURE"
    )

    if camera:

        image_bytes = camera.getvalue()

        image_hash = hashlib.sha256(
            image_bytes
        ).hexdigest()

        image_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:

            st.error(
                "❌ Could not read the image."
            )

        else:

            image_rgb, results = detect_hand(image)

            if results.multi_hand_landmarks:

                hand = results.multi_hand_landmarks[0]

                detected = classify_gesture(
                    hand.landmark
                )

                annotated = image_rgb.copy()

                mp.solutions.drawing_utils.draw_landmarks(
                    annotated,
                    hand,
                    mp.solutions.hands.HAND_CONNECTIONS
                )

                # Only score a newly captured image once
                if image_hash != st.session_state.last_image_hash:

                    st.session_state.last_image_hash = image_hash

                    st.session_state.attempts += 1

                    if detected == target:

                        st.session_state.correct += 1
                        st.session_state.score += 10
                        st.session_state.streak += 1

                        st.session_state.best_streak = max(
                            st.session_state.best_streak,
                            st.session_state.streak
                        )

                        st.success(
                            "🎉 PERFECT MATCH! +10 XP"
                        )

                        if st.session_state.streak >= 3:

                            st.success(
                                f"🔥 {st.session_state.streak} SIGN STREAK!"
                            )

                        if st.session_state.score >= 100:

                            st.balloons()

                            st.success(
                                "🏆 SIGN MASTER ACHIEVEMENT UNLOCKED!"
                            )

                    else:

                        st.session_state.streak = 0

                st.divider()

                st.markdown(
                    f"""
                    <div class="result">

                    <div class="small-label">
                    AI DETECTION RESULT
                    </div>

                    <div class="result-sign">
                    {detected}
                    </div>

                    <p>
                    ✓ Hand detected<br>
                    ✓ 21 landmarks analysed<br>
                    ✓ Gesture classified
                    </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if detected != target:

                    st.info(
                        f"Almost! I detected **{detected}**, "
                        f"but the target was **{target}**."
                    )

                if detected == "🖐️ UNKNOWN":

                    st.warning(
                        "Try better lighting, keep your hand "
                        "inside the frame and spread your fingers "
                        "clearly."
                    )

                st.write("")

                st.header("🔬 AI Hand Map")

                st.image(
                    annotated,
                    caption="MediaPipe 21-point hand landmark map",
                    use_container_width=True
                )

                st.write("")

                current_accuracy = (
                    st.session_state.correct /
                    st.session_state.attempts *
                    100
                    if st.session_state.attempts
                    else 0
                )

                st.header("📊 Your Progress")

                st.progress(
                    min(
                        st.session_state.score / 100,
                        1.0
                    )
                )

                p1, p2, p3 = st.columns(3)

                with p1:
                    st.metric(
                        "⭐ XP",
                        st.session_state.score
                    )

                with p2:
                    st.metric(
                        "📈 Accuracy",
                        f"{current_accuracy:.0f}%"
                    )

                with p3:
                    st.metric(
                        "🔥 Streak",
                        st.session_state.streak
                    )

            else:

                st.warning(
                    "🖐️ No hand detected. Place your hand "
                    "clearly inside the camera frame and try again."
                )

    else:

        st.markdown("""
        <div class="info-box">

        <h3>
        📷 Ready?
        </h3>

        <p>
        1. Choose a target sign.<br>
        2. Open the camera.<br>
        3. Show your gesture clearly.<br>
        4. Capture the image.<br>
        5. SignBridge analyses your hand landmarks.
        </p>

        </div>
        """, unsafe_allow_html=True)

# =========================================================
# RESET
# =========================================================

st.divider()

if st.button(
    "🔄 RESET ALL PROGRESS",
    use_container_width=True
):

    for key, value in DEFAULTS.items():
        st.session_state[key] = value

    st.rerun()

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

SIGNBRIDGE
<br>
PYTHON • STREAMLIT • OPENCV • MEDIAPIPE
<br><br>
Turning gestures into understanding 🖐️

</div>
""", unsafe_allow_html=True)
