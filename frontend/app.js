const elements = {
  recordButton: document.getElementById('recordButton'),
  stopButton: document.getElementById('stopButton'),
  exportButton: document.getElementById('exportButton'),
  tagButton: document.getElementById('tagButton'),
  clearButton: document.getElementById('clearButton'),
  transcript: document.getElementById('transcript'),
  tagList: document.getElementById('tagList'),
  statDuration: document.getElementById('statDuration'),
  statWords: document.getElementById('statWords'),
  statSections: document.getElementById('statSections'),
  statLastTag: document.getElementById('statLastTag'),
  suggestionList: document.getElementById('suggestionList'),
  summaryTone: document.getElementById('summaryTone'),
  summaryOutput: document.getElementById('summaryOutput'),
  quizCount: document.getElementById('quizCount'),
  quizOutput: document.getElementById('quizOutput'),
  questionInput: document.getElementById('questionInput'),
  questionOutput: document.getElementById('questionOutput'),
  gamesOutput: document.getElementById('gamesOutput'),
  summaryButton: document.getElementById('summaryButton'),
  quizButton: document.getElementById('quizButton'),
  questionButton: document.getElementById('questionButton'),
  gamesButton: document.getElementById('gamesButton'),
  sessionList: document.getElementById('sessionList'),
  toast: document.getElementById('toast'),
  recordingBadge: document.getElementById('recordingBadge'),
  sessionStatus: document.getElementById('sessionStatus'),
  meterDuration: document.getElementById('meterDuration'),
  meterWords: document.getElementById('meterWords'),
  meterTags: document.getElementById('meterTags'),
  themeToggle: document.getElementById('themeToggle'),
  year: document.getElementById('year'),
  waveform: document.getElementById('waveform')
};

const state = {
  recognition: null,
  isRecording: false,
  transcript: '',
  interim: '',
  tags: [],
  startTime: null,
  timerInterval: null,
  waveAnimation: null,
  backendAvailable: false,
  sessionId: null,
  cache: loadCache(),
  sessions: loadSessions(),
  backendId: null,
  lastSuggestionUpdate: 0
};

const STORAGE_KEYS = {
  sessions: 'omega.sessions',
  cache: 'omega.cache',
  theme: 'omega.theme'
};

function loadSessions() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.sessions) || '[]');
  } catch (error) {
    console.warn('Impossible de charger les sessions', error);
    return [];
  }
}

function saveSessions() {
  localStorage.setItem(STORAGE_KEYS.sessions, JSON.stringify(state.sessions));
}

function loadCache() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.cache) || '{}');
  } catch (error) {
    console.warn('Impossible de charger le cache', error);
    return {};
  }
}

function saveCache() {
  localStorage.setItem(STORAGE_KEYS.cache, JSON.stringify(state.cache));
}

function stringHash(value) {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(i);
    hash |= 0;
  }
  return hash >>> 0;
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60)
    .toString()
    .padStart(1, '0');
  const secs = Math.floor(seconds % 60)
    .toString()
    .padStart(2, '0');
  return `${mins}:${secs}`;
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add('visible');
  setTimeout(() => {
    elements.toast.classList.remove('visible');
  }, 2600);
}

function updateTranscript(newValue) {
  state.transcript = newValue;
  elements.transcript.value = newValue;
  updateStats();
  scheduleSuggestions();
}

function updateStats() {
  const words = state.transcript.trim().split(/\s+/).filter(Boolean);
  const sections = state.transcript.split(/\n{2,}/).filter((part) => part.trim().length > 0);
  const durationSeconds = state.startTime ? (Date.now() - state.startTime) / 1000 : 0;
  const durationText = formatDuration(durationSeconds);

  elements.statDuration.textContent = durationText;
  elements.statWords.textContent = `${words.length} mot${words.length > 1 ? 's' : ''}`;
  elements.statSections.textContent = sections.length.toString();
  elements.statLastTag.textContent = state.tags.at(-1)?.label ?? '—';
  elements.meterDuration.textContent = durationText;
  elements.meterWords.textContent = words.length.toString();
  elements.meterTags.textContent = state.tags.length.toString();
}

function scheduleSuggestions() {
  const now = Date.now();
  if (now - state.lastSuggestionUpdate < 1200) return;
  state.lastSuggestionUpdate = now;
  const text = state.transcript.trim();
  const suggestions = !text
    ? []
    : buildSuggestions(text).slice(0, 3);

  elements.suggestionList.innerHTML = '';
  suggestions.forEach((suggestion) => {
    const item = document.createElement('li');
    item.textContent = suggestion;
    elements.suggestionList.append(item);
  });
}

function buildSuggestions(text) {
  const sentences = text.split(/(?<=[.!?])\s+/).filter((sentence) => sentence.length > 30);
  const keywords = Array.from(new Set(text.match(/\b[A-ZÀ-Ü][a-zà-ü]+/g) || [])).slice(0, 4);
  const suggestions = [];
  if (sentences.length > 0) {
    suggestions.push('Créer un résumé des points clés du cours.');
  }
  if (keywords.length > 1) {
    suggestions.push(`Demander un quiz sur : ${keywords.join(', ')}.`);
  }
  if (text.length > 600) {
    suggestions.push('Générer des flashcards ou un jeu de révision.');
  }
  if (!suggestions.length) {
    suggestions.push('Ajoutez vos notes ou importez une transcription.');
  }
  return suggestions;
}

function renderTags() {
  elements.tagList.innerHTML = '';
  state.tags.forEach((tag) => {
    const item = document.createElement('li');
    item.innerHTML = `<span>${tag.label}</span>`;
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.setAttribute('aria-label', `Supprimer ${tag.label}`);
    removeButton.textContent = '×';
    removeButton.addEventListener('click', () => removeTag(tag.id));
    item.append(removeButton);
    elements.tagList.append(item);
  });
  updateStats();
}

function addTag() {
  const selectionStart = elements.transcript.selectionStart;
  const selectionEnd = elements.transcript.selectionEnd;
  let snippet = '';
  if (selectionEnd > selectionStart) {
    snippet = elements.transcript.value.slice(selectionStart, selectionEnd).trim();
  }
  const label = prompt(snippet ? 'Tag pour la sélection :' : 'Créer un tag (ex : Concept clé)');
  if (!label) return;
  const tag = {
    id:
      typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : `tag-${Date.now()}-${Math.floor(Math.random() * 10_000)}`,
    label,
    snippet,
    createdAt: new Date().toISOString()
  };
  state.tags.push(tag);
  renderTags();
  showToast('Tag ajouté');
}

function removeTag(tagId) {
  state.tags = state.tags.filter((tag) => tag.id !== tagId);
  renderTags();
}

function clearTranscript() {
  if (!state.transcript) return;
  if (!confirm('Supprimer la transcription actuelle ?')) return;
  updateTranscript('');
  state.tags = [];
  renderTags();
  showToast('Transcription nettoyée');
}

function setupTheme() {
  const applyTheme = (mode) => {
    const root = document.documentElement;
    if (mode === 'light') {
      root.classList.add('dark');
      elements.themeToggle.textContent = 'Mode nuit';
    } else {
      root.classList.remove('dark');
      elements.themeToggle.textContent = 'Mode clair';
    }
    localStorage.setItem(STORAGE_KEYS.theme, mode);
  };

  const saved = localStorage.getItem(STORAGE_KEYS.theme) || 'dark';
  applyTheme(saved);

  elements.themeToggle.addEventListener('click', () => {
    const current = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
    const next = current === 'light' ? 'dark' : 'light';
    applyTheme(next);
  });
}

function startTimer() {
  state.startTime = Date.now();
  if (state.timerInterval) clearInterval(state.timerInterval);
  state.timerInterval = setInterval(() => {
    const elapsedSeconds = (Date.now() - state.startTime) / 1000;
    const formatted = formatDuration(elapsedSeconds);
    elements.statDuration.textContent = formatted;
    elements.meterDuration.textContent = formatted;
  }, 1000);
}

function stopTimer() {
  clearInterval(state.timerInterval);
  state.timerInterval = null;
}

function drawWaveform() {
  const canvas = elements.waveform;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const { width, height } = canvas;
  ctx.clearRect(0, 0, width, height);

  const barCount = 42;
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, 'rgba(106, 123, 255, 0.85)');
  gradient.addColorStop(1, 'rgba(60, 211, 138, 0.75)');

  for (let i = 0; i < barCount; i += 1) {
    const barWidth = width / barCount;
    const x = i * barWidth;
    const noise = Math.random() * (state.isRecording ? 1 : 0.4);
    const barHeight = (Math.sin((Date.now() / 120) + i) * 0.5 + 0.5 + noise) * (height / 1.8);
    ctx.fillStyle = gradient;
    ctx.fillRect(x, (height - barHeight) / 2, barWidth * 0.75, barHeight);
  }

  state.waveAnimation = requestAnimationFrame(drawWaveform);
}

function stopWaveform() {
  if (state.waveAnimation) cancelAnimationFrame(state.waveAnimation);
  state.waveAnimation = null;
  if (!elements.waveform) return;
  const ctx = elements.waveform.getContext('2d');
  if (ctx) {
    ctx.clearRect(0, 0, elements.waveform.width, elements.waveform.height);
  }
}

function updateSessionStatus(text, variant = 'idle') {
  elements.sessionStatus.textContent = text;
  elements.sessionStatus.className = `status-dot status-${variant}`;
}

function ensureSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast('La reconnaissance vocale est indisponible sur ce navigateur.');
    return null;
  }
  if (state.recognition) return state.recognition;

  const recognition = new SpeechRecognition();
  recognition.lang = 'fr-FR';
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    state.isRecording = true;
    elements.recordButton.disabled = true;
    elements.stopButton.disabled = false;
    updateSessionStatus('En cours', 'recording');
    elements.recordingBadge.textContent = 'Enregistrement en cours…';
    startTimer();
    stopWaveform();
    drawWaveform();
  };

  recognition.onerror = (event) => {
    console.error('Erreur de reconnaissance vocale', event.error);
    showToast("L'enregistrement a été interrompu");
    stopRecording();
  };

  recognition.onend = () => {
    state.isRecording = false;
    elements.recordButton.disabled = false;
    elements.stopButton.disabled = true;
    elements.recordingBadge.textContent = '';
    stopWaveform();
    drawWaveform();
    stopTimer();
    updateSessionStatus('Prêt', 'idle');
    persistSession('auto');
  };

  recognition.onresult = (event) => {
    let finalTranscript = state.transcript;
    state.interim = '';
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const result = event.results[i];
      const text = result[0].transcript.trim();
      if (result.isFinal && text) {
        finalTranscript = `${finalTranscript} ${text}`.trim();
      } else if (!result.isFinal && text) {
        state.interim = `${state.interim} ${text}`.trim();
      }
    }
    updateTranscript(finalTranscript);
    elements.recordingBadge.textContent = state.interim
      ? `Interprétation provisoire : ${state.interim}`
      : 'Enregistrement en cours…';
  };

  state.recognition = recognition;
  return recognition;
}

async function startRecording() {
  const recognition = ensureSpeechRecognition();
  if (!recognition || state.isRecording) return;
  if (state.transcript.trim()) {
    const continueSession = confirm('Continuer l\'enregistrement sur la session actuelle ?');
    if (!continueSession) {
      await persistSession('manual');
      state.sessionId = null;
      state.backendId = null;
      state.tags = [];
      renderTags();
      updateTranscript('');
    }
  }
  recognition.start();
  updateSessionStatus('Initialisation…', 'active');
}

function stopRecording() {
  if (!state.recognition || !state.isRecording) {
    persistSession('manual');
    return;
  }
  state.recognition.stop();
}

function exportNotes() {
  if (!state.transcript) {
    showToast('Aucune note à exporter.');
    return;
  }
  const blob = new Blob(
    [
      `# Notes Omega\n\n` +
        `Date : ${new Date().toLocaleString()}\n` +
        `Tags : ${state.tags.map((tag) => tag.label).join(', ') || 'aucun'}\n\n` +
        state.transcript
    ],
    { type: 'text/plain;charset=utf-8' }
  );
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `omega-notes-${Date.now()}.txt`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast('Export généré');
}

async function pingBackend() {
  if (window.location.protocol.startsWith('file')) {
    updateSessionStatus('Mode hors ligne', 'idle');
    return;
  }
  try {
    const response = await fetch('/health', { cache: 'no-store' });
    state.backendAvailable = response.ok;
    updateSessionStatus(response.ok ? 'Serveur actif' : 'Mode hors ligne', response.ok ? 'active' : 'idle');
  } catch (error) {
    state.backendAvailable = false;
    updateSessionStatus('Mode hors ligne', 'idle');
  }
}

function persistLocalSession() {
  const transcript = state.transcript.trim();
  if (!transcript) return null;
  const existing = state.sessions.find((session) => session.id === state.sessionId);
  const fallbackId = () =>
    typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `session-${Date.now()}-${Math.floor(Math.random() * 10_000)}`;
  const payload = {
    id: state.sessionId ?? fallbackId(),
    title: inferTitle(transcript),
    transcript,
    tags: state.tags,
    updatedAt: new Date().toISOString(),
    wordCount: transcript.split(/\s+/).filter(Boolean).length,
    backendId: existing?.backendId ?? state.backendId ?? null
  };
  if (existing) {
    Object.assign(existing, payload);
  } else {
    state.sessions.unshift(payload);
  }
  state.sessionId = payload.id;
  state.backendId = payload.backendId ?? null;
  saveSessions();
  renderSessions();
  return payload;
}

async function syncWithBackend(session) {
  if (!state.backendAvailable || !session) return null;
  const hasBackendId = Boolean(state.backendId);
  const endpoint = hasBackendId ? `/api/sessions/${state.backendId}` : '/api/sessions';
  const method = hasBackendId ? 'PATCH' : 'POST';
  const body = hasBackendId
    ? { transcript: session.transcript, metadata: { tags: session.tags } }
    : { title: session.title, transcript: session.transcript, metadata: { tags: session.tags } };
  try {
    const response = await fetch(endpoint, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!response.ok) throw new Error('Synchronisation impossible');
    const data = await response.json();
    state.backendId = data.id;
    const local = state.sessions.find((item) => item.id === state.sessionId);
    if (local) {
      local.backendId = data.id;
      saveSessions();
    }
    updateSessionStatus('Synchronisé', 'active');
    return data;
  } catch (error) {
    console.warn('Impossible de synchroniser la session', error);
    updateSessionStatus('Mode hors ligne', 'idle');
    state.backendAvailable = false;
    return null;
  }
}

async function persistSession(trigger = 'manual') {
  const saved = persistLocalSession();
  if (saved) {
    showToast(trigger === 'auto' ? 'Session enregistrée' : 'Sauvegarde réalisée');
  }
  await syncWithBackend(saved);
}

function renderSessions() {
  elements.sessionList.innerHTML = '';
  if (!state.sessions.length) {
    const empty = document.createElement('p');
    empty.textContent = 'Aucune session enregistrée pour le moment.';
    empty.className = 'session-info';
    elements.sessionList.append(empty);
    return;
  }

  const template = document.getElementById('sessionTemplate');
  state.sessions.forEach((session) => {
    const instance = template.content.firstElementChild.cloneNode(true);
    instance.querySelector('.session-title').textContent = session.title;
    instance.querySelector('.session-info').textContent = `${session.wordCount} mots · ${new Date(
      session.updatedAt
    ).toLocaleString()}${session.backendId ? ' · synchronisé' : ''}`;
    instance.dataset.sessionId = session.id;
    elements.sessionList.append(instance);
  });
}

function inferTitle(transcript) {
  const firstSentence = transcript.split(/(?<=[.!?])\s+/)[0];
  return firstSentence ? firstSentence.slice(0, 60) + (firstSentence.length > 60 ? '…' : '') : 'Cours sans titre';
}

function handleSessionList(event) {
  const action = event.target.closest('button')?.dataset.action;
  if (!action) return;
  const card = event.target.closest('.session-card');
  if (!card) return;
  const { sessionId } = card.dataset;
  const session = state.sessions.find((item) => item.id === sessionId);
  if (!session) return;

  if (action === 'load') {
    state.sessionId = sessionId;
    state.backendId = session.backendId ?? null;
    state.tags = session.tags || [];
    updateTranscript(session.transcript);
    renderTags();
    showToast('Session chargée');
  } else if (action === 'delete') {
    if (!confirm('Supprimer cette session ?')) return;
    state.sessions = state.sessions.filter((item) => item.id !== sessionId);
    if (state.sessionId === sessionId) {
      state.sessionId = null;
      state.backendId = null;
      updateTranscript('');
      state.tags = [];
      renderTags();
    }
    saveSessions();
    renderSessions();
    showToast('Session supprimée');
  }
}

function getCacheKey(tool, parameters) {
  const transcriptHash = stringHash(state.transcript);
  return `${tool}-${transcriptHash}-${JSON.stringify(parameters)}`;
}

function readCache(tool, parameters) {
  const key = getCacheKey(tool, parameters);
  return state.cache[key] ?? null;
}

function writeCache(tool, parameters, value) {
  const key = getCacheKey(tool, parameters);
  state.cache[key] = { value, time: Date.now() };
  saveCache();
}

async function generateSummary() {
  if (!state.transcript.trim()) {
    showToast('Ajoutez une transcription avant de générer un résumé.');
    return;
  }
  const tone = elements.summaryTone.value;
  const cached = readCache('summary', { tone });
  if (cached) {
    elements.summaryOutput.textContent = cached.value;
    showToast('Résumé chargé depuis le cache');
    return;
  }
  elements.summaryOutput.textContent = 'Génération du résumé…';
  const response = state.backendAvailable ? await requestBackend('summary', { tone }) : null;
  const summary = response?.summary ?? fallbackSummary(state.transcript, tone);
  elements.summaryOutput.textContent = summary;
  writeCache('summary', { tone }, summary);
}

async function generateQuiz() {
  if (!state.transcript.trim()) {
    showToast('Ajoutez une transcription avant de générer un quiz.');
    return;
  }
  const count = Math.max(3, Math.min(12, Number(elements.quizCount.value) || 5));
  elements.quizCount.value = count;
  const cached = readCache('quiz', { count });
  if (cached) {
    elements.quizOutput.textContent = formatQuiz(cached.value);
    showToast('Quiz issu du cache');
    return;
  }
  elements.quizOutput.textContent = 'Création du quiz…';
  const response = state.backendAvailable ? await requestBackend('quiz', { count }) : null;
  const quiz = response?.quiz ?? fallbackQuiz(state.transcript, count);
  elements.quizOutput.textContent = formatQuiz(quiz);
  writeCache('quiz', { count }, quiz);
}

async function askQuestion() {
  const question = elements.questionInput.value.trim();
  if (!question) {
    showToast('Formulez votre question.');
    return;
  }
  if (!state.transcript.trim()) {
    showToast('Ajoutez une transcription pour contextualiser la réponse.');
    return;
  }
  const cached = readCache('question', { question });
  if (cached) {
    elements.questionOutput.textContent = cached.value;
    showToast('Réponse issue du cache');
    return;
  }
  elements.questionOutput.textContent = 'Analyse en cours…';
  const response = state.backendAvailable ? await requestBackend('questions', { question }) : null;
  const answer = response?.answer ?? fallbackQuestion(state.transcript, question);
  elements.questionOutput.textContent = answer;
  writeCache('question', { question }, answer);
}

async function generateGames() {
  if (!state.transcript.trim()) {
    showToast('Ajoutez une transcription avant de générer des jeux.');
    return;
  }
  const cached = readCache('games', {});
  if (cached) {
    elements.gamesOutput.textContent = formatGames(cached.value);
    showToast('Jeux chargés depuis le cache');
    return;
  }
  elements.gamesOutput.textContent = 'Création des jeux…';
  const response = state.backendAvailable ? await requestBackend('games', {}) : null;
  const games = response ?? fallbackGames(state.transcript);
  elements.gamesOutput.textContent = formatGames(games);
  writeCache('games', {}, games);
}

async function requestBackend(tool, payload) {
  if (!state.backendAvailable) return null;
  try {
    const session = await persistLocalSession();
    await syncWithBackend(session);
    if (!state.backendId) {
      throw new Error('Session non synchronisée');
    }
    const response = await fetch(`/api/sessions/${state.backendId}/${tool}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Erreur du serveur');
    return await response.json();
  } catch (error) {
    console.warn('Requête backend impossible', error);
    showToast('Serveur IA indisponible, utilisation du mode local.');
    state.backendAvailable = false;
    updateSessionStatus('Mode hors ligne', 'idle');
    return null;
  }
}

function fallbackSummary(text, tone) {
  const sentences = text.split(/(?<=[.!?])\s+/).filter((sentence) => sentence.length > 0);
  const highlights = sentences.slice(0, 6);
  if (tone === 'fiche') {
    return highlights
      .map((sentence) => `• ${sentence}`)
      .join('\n');
  }
  if (tone === 'narratif') {
    return `En résumé, ${highlights.join(' ')}\n\nConclusion : ${sentences.at(-1) ?? ''}`.trim();
  }
  return highlights.slice(0, 3).join(' ');
}

function fallbackQuiz(text, count) {
  const sentences = text.split(/(?<=[.!?])\s+/).filter((sentence) => sentence.length > 30);
  if (!sentences.length) return [];
  const questions = [];
  for (let i = 0; i < count; i += 1) {
    const sentence = sentences[i % sentences.length];
    const cleanSentence = sentence.replace(/\s+/g, ' ').trim();
    questions.push({
      question: `Expliquez : ${cleanSentence.slice(0, 90)}${cleanSentence.length > 90 ? '…' : ''}`,
      answer: cleanSentence
    });
  }
  return questions;
}

function fallbackQuestion(text, question) {
  const lowerQuestion = question.toLowerCase();
  const sentences = text.split(/(?<=[.!?])\s+/);
  const relevant = sentences.filter((sentence) => sentence.toLowerCase().includes(lowerQuestion.split(' ')[0] ?? ''));
  if (relevant.length) {
    return relevant.join(' ');
  }
  return "Aucune réponse directe trouvée. Relisez la section concernée ou générez un résumé.";
}

function fallbackGames(text) {
  const sentences = text.split(/(?<=[.!?])\s+/).filter(Boolean);
  return {
    flashcards: sentences.slice(0, 4).map((sentence, index) => ({
      front: `Concept ${index + 1}`,
      back: sentence.trim()
    })),
    brainstorm: sentences.slice(-3).map((sentence) => `Idée : ${sentence.trim()}`)
  };
}

function formatQuiz(quiz) {
  return quiz.map((item, index) => `${index + 1}. ${item.question}\n   → ${item.answer}`).join('\n\n');
}

function formatGames(games) {
  if (Array.isArray(games)) {
    return games
      .map((game) => `• ${game.title ?? game}`)
      .join('\n');
  }
  const parts = [];
  if (games.flashcards) {
    parts.push('Flashcards :');
    games.flashcards.forEach((card, index) => {
      parts.push(`${index + 1}. ${card.front}\n   Réponse : ${card.back}`);
    });
  }
  if (games.brainstorm) {
    parts.push('\nIdées de jeux :');
    games.brainstorm.forEach((idea) => parts.push(`• ${idea}`));
  }
  return parts.join('\n');
}

function setupEventListeners() {
  elements.recordButton.addEventListener('click', startRecording);
  elements.stopButton.addEventListener('click', stopRecording);
  elements.exportButton.addEventListener('click', exportNotes);
  elements.tagButton.addEventListener('click', addTag);
  elements.clearButton.addEventListener('click', clearTranscript);
  elements.transcript.addEventListener('input', (event) => updateTranscript(event.target.value));
  elements.summaryButton.addEventListener('click', generateSummary);
  elements.quizButton.addEventListener('click', generateQuiz);
  elements.questionButton.addEventListener('click', askQuestion);
  elements.gamesButton.addEventListener('click', generateGames);
  elements.sessionList.addEventListener('click', handleSessionList);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && state.isRecording) {
      stopRecording();
    }
  });
}

function initialize() {
  setupTheme();
  setupEventListeners();
  renderTags();
  renderSessions();
  const firstSession = state.sessions[0];
  if (firstSession) {
    state.sessionId = firstSession.id;
    state.backendId = firstSession.backendId ?? null;
    state.tags = firstSession.tags || [];
    renderTags();
    updateTranscript(firstSession.transcript);
  } else {
    updateTranscript('');
  }
  elements.year.textContent = new Date().getFullYear().toString();
  pingBackend();
  drawWaveform();
}

initialize();
