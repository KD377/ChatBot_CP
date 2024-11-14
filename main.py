import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, StrictInt
from typing import List, Optional
from GenerateResponseService import LanguageModelService
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
question_character_limit = int(os.getenv("CHARACTER_LIMIT", "500"))

model = LanguageModelService()


class YearsRequest(BaseModel):
    years: List[StrictInt]


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


selected_years: Optional[List[int]] = [1918, 2024]
restricted_years = {1940, 1941, 1942, 1943}


@app.post("/set_years")
async def set_years(request: YearsRequest):
    global selected_years

    if not request.years or not isinstance(request.years, list):
        raise HTTPException(status_code=400, detail="Nieprawidłowy format 'years'.")

    for year in request.years:
        if not isinstance(year, int):
            raise HTTPException(status_code=400, detail="Lata muszą być liczbami całkowitymi.")
        if year in restricted_years:
            raise HTTPException(status_code=400, detail="Lata 1940, 1941, 1942, 1943 są niedostępne.")

    selected_years = request.years
    return {"message": "Zakres lat został ustawiony.", "years": selected_years}


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    if not request.question or not isinstance(request.question, str) or request.question.strip() == "":
        raise HTTPException(status_code=400, detail="Nieprawidłowy format 'question'.")

    if len(request.question) > question_character_limit:
        raise HTTPException(status_code=400, detail="Zbyt długie pytanie")

    try:
        answer = model.get_model_response(request.question)

        if not answer:
            raise HTTPException(status_code=204)

        return AnswerResponse(answer=answer)

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Wewnętrzny błąd serwera")
