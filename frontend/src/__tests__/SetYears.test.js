// src/Components/SetYears.test.js
import React from 'react';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import SetYears from '../Components/SetYears';

jest.mock('axios');

describe('Komponent SetYears', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renderuje poprawnie', () => {
    render(<SetYears />);
    expect(screen.getByRole('heading', { name: 'Ustaw Zakres Lat' })).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Wpisz lata, np. 1918, 2024')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ustaw Lata' })).toBeInTheDocument();
  });

  test('pokazuje błąd przy pustym inputie', () => {
    render(<SetYears />);
    fireEvent.click(screen.getByRole('button', { name: 'Ustaw Lata' }));
    expect(screen.getByText('Proszę wpisać lata w poprawnym formacie.')).toBeInTheDocument();
  });

  test('wysyła poprawne dane do API i wyświetla komunikat sukcesu', async () => {
    axios.post.mockResolvedValue({
      data: { message: 'Zakres lat został ustawiony.' },
    });

    render(<SetYears />);

    fireEvent.change(screen.getByPlaceholderText('Wpisz lata, np. 1918, 2024'), {
      target: { value: '1918, 2024' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Ustaw Lata' }));

    expect(screen.getByRole('button', { name: 'Przetwarzanie...' })).toBeDisabled();

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('http://127.0.0.1:8000/set_years', {
        years: [1918, 2024],
      });
    });

    expect(await screen.findByText('Zakres lat został ustawiony.')).toBeInTheDocument();
  });

  test('obsługuje błędy z API', async () => {
    axios.post.mockRejectedValue({
      response: { data: { detail: 'Błąd serwera' } },
    });

    render(<SetYears />);

    fireEvent.change(screen.getByPlaceholderText('Wpisz lata, np. 1918, 2024'), {
      target: { value: '1918, 2024' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Ustaw Lata' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalled();
    });

    expect(await screen.findByText('Błąd serwera')).toBeInTheDocument();
  });
});
