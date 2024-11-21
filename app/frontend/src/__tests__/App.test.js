import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('Komponent App', () => {
  test('renderuje nagłówek i komponenty główne', () => {
    render(<App />);
    expect(
      screen.getByRole('heading', { name: 'Aplikacja Pytania i Odpowiedzi' })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: 'Ustaw Zakres Lat' })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: 'Zadaj Pytanie' })
    ).toBeInTheDocument();
  });
});