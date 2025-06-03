# doctor_chatbot.py
import streamlit as st
from openai import OpenAI

st.title("Medical Bot")

# 1) Read from Streamlit secrets
FREE_API_KEY  = st.secrets["free_api"]["key"]
FREE_API_BASE = st.secrets["free_api"]["base_url"]
DEFAULT_MODEL = st.secrets["free_api"]["default_model"]

# 2) Initialise OpenAI client against the free endpoint
client = OpenAI(
    api_key=FREE_API_KEY,
    base_url=FREE_API_BASE,
)

# 3) Session-state defaults
if "openai_model" not in st.session_state:
    st.session_state.openai_model = DEFAULT_MODEL

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4) Replay chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 5) New user input
prompt = st.chat_input("Ask your medical question…")
if not prompt:
    st.stop()

with st.chat_message("user"):
    st.markdown(prompt)
st.session_state.messages.append({"role": "user", "content": prompt})

# 6) Stream assistant reply
with st.chat_message("assistant"):
    placeholder = st.empty()
    full_response = ""
    for chunk in client.chat.completions.create(
        model=st.session_state.openai_model,
        messages=st.session_state.messages,
        stream=True,
    ):
        delta = chunk.choices[0].delta.content or ""
        full_response += delta
        placeholder.markdown(full_response + "▌")
    placeholder.markdown(full_response)

st.session_state.messages.append(
    {"role": "assistant", "content": full_response}
)
