import os
import json
import fitz
from pymongo import MongoClient
from cleantext import clean
import language_tool_python
import nltk
from nltk.corpus import stopwords

# Download necessary NLTK data
nltk.download('stopwords')

# Manually define Polish stopwords (since NLTK lacks them)
POLISH_STOPWORDS = {
    "i", "oraz", "ponieważ", "ale", "że", "który", "tego", "mnie", "ją", "on", "ona",
    "to", "się", "czy", "jest", "jak", "dla", "do", "z", "od", "po", "na", "za",
    "bez", "by", "tym", "o", "przy", "jeśli"
}


def find_pdf_files(root_dir):
    """Find all PDF files in the specified directory."""
    pdf_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def correct_text(text):
    """Clean and correct text using cleantext and LanguageTool."""
    # Clean the text with cleantext
    text = clean(
        text,
        clean_all=False,
        extra_spaces=True,
        stemming=False,
        stopwords=False,  # We handle stopwords manually
        lowercase=False,
        numbers=False,
        punct=False,
        reg='',
        reg_replace='',
        stp_lang=None  # Avoid default stopwords
    )

    # Remove Polish stopwords manually
    words = text.split()
    filtered_text = " ".join(word for word in words if word.lower() not in POLISH_STOPWORDS)

    # Perform grammar correction using language_tool_python
    tool = language_tool_python.LanguageTool('pl-PL')
    matches = tool.check(filtered_text)
    corrected_text = language_tool_python.utils.correct(filtered_text, matches)

    return corrected_text


def save_to_mongodb(collection, pdf_path, keywords):
    """Save metadata and keywords of a PDF to MongoDB."""
    document = {
        'file_path': pdf_path,
        'keywords': keywords
    }
    collection.insert_one(document)


def save_to_mongodb_binary(collection, pdf_path, legal_field):
    """Save binary PDF data and legal field classification to MongoDB."""
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
    """Load legal fields and their keywords from a JSON file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist.")

    with open(filepath, 'r', encoding='utf-8') as file:
        legal_fields = json.load(file)
    return legal_fields


def classify_legal_field(text, filepath='./legal_fields/key_words_legal_fields.json'):
    """Classify the legal field of the given text."""
    legal_fields = load_legal_fields(filepath)
    field_counts = {field: 0 for field in legal_fields}

    for field, keywords in legal_fields.items():
        for keyword in keywords:
            if keyword in text.lower():
                field_counts[field] += 1

    max_field = max(field_counts, key=field_counts.get)
    if field_counts[max_field] == 0:
        return "Unknown Legal Field"

    print(field_counts)
    return max_field


def main():
    """Main function to process PDFs and save data to MongoDB."""
    root_dir = './dziennik_ustaw'  # Adjusted to match container structure
    pdf_files = find_pdf_files(root_dir)

    print(f"Found {len(pdf_files)} PDF files.")

    # Connect to MongoDB
    client = MongoClient('mongodb://mongo:27017/')  # Use container name for MongoDB
    db = client['legal_database']
    collection = db['laws']

    for pdf_path in pdf_files:
        print(f"Processing file: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)

        # Correct text
        corrected_text = correct_text(text)

        # Classify legal field
        legal_field = classify_legal_field(corrected_text)

        # Save to MongoDB
        save_to_mongodb_binary(collection, pdf_path, legal_field)


if __name__ == "__main__":
    main()
