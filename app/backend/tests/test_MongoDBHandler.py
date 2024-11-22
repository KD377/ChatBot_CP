import unittest
from unittest.mock import patch, MagicMock
from app.backend.MongoDBHandler import MongoDBHandler
import bson


class TestMongoDBHandler(unittest.TestCase):
    @patch('app.backend.MongoDBHandler.MongoClient')
    def setUp(self, mock_mongo_client):
        # Setup mock
        self.mock_client = MagicMock()
        mock_mongo_client.return_value = self.mock_client
        self.db_name = 'test_db'
        self.collection_name = 'test_collection'
        self.handler = MongoDBHandler(db_name=self.db_name, collection_name=self.collection_name)
        self.mock_collection = self.mock_client[self.db_name][self.collection_name]

    def test_get_all_documents(self):
        # Mock data
        mock_docs = [{'file_name': 'doc1.pdf'}, {'file_name': 'doc2.pdf'}]
        self.mock_collection.find.return_value = mock_docs

        result = self.handler.get_all_documents()
        self.mock_collection.find.assert_called_once()
        self.assertEqual(result, mock_docs)

    def test_get_document_by_file_name_found(self):
        mock_doc = {'file_name': 'doc1.pdf'}
        self.mock_collection.find_one.return_value = mock_doc

        result = self.handler.get_document_by_file_name('doc1.pdf')
        self.mock_collection.find_one.assert_called_with({'file_name': 'doc1.pdf'})
        self.assertEqual(result, mock_doc)

    def test_get_document_by_file_name_not_found(self):
        self.mock_collection.find_one.return_value = None

        result = self.handler.get_document_by_file_name('nonexistent.pdf')
        self.mock_collection.find_one.assert_called_with({'file_name': 'nonexistent.pdf'})
        self.assertIsNone(result)

    def test_save_pdf_from_database_success(self):
        binary_content = b'%PDF-1.4...'
        mock_doc = {'file_name': 'doc1.pdf', 'file_data': bson.Binary(binary_content)}
        self.mock_collection.find_one.return_value = mock_doc

        with patch('builtins.open', unittest.mock.mock_open()) as mocked_file:
            self.handler.save_pdf_from_database('doc1.pdf', '/fake/output/dir')
            self.mock_collection.find_one.assert_called_with({'file_name': 'doc1.pdf'})
            mocked_file.assert_called_with('/fake/output/dir/doc1.pdf', 'wb')
            mocked_file().write.assert_called_with(bson.Binary(binary_content))

    def test_save_pdf_from_database_document_not_found(self):
        self.mock_collection.find_one.return_value = None

        with patch('builtins.print') as mocked_print:
            self.handler.save_pdf_from_database('nonexistent.pdf', '/fake/output/dir')
            self.mock_collection.find_one.assert_called_with({'file_name': 'nonexistent.pdf'})
            mocked_print.assert_called_with("Document not found or does not contain file data.")

    def test_delete_document_success(self):
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        self.mock_collection.delete_one.return_value = mock_result

        with patch('builtins.print') as mocked_print:
            self.handler.delete_document('doc1.pdf')
            self.mock_collection.delete_one.assert_called_with({'file_name': 'doc1.pdf'})
            mocked_print.assert_called_with("Document deleted successfully.")

    def test_delete_document_not_found(self):
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        self.mock_collection.delete_one.return_value = mock_result

        with patch('builtins.print') as mocked_print:
            self.handler.delete_document('nonexistent.pdf')
            self.mock_collection.delete_one.assert_called_with({'file_name': 'nonexistent.pdf'})
            mocked_print.assert_called_with("Document not found.")

    def test_get_text_from_binary_pdf_success(self):
        # Mock document with binary PDF data
        binary_content = b'%PDF-1.4...'
        mock_doc = {'file_name': 'doc1.pdf', 'file_data': bson.Binary(binary_content)}
        self.mock_collection.find_one.return_value = mock_doc

        with patch('fitz.open') as mock_fitz_open:
            mock_doc_obj = MagicMock()
            mock_page = MagicMock()
            mock_page.get_text.return_value = "Sample text"
            mock_doc_obj.__iter__.return_value = [mock_page]
            mock_fitz_open.return_value.__enter__.return_value = mock_doc_obj

            result = self.handler.get_text_from_binary_pdf('doc1.pdf')
            self.mock_collection.find_one.assert_called_with({'file_name': 'doc1.pdf'}, {'file_data': 1})
            mock_fitz_open.assert_called_with(stream=bson.Binary(binary_content), filetype="pdf")  # Corrected

            self.assertEqual(result, "Sample text")

    def test_get_text_from_binary_pdf_document_not_found(self):
        self.mock_collection.find_one.return_value = None

        with patch('builtins.print') as mocked_print:
            result = self.handler.get_text_from_binary_pdf('nonexistent.pdf')
            self.mock_collection.find_one.assert_called_with({'file_name': 'nonexistent.pdf'}, {'file_data': 1})
            mocked_print.assert_called_with("Dokument nie został znaleziony lub nie zawiera danych pliku.")
            self.assertIsNone(result)

    def test_get_files_by_legal_field(self):
        mock_docs = [{'file_name': 'doc1.pdf'}, {'file_name': 'doc2.pdf'}]
        self.mock_collection.find.return_value = mock_docs

        result = self.handler.get_files_by_legal_field('Some Legal Field')
        self.mock_collection.find.assert_called_with({'legal_field': 'Some Legal Field'}, {'file_name': 1})
        self.assertEqual(result, ['doc1.pdf', 'doc2.pdf'])


if __name__ == '__main__':
    unittest.main()
