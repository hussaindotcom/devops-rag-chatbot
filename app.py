import streamlit as st
from rag_chain import query_rag

st.title("DevOps Copilot")
st.write("Ask about deployment for our micro-services")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What's your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, sources = query_rag(prompt)
            st.markdown(response)
#            if sources:
#                with st.expander("Sources"):
#                    for i, doc in enumerate(sources):
#                        st.write(f"**Chunk {i+1} ({doc.metadata['service']}):**")
#                        st.markdown(doc.page_content[:500] + "...")  # Truncate for display
#
    st.session_state.messages.append({"role": "assistant", "content": response})
