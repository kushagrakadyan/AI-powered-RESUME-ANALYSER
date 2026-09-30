import os
import json
import time
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================
# GEMINI MODEL FALLBACK CONFIGURATION
# ============================================================

GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite",
]


# ============================================================
# PYDANTIC RESPONSE MODELS
# ============================================================

class GrammarIssue(BaseModel):
    issue: str = Field(
        description="The grammar, spelling, or styling issue found"
    )
    explanation: str = Field(
        description="Explanation of why it is an issue and how it impacts readability"
    )
    original_text: str = Field(
        description="The original sentence or phrase containing the issue"
    )
    suggested_text: str = Field(
        description="The suggested correction or rephrasing"
    )
    severity: Literal["High", "Medium", "Low"] = Field(
        description="Severity of the issue"
    )


class SkillGapAnalysis(BaseModel):
    matched_skills: List[str] = Field(
        description="Skills found in resume that match the job description or industry standard"
    )
    missing_skills: List[str] = Field(
        description="Skills required for the target role but missing from the resume"
    )
    skills_to_improve: List[str] = Field(
        description="Skills present in resume but require upskilling or certificates"
    )
    gaps_explanation: str = Field(
        description="Summary of core skill gaps and learning advice"
    )


class ImprovementSuggestion(BaseModel):
    category: str = Field(
        description="Category such as Formatting, Content, Action Verbs, Metrics & Impact"
    )
    suggestion: str = Field(
        description="Actionable suggestion to improve the resume section"
    )
    impact: Literal["High", "Medium", "Low"] = Field(
        description="Impact level"
    )


class JobMatching(BaseModel):
    match_percentage: int = Field(
        ge=0,
        le=100,
        description="ATS match score against the job description (0 to 100)"
    )
    fit_level: str = Field(
        description="Overall fit rating"
    )
    strengths: List[str] = Field(
        description="Key strengths matching this role"
    )
    gaps: List[str] = Field(
        description="Key gaps matching this role"
    )
    interview_questions: List[str] = Field(
        description="3-5 tailored interview prep questions based on this resume/job combination"
    )


class ResumeDetails(BaseModel):
    name: Optional[str] = Field(
        description="Candidate full name"
    )
    email: Optional[str] = Field(
        description="Candidate email address"
    )
    phone: Optional[str] = Field(
        description="Candidate phone number"
    )
    summary: Optional[str] = Field(
        description="Extracted summary of candidate's professional profile"
    )


class ResumeAnalysisResult(BaseModel):
    ats_score: int = Field(
        ge=0,
        le=100,
        description="Overall ATS Score out of 100 based on standard ATS parameters"
    )
    grammar_analysis: List[GrammarIssue] = Field(
        description="Grammar and spelling improvement items"
    )
    skills_analysis: SkillGapAnalysis = Field(
        description="Core skills analysis"
    )
    improvement_suggestions: List[ImprovementSuggestion] = Field(
        description="Specific actionable improvements"
    )
    job_matching: JobMatching = Field(
        description="Job matching analysis details"
    )
    resume_details: ResumeDetails = Field(
        description="Extracted candidate details"
    )


# ============================================================
# PROMPT
# ============================================================

def get_analysis_prompt(
    resume_text: str,
    job_description: Optional[str] = None
) -> str:

    if job_description:

        prompt = f"""
Analyze the following resume text against the provided job description.

--- RESUME TEXT ---
{resume_text}

--- JOB DESCRIPTION ---
{job_description}

Provide a detailed ATS-oriented analysis.
"""

    else:

        prompt = f"""
Analyze the following resume text.

Since no job description is provided, analyze the resume against
general industry standards for the candidate's target field.

Infer the target role only from the experience and skills actually
present in the resume.

--- RESUME TEXT ---
{resume_text}
"""

    return prompt


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are an expert ATS recruiter and career coach.

Analyze only the provided resume and job description.

Be specific, evidence-based, practical, and accurate.

Do not invent:
- Candidate experience
- Skills
- Metrics
- Employers
- Education
- Certifications
- Contact details
- Projects

If information is absent:
- Use null where appropriate
- Use an empty list where appropriate

Return valid structured JSON matching the provided schema.
"""


# ============================================================
# INLINE GEMINI JSON SCHEMA
# ============================================================

def _inline_json_schema(schema: dict) -> dict:
    """
    Expand Pydantic $ref/$defs so Gemini receives
    a self-contained JSON schema.
    """

    defs = schema.get("$defs", {})

    def resolve(node):

        if isinstance(node, dict):

            if "$ref" in node:

                name = node["$ref"].split("/")[-1]

                if name in defs:
                    return resolve(defs[name])

                return node

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


# ============================================================
# METHOD 1 — MODERN GOOGLE GENAI SDK
# ============================================================

def analyze_resume_via_sdk_v2(
    api_key: str,
    prompt: str,
    model_name: str
) -> dict:

    """
    Uses the modern google-genai SDK.
    """

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(

        model=model_name,

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=_inline_json_schema(
                ResumeAnalysisResult.model_json_schema()
            ),

            system_instruction=SYSTEM_INSTRUCTION
        )
    )

    return json.loads(response.text)


# ============================================================
# METHOD 2 — LEGACY GOOGLE GENERATIVE AI SDK
# ============================================================

def analyze_resume_via_sdk_v1(
    api_key: str,
    prompt: str,
    model_name: str
) -> dict:

    """
    Uses the legacy google-generativeai SDK.
    """

    import google.generativeai as genai

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(

        model_name=model_name,

        system_instruction=SYSTEM_INSTRUCTION
    )

    schema_dict = _inline_json_schema(
        ResumeAnalysisResult.model_json_schema()
    )

    generation_config = {

        "response_mime_type": "application/json",

        "response_schema": schema_dict
    }

    response = model.generate_content(

        prompt,

        generation_config=generation_config
    )

    return json.loads(response.text)


# ============================================================
# METHOD 3 — DIRECT HTTP GEMINI API
# ============================================================

def analyze_resume_via_http(
    api_key: str,
    prompt: str
) -> dict:

    """
    Direct HTTP request to Gemini API.

    Automatically:
    1. Tries Gemini 3.8 Flash
    2. Retries temporary errors
    3. Falls back to Gemini 3.7 Flash
    4. Falls back to Gemini 3.5 Flash-Lite
    """

    import requests

    headers = {
        "Content-Type": "application/json"
    }

    schema_dict = _inline_json_schema(
        ResumeAnalysisResult.model_json_schema()
    )

    payload = {

        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],

        "systemInstruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION
                }
            ]
        },

        "generationConfig": {

            "responseMimeType": "application/json",

            "responseSchema": schema_dict
        }
    }

    last_error = None

    # --------------------------------------------------------
    # Try each model
    # --------------------------------------------------------

    for model_name in GEMINI_MODELS:

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model_name}:generateContent"
            f"?key={api_key}"
        )

        print(
            f"Trying Gemini HTTP model: {model_name}"
        )

        # ----------------------------------------------------
        # Retry each model twice
        # ----------------------------------------------------

        for attempt in range(2):

            try:

                response = requests.post(

                    url,

                    headers=headers,

                    json=payload,

                    timeout=60
                )

                # ------------------------------------------------
                # SUCCESS
                # ------------------------------------------------

                if response.status_code == 200:

                    res_data = response.json()

                    try:

                        content_text = (
                            res_data["candidates"][0]
                            ["content"]["parts"][0]["text"]
                        )

                        return json.loads(content_text)

                    except (
                        KeyError,
                        IndexError,
                        ValueError
                    ) as e:

                        raise Exception(
                            "Failed to parse JSON response from "
                            f"Gemini HTTP endpoint: {e}. "
                            f"Response payload: {res_data}"
                        )

                # ------------------------------------------------
                # TEMPORARY GEMINI ERRORS
                # ------------------------------------------------

                if response.status_code in (
                    429,
                    500,
                    502,
                    503,
                    504
                ):

                    last_error = (
                        f"Gemini model {model_name} "
                        f"returned HTTP "
                        f"{response.status_code}: "
                        f"{response.text}"
                    )

                    print(
                        f"Temporary Gemini error on "
                        f"{model_name} "
                        f"(attempt {attempt + 1}/2)"
                    )

                    time.sleep(
                        2 * (attempt + 1)
                    )

                    continue

                # ------------------------------------------------
                # OTHER API ERRORS
                # ------------------------------------------------

                raise Exception(

                    "Gemini HTTP API error "
                    f"(Status {response.status_code}): "
                    f"{response.text}"
                )

            except requests.RequestException as e:

                last_error = (
                    f"Network error while contacting "
                    f"Gemini model {model_name}: {e}"
                )

                print(
                    f"Network error on {model_name} "
                    f"(attempt {attempt + 1}/2): {e}"
                )

                time.sleep(
                    2 * (attempt + 1)
                )

    # --------------------------------------------------------
    # ALL MODELS FAILED
    # --------------------------------------------------------

    raise Exception(
        "All Gemini models failed. "
        f"Last error: {last_error}"
    )


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_resume(
    resume_text: str,
    job_description: Optional[str] = None,
    api_key: Optional[str] = None
) -> dict:

    """
    Analyze resume using Gemini.

    Fallback order:

    Modern SDK
        ↓
    Legacy SDK
        ↓
    Direct HTTP
        ↓
    Multiple Gemini models
    """

    # --------------------------------------------------------
    # Resolve API key
    # --------------------------------------------------------

    resolved_api_key = (
        api_key
        or os.getenv("GEMINI_API_KEY")
    )

    if not resolved_api_key:

        raise ValueError(
            "Gemini API key is not configured. "
            "Set the GEMINI_API_KEY environment variable "
            "or provide it in the X-Gemini-API-Key request header."
        )

    # --------------------------------------------------------
    # Create prompt
    # --------------------------------------------------------

    prompt = get_analysis_prompt(
        resume_text,
        job_description
    )

    # ========================================================
    # METHOD 1 — MODERN SDK
    # ========================================================

    try:

        for model_name in GEMINI_MODELS:

            try:

                print(
                    f"Trying modern Gemini SDK model: "
                    f"{model_name}"
                )

                return analyze_resume_via_sdk_v2(
                    resolved_api_key,
                    prompt,
                    model_name
                )

            except Exception as e:

                print(
                    f"Modern SDK failed for "
                    f"{model_name}: {e}"
                )

                # Try next model

                continue

    except ImportError:

        print(
            "Modern google-genai SDK not installed. "
            "Moving to legacy SDK."
        )

    # ========================================================
    # METHOD 2 — LEGACY SDK
    # ========================================================

    try:

        for model_name in GEMINI_MODELS:

            try:

                print(
                    f"Trying legacy Gemini SDK model: "
                    f"{model_name}"
                )

                return analyze_resume_via_sdk_v1(
                    resolved_api_key,
                    prompt,
                    model_name
                )

            except Exception as e:

                print(
                    f"Legacy SDK failed for "
                    f"{model_name}: {e}"
                )

                continue

    except ImportError:

        print(
            "Legacy google-generativeai SDK not installed. "
            "Moving to HTTP fallback."
        )

    # ========================================================
    # METHOD 3 — DIRECT HTTP
    # ========================================================

    try:

        print(
            "Trying direct Gemini HTTP fallback..."
        )

        return analyze_resume_via_http(
            resolved_api_key,
            prompt
        )

    except Exception as e:

        print(
            "Direct Gemini HTTP fallback failed."
        )

        raise Exception(
            f"LLM Analysis failed: {e}"
        )