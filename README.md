# AI Support Agent

An end-to-end AI support agent: answers customer questions using RAG, takes real actions
via agent tools, is fine-tuned on domain data, and is deployed with CI/CD and production
monitoring. Built incrementally — each step is verified working before the next is added.

## Architecture (target end state)

```text
                    CUSTOMER
                       │
                       ▼
                 ┌───────────┐
                 │ Streamlit │
                 │ Frontend  │
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │  FastAPI  │
                 │   API     │
                 └─────┬─────┘
                       │
                       ▼
                 ┌────────────┐
                 │  Agent     │
                 │ LangGraph  │
                 └─────┬──────┘
                       │
            ┌──────────┼───────────┐
            ▼          ▼           ▼
           RAG       Tools        LLM
            │          │
            ▼          ▼
        Knowledge   MySQL
         Base

                    ADMIN
                       │
                       ▼
                 ┌────────────┐
                 │   Admin    │
                 │   Panel    │
                 └─────┬──────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  Ticket overview  Knowledge base  System health
                    manager        (drift, latency,
                                    fine-tune compare)
```

## Status

🔄 Step 3 — Database + ticket model (in progress, verifying MySQL round-trip)

## Roadmap

- [X] Step 1 — Project skeleton
- [X] Step 2 — Minimal chatbot backend (FastAPI running, `/` and `/health` verified)
- [ ] Step 3 — Database + ticket model (MySQL + SQLAlchemy, ticket CRUD)
- [ ] Step 4 — Support dataset (Pandas cleaning, knowledge base prep)
- [ ] Step 5 — RAG pipeline (chunking, embeddings, FAISS, BM25, RRF, reranker)
- [ ] Step 6 — LLM integration (single base LLM wired into `/chat`)
- [ ] Step 7 — LangGraph agent + real tools (`get_ticket`, `create_ticket`,
  `update_ticket`, `search_knowledge_base`, `escalate_ticket`)
- [ ] Step 8 — Streamlit customer frontend
- [ ] Step 9 — Authentication + rate limiting
- [ ] Step 10 — Admin panel (internal — see below)
- [ ] Step 11 — Fine-tuning (QLoRA; base vs fine-tuned comparison against working baseline)
- [ ] Step 12 — Evaluation (retrieval quality, faithfulness, BERTScore, ROUGE, tool
  accuracy, end-to-end success rate, latency)
- [ ] Step 13 — Docker + CI/CD (GitHub Actions)
- [ ] Step 14 — Monitoring (Evidently AI — feeds back into the admin panel)
- [ ] Step 15 — Deployment (cloud host, public URL)

### Step 10 — Admin panel (internal, operator-facing)

A separate, password-protected page (not exposed to customers) where the system operator
manages and observes the agent:

| Section                                             | Pulls from                         |
| --------------------------------------------------- | ---------------------------------- |
| Ticket overview (filter by status/priority)         | Step 3 —`Ticket` model          |
| Knowledge base manager (upload/view/delete docs)    | Step 5 — RAG documents            |
| Agent activity log (answered vs escalated)          | Step 7 — LangGraph agent          |
| System health (drift, latency, error rate)          | Step 14 — Evidently AI monitoring |
| Fine-tuning comparison (base vs fine-tuned metrics) | Step 11/12                         |

Starts as a simple shared-password-protected Streamlit page; not full role-based auth,
since that's disproportionate effort for an internal single-operator panel.

## Local development

Environment is managed with `uv` (not pip/venv directly).

```powershell
uv sync
uv run uvicorn app.main:app --reload
```

Visit:

- `http://127.0.0.1:8000` — root check
- `http://127.0.0.1:8000/docs` — interactive API docs
- `http://127.0.0.1:8000/health` — health check

### Database (MySQL)

Create the database once in MySQL Workbench:

```sql
CREATE DATABASE ai_support_agent;
```

Set the connection string as an environment variable before running the app:

```powershell
$env:DATABASE_URL = "mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/ai_support_agent"
```

## Project structure

```
ai-support-agent/
├── app/
│   ├── main.py           # FastAPI app entrypoint
│   ├── database.py        # SQLAlchemy engine/session setup
│   ├── models/            # SQLAlchemy models (Ticket, ...)
│   ├── schemas/            # Pydantic request/response schemas
│   └── routers/            # API route modules
├── frontend/               # Streamlit UI (customer-facing + admin panel)
├── data/                    # datasets (raw/processed, gitignored)
├── tests/                    # pytest tests
└── .github/                   # CI/CD workflows
```

## Tech stack (introduced incrementally, not all at once)

- **Backend**: FastAPI, Pydantic, SQLAlchemy, MySQL (via `pymysql`)
- **RAG**: LangChain, FAISS, BM25, cross-encoder reranking, HyDE
- **Agent**: LangGraph, tool-calling
- **Fine-tuning**: PyTorch, Hugging Face Transformers, PEFT (QLoRA), bitsandbytes
- **Frontend**: Streamlit (customer chat + admin panel)
- **Evaluation**: BERTScore, ROUGE, custom faithfulness/groundedness scoring
- **Deployment**: Docker, GitHub Actions, free-tier cloud host (Render/Railway/Fly.io/HF Spaces)
- **Monitoring**: Evidently AI

## Why this project

Demonstrates the full AI product lifecycle in one coherent system: data preparation,
retrieval-augmented generation, agentic tool use, model fine-tuning with measured
before/after comparison, production deployment, CI/CD, and live monitoring — rather than
a single isolated notebook or demo.
