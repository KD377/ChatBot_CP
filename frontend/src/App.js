import React from 'react';
import SetYears from './Components/SetYears';
import AskQuestion from './Components/AskQuestion';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Aplikacja Pytania i Odpowiedzi</h1>
      </header>
      <main className="app-main">
        <SetYears />
        <AskQuestion />
      </main>
    </div>
  );
}

export default App;
