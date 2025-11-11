import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRouter from './app/auth/routes.js';
import protectedRouter from './app/exampleProtectedRoutes.js';

// Load environment variables
dotenv.config();

const app = express();

// Middleware
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
  credentials: true,
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/auth', authRouter);
app.use('/protected', protectedRouter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    message: 'Authentication API is running',
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Welcome to Authentication API',
    docs: 'API documentation available at /docs (if configured)',
    endpoints: {
      auth: '/auth',
      protected: '/protected',
    },
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({
    detail: 'Internal server error',
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    detail: 'Not found',
  });
});

const PORT = process.env.PORT || 8000;
const HOST = process.env.HOST || '0.0.0.0';

app.listen(PORT, HOST, () => {
  console.log(`Server running on http://${HOST}:${PORT}`);
  console.log(`Environment: ${process.env.ENVIRONMENT || 'development'}`);
});

export default app;

