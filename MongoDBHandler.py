import os
import fitz
from pymongo import MongoClient


class MongoDBHandler:
    def __init__(self, db_name='moja_baza', collection_name='ustawy'):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_all_documents(self):
        return list(self.collection.find())

    def get_document_by_file_name(self, file_name):
        return self.collection.find_one({'file_name': file_name})

    def get_documents_by_keyword(self, keyword):
        return list(self.collection.find({'keywords': keyword}))

    def save_pdf_from_database(self, file_name, output_dir):
        document = self.collection.find_one({'file_name': file_name})
        if document and 'file_data' in document:
            binary_data = document['file_data']
            output_path = os.path.join(output_dir, file_name)
            with open(output_path, 'wb') as f:
                f.write(binary_data)
            print(f"File saved to {output_path}")
        else:
            print("Document not found or does not contain file data.")

    def update_document_keywords(self, file_name, new_keywords):
        result = self.collection.update_one(
            {'file_name': file_name},
            {'$set': {'keywords': new_keywords}}
        )
        if result.modified_count > 0:
            print("Keywords updated successfully.")
        else:
            print("Document not found or keywords already up to date.")

    def delete_document(self, file_name):
        result = self.collection.delete_one({'file_name': file_name})
        if result.deleted_count > 0:
            print("Document deleted successfully.")
        else:
            print("Document not found.")

    def create_text_index(self):
        self.collection.create_index([('keywords', 'text')])

    def search_documents_by_text(self, search_text):
        return list(self.collection.find({'$text': {'$search': search_text}}))


    # Pobiera plik PDF jako dane binarne z bazy danych i zwraca jego zawartość tekstową.
    def get_text_from_binary_pdf(self, file_name):
        document = self.collection.find_one({'file_name': file_name}, {'file_data': 1})
        if not document or 'file_data' not in document:
            print("Dokument nie został znaleziony lub nie zawiera danych pliku.")
            return None

        pdf_data = document['file_data']
        text = ""
        with fitz.open(stream=pdf_data, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()

        return text

