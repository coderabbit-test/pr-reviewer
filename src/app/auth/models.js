import { z } from 'zod';

// Request schemas
export const UserSignupRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  first_name: z.string().min(1),
  last_name: z.string().min(1),
});

export const UserLoginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export const RefreshTokenRequestSchema = z.object({
  refresh_token: z.string().min(1),
});

// Response schemas (for validation/documentation)
export const UserResponseSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  first_name: z.string(),
  last_name: z.string(),
  is_active: z.boolean(),
  created_at: z.string(),
});

export const AuthResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string().default('bearer'),
  user: UserResponseSchema,
});

export const TokenResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string().default('bearer'),
});

