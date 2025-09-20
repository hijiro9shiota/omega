import { Router } from 'express';
import { v4 as uuid } from 'uuid';
import {
  listSessions,
  getSession,
  createSession,
  updateSession
} from '../db/sessionStore.js';
import {
  summarizeTranscript,
  generateQuiz,
  answerQuestion,
  generateGames
} from '../services/analysisService.js';

const router = Router();

router.get('/', async (req, res, next) => {
  try {
    const sessions = await listSessions();
    res.json(sessions);
  } catch (error) {
    next(error);
  }
});

router.post('/', async (req, res, next) => {
  try {
    const { title, transcript, metadata } = req.body ?? {};
    if (!transcript || typeof transcript !== 'string') {
      res.status(400).json({ message: 'Le transcript est requis.' });
      return;
    }
    const session = {
      id: uuid(),
      title: title || 'Cours sans titre',
      transcript,
      metadata: metadata || {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    await createSession(session);
    res.status(201).json(session);
  } catch (error) {
    next(error);
  }
});

router.get('/:id', async (req, res, next) => {
  try {
    const session = await getSession(req.params.id);
    if (!session) {
      res.status(404).json({ message: 'Session introuvable.' });
      return;
    }
    res.json(session);
  } catch (error) {
    next(error);
  }
});

router.patch('/:id', async (req, res, next) => {
  try {
    const updates = req.body ?? {};
    if (updates.transcript && typeof updates.transcript !== 'string') {
      res.status(400).json({ message: 'Le transcript doit être une chaîne de caractères.' });
      return;
    }
    const session = await updateSession(req.params.id, updates);
    if (!session) {
      res.status(404).json({ message: 'Session introuvable.' });
      return;
    }
    res.json(session);
  } catch (error) {
    next(error);
  }
});

router.post('/:id/summary', async (req, res, next) => {
  try {
    const session = await getSession(req.params.id);
    if (!session) {
      res.status(404).json({ message: 'Session introuvable.' });
      return;
    }
    const summary = await summarizeTranscript(session.transcript);
    res.json({ summary });
  } catch (error) {
    next(error);
  }
});

router.post('/:id/quiz', async (req, res, next) => {
  try {
    const session = await getSession(req.params.id);
    if (!session) {
      res.status(404).json({ message: 'Session introuvable.' });
      return;
    }
    const { count } = req.body ?? {};
    const quiz = await generateQuiz(session.transcript, count ?? 5);
    res.json({ quiz });
  } catch (error) {
    next(error);
  }
});

router.post('/:id/questions', async (req, res, next) => {
  try {
    const session = await getSession(req.params.id);
    if (!session) {
      res.status(404).json({ message: 'Session introuvable.' });
      return;
    }
    const { question } = req.body ?? {};
    const answer = await answerQuestion(session.transcript, question);
    res.json({ answer });
  } catch (error) {
    next(error);
  }
});

router.post('/:id/games', async (req, res, next) => {
  try {
    const session = await getSession(req.params.id);
    if (!session) {
      res.status(404).json({ message: 'Session introuvable.' });
      return;
    }
    const games = await generateGames(session.transcript);
    res.json(games);
  } catch (error) {
    next(error);
  }
});

export default router;
