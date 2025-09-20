import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSpeechRecorder } from './hooks/useSpeechRecorder.js';

const API_BASE = '/api/sessions';

function wordsCount(text) {
  if (!text) {
    return 0;
  }
  return text.trim().split(/\s+/u).length;
}

export default function App() {
  const {
    isSupported,
    isRecording,
    transcript,
    startRecording,
    stopRecording,
    resetTranscript,
    error,
    language,
    setLanguage
  } = useSpeechRecorder();

  const [notes, setNotes] = useState('');
  const [hasManualEdits, setHasManualEdits] = useState(false);
  const [title, setTitle] = useState('');
  const [session, setSession] = useState(null);
  const [summary, setSummary] = useState('');
  const [quiz, setQuiz] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [games, setGames] = useState({ wordScramble: [], flashcards: [] });
  const [loading, setLoading] = useState({ summary: false, quiz: false, qa: false, games: false });
  const [statusMessage, setStatusMessage] = useState('');

  useEffect(() => {
    const lastSession = window.localStorage.getItem('omega:lastSession');
    if (lastSession) {
      const parsed = JSON.parse(lastSession);
      setSession(parsed);
      setTitle(parsed.title);
      setNotes(parsed.transcript);
    }
  }, []);

  useEffect(() => {
    if (!hasManualEdits) {
      setNotes(transcript);
    }
  }, [transcript, hasManualEdits]);

  const handleStartRecording = () => {
    setHasManualEdits(false);
    setSummary('');
    setQuiz([]);
    setAnswer('');
    setGames({ wordScramble: [], flashcards: [] });
    setStatusMessage('Début de la capture en direct…');
    startRecording();
  };

  const handleStopRecording = () => {
    stopRecording();
    setStatusMessage('Capture terminée. Relisez vos notes puis enregistrez-les.');
  };

  const handleReset = () => {
    resetTranscript();
    setNotes('');
    setHasManualEdits(false);
    setSession(null);
    setSummary('');
    setQuiz([]);
    setAnswer('');
    setQuestion('');
    setGames({ wordScramble: [], flashcards: [] });
    window.localStorage.removeItem('omega:lastSession');
    setStatusMessage('Nouvelle session prête.');
  };

  const saveSession = useCallback(async () => {
    if (!notes) {
      setStatusMessage('Ajoutez du contenu avant de sauvegarder.');
      return null;
    }
    try {
      const response = await fetch(API_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title || `Cours du ${new Date().toLocaleDateString('fr-FR')}`,
          transcript: notes,
          metadata: {
            words: wordsCount(notes),
            source: 'web-speech',
            capturedAt: new Date().toISOString()
          }
        })
      });
      if (!response.ok) {
        throw new Error('Impossible de sauvegarder la session.');
      }
      const payload = await response.json();
      setSession(payload);
      window.localStorage.setItem('omega:lastSession', JSON.stringify(payload));
      setStatusMessage('Session enregistrée localement.');
      return payload;
    } catch (err) {
      setStatusMessage(err.message);
      return null;
    }
  }, [notes, title]);

  const ensureSession = useCallback(async () => {
    if (session) {
      return session;
    }
    const fresh = await saveSession();
    return fresh;
  }, [session, saveSession]);

  const callEndpoint = useCallback(
    async (path, stateKey, onSuccess) => {
      const activeSession = await ensureSession();
      if (!activeSession) {
        return;
      }
      setLoading((prev) => ({ ...prev, [stateKey]: true }));
      setStatusMessage('Communication avec le serveur…');
      try {
        const response = await fetch(`${API_BASE}/${activeSession.id}/${path}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: path === 'questions' ? JSON.stringify({ question }) : undefined
        });
        if (!response.ok) {
          throw new Error('Requête IA indisponible actuellement.');
        }
        const result = await response.json();
        onSuccess(result);
        setStatusMessage('Opération IA terminée.');
      } catch (err) {
        setStatusMessage(err.message);
      } finally {
        setLoading((prev) => ({ ...prev, [stateKey]: false }));
      }
    },
    [ensureSession, question]
  );

  const handleSummary = () => {
    callEndpoint('summary', 'summary', ({ summary: content }) => {
      setSummary(content);
    });
  };

  const handleQuiz = () => {
    callEndpoint('quiz', 'quiz', ({ quiz: data }) => {
      setQuiz(data);
    });
  };

  const handleQuestion = () => {
    if (!question) {
      setStatusMessage('Entrez une question.');
      return;
    }
    callEndpoint('questions', 'qa', ({ answer: text }) => {
      setAnswer(text);
    });
  };

  const handleGames = () => {
    callEndpoint('games', 'games', (payload) => {
      setGames(payload);
    });
  };

  const derivedStats = useMemo(() => ({
    characters: notes.length,
    words: wordsCount(notes)
  }), [notes]);

  return (
    <div className="layout">
      <header>
        <h1>Omega Study</h1>
        <p>Un bloc-notes académique boosté à l'IA, optimisé pour minimiser l'usage de crédits cloud.</p>
      </header>

      {!isSupported && (
        <section>
          <p>
            Votre navigateur ne supporte pas la reconnaissance vocale Web. Vous pouvez tout de même coller vos
            notes manuellement puis utiliser les outils IA.
          </p>
          {error && <p>{error}</p>}
        </section>
      )}

      <section>
        <div className="controls">
          <button
            type="button"
            className="primary-btn"
            onClick={isRecording ? handleStopRecording : handleStartRecording}
            disabled={!isSupported}
          >
            {isRecording ? 'Arrêter la capture' : 'Démarrer la capture'}
          </button>
          <button type="button" className="secondary-btn" onClick={handleReset}>
            Réinitialiser
          </button>
          <button
            type="button"
            className="secondary-btn"
            onClick={() => {
              setHasManualEdits(false);
              setNotes(transcript);
            }}
          >
            Synchroniser avec l'audio
          </button>
          <select
            aria-label="Langue de transcription"
            className="secondary-btn"
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
          >
            <option value="fr-FR">Français</option>
            <option value="en-US">Anglais</option>
            <option value="es-ES">Espagnol</option>
          </select>
        </div>

        <input
          type="text"
          value={title}
          placeholder="Titre du cours"
          onChange={(event) => setTitle(event.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            borderRadius: '0.85rem',
            border: '1px solid rgba(148, 163, 184, 0.25)',
            background: 'rgba(15, 23, 42, 0.75)',
            color: '#e2e8f0',
            marginBottom: '0.75rem'
          }}
        />

        <textarea
          value={notes}
          onChange={(event) => {
            setNotes(event.target.value);
            setHasManualEdits(true);
          }}
          placeholder="Le cours s'affichera ici en temps réel. Vous pouvez corriger librement le texte."
        />
        <div className="status-bar">
          <span>{statusMessage}</span>
          <span>
            {derivedStats.words} mots · {derivedStats.characters} caractères
          </span>
        </div>
        <div className="controls" style={{ marginTop: '1rem' }}>
          <button type="button" className="primary-btn" onClick={saveSession}>
            Sauvegarder le cours
          </button>
          <button type="button" className="secondary-btn" onClick={handleSummary} disabled={loading.summary}>
            {loading.summary ? 'Résumé en cours…' : 'Résumé IA'}
          </button>
          <button type="button" className="secondary-btn" onClick={handleQuiz} disabled={loading.quiz}>
            {loading.quiz ? 'Quiz en cours…' : 'Générer un quiz'}
          </button>
          <button type="button" className="secondary-btn" onClick={handleGames} disabled={loading.games}>
            {loading.games ? 'Préparation…' : 'Créer des jeux'}
          </button>
        </div>
      </section>

      <section className="summary">
        <h2>Résumé intelligent</h2>
        {summary ? <p>{summary}</p> : <p>Lancez un résumé pour obtenir une synthèse optimisée.</p>}
      </section>

      <section className="quiz">
        <h2>Quiz adaptatif</h2>
        {quiz.length > 0 ? (
          <div className="quiz-list">
            {quiz.map((item) => (
              <div className="quiz-item" key={item.id}>
                <strong>Question:</strong> {item.question}
                <br />
                <strong>Réponse suggérée:</strong> {item.answer}
              </div>
            ))}
          </div>
        ) : (
          <p>Aucun quiz généré pour l'instant.</p>
        )}
      </section>

      <section className="qa">
        <h2>Questions instantanées</h2>
        <div className="controls">
          <input
            type="text"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Posez une question sur le cours sauvegardé"
            style={{
              flex: 1,
              minWidth: '200px',
              padding: '0.75rem 1rem',
              borderRadius: '0.85rem',
              border: '1px solid rgba(148, 163, 184, 0.25)',
              background: 'rgba(15, 23, 42, 0.75)',
              color: '#e2e8f0'
            }}
          />
          <button type="button" className="primary-btn" onClick={handleQuestion} disabled={loading.qa}>
            {loading.qa ? 'Réflexion…' : 'Répondre'}
          </button>
        </div>
        {answer && <p>{answer}</p>}
      </section>

      <section className="games">
        <h2>Jeux pédagogiques</h2>
        <div className="games-grid">
          <div>
            <h3>Mots mêlés</h3>
            {games.wordScramble.length > 0 ? (
              <ul>
                {games.wordScramble.map((entry) => (
                  <li key={entry.original}>
                    {entry.scrambled} <span style={{ color: '#38bdf8' }}>({entry.original})</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>Aucun mot généré.</p>
            )}
          </div>
          <div>
            <h3>Flashcards</h3>
            {games.flashcards.length > 0 ? (
              <ul>
                {games.flashcards.map((card) => (
                  <li key={card.term}>
                    <strong>{card.term}</strong> — {card.hint || 'Indice à compléter'}
                  </li>
                ))}
              </ul>
            ) : (
              <p>Pas encore de flashcards.</p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
