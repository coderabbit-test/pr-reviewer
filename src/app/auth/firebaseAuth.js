import admin from 'firebase-admin';
import jwt from 'jsonwebtoken';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class FirebaseAuthService {
  constructor() {
    this._initializeFirebase();
    this.jwtSecret = process.env.JWT_SECRET || 'your-secret-key';
    this.jwtAlgorithm = 'HS256';
    this.accessTokenExpiry = 60 * 60; // 1 hour in seconds
    this.refreshTokenExpiry = 7 * 24 * 60 * 60; // 7 days in seconds
  }

  _initializeFirebase() {
    try {
      // Try to get Firebase credentials from environment
      const firebaseCredentials = process.env.FIREBASE_CREDENTIALS;
      if (firebaseCredentials) {
        const credDict = JSON.parse(firebaseCredentials);
        const cred = admin.credential.cert(credDict);
        admin.initializeApp({ credential: cred });
      } else {
        // Fallback to service account file
        const serviceAccountPath = process.env.FIREBASE_SERVICE_ACCOUNT_PATH;
        if (serviceAccountPath) {
          try {
            const serviceAccount = JSON.parse(
              readFileSync(serviceAccountPath, 'utf8')
            );
            const cred = admin.credential.cert(serviceAccount);
            admin.initializeApp({ credential: cred });
          } catch (error) {
            console.error('Error reading service account file:', error);
            // Try default credentials (for development)
            admin.initializeApp();
          }
        } else {
          // Use default credentials (for development)
          admin.initializeApp();
        }
      }
    } catch (error) {
      // If app already initialized, that's okay
      if (error.code !== 'app/already-initialized') {
        console.error('Firebase initialization error:', error);
        throw error;
      }
    }
  }

  async createUser(email, password, firstName, lastName) {
    try {
      const userRecord = await admin.auth().createUser({
        email: email,
        password: password,
        displayName: `${firstName} ${lastName}`,
        emailVerified: false,
      });

      // Set custom claims
      await admin.auth().setCustomUserClaims(userRecord.uid, {
        first_name: firstName,
        last_name: lastName,
        role: 'user',
      });

      return {
        id: userRecord.uid,
        email: userRecord.email,
        first_name: firstName,
        last_name: lastName,
        is_active: !userRecord.disabled,
        created_at: userRecord.metadata.creationTime,
      };
    } catch (error) {
      throw new Error(`Failed to create user: ${error.message}`);
    }
  }

  async signInUser(email, password) {
    try {
      // Note: Firebase Admin SDK doesn't have signInWithEmailAndPassword
      // In production, you'd use Firebase Auth REST API or Firebase Client SDK
      // For now, we'll get the user and generate tokens
      const userRecord = await admin.auth().getUserByEmail(email);

      if (userRecord.disabled) {
        throw new Error('User account is disabled');
      }

      // Generate JWT tokens
      const accessToken = this._generateAccessToken(userRecord.uid, userRecord.email);
      const refreshToken = this._generateRefreshToken(userRecord.uid);

      // Get custom claims
      const customClaims = userRecord.customClaims || {};

      return {
        access_token: accessToken,
        refresh_token: refreshToken,
        user: {
          id: userRecord.uid,
          email: userRecord.email,
          first_name: customClaims.first_name || '',
          last_name: customClaims.last_name || '',
          is_active: !userRecord.disabled,
          created_at: userRecord.metadata.creationTime,
        },
      };
    } catch (error) {
      throw new Error(`Authentication failed: ${error.message}`);
    }
  }

  async verifyToken(token) {
    try {
      // First try to verify as Firebase ID token
      try {
        const decodedToken = await admin.auth().verifyIdToken(token);
        const userRecord = await admin.auth().getUser(decodedToken.uid);
        const customClaims = userRecord.customClaims || {};

        return {
          uid: userRecord.uid,
          email: userRecord.email,
          first_name: customClaims.first_name || '',
          last_name: customClaims.last_name || '',
          role: customClaims.role || 'user',
        };
      } catch (firebaseError) {
        // If not a Firebase token, try as JWT
        const decoded = jwt.verify(token, this.jwtSecret, {
          algorithms: [this.jwtAlgorithm],
        });

        if (decoded.type === 'access') {
          // Get user from Firebase to get custom claims
          const userRecord = await admin.auth().getUser(decoded.user_id);
          const customClaims = userRecord.customClaims || {};

          return {
            uid: userRecord.uid,
            email: userRecord.email,
            first_name: customClaims.first_name || '',
            last_name: customClaims.last_name || '',
            role: customClaims.role || 'user',
          };
        }

        return null;
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      return null;
    }
  }

  _generateAccessToken(userId, email) {
    const payload = {
      user_id: userId,
      email: email,
      exp: Math.floor(Date.now() / 1000) + this.accessTokenExpiry,
      iat: Math.floor(Date.now() / 1000),
      type: 'access',
    };
    return jwt.sign(payload, this.jwtSecret, { algorithm: this.jwtAlgorithm });
  }

  _generateRefreshToken(userId) {
    const payload = {
      user_id: userId,
      exp: Math.floor(Date.now() / 1000) + this.refreshTokenExpiry,
      iat: Math.floor(Date.now() / 1000),
      type: 'refresh',
    };
    return jwt.sign(payload, this.jwtSecret, { algorithm: this.jwtAlgorithm });
  }

  async refreshAccessToken(refreshToken) {
    try {
      const payload = jwt.verify(refreshToken, this.jwtSecret, {
        algorithms: [this.jwtAlgorithm],
      });

      if (payload.type !== 'refresh') {
        throw new Error('Invalid token type');
      }

      const userRecord = await admin.auth().getUser(payload.user_id);
      return this._generateAccessToken(payload.user_id, userRecord.email);
    } catch (error) {
      console.error('Token refresh failed:', error);
      return null;
    }
  }
}

// Global instance
export const firebaseAuth = new FirebaseAuthService();

