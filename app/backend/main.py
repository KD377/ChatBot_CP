import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, StrictInt
from typing import List, Optional
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .GenerateResponseService import LanguageModelService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
QUESTION_CHARACTER_LIMIT = int(os.getenv("CHARACTER_LIMIT", "500"))

# Initialize the Language Model Service
model = LanguageModelService()

# Define global variables
selected_years: Optional[List[int]] = [1918, 2024]
restricted_years = {1940, 1941, 1942, 1943}


# Pydantic models
class YearsRequest(BaseModel):
    years: List[StrictInt]


class QuestionRequest(BaseModel):
    question: str



class AnswerResponse(BaseModel):
    answer: str


# API Endpoints
@app.post("/set_years")
async def set_years(request: YearsRequest):
    """
    Endpoint to set the range of years.
    """
    global selected_years

    # Validate request
    if not request.years:
        raise HTTPException(status_code=400, detail="Nieprawidłowy format 'years'.")

    for year in request.years:
        if year in restricted_years:
            raise HTTPException(status_code=400, detail="Lata 1940, 1941, 1942, 1943 są niedostępne.")

    # Update selected years
    selected_years = request.years
    return {"message": "Zakres lat został ustawiony.", "years": selected_years}


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Endpoint to ask a question and get a response.
    """
    # Validate the question
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Nieprawidłowy format 'question'.")

    if len(request.question) > QUESTION_CHARACTER_LIMIT:
        raise HTTPException(status_code=400, detail="Zbyt długie pytanie.")

    # Process the question
    try:
        answer = model.get_model_response(request.question)
        if not answer:
            raise HTTPException(status_code=204, detail="Brak odpowiedzi od modelu.")
        return AnswerResponse(answer=answer)

    except HTTPException as e:
        raise e  # Re-raise specific HTTP exceptions

    except Exception as e:
        # Log error and return server error
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Wewnętrzny błąd serwera")


@app.get("/")
async def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "ok"}
