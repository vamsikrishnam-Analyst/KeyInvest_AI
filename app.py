import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import requests
import json

# Load environment variables (in case we add API keys or other configs later)
load_dotenv()

# --- Streamlit Page Setup ---
# Setting up the page title, icon, and layout — keeping it consistent with KeyBank branding
st.set_page_config(page_title="KeyInvest AI", page_icon="🔑", layout="wide")

# --- Header Section ---
# Displaying the KeyBank logo and app title
st.image("docs/KeyBank-logo.png", width=180)
st.title("KeyInvest AI")
st.markdown("### Your personalized KeyBank investment assistant")

# --- Load Investment Dataset ---
# Path to your local dataset — make sure the CSV exists in the /data folder
data_path = "data/investment_plans.csv"

try:
    df = pd.read_csv(data_path)
except Exception as e:
    st.error(f"⚠️ Could not load dataset: {e}")
    st.stop()

# --- Sidebar Filters ---
# Simple filter to let users select investment options by risk level
st.sidebar.header("Filter Investment Options")
risk_filter = st.sidebar.selectbox("Select Risk Level", ["All"] + df["RiskLevel"].unique().tolist())

# If user chooses a specific risk level, filter the DataFrame accordingly
if risk_filter != "All":
    df = df[df["RiskLevel"] == risk_filter]

# --- Display Investment Plans ---
st.write("### Recommended Plans")
st.dataframe(df[["PlanName", "Type", "RiskLevel", "ExpectedReturn", "DurationYears", "Description"]])

st.caption("Powered by KeyBank Data • Built by Vamsi Krishna Mulinti")

# --- AI Assistant Section ---
# Main chat-style interface where users can ask questions
st.subheader("💬 Looking to Invest? Ask KeyInvest AI")
user_query = st.text_input("Ask a question about these plans (e.g., 'What’s the best low-risk option under $500?')")

# --- Connect to Ollama (Local LLM) ---
# This part sends the user’s question + dataset context to the local model (llama3)
if user_query:
    # Convert the dataframe to string so the model can understand the dataset context
    context = df.to_string(index=False)
    
    # Build a concise prompt for the model
    prompt = f"""
    You are KeyInvest AI, an investment assistant for KeyBank customers.
    Use this dataset context to answer accurately, clearly, and professionally.

    Dataset:
    {context}

    User question: {user_query}
    Answer:
    """

    # Processing phase indicator (spinner)
    with st.spinner("Analyzing investment plans..."):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )

            # Parse and display the model’s response
            data = response.json()
            answer = data.get("response", "No response received.")
            st.success(answer)

        # Catch-all in case Ollama isn’t running or connection fails
        except Exception as e:
            st.error(f"⚠️ Error connecting to Ollama: {e}")
