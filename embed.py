# embed.py
import os
import uuid
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import shutil

SOURCE_FILE = "data/abdominal_clean.txt"
PERSIST_DIR = "medical_chroma"

def main():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        raw = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(raw)

    docs = [
        Document(
            page_content=c,
            metadata={"source": "mayo_abdominal_pain_causes", "id": str(uuid.uuid4())}
        )
        for c in chunks
    ]

    # Clean old DB so we know we're reading the latest
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(docs, embeddings, persist_directory=PERSIST_DIR)
    db.persist()
    print(f"✅ Chroma persisted at {PERSIST_DIR}/")

if __name__ == "__main__":
    main()
