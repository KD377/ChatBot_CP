import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.backend.main import app

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    yield


@patch('app.backend.main.LanguageModelService.get_model_response')
def test_valid_question(mock_get_model_response):
    mock_get_model_response.return_value = "Próbna odpowiedź na potrzeby testów"

    question = "Co grozi za nierozliczenie podatku VAT w terminie?"

    response = client.post("/ask", json={"question": question})

    assert response.status_code == 200
    assert response.json()["answer"] == "Próbna odpowiedź na potrzeby testów"
    mock_get_model_response.assert_called_once_with(question)


@patch('app.backend.main.LanguageModelService.get_model_response')
def test_valid_question_without_sense(mock_get_model_response):
    mock_get_model_response.return_value = "Próbna odpowiedź na potrzeby testów"

    question = "Co najlepiej zjeść na obiad urodiznowy cioci?"

    response = client.post("/ask", json={"question": question})

    assert response.status_code == 200
    assert response.json()["answer"] is not None
    mock_get_model_response.assert_called_once_with(question)


@patch('app.backend.main.LanguageModelService.get_model_response')
def test_empty_string_question_provided(mock_get_model_response):
    response = client.post("/ask", json={"question": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "Nieprawidłowy format 'question'."

    mock_get_model_response.assert_not_called()


@patch('app.backend.main.LanguageModelService.get_model_response')
def test_unprocessable_entity(mock_get_model_response):
    response = client.post("/ask", json={"differentElement": ""})

    assert response.status_code == 422
    mock_get_model_response.assert_not_called()
    assert response.json() is not None


@patch('app.backend.main.LanguageModelService.get_model_response')
def test_question_is_not_of_type_str(mock_get_model_response):
    response = client.post("/ask", json={"question": 2000})

    assert response.status_code == 422
    mock_get_model_response.assert_not_called()
    assert response.json() is not None


@patch('app.backend.main.LanguageModelService.get_model_response')
def test_question_is_too_long(mock_get_model_response):
    long_question = "A" * 2001
    response = client.post("/ask", json={"question": long_question})

    assert response.status_code == 400
    assert response.json()["detail"] == "Zbyt długie pytanie."
    mock_get_model_response.assert_not_called()


@patch('app.backend.main.LanguageModelService.get_model_response')
def test_ask_question_no_answer(mock_get_model_response):
    mock_get_model_response.return_value = None

    question = "What happens if no response is generated?"
    response = client.post("/ask", json={"question": question})

    assert response.status_code == 204

    mock_get_model_response.assert_called_once_with(question)


@patch('app.backend.main.LanguageModelService.get_model_response')
def test_ask_question_internal_server_error(mock_get_model_response):
    mock_get_model_response.side_effect = Exception("Simulated internal error")

    question = "What happens in case of an unexpected error?"

    response = client.post("/ask", json={"question": question})

    assert response.status_code == 500
    assert response.json()["detail"] == "Wewnętrzny błąd serwera"

    mock_get_model_response.assert_called_once_with(question)


def test_set_years_valid_request():
    response = client.post("/set_years", json={"years": [2020, 2021, 2022]})

    assert response.status_code == 200

    assert response.json() == {
        "message": "Zakres lat został ustawiony.",
        "years": [2020, 2021, 2022]
    }


def test_set_years_empty_list():
    response = client.post("/set_years", json={"years": []})

    assert response.status_code == 400

    assert response.json()["detail"] == "Nieprawidłowy format 'years'."


def test_set_years_not_a_list():
    response = client.post("/set_years", json={"years": "2020"})

    assert response.status_code == 422
    assert response.json() is not None


def test_set_years_with_string():
    response = client.post("/set_years", json={"years": [2020, "2021", 2022]})
    assert response.status_code == 422


def test_set_years_contains_restricted_year():
    response = client.post("/set_years", json={"years": [2020, 1940, 2022]})

    assert response.status_code == 400

    assert response.json()["detail"] == "Lata 1940, 1941, 1942, 1943 są niedostępne."


def test_set_years_missing_years_key():
    response = client.post("/set_years", json={})

    assert response.status_code == 422
