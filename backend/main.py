import os
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

from services.parser import parse_resume
from services.llm import analyze_resume

app = FastAPI(title="AI Resume Analyzer API")

# Configure CORS so our React frontend can query the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_resume_endpoint(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    x_gemini_api_key: Optional[str] = Header(None)
):
    # Extract file contents
    try:
        file_bytes = await file.read()
        filename = file.filename or "resume.pdf"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")

    # Extract text from document
    try:
        resume_text = parse_resume(file_bytes, filename)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume document: {str(e)}")

    if not resume_text or len(resume_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="The uploaded document contains no text. Please upload a machine-readable document.")

    # Call Gemini to analyze the resume
    try:
        analysis_result = analyze_resume(
            resume_text=resume_text,
            job_description=job_description,
            api_key=x_gemini_api_key
        )
        return analysis_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Analysis failed: {str(e)}")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_api_key_configured": bool(os.getenv("GEMINI_API_KEY"))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)