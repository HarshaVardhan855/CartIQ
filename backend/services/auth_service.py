import hashlib
import os
import uuid
import re
from typing import Tuple, Dict, Any, Optional
from database.connection import get_db
from database.models import UserModel

class AuthService:
    def __init__(self):
        pass

    def _hash_password(self, password: str, salt: bytes = None) -> str:
        """Hashes a password using PBKDF2 HMAC with SHA-256."""
        if salt is None:
            salt = os.urandom(16)
        
        # 100,000 iterations is a reasonable baseline for PBKDF2
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        # Store as salt$hash to verify later
        return f"{salt.hex()}${key.hex()}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifies a password against a stored hash."""
        try:
            salt_hex, key_hex = password_hash.split('$')
            salt = bytes.fromhex(salt_hex)
            key = bytes.fromhex(key_hex)
            
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
            )
            return new_key == key
        except ValueError:
            return False

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validates password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        return True, ""

    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validates email format."""
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_regex.match(email):
            return False, "Invalid email address format."
        return True, ""

    def register_user(self, full_name: str, email: str, password: str) -> Tuple[bool, str]:
        """Registers a new user in the database."""
        if not full_name.strip():
            return False, "Full Name is required."
        
        is_valid_email, email_msg = self.validate_email(email)
        if not is_valid_email:
            return False, email_msg
            
        is_valid_pwd, pwd_msg = self.validate_password(password)
        if not is_valid_pwd:
            return False, pwd_msg

        db = next(get_db())
        try:
            # Check if email exists
            existing_user = db.query(UserModel).filter(UserModel.email == email).first()
            if existing_user:
                return False, "Email is already registered."
            
            user_id = str(uuid.uuid4())
            pwd_hash = self._hash_password(password)
            
            new_user = UserModel(
                id=user_id,
                full_name=full_name.strip(),
                email=email.strip().lower(),
                password_hash=pwd_hash
            )
            
            db.add(new_user)
            db.commit()
            return True, "User registered successfully."
        except Exception as e:
            db.rollback()
            return False, f"An error occurred: {str(e)}"
        finally:
            db.close()

    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Authenticates a user and returns their safe session data."""
        if not email or not password:
            return False, None, "Email and password are required."
            
        db = next(get_db())
        try:
            user = db.query(UserModel).filter(UserModel.email == email.strip().lower()).first()
            if not user:
                return False, None, "Invalid email or password."
                
            if not self._verify_password(password, user.password_hash):
                return False, None, "Invalid email or password."
                
            # Return safe user data for session
            user_data = {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email
            }
            return True, user_data, "Login successful."
        except Exception as e:
            return False, None, f"An error occurred: {str(e)}"
        finally:
            db.close()
