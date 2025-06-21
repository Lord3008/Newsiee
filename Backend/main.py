import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re

load_dotenv()

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class QuestionRequest(BaseModel):
    questionType: str
    topic: str
    examType: str

@app.post("/generate-questions")
async def generate_questions(req: QuestionRequest):
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = (
        f"Generate 5 {req.questionType.upper()} questions for the topic '{req.topic}' "
        f"for the '{req.examType}' exam. "
        "For MCQ, provide options and the correct answer. "
        "For analytical or descriptive, provide the question and a sample answer. "
        "Respond in JSON as a list named 'questions', each item with keys: "
        "'question', 'options' (if MCQ), and 'answer'."
    )
    response = model.generate_content(prompt)
    # Try to extract JSON from the response
    match = re.search(r"\{.*\}", response.text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return {"questions": data["questions"]}
        except Exception:
            pass
    try:
        data = json.loads(response.text)
        return {"questions": data["questions"]}
    except Exception:
        return {"questions": [{"question": "Could not parse Gemini response.", "answer": ""}]}
