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
