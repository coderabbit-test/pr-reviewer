"""
Security utilities and helpers for authentication
"""
import re
import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta


class PasswordValidator:
    """Password validation utility"""
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """
        Validate password strength and return detailed feedback
        """
        issues = []
        score = 0
        
        # Length check
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        else:
            score += 1
            
        # Uppercase check
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        else:
            score += 1
            
        # Lowercase check
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 1
            
        # Number check
        if not re.search(r'\d', password):
            issues.append("Password must contain at least one number")
        else:
            score += 1
            
        # Special character check
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")
        else:
            score += 1
            
        # Common password check
        common_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master"
        ]
        
        if password.lower() in common_passwords:
            issues.append("Password is too common")
            score -= 1
            
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]
        strength = strength_levels[min(score, len(strength_levels) - 1)]
        
        return {
            "valid": len(issues) == 0,
            "score": score,
            "strength": strength,
            "issues": issues
        }


class SecurityHeaders:
    """Security headers utility"""
    
    @staticmethod
    def get_security_headers() -> dict:
        """
        Get recommended security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


class TokenGenerator:
    """Token generation utilities"""
    
    @staticmethod
    def generate_session_token() -> str:
        """
        Generate a secure session token
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key
        """
        return secrets.token_urlsafe(48)
    
    @staticmethod
    def generate_verification_code() -> str:
        """
        Generate a 6-digit verification code
        """
        return f"{secrets.randbelow(1000000):06d}"


class IPWhitelist:
    """IP whitelist management"""
    
    def __init__(self):
        self.allowed_ips = set()
        self.blocked_ips = set()
    
    def add_allowed_ip(self, ip: str):
        """Add IP to whitelist"""
        self.allowed_ips.add(ip)
    
    def add_blocked_ip(self, ip: str):
        """Add IP to blacklist"""
        self.blocked_ips.add(ip)
    
    def is_ip_allowed(self, ip: str) -> bool:
        """Check if IP is allowed"""
        if ip in self.blocked_ips:
            return False
        if not self.allowed_ips:  # If no whitelist, allow all
            return True
        return ip in self.allowed_ips


class AuditLogger:
    """Audit logging utility"""
    
    def __init__(self):
        self.logs = []
    
    def log_event(self, 
                  user_id: str, 
                  action: str, 
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  details: Optional[dict] = None):
        """
        Log an audit event
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {}
        }
        
        self.logs.append(log_entry)
        
        # In production, this would save to a database
        print(f"AUDIT: {log_entry}")
    
    def get_user_logs(self, user_id: str, limit: int = 100) -> list:
        """
        Get audit logs for a specific user
        """
        user_logs = [log for log in self.logs if log["user_id"] == user_id]
        return sorted(user_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]


# Global instances
password_validator = PasswordValidator()
security_headers = SecurityHeaders()
token_generator = TokenGenerator()
ip_whitelist = IPWhitelist()
audit_logger = AuditLogger()
