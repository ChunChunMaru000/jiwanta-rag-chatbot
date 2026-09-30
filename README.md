# Jiwanta Café Chatbot

A customer service chatbot for Jiwanta Café & Space, built with a Retrieval-Augmented Generation (RAG) pipeline in Python. Customers can ask about the menu, prices, opening hours, facilities, and policies, and get answers grounded in the café's own knowledge base.

This project started as my undergraduate thesis (Information Technology Education, UPGRIS), first built with Flowise. After Flowise reached end of service, I rebuilt it from scratch in Python.

## How it works

1. **Ingest:** the knowledge base PDF is split into sections (one chunk per menu category, so the whole category stays together), embedded with `text-embedding-3-small`, and stored in ChromaDB.
2. **Retrieve:** a customer question is embedded and the most similar chunks are fetched.
3. **Generate:** `gpt-4o-mini` answers using only the retrieved context and a system prompt.
4. **Conversation memory:** follow-up questions are rewritten into standalone questions before retrieval, so "what about the cheapest one?" still finds the right chunks.
5. **API and widget:** a FastAPI service exposes `POST /chat`, and a small vanilla JavaScript widget on the café website calls it.

## Tech stack

Python, FastAPI, OpenAI API, ChromaDB, pypdf, HTML/CSS/JavaScript

## Project structure

- `ingest.py`: builds the vector database from the PDF
- `chat.py`: the RAG pipeline (retrieval, query rewriting, answer generation)
- `api.py`: FastAPI service
- `frontend/`: the café website and chat widget
- `prompts/`: system prompt
- `data/`: knowledge base

## Run locally

1. Create a virtual environment and install dependencies:
   `python -m venv venv`, activate it, then `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your OpenAI API key.
3. Build the database: `python ingest.py`
4. Start the API: `uvicorn api:app --reload`
5. Open `frontend/index.html` (for example with VS Code Live Server) and use the chat button.

website kini juga tersedia di http://127.0.0.1:8000

## API

`POST /chat`

    {
      "pertanyaan": "What milk-based drinks are available?",
      "riwayat": []
    }

Returns `{"jawaban": "..."}`. `riwayat` is the recent conversation as a list of `{"role": "user" | "assistant", "content": "..."}` items.

## Design decisions

- Chunking by section instead of fixed size fixed a bug where the bot listed only some of the cheapest items in a category.
- Only `user` and `assistant` roles are accepted from the client, and input lengths are limited, to prevent prompt injection through the history and to control API cost.
- The server is stateless: the browser sends the recent history with each request.

## Known limitations

- Questions like "cheapest item" depend on the model reading a list correctly. Computing these in code would be more reliable.
- No automated evaluation set yet.