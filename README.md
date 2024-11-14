# ChatBot_CP



Thought for 31 seconds

W porządku! Poniżej przedstawiam kompletny kod źródłowy oraz pliki wymagane do realizacji Twojego projektu.

Struktura projektu
css
Copy code
ChatBot_CP/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── utils.py
├── dziennik_ustaw/
│   └── [Twoje pliki PDF]
├── docker-compose.yml
├── requirements.txt
├── scraper.py
└── load_pdfs.py
Plik requirements.txt
plaintext
Copy code
fastapi
uvicorn[standard]
pymongo
python-multipart
pdfminer.six
scikit-learn
nltk
tqdm
Zainstaluj wymagane pakiety za pomocą polecenia:

bash
Copy code
pip install -r requirements.txt
Plik docker-compose.yml
yaml
Copy code
version: '3.8'
services:
  mongodb:
    image: mongo
    container_name: mongodb
    ports:
      - "27017:27017"
    volumes:
      - ./data/db:/data/db
Uruchom MongoDB za pomocą:

bash
Copy code
docker-compose up -d
Plik app/main.py
python
Copy code
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
Plik app/models.py
python
Copy code
from pydantic import BaseModel

class LawDocument(BaseModel):
    title: str
    text: str
    metadata: dict
Plik app/database.py
python
Copy code
from pymongo import MongoClient

def get_collection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dziennik_ustaw']
    collection = db['laws']
    return collection
Plik app/utils.py
python
Copy code
import nltk
from nltk.tokenize import word_tokenize

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    return ' '.join(tokens)
Skrypt load_pdfs.py do wczytywania plików PDF i zapisu do bazy danych
python
Copy code
import os
from pdfminer.high_level import extract_text
from app.database import get_collection
from app.utils import preprocess_text
from tqdm import tqdm

def process_pdfs(pdf_directory):
    collection = get_collection()
    for root, dirs, files in os.walk(pdf_directory):
        for file in tqdm(files):
            if file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                try:
                    text = extract_text(file_path)
                    preprocessed_text = preprocess_text(text)
                    title = file
                    document = {
                        "title": title,
                        "text": preprocessed_text,
                        "metadata": {}  # Możesz dodać tutaj dodatkowe metadane
                    }
                    collection.insert_one(document)
                except Exception as e:
                    print(f"Błąd przetwarzania pliku {file_path}: {e}")

if __name__ == "__main__":
    pdf_directory = './dziennik_ustaw'
    process_pdfs(pdf_directory)
Aktualizacja pliku scraper.py
Jeśli chcesz kontynuować pobieranie plików PDF, możesz użyć swojego obecnego skryptu scraper.py. Upewnij się, że pliki PDF są zapisywane w katalogu dziennik_ustaw/, aby skrypt load_pdfs.py mógł je przetworzyć.

Uruchomienie aplikacji FastAPI
Aby uruchomić aplikację, wykonaj w terminalu:

bash
Copy code
uvicorn app.main:app --reload
Aplikacja będzie dostępna pod adresem http://127.0.0.1:8000

Testowanie API
Możesz przetestować API za pomocą narzędzia takiego jak curl lub Postman.

Przykładowe zapytanie za pomocą curl:

bash
Copy code
curl -X POST "http://127.0.0.1:8000/search" -H "Content-Type: application/json" -d '{"keywords": "kodeks cywilny", "limit": 5}'
Przykładowe zapytanie w Postmanie:

Metoda: POST
URL: http://127.0.0.1:8000/search
Body (JSON):
json
Copy code
{
  "keywords": "kodeks cywilny",
  "limit": 5
}
Dodatkowe uwagi
Biblioteka pdfminer.six jest używana do ekstrakcji tekstu z plików PDF.

NLTK jest używane do tokenizacji tekstu. Upewnij się, że pobrałeś pakiet punktówacji:

python
Copy code
import nltk
nltk.download('punkt')
TF-IDF jest używane do wyszukiwania najbardziej dopasowanych dokumentów do podanych słów kluczowych.

tqdm dodaje pasek postępu podczas przetwarzania plików PDF.

Baza danych MongoDB musi być uruchomiona przed wczytaniem plików PDF i uruchomieniem aplikacji FastAPI.

Kroki do wykonania
Uruchom MongoDB:

bash
Copy code
docker-compose up -d
Wczytaj pliki PDF do bazy danych:

bash
Copy code
python load_pdfs.py
Uruchom aplikację FastAPI:

bash
Copy code
uvicorn app.main:app --reload
Przetestuj API za pomocą curl lub Postmana.

Jeśli napotkasz jakiekolwiek problemy lub masz dodatkowe pytania, daj znać! Chętnie pomogę w dalszych krokach.