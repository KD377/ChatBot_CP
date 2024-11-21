import os
import json
import fitz  # PyMuPDF
from pymongo import MongoClient, errors
from bson import Binary
from cleantext import clean
import language_tool_python
from typing import List, Dict, Optional

# Configuration Constants
MONGODB_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'moja_baza'
COLLECTION_NAME = 'ustawy'
LEGAL_FIELDS_FILEPATH = './legal_fields/key_words_legal_fields.json'
PDF_ROOT_DIR = './dziennik_ustaw'

# Define custom Polish stopwords
POLISH_STOPWORDS = [
    "i", "oraz", "ponieważ", "ale", "że", "który", "tego", "mnie", "ją", "on", "ona",
    "to", "się", "czy", "jest", "jak", "dla", "do", "z", "od", "po", "na", "za",
    "bez", "by", "tym", "o", "przy", "jeśli"
]


def find_pdf_files(root_dir: str) -> List[str]:
    """
    Find all PDF files in the specified directory.

    Args:
        root_dir (str): The root directory to search for PDF files.

    Returns:
        List[str]: A list of full paths to PDF files.
    """
    pdf_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                pdf_files.append(full_path)
    print(f"Znaleziono {len(pdf_files)} plików PDF w {root_dir}.")
    return pdf_files


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        Optional[str]: The extracted text or None if extraction fails.
    """
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text()
                if page_text:
                    text += page_text
                else:
                    print(f"Strona {page_num} w pliku {pdf_path} jest pusta.")
        if not text.strip():
            print(f"Ostrzeżenie: Brak tekstu w pliku {pdf_path}.")
            return None
        return text
    except Exception as e:
        print(f"Błąd podczas ekstrakcji tekstu z {pdf_path}: {e}")
        return None


def correct_text(text: str) -> Optional[str]:
    """
    Clean and correct text using cleantext and LanguageTool.

    Args:
        text (str): The text to be cleaned and corrected.

    Returns:
        Optional[str]: The corrected text or None if processing fails.
    """
    if not text.strip():
        print("Ostrzeżenie: Pusty tekst przekazany do funkcji correct_text.")
        return None

    try:
        # Clean the text with cleantext, passing custom stopwords
        cleaned_text = clean(
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
            lang="pl",
            stopwords=POLISH_STOPWORDS  # Pass the custom stopwords list
        )

        # Initialize LanguageTool for Polish
        tool = language_tool_python.LanguageTool('pl-PL')
        matches = tool.check(cleaned_text)
        corrected_text = language_tool_python.utils.correct(cleaned_text, matches)

        return corrected_text
    except Exception as e:
        print(f"Błąd podczas korekty tekstu: {e}")
        return None


def load_legal_fields(filepath: str) -> Dict[str, List[str]]:
    """
    Load legal fields and their keywords from a JSON file.

    Args:
        filepath (str): The path to the JSON file containing legal fields.

    Returns:
        Dict[str, List[str]]: A dictionary mapping legal fields to their keywords.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Plik {filepath} nie istnieje.")

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            legal_fields = json.load(file)
        print(f"Załadowano dziedziny prawa z {filepath}.")
        return legal_fields
    except json.JSONDecodeError as e:
        print(f"Błąd podczas dekodowania JSON z {filepath}: {e}")
        raise


def classify_legal_field(text: str, legal_fields: Dict[str, List[str]]) -> str:
    """
    Classify the legal field of the given text based on keyword occurrences.

    Args:
        text (str): The text to classify.
        legal_fields (Dict[str, List[str]]): A dictionary of legal fields and their keywords.

    Returns:
        str: The classified legal field or "Nieznana dziedzina prawa" if no match is found.
    """
    if not text:
        print("Ostrzeżenie: Pusty tekst przekazany do klasyfikacji dziedziny prawa.")
        return "Nieznana dziedzina prawa"

    field_counts = {field: 0 for field in legal_fields}

    text_lower = text.lower()
    for field, keywords in legal_fields.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                field_counts[field] += 1

    max_field = max(field_counts, key=field_counts.get)
    if field_counts[max_field] == 0:
        print("Nie znaleziono pasującej dziedziny prawa. Klasyfikacja jako 'Nieznana dziedzina prawa'.")
        return "Nieznana dziedzina prawa"

    print(f"Klasyfikacja tekstu do dziedziny prawa: {max_field}")
    return max_field


def save_to_mongodb_binary(collection, pdf_path: str, legal_field: str) -> None:
    """
    Save binary PDF data and legal field classification to MongoDB.

    Args:
        collection: The MongoDB collection to insert the document into.
        pdf_path (str): The path to the PDF file.
        legal_field (str): The classified legal field.
    """
    try:
        with open(pdf_path, 'rb') as f:
            binary_data = Binary(f.read())

        document = {
            'file_name': os.path.basename(pdf_path),
            'file_data': binary_data,
            'legal_field': legal_field
        }

        collection.insert_one(document)
        print(f"Zapisano dane binarne z {pdf_path} do MongoDB.")
    except Exception as e:
        print(f"Błąd podczas zapisywania danych binarnych z {pdf_path} do MongoDB: {e}")


def connect_to_mongodb(uri: str) -> MongoClient:
    """
    Establish a connection to MongoDB.

    Args:
        uri (str): The MongoDB connection URI.

    Returns:
        MongoClient: The MongoDB client instance.
    """
    try:
        client = MongoClient(uri)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("Pomyslnie połączono z MongoDB.")
        return client
    except errors.ConnectionFailure as e:
        print(f"Nie można połączyć się z MongoDB: {e}")
        raise


def main():
    """
    Main function to process PDFs and save data to MongoDB.
    """
    try:
        # Load legal fields
        legal_fields = load_legal_fields(LEGAL_FIELDS_FILEPATH)

        # Find PDF files
        pdf_files = find_pdf_files(PDF_ROOT_DIR)
        if not pdf_files:
            print("Ostrzeżenie: Nie znaleziono plików PDF do przetworzenia.")
            return

        # Connect to MongoDB
        client = connect_to_mongodb(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        for pdf_path in pdf_files:
            print(f"Przetwarzanie pliku: {pdf_path}")
            text = extract_text_from_pdf(pdf_path)

            if not text:
                print(f"Pominięto plik {pdf_path} z powodu braku tekstu.")
                continue

            # Korekta tekstu
            corrected_text = correct_text(text)

            if not corrected_text:
                print(f"Pominięto plik {pdf_path} z powodu błędu korekty tekstu.")
                continue

            # Klasyfikacja dziedziny prawa
            legal_field = classify_legal_field(corrected_text, legal_fields)

            # Zapis do MongoDB
            save_to_mongodb_binary(collection, pdf_path, legal_field)

        print("Przetwarzanie plików PDF zakończone pomyślnie.")

    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")


if __name__ == "__main__":
    main()
