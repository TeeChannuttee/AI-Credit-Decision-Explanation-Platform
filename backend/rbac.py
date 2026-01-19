"""
Role-Based Access Control (RBAC) System

Implements authentication and authorization for the platform.

Roles:
- Admin: Full access, can manage users and system
- Credit Officer: Can review and override decisions
- Auditor: Read-only access to audit logs
"""

from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import jwt
import hashlib
from pydantic import BaseModel

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Simple password hashing for demo"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return hash_password(plain_password) == hashed_password

class UserRole(str, Enum):
    ADMIN = "admin"
    OFFICER = "credit_officer"
    AUDITOR = "auditor"

class User(BaseModel):
    """User model"""
    username: str
    email: str
    full_name: str
    role: UserRole
    disabled: bool = False

class UserInDB(User):
    """User model with hashed password"""
    hashed_password: str

# Mock user database (replace with real database in production)
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "System Administrator",
        "email": "admin@example.com",
        "hashed_password": hash_password("admin123"),
        "role": UserRole.ADMIN,
        "disabled": False,
    },
    "officer": {
        "username": "officer",
        "full_name": "Credit Officer",
        "email": "officer@example.com",
        "hashed_password": hash_password("officer123"),
        "role": UserRole.OFFICER,
        "disabled": False,
    },
    "auditor": {
        "username": "auditor",
        "full_name": "System Auditor",
        "email": "auditor@example.com",
        "hashed_password": hash_password("auditor123"),
        "role": UserRole.AUDITOR,
        "disabled": False,
    }
}

class RBACManager:
    """Manage role-based access control"""
    
    def __init__(self):
        self.permissions = {
            UserRole.ADMIN: [
                "view_applications",
                "make_decisions",
                "override_decisions",
                "view_audit_logs",
                "manage_users",
                "manage_system"
            ],
            UserRole.OFFICER: [
                "view_applications",
                "make_decisions",
                "override_decisions",
                "view_audit_logs"
            ],
            UserRole.AUDITOR: [
                "view_applications",
                "view_audit_logs"
            ]
        }
    
    def verify_password_method(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return verify_password(plain_password, hashed_password)
    
    def get_password_hash_method(self, password: str) -> str:
        """Hash password"""
        return hash_password(password)
    
    def get_user(self, username: str) -> Optional[UserInDB]:
        """Get user from database"""
        if username in fake_users_db:
            user_dict = fake_users_db[username]
            return UserInDB(**user_dict)
        return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Authenticate user"""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password_method(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has permission"""
        user_permissions = self.permissions.get(user.role, [])
        return permission in user_permissions
    
    def check_access(self, user: User, resource: str, action: str) -> bool:
        """Check if user can perform action on resource"""
        permission = f"{action}_{resource}"
        return self.has_permission(user, permission)

# Example usage
if __name__ == "__main__":
    rbac = RBACManager()
    
    print("="*60)
    print("RBAC SYSTEM DEMO")
    print("="*60)
    
    # Test authentication
    print("\n1. Testing Authentication:")
    user = rbac.authenticate_user("officer", "officer123")
    if user:
        print(f"✓ Authenticated: {user.full_name} ({user.role})")
        
        # Create token
        token = rbac.create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        print(f"✓ Token created: {token[:50]}...")
        
        # Verify token
        payload = rbac.verify_token(token)
        if payload:
            print(f"✓ Token verified: {payload}")
    
    # Test permissions
    print("\n2. Testing Permissions:")
    
    admin = rbac.get_user("admin")
    officer = rbac.get_user("officer")
    auditor = rbac.get_user("auditor")
    
    print(f"\nAdmin permissions:")
    for perm in ["make_decisions", "override_decisions", "manage_users"]:
        has_perm = rbac.has_permission(admin, perm)
        print(f"  {perm}: {'✓' if has_perm else '✗'}")
    
    print(f"\nOfficer permissions:")
    for perm in ["make_decisions", "override_decisions", "manage_users"]:
        has_perm = rbac.has_permission(officer, perm)
        print(f"  {perm}: {'✓' if has_perm else '✗'}")
    
    print(f"\nAuditor permissions:")
    for perm in ["make_decisions", "override_decisions", "view_audit_logs"]:
        has_perm = rbac.has_permission(auditor, perm)
        print(f"  {perm}: {'✓' if has_perm else '✗'}")
    
    print("\n" + "="*60)
    print("RBAC SYSTEM READY")
    print("="*60)
    print("\nDefault Users:")
    print("  admin / admin123 (Full access)")
    print("  officer / officer123 (Decision making)")
    print("  auditor / auditor123 (Read-only)")
