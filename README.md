# Blood Test Analyser — Debugged & Safe

This repository fixes the broken CrewAI-based project and adds safe fallbacks so it runs **with or without** external LLMs.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open: `POST /analyze` with a PDF file (`file`) and optional `query` (form field).

### Example (curl)

```bash
curl -X POST http://localhost:8000/analyze   -F "query=Analyze for key markers"   -F "file=@data/sample.pdf"
```

## What Was Broken (and How I Fixed It)

1. **README typo** — `requirement.txt` → `requirements.txt` and missing usage steps.  
2. **Unsafe / hallucination-prone task prompts** in `task.py` and README snippet → replaced with safety-first, verifiable instructions and JSON output contract.  
3. **Undefined `llm` in `agents.py`** (`llm = llm`) and harmful backstory → defined optional CrewAI `LLM` via env vars, replaced with evidence-based medical role.  
4. **CrewAI hard dependency** — app crashed if CrewAI or API keys absent → implemented graceful **fallback** path using `pypdf` + **rule-based analyzer** (`simple_blood_analysis`).  
5. **`tools.py`** — missing PDF extraction, unused imports, unclear async signatures → implemented robust `BloodTestReportTool.read_data_tool()` using `pypdf` and removed unused code.  
6. **`main.py`** — incomplete `run_crew()`, missing JSON-safe return, no content-type guard, no cleanup guarantees → rewrote as `run_pipeline()` with clear error handling and file cleanup.  
7. **Security** — removed instructions encouraging fabrication; added validation (PDF only) and safer defaults.  

## Optional Enhancements (Bonus)

### Queue Worker (Celery + Redis)
- Start Redis (e.g., Docker: `docker run -p 6379:6379 redis`).
- Run worker: `celery -A worker.app worker -l INFO`
- The API can enqueue jobs instead of inline processing (see `worker.py` example).

### Database (SQLAlchemy + SQLite)
- Save request/response pairs for auditability. See `db.py` for a minimal implementation.

> These files are scaffolded in comments in the code for easy extension.

## API

- `POST /analyze` — multipart form with:  
  - `file`: PDF blood report  
  - `query` (optional): analysis request (string)  
- Response (fallback mode):
```json
{
  "summary": "Rule-based analysis (fallback)",
  "findings": ["..."]
}
```

In CrewAI mode, the response contains a `result` string produced by the crew; you can adapt the task to emit strict JSON.

## Environment Variables (if using LLMs)

- `OPENAI_API_KEY` (and select model in `OPENAI_MODEL`, e.g., `gpt-4o-mini`)
- Any keys required by search tools (e.g., Serper `SERPER_API_KEY`).

## Testing

- Health check: `GET /health`  
- Try with provided `data/sample.pdf`. If your PDF has poor text extraction, consider `pdfplumber` or OCR.

## Folder Structure

```
.
├── main.py
├── agents.py
├── task.py
├── tools.py
├── requirements.txt
├── README.md
└── data/
    └── sample.pdf
```

## Notes

- This project **never** fabricates medical values. It flags uncertainty properly.  
- Replace the rule-based fallback with an LLM when keys are available, maintaining the same output schema.

Sreeja(rsreeja2478@gmail.com)
