import request from 'supertest';
import app from '../index.js';

describe('Authentication API', () => {
  describe('Health Check', () => {
    it('should return healthy status', async () => {
      const response = await request(app).get('/health');
      expect(response.status).toBe(200);
      expect(response.body.status).toBe('healthy');
    });
  });

  describe('Root Endpoint', () => {
    it('should return welcome message', async () => {
      const response = await request(app).get('/');
      expect(response.status).toBe(200);
      expect(response.body.message).toBe('Welcome to Authentication API');
    });
  });

  describe('POST /auth/signup', () => {
    it('should validate email format', async () => {
      const response = await request(app)
        .post('/auth/signup')
        .send({
          email: 'invalid-email',
          password: 'password123',
          first_name: 'John',
          last_name: 'Doe',
        });

      expect(response.status).toBe(400);
      expect(response.body.detail).toContain('email');
    });

    it('should validate required fields', async () => {
      const response = await request(app)
        .post('/auth/signup')
        .send({
          email: 'test@example.com',
        });

      expect(response.status).toBe(400);
    });

    it('should validate password length', async () => {
      const response = await request(app)
        .post('/auth/signup')
        .send({
          email: 'test@example.com',
          password: '123',
          first_name: 'John',
          last_name: 'Doe',
        });

      expect(response.status).toBe(400);
    });
  });

  describe('POST /auth/login', () => {
    it('should validate email format', async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({
          email: 'invalid-email',
          password: 'password123',
        });

      expect(response.status).toBe(400);
    });

    it('should require email and password', async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({
          email: 'test@example.com',
        });

      expect(response.status).toBe(400);
    });
  });

  describe('POST /auth/refresh', () => {
    it('should require refresh_token', async () => {
      const response = await request(app)
        .post('/auth/refresh')
        .send({});

      expect(response.status).toBe(400);
    });
  });

  describe('GET /auth/me', () => {
    it('should require authentication', async () => {
      const response = await request(app).get('/auth/me');

      expect(response.status).toBe(401);
    });
  });

  describe('GET /auth/verify', () => {
    it('should require authentication', async () => {
      const response = await request(app).get('/auth/verify');

      expect(response.status).toBe(401);
    });
  });

  describe('Protected Routes', () => {
    it('should require authentication for /protected/user-info', async () => {
      const response = await request(app).get('/protected/user-info');

      expect(response.status).toBe(401);
    });

    it('should require authentication for /protected/active-only', async () => {
      const response = await request(app).get('/protected/active-only');

      expect(response.status).toBe(401);
    });

    it('should require authentication for /protected/admin-only', async () => {
      const response = await request(app).get('/protected/admin-only');

      expect(response.status).toBe(401);
    });
  });
});

