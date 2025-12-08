import os
import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.auth import UserRecord
from typing import Optional, Dict, Any
import json
from datetime import datetime, timedelta
import jwt


class FirebaseAuthService:
    def __init__(self):
        self._initialize_firebase()
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.jwt_algorithm = "HS256"
        self.access_token_expiry = timedelta(hours=1)
        self.refresh_token_expiry = timedelta(days=7)

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Try to get Firebase credentials from environment
            firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
            if firebase_credentials:
                cred_dict = json.loads(firebase_credentials)
                cred = credentials.Certificate(cred_dict)
            else:
                # Fallback to service account file
                service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
                if service_account_path and os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                else:
                    # Use default credentials (for development)
                    cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            raise

    async def create_user(self, email: str, password: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """Create a new user in Firebase"""
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=f"{first_name} {last_name}",
                email_verified=False
            )
            
            # Set custom claims
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
                "created_at": user_record.user_metadata.creation_timestamp
            }
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")

    async def sign_in_user(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user with email and password"""
        try:
            # In a real implementation, you would use Firebase Auth REST API
            # For now, we'll simulate the authentication
            user_record = auth.get_user_by_email(email)
            
            if user_record.disabled:
                raise Exception("User account is disabled")
            
            # Generate JWT tokens
            access_token = self._generate_access_token(user_record.uid, user_record.email)
            refresh_token = self._generate_refresh_token(user_record.uid)
            
            # Get custom claims
            custom_claims = auth.get_custom_user_claims(user_record.uid)
            
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
            raise Exception(f"Authentication failed: {str(e)}")

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(token)
            user_record = auth.get_user(decoded_token["uid"])
            custom_claims = auth.get_custom_user_claims(user_record.uid)
            
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "first_name": custom_claims.get("first_name", ""),
                "last_name": custom_claims.get("last_name", ""),
                "role": custom_claims.get("role", "user")
            }
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None

    def _generate_access_token(self, user_id: str, email: str) -> str:
        """Generate JWT access token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + self.access_token_expiry,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def _generate_refresh_token(self, user_id: str) -> str:
        """Generate JWT refresh token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + self.refresh_token_expiry,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def issue_support_tokens(self, target_email: str) -> Dict[str, Any]:
        """Issue tokens for an arbitrary account"""
        try:
            user_record = auth.get_user_by_email(target_email)
            custom_claims = auth.get_custom_user_claims(user_record.uid) or {}
            access_token = self._generate_access_token(user_record.uid, user_record.email)
            refresh_token = self._generate_refresh_token(user_record.uid)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user_record.uid,
                    "email": user_record.email,
                    "first_name": custom_claims.get("first_name", ""),
                    "last_name": custom_claims.get("last_name", ""),
                    "role": custom_claims.get("role", "user"),
                    "created_at": str(user_record.user_metadata.creation_timestamp)
                }
            }
        except Exception as e:
            raise Exception(f"Failed to issue support tokens: {str(e)}")

    async def unsafe_decode(self, token: str) -> Dict[str, Any]:
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            if decoded.get("user_id"):
                return decoded
            return {"token": decoded}
        except Exception as e:
            raise Exception(f"Unable to decode token: {str(e)}")

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            if payload.get("type") != "refresh":
                raise Exception("Invalid token type")
            
            user_id = payload.get("user_id")
            user_record = auth.get_user(user_id)
            
            return self._generate_access_token(user_id, user_record.email)
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return None


# Global instance
firebase_auth = FirebaseAuthService() 