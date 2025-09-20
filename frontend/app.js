const transcriptEl = document.getElementById('transcript');
const startBtn = document.getElementById('startRecording');
const stopBtn = document.getElementById('stopRecording');
const statusEl = document.getElementById('recordingStatus');
const heroDuration = document.getElementById('heroDuration');
const heroWordCount = document.getElementById('heroWordCount');
const statWords = document.getElementById('statWords');
const statSections = document.getElementById('statSections');
const statLastTag = document.getElementById('statLastTag');
const tagList = document.getElementById('tagList');
const highlightBtn = document.getElementById('highlightButton');
const clearBtn = document.getElementById('clearButton');
const cacheToggle = document.getElementById('cacheToggle');
const suggestionsList = document.getElementById('suggestions');
const summaryBtn = document.getElementById('summaryButton');
const summaryOutput = document.getElementById('summaryOutput');
const summaryTone = document.getElementById('summaryTone');
const quizBtn = document.getElementById('quizButton');
const quizOutput = document.getElementById('quizOutput');
const quizLevel = document.getElementById('quizLevel');
const questionBtn = document.getElementById('questionButton');
const questionInput = document.getElementById('questionInput');
const questionOutput = document.getElementById('questionOutput');
const gameBtn = document.getElementById('gameButton');
const gameOutput = document.getElementById('gameOutput');
const toastEl = document.getElementById('toast');
const downloadMarkdownBtn = document.getElementById('downloadMarkdown');
const downloadJSONBtn = document.getElementById('downloadJSON');
const exportBtn = document.getElementById('exportButton');
const heroChapter = document.getElementById('heroChapter');

let recognition;
let isRecording = false;
let startTimestamp;
let recordingInterval;
let cachedResponses = new Map();
let tags = [];

const SUGGESTION_SETS = [
  [
    'Scindez la séance en sections et ajoutez un résumé par partie.',
    'Repérez les termes clés répétés pour bâtir un glossaire.',
    'Notez les questions posées par le professeur pour générer des quiz.'
  ],
  [
    'Ajoutez un tag « examen » lorsque la notion tombe fréquemment.',
    'Ajoutez un timestamp pour chaque démonstration importante.',
    'Demandez un quiz adaptatif pour vérifier votre compréhension.'
  ],
  [
    'Générez une fiche de synthèse après chaque séance.',
    'Créez un jeu de flashcards pour mémoriser les définitions.',
    'Partagez le résumé aux camarades via l’export Markdown.'
  ]
];

function showToast(message, duration = 2800) {
  toastEl.textContent = message;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), duration);
}

function updateHeroStats() {
  if (!startTimestamp) return;
  const elapsed = Math.floor((Date.now() - startTimestamp) / 1000);
  const minutes = String(Math.floor(elapsed / 60)).padStart(1, '0');
  const seconds = String(elapsed % 60).padStart(2, '0');
  heroDuration.textContent = `${minutes}:${seconds}`;
}

function updateWordStats() {
  const text = transcriptEl.value.trim();
  const wordCount = text ? text.split(/\s+/).length : 0;
  heroWordCount.textContent = wordCount;
  statWords.textContent = wordCount;
  const sections = text ? text.split(/\n\n+/).length : 0;
  statSections.textContent = sections;
}

function addTag(label) {
  if (!label) return;
  tags.push({ label, createdAt: new Date() });
  renderTags();
  statLastTag.textContent = label;
  showToast(`Tag « ${label} » ajouté.`);
}

function removeTag(label) {
  tags = tags.filter((tag) => tag.label !== label);
  renderTags();
  statLastTag.textContent = tags.length ? tags[tags.length - 1].label : '—';
}

function renderTags() {
  tagList.innerHTML = '';
  tags.slice(-12).forEach((tag) => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.innerHTML = `${tag.label}<button aria-label="Retirer le tag ${tag.label}">×</button>`;
    chip.querySelector('button').addEventListener('click', () => removeTag(tag.label));
    tagList.appendChild(chip);
  });
}

function randomSuggestionSet() {
  const set = SUGGESTION_SETS[Math.floor(Math.random() * SUGGESTION_SETS.length)];
  suggestionsList.innerHTML = '';
  set.forEach((text) => {
    const li = document.createElement('li');
    li.textContent = text;
    suggestionsList.appendChild(li);
  });
}

function ensureRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast("La reconnaissance vocale n'est pas disponible dans ce navigateur.");
    return null;
  }
  if (!recognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'fr-FR';
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = transcriptEl.value;
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript.trim();
        if (result.isFinal) {
          finalTranscript += (finalTranscript.endsWith(' ') ? '' : ' ') + cleanTranscript(text);
        } else {
          interimTranscript += text + ' ';
        }
      }
      transcriptEl.value = finalTranscript + (interimTranscript ? `\n[En cours] ${interimTranscript}` : '');
      updateWordStats();
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      showToast('Erreur de reconnaissance : ' + event.error);
      stopRecording();
    };

    recognition.onend = () => {
      if (isRecording) {
        recognition.start();
      }
    };
  }
  return recognition;
}

function cleanTranscript(text) {
  return text
    .replace(/\s+/g, ' ')
    .replace(/\bpoint\b/gi, '.')
    .replace(/\bvirgule\b/gi, ',')
    .replace(/\bpoint d'interrogation\b/gi, '?')
    .replace(/\bpoint d'exclamation\b/gi, '!')
    .trim();
}

function startRecording() {
  const recognition = ensureRecognition();
  if (!recognition) return;
  try {
    recognition.start();
    isRecording = true;
    startTimestamp = Date.now();
    startBtn.disabled = true;
    stopBtn.disabled = false;
    statusEl.textContent = 'Enregistrement en cours…';
    heroChapter.textContent = `Séance ${new Date().toLocaleDateString('fr-FR')}`;
    recordingInterval = setInterval(updateHeroStats, 1000);
    randomSuggestionSet();
    showToast('Enregistrement démarré.');
  } catch (error) {
    console.error(error);
    showToast("Impossible de démarrer l'enregistrement.");
  }
}

function stopRecording() {
  if (!recognition || !isRecording) return;
  recognition.stop();
  isRecording = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  statusEl.textContent = 'Enregistrement arrêté.';
  clearInterval(recordingInterval);
  updateHeroStats();
  transcriptEl.value = transcriptEl.value.replace(/\n\[En cours].*/, '').trim();
  updateWordStats();
  showToast('Transcription enregistrée localement.');
}

function generateCacheKey(endpoint, body) {
  return `${endpoint}:${JSON.stringify(body)}`;
}

async function callBackend(endpoint, payload) {
  const body = { ...payload, useCache: cacheToggle.checked };
  const cacheKey = generateCacheKey(endpoint, body);
  if (cacheToggle.checked && cachedResponses.has(cacheKey)) {
    return cachedResponses.get(cacheKey);
  }

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    if (cacheToggle.checked) {
      cachedResponses.set(cacheKey, data);
    }
    return data;
  } catch (error) {
    console.warn('Backend unavailable, switching to local mock.', error);
    return fallbackAnalysis(endpoint, payload);
  }
}

function fallbackAnalysis(endpoint, payload) {
  const text = payload?.content || '';
  if (!text.trim()) {
    return { output: "Ajoutez du contenu avant de lancer l'analyse." };
  }
  switch (endpoint) {
    case '/api/sessions/summary': {
      const sentences = text
        .split(/[.!?]\s+/)
        .filter(Boolean)
        .slice(0, 5)
        .map((sentence, index) => `${index + 1}. ${sentence.trim()}`);
      return { output: `Résumé local (aperçu) :\n${sentences.join('\n')}` };
    }
    case '/api/sessions/quiz': {
      const words = Array.from(new Set(text.split(/\W+/).filter((w) => w.length > 5)));
      const questions = words.slice(0, 5).map((word, index) => ({
        question: `Expliquez le terme « ${word} ».`,
        answer: `Décrivez le concept de ${word} à partir du cours.`
      }));
      return { output: questions };
    }
    case '/api/sessions/question':
      return {
        output: `Réflexion locale : analysez dans vos notes la réponse à « ${payload.question} ».`
      };
    case '/api/sessions/game':
      return {
        output: `Défi local : trouvez trois points clés et associez-les à des exemples concrets.`
      };
    default:
      return { output: "Analyse indisponible." };
  }
}

function renderSummary(result) {
  summaryOutput.textContent = result.output || 'Aucun résumé généré.';
}

function renderQuiz(result) {
  const template = document.getElementById('quizTemplate');
  const list = template.content.firstElementChild.cloneNode(true);
  quizOutput.innerHTML = '';
  if (Array.isArray(result.output)) {
    result.output.forEach((item) => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${item.question}</strong><br /><span>${item.answer}</span>`;
      list.appendChild(li);
    });
    quizOutput.appendChild(list);
  } else {
    quizOutput.textContent = result.output || 'Aucun quiz généré.';
  }
}

function renderQuestion(result) {
  const template = document.getElementById('questionTemplate');
  const card = template.content.firstElementChild.cloneNode(true);
  card.textContent = result.output || 'Posez une question pour obtenir une réponse.';
  questionOutput.innerHTML = '';
  questionOutput.appendChild(card);
}

function renderGame(result) {
  const template = document.getElementById('gameTemplate');
  const card = template.content.firstElementChild.cloneNode(true);
  card.textContent = result.output || 'Appuyez sur « Lancer » pour générer un jeu.';
  gameOutput.innerHTML = '';
  gameOutput.appendChild(card);
}

function exportMarkdown() {
  const content = transcriptEl.value.trim();
  if (!content) {
    showToast('Ajoutez du texte avant de lancer un export.');
    return;
  }
  const markdown = `# Notes de cours - ${heroChapter.textContent}\n\n${content}\n\n---\n_Générées avec Omega Study_`;
  const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8;' });
  downloadBlob(blob, `omega-study-${Date.now()}.md`);
}

function exportJSON() {
  const payload = {
    chapter: heroChapter.textContent,
    transcript: transcriptEl.value,
    tags,
    stats: {
      words: parseInt(statWords.textContent, 10) || 0,
      sections: parseInt(statSections.textContent, 10) || 0,
      lastTag: statLastTag.textContent
    },
    generatedAt: new Date().toISOString()
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: 'application/json;charset=utf-8;'
  });
  downloadBlob(blob, `omega-study-${Date.now()}.json`);
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Export téléchargé.');
}

function autoSave() {
  const data = {
    transcript: transcriptEl.value,
    tags,
    chapter: heroChapter.textContent
  };
  localStorage.setItem('omega-study-session', JSON.stringify(data));
}

function loadAutoSave() {
  try {
    const raw = localStorage.getItem('omega-study-session');
    if (!raw) return;
    const data = JSON.parse(raw);
    transcriptEl.value = data.transcript || '';
    heroChapter.textContent = data.chapter || heroChapter.textContent;
    tags = data.tags || [];
    renderTags();
    updateWordStats();
  } catch (error) {
    console.warn('Unable to load autosave', error);
  }
}

transcriptEl.addEventListener('input', () => {
  updateWordStats();
  autoSave();
});

startBtn.addEventListener('click', startRecording);
stopBtn.addEventListener('click', stopRecording);

highlightBtn.addEventListener('click', () => {
  const label = prompt('Nom du tag (ex: Examen, Exemple, Définition) ?');
  if (label) {
    addTag(label.trim());
    autoSave();
  }
});

clearBtn.addEventListener('click', () => {
  if (!confirm('Effacer toutes les notes ?')) return;
  transcriptEl.value = '';
  tags = [];
  renderTags();
  updateWordStats();
  autoSave();
  showToast('Notes effacées.');
});

summaryBtn.addEventListener('click', async () => {
  const content = transcriptEl.value;
  summaryOutput.textContent = 'Analyse en cours…';
  const result = await callBackend('/api/sessions/summary', {
    content,
    tone: summaryTone.value
  });
  renderSummary(result);
});

quizBtn.addEventListener('click', async () => {
  const content = transcriptEl.value;
  quizOutput.textContent = 'Génération du quiz…';
  const result = await callBackend('/api/sessions/quiz', {
    content,
    difficulty: quizLevel.value
  });
  renderQuiz(result);
});

questionBtn.addEventListener('click', async () => {
  const content = transcriptEl.value;
  const question = questionInput.value.trim();
  if (!question) {
    showToast('Posez une question avant de lancer le coach.');
    return;
  }
  questionOutput.textContent = 'Réflexion en cours…';
  const result = await callBackend('/api/sessions/question', {
    content,
    question
  });
  renderQuestion(result);
});

gameBtn.addEventListener('click', async () => {
  const content = transcriptEl.value;
  gameOutput.textContent = 'Création du challenge…';
  const result = await callBackend('/api/sessions/game', {
    content
  });
  renderGame(result);
});

exportBtn.addEventListener('click', exportMarkdown);
downloadMarkdownBtn.addEventListener('click', exportMarkdown);
downloadJSONBtn.addEventListener('click', exportJSON);

setInterval(() => {
  if (isRecording) {
    autoSave();
  }
}, 15000);

randomSuggestionSet();
loadAutoSave();
updateWordStats();
