from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.database import get_collection
from app.utils import preprocess_text
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk

nltk.download('punkt')

app = FastAPI()

class QueryModel(BaseModel):
    keywords: str
    limit: int = 5

@app.get("/")
def read_root():
    return {"message": "Witaj w prawniczym czacie!"}

@app.post("/search")
def search_laws(query: QueryModel):
    collection = get_collection()
    all_docs = list(collection.find({}, {"_id": 0}))
    if not all_docs:
        raise HTTPException(status_code=404, detail="Brak dokumentów w bazie danych.")

    documents = [doc['text'] for doc in all_docs]
    titles = [doc['title'] for doc in all_docs]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    query_vec = vectorizer.transform([query.keywords])

    scores = (tfidf_matrix * query_vec.T).toarray()

    results = sorted(
        zip(titles, scores),
        key=lambda x: x[1],
        reverse=True
    )

    top_results = [{"title": title, "score": float(score)} for title, score in results[:query.limit]]
    return {"results": top_results}
