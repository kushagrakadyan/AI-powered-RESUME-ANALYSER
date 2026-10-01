# ResuMate AI — AI-Powered Resume Analyzer

A full-stack resume analyzer with a React/Vite frontend, FastAPI backend, PDF/DOCX/TXT parsing and structured Gemini analysis.

## Features
- Upload PDF, DOCX or TXT resumes (up to 8 MB)
- Optional job description matching
- ATS score (0–100)
- Skill matching, missing skills and upskilling areas
- Grammar/writing suggestions
- Prioritized improvement plan
- Tailored interview questions
- Candidate detail extraction
- Exportable text report
- Responsive dashboard UI
- Gemini API via backend environment variable or request header.

## Project structure
```text
ATS finder/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .env.example
│   └── package.json
└── backend/
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    └── services/
        ├── parser.py
        └── llm.py
```

## 1. Backend setup
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

Put your Gemini key in `backend/.env`:
```env
GEMINI_API_KEY=your_real_key
```

Start API:
```bash
uvicorn main:app --reload --port 8000
```

Health check: `http://localhost:8000/api/health`

## 2. Frontend setup
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```

The Vite app normally runs at `http://localhost:5173`.

If the backend is deployed somewhere else, create `frontend/.env`:
```env
VITE_API_URL=https://your-backend-domain.com
```
Then restart Vite.

## 3. Production build
```bash
cd frontend
npm run build
npm run preview
```

## API
### `GET /api/health`
Returns API health and whether a backend Gemini key is configured.

### `POST /api/analyze`
Multipart fields:
- `file`: PDF, DOCX or TXT resume
- `job_description`: optional text

Optional header:
- `X-Gemini-API-Key`: Gemini key. Prefer configuring it server-side for production.

## Deployment notes
- Keep `GEMINI_API_KEY` on the server; do not commit `.env`.
- Set the deployed frontend's `VITE_API_URL` to the backend URL.
- For production, replace `allow_origins=["*"]` with the exact frontend domain.
- The current analyzer is stateless: uploaded resume contents are processed for the request and are not persisted by the application.
