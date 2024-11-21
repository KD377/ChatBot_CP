import React, { useState } from 'react';
import axios from 'axios';
import './css/SetYears.css';

function SetYears() {
  const [years, setYears] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSetYears = async () => {
    if (!years.trim()) {
      setError('Proszę wpisać lata w poprawnym formacie.');
      setMessage('');
      return;
    }

    setIsLoading(true);
    setMessage('');
    setError('');

    try {
      const yearsArray = years
        .split(',')
        .map(year => parseInt(year.trim()))
        .filter(year => !isNaN(year));

      if (yearsArray.length === 0) {
        throw new Error('Wprowadź przynajmniej jeden poprawny rok.');
      }

      const response = await axios.post('http://127.0.0.1:8000/set_years', { years: yearsArray });
      setMessage(response.data.message);
    } catch (err) {
      setError(err.response ? err.response.data.detail : 'Wystąpił błąd. Spróbuj ponownie.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="set-years">
      <h2>Ustaw Zakres Lat</h2>
      <input
        type="text"
        value={years}
        onChange={(e) => setYears(e.target.value)}
        placeholder="Wpisz lata, np. 1918, 2024"
      />
      <button onClick={handleSetYears} disabled={isLoading}>
        {isLoading ? 'Przetwarzanie...' : 'Ustaw Lata'}
      </button>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default SetYears;
