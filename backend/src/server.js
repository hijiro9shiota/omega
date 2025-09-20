import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import compression from 'compression';
import helmet from 'helmet';
import pino from 'pino';
import sessionRoutes from './routes/sessionRoutes.js';

const app = express();
const logger = pino({ level: process.env.LOG_LEVEL ?? 'info' });
const PORT = process.env.PORT ?? 4000;

app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '2mb' }));
app.use(compression());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

app.use('/api/sessions', sessionRoutes);

app.use((err, req, res, next) => {
  logger.error({ err }, 'Unhandled error');
  res.status(500).json({ message: 'Erreur serveur. Réessayez plus tard.' });
});

app.listen(PORT, () => {
  logger.info(`Serveur lancé sur http://localhost:${PORT}`);
});
