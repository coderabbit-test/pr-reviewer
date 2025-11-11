import { firebaseAuth } from './firebaseAuth.js';

/**
 * Middleware to get current authenticated user from token
 */
export async function getCurrentUser(req, res, next) {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        detail: 'Could not validate credentials',
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix
    
    if (!token) {
      return res.status(401).json({
        detail: 'Could not validate credentials',
      });
    }

    const userData = await firebaseAuth.verifyToken(token);
    
    if (!userData) {
      return res.status(401).json({
        detail: 'Invalid authentication credentials',
      });
    }

    req.user = userData;
    next();
  } catch (error) {
    return res.status(401).json({
      detail: 'Invalid authentication credentials',
    });
  }
}

/**
 * Middleware to get current active user
 */
export async function getCurrentActiveUser(req, res, next) {
  try {
    await getCurrentUser(req, res, () => {
      if (!req.user || req.user.is_active === false) {
        return res.status(400).json({
          detail: 'Inactive user',
        });
      }
      next();
    });
  } catch (error) {
    return res.status(401).json({
      detail: 'Invalid authentication credentials',
    });
  }
}

/**
 * Middleware factory to require specific role
 */
export function requireRole(requiredRole) {
  return async (req, res, next) => {
    try {
      await getCurrentUser(req, res, () => {
        const userRole = req.user?.role || 'user';
        
        if (userRole !== requiredRole && userRole !== 'admin') {
          return res.status(403).json({
            detail: `Access denied. Required role: ${requiredRole}`,
          });
        }
        
        next();
      });
    } catch (error) {
      return res.status(401).json({
        detail: 'Invalid authentication credentials',
      });
    }
  };
}

// Predefined role middlewares
export const requireAdmin = requireRole('admin');
export const requireUser = requireRole('user');

