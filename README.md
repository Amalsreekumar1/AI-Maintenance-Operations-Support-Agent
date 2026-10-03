# AI Maintenance & Operations Support Agent

An end-to-end AI support agent for industrial equipment maintenance: answers
technician questions using RAG, takes actions via agent tools, is fine-tuned on
domain data, and is deployed with CI/CD and monitoring. Built incrementally —
each step verified working before the next is added.

**Domain:** manufacturing/energy equipment maintenance and troubleshooting.

## Status

✅ Steps 1–4 complete. Next: Step 5 — RAG pipeline.

## Roadmap

- [X] Step 1 — Project skeleton
- [X] Step 2 — Minimal FastAPI backend
- [X] Step 3 — Database + ticket model
  - `Ticket` model (MySQL/SQLAlchemy), `TicketStatus` + `TicketPriority` enums
  - `TicketCreate` / `TicketUpdate` schemas (partial updates)
  - Service layer: `create_ticket`, `get_equipment_tickets`, `update_ticket`,
    `check_ticket` (duplicate detection)
  - Router: `POST /tickets/`, `GET /tickets/{id}`, `PATCH /tickets/{id}` — tested
- [X] Step 4 — Support dataset
  - Dataset: `mustafakeser/injection-molding-QA` (Hugging Face), 5,000 Q&A pairs
    on industrial injection molding troubleshooting/maintenance
  - Cleaned: dropped 2 null rows → 4,998 rows; verified no duplicates, no
    placeholder/templating issues, no broken outliers
  - Saved as `data/injection_molding_qa_cleaned.csv`
- [ ] Step 5 — RAG pipeline (chunking, embeddings, FAISS, BM25, RRF, reranker)
- [ ] Step 6 — LLM integration (`/chat` endpoint)
- [ ] Step 7 — LangGraph agent + tools
- [ ] Step 8 — Streamlit technician frontend
- [ ] Step 9 — Authentication + rate limiting
- [ ] Step 10 — Admin panel
- [ ] Step 11 — Fine-tuning (QLoRA, base vs fine-tuned comparison)
- [ ] Step 12 — Evaluation
- [ ] Step 13 — Docker + CI/CD
- [ ] Step 14 — Monitoring (Evidently AI)
- [ ] Step 15 — Deployment
- [ ] Future — AWS S3 knowledge base storage (cloud analytics exposure)

## Local development

```powershell
uv sync
uv run uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/docs` — test endpoints. MySQL connection via `DATABASE_URL`
in `.env` (not committed). Tables auto-created via `Base.metadata.create_all()` —
drop and recreate manually after any column rename or type change.

## API endpoints

| Method    | Path              | Purpose                                                               |
| --------- | ----------------- | --------------------------------------------------------------------- |
| `POST`  | `/tickets/`     | Create a ticket (`equipment_id` query param, `TicketCreate` body) |
| `GET`   | `/tickets/{id}` | Get all tickets for an equipment id                                   |
| `PATCH` | `/tickets/{id}` | Partially update status/priority                                      |

## Project structure

```
ai-support-agent/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/ticket.py
│   ├── schemas/ticket.py
│   ├── services/ticket_service.py
│   └── routers/tickets.py
├── frontend/      # not yet built
├── data/           # datasets + notebooks (gitignored raw data)
├── tests/           # not yet written
└── .github/          # not yet configured
```

## Tech stack

FastAPI, Pydantic, SQLAlchemy, MySQL · Pandas/Jupyter · LangChain, FAISS, BM25
(planned) · LangGraph (planned) · PyTorch, PEFT/QLoRA (planned) · Streamlit
(planned) · Evidently AI (planned) · Docker, GitHub Actions (planned)
