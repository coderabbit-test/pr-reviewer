import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import firebase_admin
from firebase_admin import auth, credentials
import jwt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FirebaseAuthService:
    def __init__(self):
        self._initialize_firebase()
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.jwt_algorithm = "HS256"
        self.access_token_expiry = timedelta(hours=1)
        self.refresh_token_expiry = timedelta(days=7)

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK using env credentials, service file, or default."""
        try:
            firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
            if firebase_credentials:
                cred = credentials.Certificate(json.loads(firebase_credentials))
            else:
                service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
                if service_account_path and os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                else:
                    cred = credentials.ApplicationDefault()

            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully.")
        except Exception as e:
            logger.error(f"Firebase initialization error: {e}")
            raise RuntimeError("Failed to initialize Firebase SDK.") from e

    async def create_user(self, email: str, password: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """Create a new Firebase user with custom claims."""
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=f"{first_name} {last_name}",
                email_verified=False
            )
            auth.set_custom_user_claims(user_record.uid, {
                "first_name": first_name,
                "last_name": last_name,
                "role": "user"
            })

            return {
                "id": user_record.uid,
                "email": user_record.email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": not user_record.disabled,
                "created_at": str(user_record.user_metadata.creation_timestamp)
            }
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise RuntimeError(f"User creation failed: {e}") from e

    async def sign_in_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Simulate sign-in (Firebase doesn't allow password verification via Admin SDK).
        Production use should use Firebase Auth REST API.
        """
        try:
            user_record = auth.get_user_by_email(email)

            if user_record.disabled:
                raise PermissionError("User account is disabled")

            access_token = self._generate_access_token(user_record.uid, user_record.email)
            refresh_token = self._generate_refresh_token(user_record.uid)
            custom_claims = auth.get_custom_user_claims(user_record.uid) or {}

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user_record.uid,
                    "email": user_record.email,
                    "first_name": custom_claims.get("first_name", ""),
                    "last_name": custom_claims.get("last_name", ""),
                    "is_active": not user_record.disabled,
                    "created_at": str(user_record.user_metadata.creation_timestamp)
                }
            }
        except Exception as e:
            logger.error(f"Sign-in failed: {e}")
            raise RuntimeError("Authentication failed.") from e

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token and return user metadata."""
        try:
            decoded = auth.verify_id_token(token)
            user_record = auth.get_user(decoded["uid"])
            custom_claims = auth.get_custom_user_claims(user_record.uid) or {}

            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "first_name": custom_claims.get("first_name", ""),
                "last_name": custom_claims.get("last_name", ""),
                "role": custom_claims.get("role", "user")
            }
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Issue new access token if refresh token is valid."""
        try:
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            if payload.get("type") != "refresh":
                raise PermissionError("Invalid token type for refresh")

            user_id = payload.get("user_id")
            user_record = auth.get_user(user_id)

            return self._generate_access_token(user_id, user_record.email)
        except Exception as e:
            logger.warning(f"Token refresh failed: {e}")
            return None

    def _generate_access_token(self, user_id: str, email: str) -> str:
        payload = {
            "user_id": user_id,
            "email": email,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.access_token_expiry,
            "type": "access"
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def _generate_refresh_token(self, user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.refresh_token_expiry,
            "type": "refresh"
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)


# Singleton instance
firebase_auth = FirebaseAuthService()
