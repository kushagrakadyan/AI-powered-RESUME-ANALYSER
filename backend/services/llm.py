import os
import json
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# Define Pydantic structures for structured Gemini responses
class GrammarIssue(BaseModel):
    issue: str = Field(description="The grammar, spelling, or styling issue found")
    explanation: str = Field(description="Explanation of why it is an issue and how it impacts readability")
    original_text: str = Field(description="The original sentence or phrase containing the issue")
    suggested_text: str = Field(description="The suggested correction or rephrasing")
    severity: Literal['High', 'Medium', 'Low'] = Field(description="Severity of the issue")

class SkillGapAnalysis(BaseModel):
    matched_skills: List[str] = Field(description="Skills found in resume that match the job description or industry standard")
    missing_skills: List[str] = Field(description="Skills required for the target role but missing from the resume")
    skills_to_improve: List[str] = Field(description="Skills present in resume but require upskilling or certificates")
    gaps_explanation: str = Field(description="Summary of core skill gaps and learning advice")

class ImprovementSuggestion(BaseModel):
    category: str = Field(description="Category (e.g. Formatting, Content, Action Verbs, Metrics & Impact)")
    suggestion: str = Field(description="Actionable suggestion to improve the resume section")
    impact: Literal['High', 'Medium', 'Low'] = Field(description="Impact level")

class JobMatching(BaseModel):
    match_percentage: int = Field(ge=0, le=100, description="ATS match score against the job description (0 to 100)")
    fit_level: str = Field(description="Overall fit rating")
    strengths: List[str] = Field(description="Key strengths matching this role")
    gaps: List[str] = Field(description="Key gaps matching this role")
    interview_questions: List[str] = Field(description="3-5 tailored interview prep questions based on this resume/job combination")

class ResumeDetails(BaseModel):
    name: Optional[str] = Field(description="Candidate full name")
    email: Optional[str] = Field(description="Candidate email address")
    phone: Optional[str] = Field(description="Candidate phone number")
    summary: Optional[str] = Field(description="Extracted summary of candidate's professional profile")

class ResumeAnalysisResult(BaseModel):
    ats_score: int = Field(ge=0, le=100, description="Overall ATS Score out of 100 based on standard ATS parameters")
    grammar_analysis: List[GrammarIssue] = Field(description="Grammar and spelling improvement items")
    skills_analysis: SkillGapAnalysis = Field(description="Core skills analysis")
    improvement_suggestions: List[ImprovementSuggestion] = Field(description="Specific actionable improvements")
    job_matching: JobMatching = Field(description="Job matching analysis details")
    resume_details: ResumeDetails = Field(description="Extracted candidate details")


def get_analysis_prompt(resume_text: str, job_description: Optional[str] = None) -> str:
    if job_description:
        prompt = f"""
Analyze the following resume text against the provided job description.

--- RESUME TEXT ---
{resume_text}

--- JOB DESCRIPTION ---
{job_description}
"""
    else:
        prompt = f"""
Analyze the following resume text. Since no job description is provided, analyze the resume against general industry standards for the candidate's target field (infer the target role from their experience/skills).

--- RESUME TEXT ---
{resume_text}
"""
    return prompt


def analyze_resume_via_sdk_v2(api_key: str, prompt: str) -> dict:
    """Uses the official google-genai SDK."""
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_inline_json_schema(ResumeAnalysisResult.model_json_schema()),
            system_instruction="You are an expert ATS recruiter and career coach. Analyze only the provided resume and job description. Be specific, evidence-based, and practical. Return valid structured JSON matching the schema. Do not invent candidate experience, skills, metrics, employers, or contact details. If information is absent, use null or an empty list."
        )
    )
    return json.loads(response.text)



def _inline_json_schema(schema: dict) -> dict:
    """Expand Pydantic $ref/$defs so Gemini REST API receives a self-contained schema."""
    defs = schema.get("$defs", {})

    def resolve(node):
        if isinstance(node, dict):
            if "$ref" in node:
                name = node["$ref"].split("/")[-1]
                return resolve(defs[name])
            out = {}
            for key, value in node.items():
                if key == "$defs":
                    continue
                out[key] = resolve(value)
            return out
        if isinstance(node, list):
            return [resolve(item) for item in node]
        return node

    return resolve(schema)

def analyze_resume_via_sdk_v1(api_key: str, prompt: str) -> dict:
    """Uses the legacy google-generativeai SDK."""
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name='gemini-3.8-flash',
        system_instruction="You are an expert ATS recruiter and career coach. Analyze only the provided resume and job description. Be specific, evidence-based, and practical. Return valid structured JSON matching the schema. Do not invent candidate experience, skills, metrics, employers, or contact details. If information is absent, use null or an empty list."
    )
    
    # In legacy SDK, we pass schema to generation_config
    schema_dict = _inline_json_schema(ResumeAnalysisResult.model_json_schema())
    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": schema_dict
    }
    
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )
    return json.loads(response.text)


def analyze_resume_via_http(api_key: str, prompt: str) -> dict:
    """Direct HTTP POST to Gemini API. Highly resilient fallback."""
    import requests
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    schema_dict = _inline_json_schema(ResumeAnalysisResult.model_json_schema())
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": "You are an expert ATS (Applicant Tracking System) recruiter and career coach. Review the resume and analyze it thoroughly."}
            ]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema_dict
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Gemini HTTP API error (Status {response.status_code}): {response.text}")
        
    res_data = response.json()
    try:
        content_text = res_data['candidates'][0]['content']['parts'][0]['text']
        return json.loads(content_text)
    except (KeyError, IndexError, ValueError) as e:
        raise Exception(f"Failed to parse JSON response from Gemini HTTP endpoint: {e}. Response payload: {res_data}")


def analyze_resume(resume_text: str, job_description: Optional[str] = None, api_key: Optional[str] = None) -> dict:
    """Analyzes the resume text, falling back gracefully through available connection methods."""
    # Resolve API Key: passed parameter -> env var
    resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not resolved_api_key:
        raise ValueError("Gemini API key is not configured. Set the GEMINI_API_KEY environment variable or provide it in the X-Gemini-API-Key request header.")
        
    prompt = get_analysis_prompt(resume_text, job_description)
    
    # Try Method 1: Modern google-genai SDK (SDK v2)
    try:
        return analyze_resume_via_sdk_v2(resolved_api_key, prompt)
    except ImportError:
        pass
    except Exception as e:
        print(f"Failed analysis via google-genai SDK v2, falling back. Error: {e}")
        
    # Try Method 2: Legacy google-generativeai SDK (SDK v1)
    try:
        return analyze_resume_via_sdk_v1(resolved_api_key, prompt)
    except ImportError:
        pass
    except Exception as e:
        print(f"Failed analysis via google-generativeai SDK v1, falling back. Error: {e}")
        
    # Try Method 3: HTTP Direct Request (requires zero SDKs, only standard requests)
    try:
        return analyze_resume_via_http(resolved_api_key, prompt)
    except Exception as e:
        print(f"Failed analysis via direct HTTP, no other fallback. Error: {e}")
        raise e
