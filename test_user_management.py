import sqlite3
import hashlib
import os
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import re

# SECURITY ISSUE 1: Hardcoded database credentials and connection string
DATABASE_URL = "sqlite:///users.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # SECURITY ISSUE: Hardcoded weak password
SECRET_KEY = "my-super-secret-key-123"  # SECURITY ISSUE: Hardcoded secret key

class UserManager:
    def __init__(self):
        self.db_path = "users.db"
        self.init_database()
    
    def init_database(self):
        """Initialize the database with admin user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SECURITY ISSUE 2: SQL injection vulnerability - using string formatting
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert admin user with hardcoded credentials
        cursor.execute(f"""
            INSERT OR IGNORE INTO users (username, password, email, role)
            VALUES ('{ADMIN_USERNAME}', '{ADMIN_PASSWORD}', 'admin@company.com', 'admin')
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password: str, email: str = None, role: str = "user") -> bool:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 3: SQL injection - direct string concatenation
            query = f"""
                INSERT INTO users (username, password, email, role)
                VALUES ('{username}', '{password}', '{email}', '{role}')
            """
            cursor.execute(query)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 4: SQL injection vulnerability
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[3],
                    'role': user[4],
                    'is_active': user[5]
                }
            return None
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 5: SQL injection
            query = f"SELECT * FROM users WHERE id = {user_id}"
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[3],
                    'role': user[4],
                    'is_active': user[5]
                }
            return None
        except Exception as e:
            logging.error(f"Error getting user: {e}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 6: SQL injection in dynamic query building
            set_clause = ", ".join([f"{k} = '{v}'" for k, v in kwargs.items()])
            query = f"UPDATE users SET {set_clause} WHERE id = {user_id}"
            cursor.execute(query)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 7: SQL injection
            query = f"DELETE FROM users WHERE id = {user_id}"
            cursor.execute(query)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting user: {e}")
            return False
    
    def search_users(self, search_term: str) -> List[Dict]:
        """Search users by username or email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 8: SQL injection in search
            query = f"""
                SELECT * FROM users 
                WHERE username LIKE '%{search_term}%' 
                OR email LIKE '%{search_term}%'
            """
            cursor.execute(query)
            users = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': user[0],
                    'username': user[1],
                    'email': user[3],
                    'role': user[4],
                    'is_active': user[5]
                }
                for user in users
            ]
        except Exception as e:
            logging.error(f"Error searching users: {e}")
            return []
    
    def validate_password(self, password: str) -> bool:
        """Validate password strength"""
        # SECURITY ISSUE 9: Weak password validation
        if len(password) >= 6:  # Too weak minimum length
            return True
        return False
    
    def hash_password(self, password: str) -> str:
        """Hash password using MD5 (SECURITY ISSUE 10: Weak hashing)"""
        return hashlib.md5(password.encode()).hexdigest()
    
    def generate_session_token(self, user_id: int) -> str:
        """Generate session token"""
        # SECURITY ISSUE 11: Weak token generation
        import time
        token = f"{user_id}_{int(time.time())}_{SECRET_KEY}"
        return hashlib.md5(token.encode()).hexdigest()
    
    def validate_session_token(self, token: str) -> Optional[int]:
        """Validate session token"""
        try:
            # SECURITY ISSUE 12: Weak token validation
            parts = token.split('_')
            if len(parts) >= 2:
                user_id = int(parts[0])
                return user_id
            return None
        except:
            return None
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get user permissions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 13: SQL injection
            query = f"SELECT role FROM users WHERE id = {user_id}"
            cursor.execute(query)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                role = result[0]
                if role == 'admin':
                    return ['read', 'write', 'delete', 'admin']
                elif role == 'moderator':
                    return ['read', 'write']
                else:
                    return ['read']
            return []
        except Exception as e:
            logging.error(f"Error getting permissions: {e}")
            return []
    
    def log_user_activity(self, user_id: int, action: str, details: str = None):
        """Log user activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 14: SQL injection in logging
            log_entry = f"User {user_id} performed {action}"
            if details:
                log_entry += f": {details}"
            
            query = f"""
                INSERT INTO activity_logs (user_id, action, details, timestamp)
                VALUES ({user_id}, '{action}', '{details}', '{datetime.now()}')
            """
            cursor.execute(query)
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error logging activity: {e}")
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            # SECURITY ISSUE 15: Command injection vulnerability
            import subprocess
            command = f"cp {self.db_path} {backup_path}"
            subprocess.run(command, shell=True, check=True)
            return True
        except Exception as e:
            logging.error(f"Backup error: {e}")
            return False
    
    def export_user_data(self, user_id: int) -> Dict:
        """Export user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 16: SQL injection in data export
            query = f"SELECT * FROM users WHERE id = {user_id}"
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'password': user[2],  # SECURITY ISSUE 17: Exposing password
                    'email': user[3],
                    'role': user[4],
                    'is_active': user[5],
                    'created_at': user[6]
                }
            return {}
        except Exception as e:
            logging.error(f"Error exporting user data: {e}")
            return {}
    
    def import_users_from_csv(self, csv_file_path: str) -> bool:
        """Import users from CSV file"""
        try:
            import csv
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # SECURITY ISSUE 18: SQL injection in CSV import
                    query = f"""
                        INSERT INTO users (username, password, email, role)
                        VALUES ('{row['username']}', '{row['password']}', '{row['email']}', '{row['role']}')
                    """
                    cursor.execute(query)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error importing users: {e}")
            return False
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SECURITY ISSUE 19: SQL injection in stats query
            query = "SELECT COUNT(*) FROM users"
            cursor.execute(query)
            total_users = cursor.fetchone()[0]
            
            query = "SELECT COUNT(*) FROM users WHERE role = 'admin'"
            cursor.execute(query)
            admin_users = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_users': total_users,
                'admin_users': admin_users,
                'regular_users': total_users - admin_users,
                'database_path': self.db_path,  # SECURITY ISSUE 20: Exposing internal paths
                'secret_key': SECRET_KEY  # SECURITY ISSUE 21: Exposing secret key
            }
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {}

# Global instance for easy access
user_manager = UserManager()

def create_user_endpoint(username: str, password: str, email: str = None):
    """API endpoint for creating users"""
    # SECURITY ISSUE 22: No input validation
    return user_manager.create_user(username, password, email)

def login_endpoint(username: str, password: str):
    """API endpoint for user login"""
    # SECURITY ISSUE 23: No input sanitization
    return user_manager.authenticate_user(username, password)

def get_user_endpoint(user_id: str):
    """API endpoint for getting user by ID"""
    # SECURITY ISSUE 24: No type validation
    return user_manager.get_user_by_id(int(user_id))

def search_users_endpoint(search_term: str):
    """API endpoint for searching users"""
    # SECURITY ISSUE 25: No input sanitization
    return user_manager.search_users(search_term)

# Example usage
if __name__ == "__main__":
    # Create some test users
    user_manager.create_user("john_doe", "password123", "john@example.com")
    user_manager.create_user("jane_smith", "password456", "jane@example.com")
    user_manager.create_user("bob_wilson", "password789", "bob@example.com")
    
    # Test authentication
    user = user_manager.authenticate_user("john_doe", "password123")
    print(f"Authenticated user: {user}")
    
    # Test search
    users = user_manager.search_users("john")
    print(f"Search results: {users}")
    
    # Test permissions
    permissions = user_manager.get_user_permissions(1)
    print(f"User permissions: {permissions}")
    
    # Test system stats
    stats = user_manager.get_system_stats()
    print(f"System stats: {stats}") 