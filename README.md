# AI Maintenance & Operations Support Agent

An end-to-end AI support agent for industrial equipment maintenance and operations:
answers technician questions using RAG, takes real actions via agent tools, is
fine-tuned on domain data, and is deployed with CI/CD and production monitoring.
Built incrementally — each step is verified working before the next is added.

**Domain focus:** manufacturing / energy (industrial equipment maintenance and
troubleshooting), chosen to align with existing sensor-data and time-series
experience rather than a generic e-commerce use case.

## Architecture (target end state)

```text
                  TECHNICIAN
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
        Knowledge    MySQL
         Base      (equipment,
       (manuals,     tickets)
      procedures)

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
  (by equipment)    manager        (drift, latency,
                                    fine-tune compare)
```

## Status

🔄 Step 4 — Support dataset (in progress): dataset selected, download/exploration
underway. Domain pivot from e-commerce to industrial maintenance applied to the
data layer; code-level renames (`customer_id` → `equipment_id`, function renames)
are the next concrete task before resuming Step 4 cleaning.

## Roadmap

- [X] Step 1 — Project skeleton
- [X] Step 2 — Minimal chatbot backend (FastAPI running, `/` and `/health` verified)
- [X] Step 3 — Database + ticket model
  - [X] `Ticket` model (MySQL, SQLAlchemy) with `TicketStatus` and `TicketPriority` enums,
    enforced at the database level (`Column(Enum(...))`)
  - [X] `TicketCreate` / `TicketUpdate` Pydantic schemas (partial updates supported via
    optional fields)
  - [X] Service layer: `create_ticket`, `get_customer_tickets`, `update_ticket`,
    `check_ticket` (duplicate-detection before creating a new ticket)
  - [X] Router: `POST /tickets/`, `GET /tickets/{customer_id}`, `PATCH /tickets/{id}` —
    all tested working against MySQL through `/docs`
  - [ ] **Domain rename (in progress):** `customer_id` → `equipment_id` across
    `models/ticket.py`, `services/ticket_service.py`, `routers/tickets.py`;
    `get_customer_tickets` → `get_equipment_tickets`; table will need to be
    dropped and recreated after the column rename
- [ ] Step 4 — Support dataset (in progress)
  - [X] Domain decided: industrial equipment maintenance/troubleshooting
    (manufacturing/energy), replacing the original e-commerce dataset
  - [X] Dataset selected: `nick007x/eevblog-posts` (Hugging Face) — 200K+ real
    electronics/equipment troubleshooting forum conversations (mentor/apprentice
    structure), chosen over a smaller synthetic maintenance Q&A set for volume
    and authenticity
  - [ ] Download and load dataset (`.parquet`, via `pyarrow`)
  - [ ] Explore shape, columns, nulls (same process as the earlier e-commerce dataset)
  - [ ] Clean and extract usable question → expert-answer pairs from forum threads
    (more effort than a pre-structured instruction/response dataset, since forum
    posts include thread context, mixed quality, and non-answer replies)
- [ ] Step 5 — RAG pipeline (chunking, embeddings, FAISS, BM25, RRF, reranker)
- [ ] Step 6 — LLM integration (single base LLM wired into `/chat`)
- [ ] Step 7 — LangGraph agent + real tools (`get_ticket`, `create_ticket`,
  `update_ticket`, `search_knowledge_base`, `escalate_ticket`)
- [ ] Step 8 — Streamlit technician-facing frontend
- [ ] Step 9 — Authentication + rate limiting
- [ ] Step 10 — Admin panel (internal — see below)
- [ ] Step 11 — Fine-tuning (QLoRA; base vs fine-tuned comparison against working baseline)
- [ ] Step 12 — Evaluation (retrieval quality, faithfulness, BERTScore, ROUGE, tool
  accuracy, end-to-end success rate, latency)
- [ ] Step 13 — Docker + CI/CD (GitHub Actions)
- [ ] Step 14 — Monitoring (Evidently AI — feeds back into the admin panel)
- [ ] Step 15 — Deployment (cloud host, public URL)
- [ ] Future enhancement — cloud analytics touchpoint: store cleaned knowledge base
  data in AWS S3; optionally query with Athena. Not required for core
  functionality, added for cloud-platform exposure relevant to target job
  postings.

### Step 10 — Admin panel (internal, operator-facing)

A separate, password-protected page (not exposed to technicians) where the system
operator manages and observes the agent:

| Section                                                   | Pulls from                         |
| --------------------------------------------------------- | ---------------------------------- |
| Ticket overview (filter by status/priority, by equipment) | Step 3 —`Ticket` model          |
| Knowledge base manager (upload/view/delete docs)          | Step 5 — RAG documents            |
| Agent activity log (answered vs escalated)                | Step 7 — LangGraph agent          |
| System health (drift, latency, error rate)                | Step 14 — Evidently AI monitoring |
| Fine-tuning comparison (base vs fine-tuned metrics)       | Step 11/12                         |

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
- `http://127.0.0.1:8000/docs` — interactive API docs (test all ticket endpoints here)
- `http://127.0.0.1:8000/health` — health check

### Database (MySQL)

Create the database once in MySQL Workbench:

```sql
CREATE DATABASE ai_support_agent;
```

Set the connection string as an environment variable (in a `.env` file, never committed)
before running the app:

```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/ai_support_agent
```

Tables are created automatically on app startup via `Base.metadata.create_all()`. If the
`Ticket` model's column types or names change (e.g. the `customer_id` → `equipment_id`
rename, or switching a column to a new `Enum`), the existing table must be dropped
manually and recreated — `create_all()` only creates missing tables, it does not alter
existing ones. A proper migration tool (Alembic) is a future improvement once the schema
stabilizes.

## API endpoints (current; field names mid-rename, see roadmap)

| Method    | Path              | Purpose                                                                          |
| --------- | ----------------- | -------------------------------------------------------------------------------- |
| `POST`  | `/tickets/`     | Create a new ticket (equipment/reporter id as query param,`TicketCreate` body) |
| `GET`   | `/tickets/{id}` | Get all tickets for a given equipment id                                         |
| `PATCH` | `/tickets/{id}` | Partially update a ticket's`status` and/or `priority`                        |

## Project structure

```
ai-support-agent/
├── app/
│   ├── main.py              # FastAPI app entrypoint, router wiring, table creation
│   ├── database.py           # SQLAlchemy engine, SessionLocal, Base, get_db()
│   ├── models/
│   │   └── ticket.py          # Ticket model, TicketStatus, TicketPriority enums
│   ├── schemas/
│   │   └── ticket.py           # TicketCreate, TicketUpdate (Pydantic)
│   ├── services/
│   │   └── ticket_service.py    # create_ticket, get_equipment_tickets, update_ticket,
│   │                              # check_ticket (duplicate detection)
│   └── routers/
│       └── tickets.py             # HTTP endpoints, calls service layer
├── frontend/                # Streamlit UI (technician-facing + admin panel) — not yet built
├── data/                     # datasets (raw/processed, gitignored) + notebooks for
│   │                           exploration (e.g. explore_dataset.ipynb)
├── tests/                     # pytest tests — not yet written
└── .github/                    # CI/CD workflows — not yet configured
```

## Tech stack (introduced incrementally, not all at once)

- **Backend**: FastAPI, Pydantic, SQLAlchemy, MySQL (via `pymysql`)
- **Data exploration**: Pandas, Jupyter (via VS Code notebooks)
- **RAG**: LangChain, FAISS, BM25, cross-encoder reranking, HyDE
- **Agent**: LangGraph, tool-calling
- **Fine-tuning**: PyTorch, Hugging Face Transformers, PEFT (QLoRA), bitsandbytes
- **Frontend**: Streamlit (technician chat + admin panel)
- **Evaluation**: BERTScore, ROUGE, custom faithfulness/groundedness scoring
- **Deployment**: Docker, GitHub Actions, free-tier cloud host (Render/Railway/Fly.io/HF Spaces)
- **Monitoring**: Evidently AI
- **Cloud analytics (planned)**: AWS S3 (knowledge base storage), optionally Athena

## Why this project

Demonstrates the full AI product lifecycle in one coherent system, applied to a
manufacturing/energy maintenance-support use case: data preparation,
retrieval-augmented generation, agentic tool use, model fine-tuning with measured
before/after comparison, production deployment, CI/CD, and live monitoring — rather
than a single isolated notebook or demo, and rather than a generic, unfocused domai

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
        Knowledge    MySQL
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

✅ Step 3 — Database + ticket model: **complete and verified end-to-end**
(create, read, and update all tested against real MySQL data through `/docs`)

## Roadmap

- [X] Step 1 — Project skeleton
- [X] Step 2 — Minimal chatbot backend (FastAPI running, `/` and `/health` verified)
- [X] Step 3 — Database + ticket model
  - [X] `Ticket` model (MySQL, SQLAlchemy) with `TicketStatus` and `TicketPriority` enums,
    enforced at the database level (`Column(Enum(...))`)
  - [X] `TicketCreate` / `TicketUpdate` Pydantic schemas (partial updates supported via
    optional fields)
  - [X] Service layer: `create_ticket`, `get_customer_tickets`, `update_ticket`
  - [X] Router: `POST /tickets/`, `GET /tickets/{customer_id}`, `PATCH /tickets/{id}` —
    all tested working against MySQL through `/docs`
  - [X] `check_ticket` — duplicate-detection helper (check for an existing open ticket
    on the same issue before creating a new one) — not yet implemented, not blocking
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
- `http://127.0.0.1:8000/docs` — interactive API docs (test all ticket endpoints here)
- `http://127.0.0.1:8000/health` — health check

### Database (MySQL)

Create the database once in MySQL Workbench:

```sql
CREATE DATABASE ai_support_agent;
```

Set the connection string as an environment variable (in a `.env` file, never committed)
before running the app:

```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/ai_support_agent
```

Tables are created automatically on app startup via `Base.metadata.create_all()`. If the
`Ticket` model's column types change (e.g. switching a column to a new `Enum`), the
existing table must be dropped manually and recreated — `create_all()` only creates
missing tables, it does not alter existing ones. A proper migration tool (Alembic) is a
future improvement once the schema stabilizes.

## API endpoints (current)

| Method    | Path                       | Purpose                                                                     |
| --------- | -------------------------- | --------------------------------------------------------------------------- |
| `POST`  | `/tickets/`              | Create a new ticket (`customer_id` as query param, `TicketCreate` body) |
| `GET`   | `/tickets/{customer_id}` | Get all tickets belonging to a customer                                     |
| `PATCH` | `/tickets/{id}`          | Partially update a ticket's`status` and/or `priority`                   |

## Project structure

```
ai-support-agent/
├── app/
│   ├── main.py              # FastAPI app entrypoint, router wiring, table creation
│   ├── database.py           # SQLAlchemy engine, SessionLocal, Base, get_db()
│   ├── models/
│   │   └── ticket.py          # Ticket model, TicketStatus, TicketPriority enums
│   ├── schemas/
│   │   └── ticket.py           # TicketCreate, TicketUpdate (Pydantic)
│   ├── services/
│   │   └── ticket_service.py    # create_ticket, get_customer_tickets, update_ticket
│   └── routers/
│       └── tickets.py             # HTTP endpoints, calls service layer
├── frontend/                # Streamlit UI (customer-facing + admin panel) — not yet built
├── data/                     # datasets (raw/processed, gitignored)
├── tests/                     # pytest tests — not yet written
└── .github/                    # CI/CD workflows — not yet configured
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
a single isolated notebook or dem

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
- [X] Step 3 — Database + ticket model (MySQL + SQLAlchemy, ticket CRUD)
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
