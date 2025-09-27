import io
import json
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv

# --- Google Gemini API Configuration ---
# Load environment variables from a .env file
load_dotenv()

# Get the API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Please set it in your .env file.")

# Configure the Gemini client
genai.configure(api_key=GOOGLE_API_KEY)


async def get_project_analysis_from_gemini(document_text: str):
    """
    Makes a real API call to the Google Gemini model to get project analysis.
    """
    # The prompt engineering here is key. We ask the model for a specific JSON structure.
    system_prompt = f"""
    You are a world-class software project analyst. Your task is to analyze the provided project requirements document and generate a comprehensive analysis.
    The current date is Saturday, September 27, 2025. You are based in India.

    Your output MUST be a single, minified JSON object with the following structure:
    {{
      "projectName": "A concise project name inferred from the document",
      "projectSummary": "A brief, one-paragraph summary of the project's goals",
      "techStack": {{
        "frontend": {{ "name": "e.g., Next.js", "reason": "Why this is a good choice for the project." }},
        "backend": {{ "name": "e.g., FastAPI (Python)", "reason": "Why this is a good choice for the project." }},
        "database": {{ "name": "e.g., PostgreSQL", "reason": "Why this is a good choice for the project." }},
        "deployment": {{ "name": "e.g., Vercel & AWS EC2", "reason": "Why this is a good choice for the project." }}
      }},
      "estimation": {{
        "functionPoints": {{
          "totalFP": "Estimated total function points (e.g., 250)",
          "analysis": "Brief explanation of how function points were derived from the requirements."
        }},
        "cocomo": {{
          "model": "Basic",
          "projectType": "Semi-detached (for a typical business application)",
          "effortMonths": "Calculated effort in person-months (e.g., 25)",
          "developmentTimeMonths": "Calculated development time in months (e.g., 6)",
          "personnelRequired": "Calculated number of personnel required (e.g., 4)"
        }}
      }},
      "costEstimation": {{
         "currency": "INR",
         "personnelCost": "Estimated cost for development team per month.",
         "infrastructureCost": "Estimated monthly cost for servers, databases, etc.",
         "totalProjectCost": "Total estimated cost for the project duration.",
         "breakdown": "A brief explanation of the cost components."
      }},
      "riskAnalysis": [
        {{ "risk": "Technical Debt", "mitigation": "Adopt a modular architecture and conduct regular code reviews." }},
        {{ "risk": "Scope Creep", "mitigation": "Implement a strict change control process and clear project milestones." }},
        {{ "risk": "Market Competition", "mitigation": "Focus on a unique value proposition and gather user feedback early." }}
      ]
    }}
    """

    # Model configuration
    # Using gemini-1.5-flash for speed and cost-effectiveness
    model = genai.GenerativeModel(
        model_name='gemini-2.5-pro',
        system_instruction=system_prompt
    )

    # The user prompt is the text extracted from the document
    prompt_parts = [
        "Here is the project requirements document:",
        document_text,
        "Please provide the analysis in the specified JSON format."
    ]

    try:
        # Generate content
        response = await model.generate_content_async(prompt_parts)

        # Clean up the response to extract just the JSON
        response_text = response.text.strip()
        # Find the start and end of the JSON object
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            raise ValueError(
                "No valid JSON object found in the model's response.")

        json_string = response_text[json_start:json_end]

        # Parse the JSON string into a Python dictionary
        return json.loads(json_string)

    except Exception as e:
        print(f"Error during Gemini API call: {e}")

        raise HTTPException(
            status_code=500, detail=f"An error occurred with the AI model: {str(e)}")


# --- FastAPI Application ---

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://srs-document-analyzer.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_text_from_file(file: UploadFile):
    filename = file.filename
    content = ""
    file_bytes = file.file.read()
    file.file.seek(0)

    try:
        if filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            for page in pdf_reader.pages:
                content += page.extract_text() or ""
        elif filename.endswith(".docx"):
            doc = Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                content += para.text + "\n"
        elif filename.endswith(".txt"):
            content = file_bytes.decode("utf-8")
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported file format. Please upload a .pdf, .docx, or .txt file.")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing file: {str(e)}")

    return content


@app.get("/")
def read_root():
    return {"message": "Welcome to the Project Analysis API"}


@app.post("/api/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    document_text = read_text_from_file(file)

    if not document_text.strip():
        raise HTTPException(
            status_code=400, detail="The uploaded document is empty or could not be read.")

    try:
        analysis_result = await get_project_analysis_from_gemini(document_text)
        return analysis_result
    except HTTPException as e:
        # Re-raise HTTP exceptions from the Gemini function
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get analysis from AI model: {str(e)}")
