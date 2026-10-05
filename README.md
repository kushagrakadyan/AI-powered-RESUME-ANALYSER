# ResuMate AI — AI-Powered Resume Analyzer

> **Analyze. Improve. Get Interview-Ready.**

ResuMate AI is a full-stack AI-powered resume analysis platform that helps candidates evaluate and improve their resumes against modern ATS (Applicant Tracking System) requirements.

The application extracts resume content from **PDF, DOCX, and TXT files**, analyzes it using **Google Gemini**, and generates structured insights including ATS scoring, skill matching, missing skills, writing improvements, an actionable improvement plan, and tailored interview questions.

---

## ✨ Features

* 📄 **Multi-format Resume Upload**

  * PDF
  * DOCX
  * TXT
  * Maximum file size: **8 MB**

* 🤖 **AI-Powered Resume Analysis**

  * Structured analysis using Gemini
  * Automated resume evaluation
  * Candidate information extraction

* 📊 **ATS Score**

  * Resume score from **0–100**
  * Identifies areas affecting ATS performance

* 🎯 **Job Description Matching**

  * Compare resume against a target job description
  * Identify matching skills
  * Detect missing or recommended skills

* 🛠️ **Resume Improvement Suggestions**

  * Grammar and writing recommendations
  * Content improvement suggestions
  * Prioritized action plan

* 💼 **Interview Preparation**

  * Generates tailored interview questions
  * Questions are based on the candidate's resume and target role

* 📑 **Exportable Report**

  * Generate a structured text report of the analysis

* 📱 **Responsive Dashboard**

  * Clean and modern interface
  * Works across desktop and mobile screen sizes

* 🔐 **Secure API Key Handling**

  * Gemini API key can be configured through backend environment variables
  * API keys are not required to be exposed in the frontend

---

## 🏗️ Tech Stack

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

### AI & Processing

* Google Gemini API
* PDF parsing
* DOCX parsing
* TXT processing

### Development & Deployment

* Git
* GitHub
* npm
* Python Virtual Environment

---

## 📂 Project Structure

```text
ATS finder/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── .env.example
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   │
│   └── services/
│       ├── parser.py
│       └── llm.py
│
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have the following installed:

* Python 3.10+
* Node.js 18+
* npm
* Git
* Gemini API key

---

# ⚙️ Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file from the provided example:

**Windows:**

```bash
copy .env.example .env
```

Then add your Gemini API key:

```env
GEMINI_API_KEY=your_real_gemini_api_key
```

> ⚠️ Never commit your `.env` file or expose your Gemini API key in frontend code.

### 5. Start the backend

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/api/health
```

---

# 🎨 Frontend Setup

Open a new terminal and navigate to the frontend:

```bash
cd frontend
```

### 1. Install dependencies

```bash
npm install
```

### 2. Start the development server

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔗 Environment Configuration

If the backend is running locally, the frontend can use the default API configuration.

For a deployed backend, create:

```text
frontend/.env
```

Add:

```env
VITE_API_URL=https://your-backend-domain.com
```

After changing environment variables, restart the Vite development server.

---

# 📡 API Documentation

## Health Check

### `GET /api/health`

Checks whether the backend is running and whether a Gemini API key is configured.

### Example Response

```json
{
  "status": "ok",
  "gemini_configured": true
}
```

---

## Resume Analysis

### `POST /api/analyze`

Analyzes an uploaded resume and optionally compares it against a job description.

### Multipart Fields

| Field             | Type   | Required | Description              |
| ----------------- | ------ | -------: | ------------------------ |
| `file`            | File   |      Yes | PDF, DOCX, or TXT resume |
| `job_description` | String |       No | Target job description   |

### Supported Formats

```text
.pdf
.docx
.txt
```

### Maximum File Size

```text
8 MB
```

### Optional Header

```http
X-Gemini-API-Key: your_api_key
```

For production deployments, configuring the API key on the backend through environment variables is recommended.

---

# 🔄 Application Workflow

```text
        ┌─────────────────────┐
        │   Upload Resume     │
        │  PDF / DOCX / TXT   │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │   FastAPI Backend   │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │  Resume Parser      │
        │ PDF / DOCX / TXT    │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Extracted Resume    │
        │      Content        │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │    Gemini AI        │
        │     Analysis        │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Structured Results  │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────────────┐
        │ ATS Score • Skills • Gaps   │
        │ Suggestions • Interview Qs  │
        └─────────────────────────────┘
```

---

# 📊 Analysis Output

ResuMate AI provides structured insights such as:

### ATS Evaluation

* Overall ATS score
* Resume strengths
* Potential ATS issues
* Formatting/content observations

### Skills Analysis

* Detected skills
* Matching skills
* Missing skills
* Recommended upskilling areas

### Writing Analysis

* Grammar issues
* Writing improvements
* Clarity recommendations
* Professional language suggestions

### Improvement Plan

Recommendations are prioritized to help candidates focus on the most impactful resume changes first.

### Interview Preparation

The system generates role-relevant interview questions based on the candidate's resume and, when provided, the target job description.

---

# 🖥️ Production Build

To create a production build of the frontend:

```bash
cd frontend
npm run build
```

To preview the production build locally:

```bash
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


---

# ☁️ Deployment

The application can be deployed as two separate services:

```text
┌────────────────────┐
│     Frontend       │
│   React + Vite     │
└─────────┬──────────┘
          │
          │ HTTPS API
          ▼
┌────────────────────┐
│      Backend       │
│ FastAPI + Gemini   │
└────────────────────┘
```

### Frontend

Deploy the `frontend` directory to a static hosting provider such as:

* Vercel
* Netlify
* Cloudflare Pages

Configure:

```env
VITE_API_URL=https://your-backend-domain.com
```

### Backend

Deploy the `backend` service to a Python-compatible hosting provider such as:

* Render
* Railway
* Fly.io

Configure the environment variable:

```env
GEMINI_API_KEY=your_real_gemini_api_key
```

> The exact deployment configuration depends on the hosting provider.

---

# 🔐 Security

For production usage:

* Never commit `.env` files.
* Never hard-code API keys in source code.
* Keep `GEMINI_API_KEY` on the server.
* Use HTTPS for deployed applications.
* Restrict CORS to the production frontend domain.
* Validate uploaded file types and sizes.
* Avoid logging sensitive resume content.

For example, replace a permissive CORS configuration such as:

```python
allow_origins=["*"]
```

with your actual frontend domain in production.

---

# 📝 Privacy

ResuMate AI is designed around a stateless analysis workflow.

Uploaded resume content is processed for the analysis request and is not intentionally persisted by the application.

Users should still avoid uploading documents containing unnecessary sensitive personal information.

---

# 🛠️ Development

### Start Backend

```bash
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

The frontend and backend should then run independently:

```text
Frontend → http://localhost:5173
Backend  → http://localhost:8000
```

---

# 🧪 Testing the API

You can verify the backend is running by opening:

```text
http://localhost:8000/api/health
```

For API exploration, FastAPI also provides interactive documentation when enabled:

```text
http://localhost:8000/docs
```

---

# 🚧 Future Improvements

Potential improvements for future versions include:

* 🔐 User authentication
* 💾 Resume history and saved analyses
* 📈 Resume score tracking over time
* 📄 PDF report generation
* 🎯 Role-specific resume optimization
* 🧠 Multiple AI model support
* 🔍 More advanced ATS keyword analysis
* 🌐 Multi-language resume analysis
* 📊 Resume comparison
* 💼 Job-board integration
* 📬 Automated job matching
* ☁️ Cloud-based resume storage with user consent

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

### Fork the repository

```bash
git clone https://github.com/your-username/your-repository.git
```

### Create a feature branch

```bash
git checkout -b feature/your-feature
```

### Commit your changes

```bash
git add .
git commit -m "Add your feature"
```

### Push the branch

```bash
git push origin feature/your-feature
```

Then open a Pull Request.

---

# 📄 License

This project is intended for educational and portfolio purposes.

If you plan to distribute or commercially use the project, add an appropriate open-source or proprietary license.

---

# 👨‍💻 Author

**Kushagra Kadyan**

Built with **React, FastAPI, Python and Google Gemini AI**.

---

## ⭐ Support

If you find **ResuMate AI** useful, consider giving the repository a ⭐ on GitHub.
