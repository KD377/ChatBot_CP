import React, { useState } from 'react';
import axios from 'axios';
import './css/AskQuestion.css';

function AskQuestion() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      setError('Proszę wpisać pytanie.');
      return;
    }

    setIsLoading(true);
    setError('');
    setAnswer('');
    try {
      const response = await axios.post('http://127.0.0.1:8000/ask', { question });
      setAnswer(response.data.answer);
    } catch (err) {
      setError(err.response ? err.response.data.detail : 'Wystąpił błąd. Spróbuj ponownie.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="ask-question">
      <h2>Zadaj Pytanie</h2>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Wpisz swoje pytanie..."
        maxLength={500}
      />
      <button onClick={handleAskQuestion} disabled={isLoading}>
        {isLoading ? 'Wysyłanie...' : 'Zadaj Pytanie'}
      </button>
      {answer && <p className="answer">Odpowiedź: {answer}</p>}
      {error && <p className="error">Błąd: {error}</p>}
    </div>
  );
}

export default AskQuestion;
