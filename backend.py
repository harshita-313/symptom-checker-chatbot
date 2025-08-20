# backend.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from transformers import pipeline

# ====== Request Models ======
class ValidateReq(BaseModel):
    mainSymptom: str

class ChatReq(BaseModel):
    mainSymptom: str
    refineAnswer: Optional[str] = ""

# ====== App & CORS ======
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

system_prompt = """
You are a medical health assistant. 
From the retrieved information, list only possible diseases or medical conditions related to the symptoms. 
Do NOT output general statements like 'abdominal pain can be mild or severe'.
For each condition:
- Name the disease clearly
- Give a short description (2–3 lines)
"""

# ====== Embeddings + Vector DB ======
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory="medical_chroma", embedding_function=embeddings)

# Use a thresholded retriever so we don't manually inspect doc.score later
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 6, "score_threshold": 0.2}
)

# ====== Lightweight Summarizer (smaller than bart-large-cnn) ======
# First call still downloads the model, but it's ~300MB instead of ~1.6GB
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")

# ====== In-scope Gate (simple keywords; you can later replace with a fine-tuned classifier) ======
ABDOMINAL_KEYWORDS = [
    "abdominal","stomach","belly","lower abdomen","upper abdomen","tummy",
    "gas","indigestion","appendix","appendicitis","bowel","intestine","abdomen","stomachache"
]

def is_abdominal(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in ABDOMINAL_KEYWORDS)

# ====== Endpoints ======
@app.post("/validate")
def validate(req: ValidateReq):
    if not is_abdominal(req.mainSymptom):
        return {"ok": False, "reply": "I'm sorry but I am trained only on abdominal pain in adults."}
    return {"ok": True}

@app.post("/chat")
def chat(req: ChatReq):
    # Guardrail: out-of-scope
    if not is_abdominal(req.mainSymptom):
        return {"reply": "I'm sorrybut I am trained only on abdominal pain in adults."}

    # Retrieve docs separately for main symptom and refined answer
    docs_main = retriever.get_relevant_documents(req.mainSymptom)
    docs_refine = retriever.get_relevant_documents(req.refineAnswer or "")
    docs = docs_main + docs_refine

    if not docs:
        return {"reply": "I'm sorry, I could not find relevant information."}

    # System prompt to enforce disease-focused output
    system_prompt = """
        You are a medical assistant.
        From the retrieved text, list only possible diseases or medical conditions related to the symptoms.
        For each condition:
        - Give the name of the disease
        - Provide a short description (2–3 lines)
        Do NOT include generic text like 'abdominal pain can be mild or severe'.
        """

    # Extract disease-focused bullet points
    bullet_points = []
    for d in docs[:5]:
        text = d.page_content.strip()
        summary = summarizer(text[:1200], max_length=80, min_length=30, do_sample=False, truncation=True)[0]["summary_text"]
        bullet_points.append(f"• {summary}")

    # Check for red-flag symptoms
    red_flags = [
        "severe", "worsening", "rigid abdomen", "blood in stool", 
        "blood in vomit", "pregnant", "chest pain", "high fever"
    ]
    urgent = any(k in (req.mainSymptom + " " + (req.refineAnswer or "")).lower() for k in red_flags)
    urgent_note = "\n\n⚠️ If symptoms are severe, worsening, or you notice red-flag signs, seek urgent medical care." if urgent else ""

    # Construct reply
    reply = (
        "Here’s what I found related to abdominal pain in adults:\n\n"
        + "\n\n".join(bullet_points)
    )

    return {"reply": reply}