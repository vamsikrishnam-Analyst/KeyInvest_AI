from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os
import streamlit as st

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- PAGE SETUP ---
st.set_page_config(page_title="KeyInvest AI", page_icon="🗝️", layout="centered")

# --- TITLE & HEADER ---
st.image("docs/KeyBank-logo.png", width=200)  # Keep your KeyBank logo here
st.markdown("<h2 style='text-align: center; color: #B30C00;'>KeyInvest AI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Your virtual KeyBank investment assistant</p>", unsafe_allow_html=True)

# --- API SETUP ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
if "last_input" not in st.session_state:
    st.session_state["last_input"] = ""

# --- CHAT DISPLAY AREA ---
chat_container = st.container()
with chat_container:
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(
                f"<div style='background-color:#f5f5f5; padding:10px; border-radius:8px; margin-bottom:5px;'>"
                f"<b>🗝️ You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='background-color:#ffffff; padding:10px; border:1px solid #ddd; border-radius:8px; margin-bottom:5px;'>"
                f"<b>🤖 KeyInvest AI:</b> {msg['content']}</div>", unsafe_allow_html=True)

# --- WELCOME MESSAGE ---
if not st.session_state["messages"]:
    st.markdown("<p style='color:black;'>💬 Welcome! Ask me anything about KeyBank’s investment options — for example, ‘What’s a low-risk plan?’</p>", unsafe_allow_html=True)

# --- USER INPUT BOX ---
user_input = st.chat_input("Type your question below:")

# --- CHAT LOGIC ---
if user_input and st.session_state["last_input"] != user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["last_input"] = user_input

    # Build context
    context = df.to_string(index=False)
    prompt = f"""
    You are KeyInvest AI, a friendly financial assistant for KeyBank customers.
    Use this dataset to suggest suitable KeyBank investment options.
    Include approximate expected returns when relevant:
      - Low Risk: ~3–4% annual return
      - Moderate Risk: ~5–7% annual return
      - High Risk: ~8–10% annual return
    Keep the answer short (3–5 lines) and natural.

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
                max_tokens=180
            )

            answer = response.choices[0].message.content.strip()
            answer += "\n\n🔗 [Visit KeyBank Investments](https://www.key.com/personal/investments/index.jsp)"
            st.session_state["messages"].append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"⚠️ Something went wrong: {e}")

# --- FOOTER ---
st.markdown(
    "<br><a href='https://www.key.com/personal/investments/index.jsp' target='_blank' style='color:#B30C00;'>Visit KeyBank Investments</a>",
    unsafe_allow_html=True,
)
st.caption("Built by Vamsi Krishna Mulinti • Powered by OpenAI • Prototype for KeyBank AI")
