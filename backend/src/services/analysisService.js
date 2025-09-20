import crypto from 'node:crypto';
import { OpenAI } from 'openai';

const openaiApiKey = process.env.OPENAI_API_KEY;
const openai = openaiApiKey ? new OpenAI({ apiKey: openaiApiKey }) : null;
const responseCache = new Map();

function buildCacheKey(type, payload) {
  return crypto.createHash('sha256').update(`${type}:${payload}`).digest('hex');
}

function chunkTranscript(transcript, maxChunkSize = 1200) {
  if (!transcript) {
    return [];
  }
  const sentences = transcript.split(/(?<=[.!?])\s+/u);
  const chunks = [];
  let current = '';
  for (const sentence of sentences) {
    if ((current + ' ' + sentence).trim().length > maxChunkSize && current) {
      chunks.push(current.trim());
      current = sentence;
    } else {
      current = `${current} ${sentence}`.trim();
    }
  }
  if (current) {
    chunks.push(current.trim());
  }
  return chunks;
}

function extractiveSummary(transcript, sentenceCount = 5) {
  const sentences = transcript.split(/(?<=[.!?])\s+/u).filter(Boolean);
  return sentences.slice(0, sentenceCount).join(' ');
}

function fallbackQuiz(transcript, questionCount = 5) {
  const sentences = transcript.split(/(?<=[.!?])\s+/u).filter(Boolean);
  const selected = sentences.slice(0, questionCount);
  return selected.map((sentence, index) => ({
    id: index + 1,
    question: `Expliquez: ${sentence}`,
    answer: sentence
  }));
}

function fallbackGames(transcript) {
  const keywords = transcript
    .split(/[^\p{L}\p{N}]+/u)
    .filter((word) => word.length > 6)
    .slice(0, 10);
  return {
    wordScramble: keywords.map((word) => ({
      original: word,
      scrambled: word.split('').sort(() => 0.5 - Math.random()).join('')
    })),
    flashcards: keywords.map((word) => ({ term: word, hint: transcript.includes(word) ? 'Vu dans le cours' : '' }))
  };
}

async function callOpenAI(prompt, responseFormat = 'text') {
  if (!openai) {
    return null;
  }
  const cacheKey = buildCacheKey(responseFormat, prompt);
  if (responseCache.has(cacheKey)) {
    return responseCache.get(cacheKey);
  }
  const response = await openai.responses.create({
    model: 'gpt-4o-mini',
    input: prompt,
    max_output_tokens: 600,
    temperature: 0.3
  });
  const text = response.output_text;
  responseCache.set(cacheKey, text);
  return text;
}

export async function summarizeTranscript(transcript) {
  if (!transcript) {
    return '';
  }
  if (!openai || transcript.length < 1200) {
    return extractiveSummary(transcript);
  }
  const chunks = chunkTranscript(transcript, 2000);
  const summaries = [];
  for (const chunk of chunks) {
    const summary = await callOpenAI(`Résume de manière concise le passage suivant en français:\n${chunk}`);
    summaries.push(summary ?? extractiveSummary(chunk, 3));
  }
  const combined = summaries.join('\n');
  const finalSummary = await callOpenAI(`Combine et synthétise ce résumé en trois paragraphes maximum:\n${combined}`);
  return finalSummary ?? extractiveSummary(combined, 6);
}

export async function generateQuiz(transcript, desiredCount = 5) {
  if (!transcript) {
    return [];
  }
  if (!openai || transcript.length < 800) {
    return fallbackQuiz(transcript, desiredCount);
  }
  const prompt = `Génère ${desiredCount} questions de quiz basées sur le texte suivant. Réponds en JSON avec un tableau d'objets {id, question, answer}. Texte:\n${transcript}`;
  const aiResponse = await callOpenAI(prompt, 'quiz');
  if (!aiResponse) {
    return fallbackQuiz(transcript, desiredCount);
  }
  try {
    const parsed = JSON.parse(aiResponse);
    if (Array.isArray(parsed)) {
      return parsed;
    }
  } catch (error) {
    // ignore and fallback
  }
  return fallbackQuiz(transcript, desiredCount);
}

export async function answerQuestion(transcript, question) {
  if (!question) {
    return 'Veuillez poser une question.';
  }
  if (!openai || transcript.length < 600) {
    const sentences = transcript.split(/(?<=[.!?])\s+/u).filter((sentence) =>
      sentence.toLowerCase().includes(question.toLowerCase())
    );
    return sentences.join(' ') || 'Aucun passage pertinent trouvé dans le cours.';
  }
  const prompt = `En t'appuyant strictement sur le texte suivant, réponds à la question donnée. Si la réponse n'est pas disponible, dis-le explicitement. Texte:\n${transcript}\nQuestion: ${question}`;
  const response = await callOpenAI(prompt, 'qa');
  return response ?? 'Aucune réponse IA disponible pour le moment.';
}

export async function generateGames(transcript) {
  if (!transcript) {
    return { wordScramble: [], flashcards: [] };
  }
  if (!openai || transcript.length < 1000) {
    return fallbackGames(transcript);
  }
  const prompt = `À partir du texte suivant, crée deux activités: 1) un jeu de lettres mêlées avec 5 mots clés, 2) 5 flashcards (terme + indice). Réponds en JSON {wordScramble: [{original, scrambled}], flashcards: [{term, hint}]}. Texte:\n${transcript}`;
  const response = await callOpenAI(prompt, 'games');
  if (!response) {
    return fallbackGames(transcript);
  }
  try {
    const parsed = JSON.parse(response);
    if (parsed.wordScramble && parsed.flashcards) {
      return parsed;
    }
  } catch (error) {
    // ignore and fallback
  }
  return fallbackGames(transcript);
}
