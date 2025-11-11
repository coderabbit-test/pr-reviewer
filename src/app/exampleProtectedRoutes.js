import express from 'express';
import {
  getCurrentUser,
  getCurrentActiveUser,
  requireAdmin,
  requireUser,
} from './auth/middleware.js';

const router = express.Router();

/**
 * @route GET /protected/user-info
 * @desc Get information about the currently authenticated user
 */
router.get('/user-info', getCurrentUser, (req, res) => {
  res.json({
    message: 'User information retrieved successfully',
    user: {
      id: req.user.uid,
      email: req.user.email,
      first_name: req.user.first_name,
      last_name: req.user.last_name,
      role: req.user.role,
    },
  });
});

/**
 * @route GET /protected/active-only
 * @desc Endpoint that only allows active users
 */
router.get('/active-only', getCurrentActiveUser, (req, res) => {
  res.json({
    message: 'This endpoint is only accessible to active users',
    user_email: req.user.email,
  });
});

/**
 * @route GET /protected/admin-only
 * @desc Endpoint that only allows admin users
 */
router.get('/admin-only', requireAdmin, (req, res) => {
  res.json({
    message: 'This endpoint is only accessible to admin users',
    admin_email: req.user.email,
  });
});

/**
 * @route GET /protected/user-or-admin
 * @desc Endpoint that allows both regular users and admins
 */
router.get('/user-or-admin', requireUser, (req, res) => {
  res.json({
    message: 'This endpoint is accessible to users and admins',
    user_email: req.user.email,
    user_role: req.user.role,
  });
});

/**
 * @route POST /protected/create-resource
 * @desc Example of creating a resource with user authentication
 */
router.post('/create-resource', getCurrentActiveUser, (req, res) => {
  res.json({
    message: 'Resource created successfully',
    resource: req.body,
    created_by: req.user.email,
    user_id: req.user.uid,
  });
});

/**
 * @route DELETE /protected/delete-resource/:resource_id
 * @desc Example of deleting a resource (admin only)
 */
router.delete('/delete-resource/:resource_id', requireAdmin, (req, res) => {
  res.json({
    message: `Resource ${req.params.resource_id} deleted successfully`,
    deleted_by: req.user.email,
  });
});

export default router;

