import unittest
from unittest.mock import patch, mock_open, MagicMock
from app.backend.helpers.load_pdfs import (
    find_pdf_files,
    extract_text_from_pdf,
    save_to_mongodb,
    save_to_mongodb_binary,
    load_legal_fields,
    classify_legal_field
)
import bson


class TestLoadPdfs(unittest.TestCase):
    @patch('os.walk')
    def test_find_pdf_files(self, mock_walk):
        # Mock os.walk to return a predefined file structure
        mock_walk.return_value = [
            ('/fake/dir', ('subdir',), ('file1.pdf', 'file2.txt')),
            ('/fake/dir/subdir', (), ('file3.PDF', 'file4.doc'))
        ]
        expected = ['/fake/dir/file1.pdf', '/fake/dir/subdir/file3.PDF']
        result = find_pdf_files('/fake/dir')
        self.assertEqual(result, expected)

    @patch('fitz.open')
    def test_extract_text_from_pdf(self, mock_fitz_open):
        # Mock PDF text extraction
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page text"
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        result = extract_text_from_pdf('/fake/file.pdf')
        mock_fitz_open.assert_called_with('/fake/file.pdf')
        self.assertEqual(result, "Page text")

    @patch('app.backend.helpers.load_pdfs.MongoClient')
    def test_save_to_mongodb(self, mock_mongo_client):
        mock_collection = MagicMock()
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_collection
        mock_mongo_client.return_value = mock_client

        # Assuming default db and collection names
        save_to_mongodb(mock_collection, '/fake/file.pdf', ['keyword1', 'keyword2'])
        mock_collection.insert_one.assert_called_with({
            'file_path': '/fake/file.pdf',
            'keywords': ['keyword1', 'keyword2']
        })

    @patch('builtins.open', new_callable=mock_open, read_data=b'%PDF-1.4...')
    def test_save_to_mongodb_binary(self, mock_file):
        mock_collection = MagicMock()
        save_to_mongodb_binary(mock_collection, '/fake/file.pdf', 'Some Legal Field')

        mock_file.assert_called_with('/fake/file.pdf', 'rb')  # Corrected to full path
        mock_collection.insert_one.assert_called_once()

        args, kwargs = mock_collection.insert_one.call_args
        inserted_document = args[0]
        self.assertEqual(inserted_document['file_name'], 'file.pdf')
        self.assertIsInstance(inserted_document['file_data'], bson.Binary)
        self.assertEqual(inserted_document['legal_field'], 'Some Legal Field')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"Field1": ["keyword1", "keyword2"]}')
    def test_load_legal_fields_exists(self, mock_file, mock_exists):
        mock_exists.return_value = True
        result = load_legal_fields('./helpers/legal_fields/key_words_legal_fields.json')
        mock_file.assert_called_with('./helpers/legal_fields/key_words_legal_fields.json', 'r', encoding='utf-8')
        self.assertEqual(result, {"Field1": ["keyword1", "keyword2"]})

    @patch('os.path.exists')
    def test_load_legal_fields_not_exists(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            load_legal_fields('./helpers/legal_fields/key_words_legal_fields.json')

    @patch('app.backend.helpers.load_pdfs.load_legal_fields')
    def test_classify_legal_field(self, mock_load_legal_fields):
        mock_load_legal_fields.return_value = {
            "Finance": ["tax", "budget"],
            "Health": ["medicine", "hospital"]
        }

        text = "The government announced a new tax reform."
        expected_field = "Finance"
        with patch('builtins.print') as mocked_print:
            result = classify_legal_field(text)
            self.assertEqual(result, expected_field)
            mocked_print.assert_called_with({'Finance': 1, 'Health': 0})

    @patch('app.backend.helpers.load_pdfs.load_legal_fields')
    def test_classify_legal_field_no_match(self, mock_load_legal_fields):
        mock_load_legal_fields.return_value = {
            "Finance": ["tax", "budget"],
            "Health": ["medicine", "hospital"]
        }

        text = "This text does not match any keywords."
        expected_field = "Nieznana dziedzina prawa"
        with patch('builtins.print') as mocked_print:
            result = classify_legal_field(text)
            self.assertEqual(result, expected_field)
            mocked_print.assert_not_called()


if __name__ == '__main__':
    unittest.main()
