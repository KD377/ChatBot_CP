import os
import json
import fitz
from pymongo import MongoClient
from unidecode import unidecode
from cleantext import clean
import language_tool_python

def find_pdf_files(root_dir):
    pdf_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def correct_text(text):
    text = clean(
        text,
        fix_unicode=True,
        to_ascii=False,
        lower=False,
        no_line_breaks=False,
        no_urls=True,
        no_emails=True,
        no_phone_numbers=True,
        no_numbers=False,
        no_digits=False,
        no_currency_symbols=False,
        no_punct=False,
        replace_with_punct="",
        lang="pl"
    )
    tool = language_tool_python.LanguageTool('pl-PL')
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text

# def extract_keywords(text, max_keywords=10):
#     # Użyj alternatywnego modelu
#     model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
#     kw_model = KeyBERT(model=model)
#
#     # Sprawdzenie długości tekstu
#     if len(text.strip()) == 0:
#         print("Brak tekstu do analizy")
#         return []
#
#     # Generowanie słów kluczowych
#     keywords = kw_model.extract_keywords(
#         text,
#         keyphrase_ngram_range=(1, 2),
#         stop_words=None,
#         top_n=max_keywords
#     )
#
#     # Sprawdzenie wyniku
#     if not keywords:
#         print("Brak słów kluczowych")
#
#     return [kw[0] for kw in keywords]

def save_to_mongodb(collection, pdf_path, keywords):
    document = {
        'file_path': pdf_path,
        'keywords': keywords
    }
    collection.insert_one(document)

def save_to_mongodb_binary(collection, pdf_path, legal_field):
    with open(pdf_path, 'rb') as f:
        import bson
        binary_data = bson.Binary(f.read())
    document = {
        'file_name': os.path.basename(pdf_path),
        'file_data': binary_data,
        'legal_field': legal_field
    }
    collection.insert_one(document)


def load_legal_fields(filepath='./legal_fields/key_words_legal_fields.json'):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Plik {filepath} nie istnieje.")

    with open(filepath, 'r', encoding='utf-8') as file:
        legal_fields = json.load(file)
    return legal_fields


def classify_legal_field(text, filepath='./legal_fields/key_words_legal_fields.json'):
    legal_fields = load_legal_fields(filepath)

    field_counts = {field: 0 for field in legal_fields}

    for field, keywords in legal_fields.items():
        for keyword in keywords:
            if keyword in text.lower():
                field_counts[field] += 1


    max_field = max(field_counts, key=field_counts.get)
    if field_counts[max_field] == 0:
        return "Nieznana dziedzina prawa"

    print(field_counts)
    return max_field

def main():
    root_dir = './dziennik_ustaw'
    pdf_files = find_pdf_files(root_dir)
    print(f"Znaleziono {len(pdf_files)} plików PDF.")

    # Połączenie z MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['moja_baza']
    collection = db['ustawy']

    for pdf_path in pdf_files:
        print(f"Przetwarzanie pliku: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)

        # Korekta tekstu
        corrected_text = correct_text(text)

        # keywords = extract_keywords(corrected_text)
        legal_field = classify_legal_field(corrected_text)

        # Wybierz jedną z funkcji zapisu:
        # save_to_mongodb(collection, pdf_path, keywords)
        # lub
        save_to_mongodb_binary(collection, pdf_path, legal_field)

if __name__ == "__main__":
    main()
