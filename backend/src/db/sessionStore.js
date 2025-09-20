import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_PATH = join(__dirname, '../../data/sessions.json');

async function readSessions() {
  try {
    const raw = await readFile(DATA_PATH, 'utf8');
    return JSON.parse(raw);
  } catch (error) {
    if (error.code === 'ENOENT') {
      return [];
    }
    throw error;
  }
}

async function writeSessions(sessions) {
  await writeFile(DATA_PATH, JSON.stringify(sessions, null, 2), 'utf8');
}

export async function listSessions() {
  return readSessions();
}

export async function getSession(id) {
  const sessions = await readSessions();
  return sessions.find((session) => session.id === id) ?? null;
}

export async function createSession(session) {
  const sessions = await readSessions();
  sessions.push(session);
  await writeSessions(sessions);
  return session;
}

export async function updateSession(id, updates) {
  const sessions = await readSessions();
  const index = sessions.findIndex((session) => session.id === id);
  if (index === -1) {
    return null;
  }
  const updated = { ...sessions[index], ...updates, updatedAt: new Date().toISOString() };
  sessions[index] = updated;
  await writeSessions(sessions);
  return updated;
}
