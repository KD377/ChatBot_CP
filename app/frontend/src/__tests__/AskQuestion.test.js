import React from 'react';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import AskQuestion from '../Components/AskQuestion';

jest.mock('axios');

describe('Komponent AskQuestion', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renderuje poprawnie', () => {
    render(<AskQuestion />);
    expect(screen.getByRole('heading', { name: 'Zadaj Pytanie' })).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Wpisz swoje pytanie...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Zadaj Pytanie' })).toBeInTheDocument();
  });

  test('pokazuje błąd przy pustym pytaniu', () => {
    render(<AskQuestion />);
    fireEvent.click(screen.getByRole('button', { name: 'Zadaj Pytanie' }));
    expect(screen.getByText('Błąd: Proszę wpisać pytanie.')).toBeInTheDocument();
  });

  test('wysyła poprawne dane do API i wyświetla odpowiedź', async () => {
    axios.post.mockResolvedValue({
      data: { answer: 'To jest odpowiedź na Twoje pytanie.' },
    });

    render(<AskQuestion />);

    fireEvent.change(screen.getByPlaceholderText('Wpisz swoje pytanie...'), {
      target: { value: 'Jakie jest dzisiaj święto?' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Zadaj Pytanie' }));

    expect(screen.getByRole('button', { name: 'Wysyłanie...' })).toBeDisabled();

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('http://127.0.0.1:8000/ask', {
        question: 'Jakie jest dzisiaj święto?',
      });
    });

    expect(await screen.findByText('Odpowiedź: To jest odpowiedź na Twoje pytanie.')).toBeInTheDocument();
  });

  test('obsługuje błędy z API', async () => {
    axios.post.mockRejectedValue({
      response: { data: { detail: 'Błąd serwera' } },
    });

    render(<AskQuestion />);

    fireEvent.change(screen.getByPlaceholderText('Wpisz swoje pytanie...'), {
      target: { value: 'Jakie jest dzisiaj święto?' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Zadaj Pytanie' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalled();
    });

    expect(await screen.findByText('Błąd: Błąd serwera')).toBeInTheDocument();
  });
});
