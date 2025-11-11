import express from 'express';
import { firebaseAuth } from './firebaseAuth.js';
import { getCurrentUser } from './middleware.js';
import {
  UserSignupRequestSchema,
  UserLoginRequestSchema,
  RefreshTokenRequestSchema,
} from './models.js';

const router = express.Router();

// Validation middleware helper
const validate = (schema) => {
  return (req, res, next) => {
    try {
      schema.parse(req.body);
      next();
    } catch (error) {
      return res.status(400).json({
        detail: error.errors.map((e) => `${e.path.join('.')}: ${e.message}`).join(', '),
      });
    }
  };
};

/**
 * @route POST /auth/signup
 * @desc Create a new user account
 */
router.post('/signup', validate(UserSignupRequestSchema), async (req, res) => {
  try {
    const { email, password, first_name, last_name } = req.body;

    // Create user in Firebase
    const user = await firebaseAuth.createUser(
      email,
      password,
      first_name,
      last_name
    );

    // Sign in the user to get tokens
    const authResult = await firebaseAuth.signInUser(email, password);

    res.status(201).json({
      access_token: authResult.access_token,
      refresh_token: authResult.refresh_token,
      token_type: 'bearer',
      user: authResult.user,
    });
  } catch (error) {
    res.status(400).json({
      detail: error.message,
    });
  }
});

/**
 * @route POST /auth/login
 * @desc Authenticate user and return access tokens
 */
router.post('/login', validate(UserLoginRequestSchema), async (req, res) => {
  try {
    const { email, password } = req.body;

    const authResult = await firebaseAuth.signInUser(email, password);

    res.json({
      access_token: authResult.access_token,
      refresh_token: authResult.refresh_token,
      token_type: 'bearer',
      user: authResult.user,
    });
  } catch (error) {
    res.status(401).json({
      detail: 'Invalid email or password',
    });
  }
});

/**
 * @route POST /auth/refresh
 * @desc Refresh access token using refresh token
 */
router.post('/refresh', validate(RefreshTokenRequestSchema), async (req, res) => {
  try {
    const { refresh_token } = req.body;

    const newAccessToken = await firebaseAuth.refreshAccessToken(refresh_token);

    if (!newAccessToken) {
      return res.status(401).json({
        detail: 'Invalid refresh token',
      });
    }

    res.json({
      access_token: newAccessToken,
      token_type: 'bearer',
    });
  } catch (error) {
    res.status(401).json({
      detail: 'Invalid refresh token',
    });
  }
});

/**
 * @route GET /auth/me
 * @desc Get current user information
 */
router.get('/me', getCurrentUser, async (req, res) => {
  try {
    const currentUser = req.user;

    res.json({
      id: currentUser.uid,
      email: currentUser.email,
      first_name: currentUser.first_name,
      last_name: currentUser.last_name,
      is_active: true,
      created_at: '', // You might want to fetch this from your database
    });
  } catch (error) {
    res.status(500).json({
      detail: 'Internal server error',
    });
  }
});

/**
 * @route POST /auth/logout
 * @desc Logout user (client should discard tokens)
 */
router.post('/logout', (req, res) => {
  res.json({
    message: 'Successfully logged out',
  });
});

/**
 * @route GET /auth/verify
 * @desc Verify if the current token is valid
 */
router.get('/verify', getCurrentUser, async (req, res) => {
  const currentUser = req.user;

  res.json({
    valid: true,
    user: {
      id: currentUser.uid,
      email: currentUser.email,
      role: currentUser.role,
    },
  });
});

export default router;

