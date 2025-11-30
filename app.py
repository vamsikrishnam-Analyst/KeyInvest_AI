from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os
import streamlit as st

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- PAGE SETUP ---
st.set_page_config(page_title="KeyInvest AI", page_icon="🔑", layout="centered")

# --- TITLE & HEADER ---
st.image("docs/KeyBank-logo.png", width=200)
st.markdown("<h2 style='text-align: center; color: #B30C00;'>KeyInvest AI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Your virtual KeyBank investment assistant</p>", unsafe_allow_html=True)

# --- SAMPLE DATASET ---
data = {
    "Risk Level": ["Low", "Moderate", "High"],
    "Expected Return (%)": [3.5, 6.0, 9.0],
    "Investment Option": [
        "Key Secure Bond Fund",
        "Key Balanced Growth Fund",
        "Key Aggressive Equity Portfolio"
    ]
}
df = pd.DataFrame(data)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# ---------------------------------------------------------
# --- CHAT DISPLAY (LEFT/RIGHT BUBBLES) ---
# ---------------------------------------------------------
chat_container = st.container()
with chat_container:
    for msg in st.session_state["messages"]:

        # USER BUBBLE (RIGHT SIDE)
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style='display:flex; justify-content:flex-end; margin:8px 0;'>
                    <div style='background-color:#e8e8e8; padding:10px 14px; border-radius:12px;
                                max-width:70%; text-align:left; box-shadow:0 1px 2px rgba(0,0,0,0.12);'>
                        <b><span style='color:#B30C00;'>🔑 You:</span></b> {msg['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # BOT BUBBLE (LEFT SIDE)
        else:
            st.markdown(
                f"""
                <div style='display:flex; justify-content:flex-start; margin:8px 0;'>
                    <div style='background-color:#ffffff; padding:10px 14px; border-radius:12px;
                                border:1px solid #ddd; max-width:70%; text-align:left;
                                box-shadow:0 1px 2px rgba(0,0,0,0.08);'>
                        <b><span style='color:#B30C00;'>🔑 KeyInvest AI:</span></b> {msg['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# --- WELCOME MESSAGE ---
if not st.session_state["messages"]:
    st.markdown(
        "<p style='color:black;'>💬 Welcome! Ask me anything about KeyBank’s investment options — for example, ‘What’s a low-risk plan?’</p>",
        unsafe_allow_html=True
    )

# --- USER INPUT ---
user_input = st.chat_input("Type your question below:")

# ---------------------------------------------------------
# --- CHAT LOGIC ---
# ---------------------------------------------------------
if user_input:

    st.session_state["messages"].append({"role": "user", "content": user_input})

    context = df.to_string(index=False)

    prompt = f"""
    You are KeyInvest AI, a friendly financial assistant for KeyBank customers.
    Use this dataset to suggest suitable KeyBank investment options.
    Include approximate expected returns:
      - Low: ~3–4% annually
      - Moderate: ~5–7% annually
      - High: ~8–10% annually
    Keep answers short (3–5 lines), clear, and natural.

    Dataset:
    {context}

    Customer Question: {user_input}
    """

    with st.spinner("Analyzing investment options..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are KeyInvest AI, a helpful KeyBank investment advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=250
            )

            answer = response.choices[0].message.content.strip()
            answer += "\n\n🔗 [Visit KeyBank Investments](https://www.key.com/personal/financial-wellness/investing-retirement.html?page=2)"

            st.session_state["messages"].append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"⚠️ Something went wrong: {e}")

    st.rerun()


# ---------------------------------------------------------
# --- FOOTER WITH PERFECT ALIGNMENT ---
# ---------------------------------------------------------

# EXACT LINK WITH TIGHT SPACING ABOVE
st.markdown(
    "<div style='text-align:center; margin-top:10px;'>"
    "<a href='https://www.key.com/personal/financial-wellness/investing-retirement.html?page=2' "
    "target='_blank' style='color:#B30C00;'>Visit KeyBank Investments</a>"
    "</div>",
    unsafe_allow_html=True
)

# RESTART BUTTON RIGHT BELOW THE LINK (NO EXTRA SPACE)
if st.session_state["messages"]:
    st.markdown(
        """
        <div style='display:flex; justify-content:center; margin-top:6px; margin-bottom:8px;'>
            <button onclick="window.location.reload();" 
                style="
                    background-color:white; 
                    border:1px solid #cccccc; 
                    padding:6px 16px; 
                    border-radius:6px; 
                    font-size:14px; 
                    cursor:pointer;">
                🔄 Restart Conversation
            </button>
        </div>
        """,
        unsafe_allow_html=True
    )

# FOOTER SIGNATURE
st.caption("Built by Vamsi Krishna Mulinti • Powered by OpenAI • Prototype for KeyBank AI")
