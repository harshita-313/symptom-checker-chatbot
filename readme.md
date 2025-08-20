# Abdominal Pain Symptom Checker Chatbot

This project is a **medical AI chatbot** designed specifically to provide **insights about abdominal pain in adults**. It combines web scraping, embeddings, vector search, and transformer-based summarization to deliver **concise, human-like medical guidance**.

---

## Project Overview

The chatbot is trained exclusively on information from the **Mayo Clinic** for the symptom **“abdominal pain in adults”**. Users interact via a **step-by-step interface** where they provide symptom details, and the bot retrieves relevant causes, conditions, and advice from its knowledge base.

Unlike rule-based systems, this chatbot uses a **transformer-based approach**, allowing it to:

- Understand **natural language queries**.
- Provide **context-aware responses**.
- Summarize **long medical texts into short, actionable insights**.

The system also handles **simple conversational queries** like greetings, ensuring a smooth and human-like interaction.

---

## Key Features

### Symptom-Focused Intelligence
- Only responds to queries about abdominal pain in adults.
- Filters out out-of-scope questions and informs the user if the symptom is unsupported.

### Semantic Search with Embeddings
- Uses **HuggingFace embeddings** (`sentence-transformers/all-MiniLM-L6-v2`) to represent text chunks.
- Stores and searches data efficiently in **ChromaDB** using a **similarity score threshold** to return the most relevant results.

### Summarized Medical Insights
- Uses **`distilbart-cnn-6-6` transformer** to summarize retrieved text into short, human-readable points.
- Highlights **possible diseases and medical conditions** with concise descriptions.
- Focuses on **educational insights**, not generic statements.

### Step-by-Step User Guidance
- 4-step interface:
  1. **User information** (age, sex)
  2. **Main symptom input**
  3. **Follow-up refinement questions** (nature, triggers, associated symptoms)
  4. **Final summarized insights**
- Step 3 dynamically generates **random question templates** to get detailed symptom descriptions.

### Red-Flag Detection
- Detects urgent symptoms like:
  - Severe or worsening pain
  - Blood in stool or vomit
  - Chest pain, high fever
  - Pregnancy
- Advises **immediate medical attention** if red-flag symptoms are detected.

---

## Technical Workflow

1. **Data Collection**
   - Scrapes Mayo Clinic’s abdominal pain page using `requests` and `BeautifulSoup`.
   - Cleans and structures text to focus on headings, paragraphs, and lists.

2. **Data Processing & Embeddings**
   - Splits raw text into chunks using `RecursiveCharacterTextSplitter`.
   - Converts chunks into embeddings with HuggingFace.
   - Stores vectors in **ChromaDB** for semantic search.

3. **Backend (FastAPI)**
   - Receives symptom queries.
   - Retrieves relevant document chunks from ChromaDB.
   - Summarizes the top results with transformer models.
   - Returns **structured, readable summaries** for frontend consumption.

4. **Frontend (ReactJS)**
   - Stepwise symptom input and refinement.
   - Displays **summarized health insights**.
   - Shows inline warnings for out-of-scope inputs.

---

## Skills & Technologies Demonstrated

- **Web scraping and text cleaning**
- **Text embeddings & semantic search**
- **Vector databases (ChromaDB)**
- **Transformer-based summarization (HuggingFace Transformers)**
- **FastAPI for backend services**
- **ReactJS for frontend interface**
- **Data pipeline orchestration**: scraping → embedding → semantic retrieval → summarization → UI

---

## Outcome

- Developed a **fine-tuned AI workflow** for a specific medical symptom.
- Demonstrated **end-to-end chatbot functionality**:
  - From raw data scraping to interactive frontend.
  - From semantic search to readable, concise summaries.
- Showcased ability to integrate **LLM embeddings, vector search, and summarization** in a production-like pipeline.
- Designed a system that can be extended to **other symptoms or domains**.

---

> ⚠️ Note: This chatbot is intended for **educational purposes only** and is **not a substitute for professional medical advice**. Users should consult healthcare professionals for serious symptoms.
