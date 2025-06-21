from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate

import os

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
        return transcript
    except TranscriptsDisabled:
        return None

def split_transcript(transcript, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.create_documents([transcript])

def build_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return FAISS.from_documents(chunks, embeddings)

def get_retriever(vector_store, k=4):
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})

def build_prompt():
    return PromptTemplate(
        template="""
          You are a helpful assistant.
          Answer ONLY from the provided transcript context.
          If the context is insufficient, just say you don't know.

          {context}
          Question: {question}
        """,
        input_variables=['context', 'question']
    )

def summarize_youtube_video(video_id, question="Summarize the video"):
    transcript = get_transcript(video_id)
    if not transcript:
        return "No captions available for this video."
    chunks = split_transcript(transcript)
    vector_store = build_vector_store(chunks)
    retriever = get_retriever(vector_store)
    retrieved_docs = retriever.invoke(question)
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    prompt = build_prompt()
    final_prompt = prompt.invoke({"context": context_text, "question": question})
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
    answer = llm.invoke(final_prompt)
    return answer.content
