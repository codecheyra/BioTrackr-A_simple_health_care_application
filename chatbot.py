import streamlit as st
from openai import OpenAI

st.title("Medical Bot")

# 1) instantiate the v1 client
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],  # default so you could omit this
)

# default model
if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-3.5-turbo"

# chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# replay past messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# get new user input
prompt = st.chat_input("Ask your medical question…")
if prompt:
    # show user
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # stream assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        for chunk in client.chat.completions.create(
            model=st.session_state.openai_model,
            messages=st.session_state.messages,
            stream=True,
        ):
            # each chunk is a Pydantic model; extract the delta content
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # save assistant reply
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
