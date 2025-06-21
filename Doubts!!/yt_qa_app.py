import streamlit as st
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ytrag import get_transcript, split_transcript, build_vector_store, get_retriever, build_prompt
from langchain_google_genai import ChatGoogleGenerativeAI

def extract_video_id(url):
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

st.title("YouTube Video Question Answering")

yt_url = st.text_input("Enter YouTube Video URL:")

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "video_id" not in st.session_state:
    st.session_state.video_id = None

if yt_url:
    video_id = extract_video_id(yt_url)
    if not video_id:
        st.error("Invalid YouTube URL.")
    else:
        gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_api_key or gemini_api_key.strip() == "":
            st.error("Please set the GEMINI_API_KEY in your .env file.")
        else:
            os.environ["GOOGLE_API_KEY"] = gemini_api_key
            if st.session_state.video_id != video_id:
                try:
                    with st.spinner("Processing video transcript..."):
                        transcript = get_transcript(video_id)
                        if not transcript:
                            st.error("No captions available for this video.")
                            st.session_state.vector_store = None
                            st.session_state.retriever = None
                        else:
                            chunks = split_transcript(transcript)
                            vector_store = build_vector_store(chunks)
                            retriever = get_retriever(vector_store)
                            st.session_state.vector_store = vector_store
                            st.session_state.retriever = retriever
                            st.session_state.video_id = video_id
                except Exception as e:
                    st.error(f"Failed to fetch transcript. Reason: {e}")
                    st.session_state.vector_store = None
                    st.session_state.retriever = None

            if st.session_state.retriever:
                st.markdown("**Ask a question about the video:**")
                with st.form(key="qa_form", clear_on_submit=True):
                    user_q = st.text_input("Your question:", key="qa_input")
                    submit_q = st.form_submit_button("Submit")
                if submit_q and user_q:
                    prompt = build_prompt()
                    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
                    retrieved_docs = st.session_state.retriever.invoke(user_q)
                    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
                    final_prompt = prompt.invoke({"context": context_text, "question": user_q})
                    with st.spinner("Answering..."):
                        answer = llm.invoke(final_prompt)
                    st.markdown("**Answer:**")
                    st.write(answer.content)
