#!/usr/bin/env python
"""
Script to create a new user in the h4h application.

Usage:
    python scripts/create_user.py <username> <password>

Example:
    python scripts/create_user.py admin mypassword123
"""

import sys
import os

# Add the parent directory to the path so we can import hfh
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hfh.app import APP
from hfh.db import DB
from hfh.models.user import User
from hfh.services.auth_service import AuthService


def create_user(username, password):
    """Create a new user with the given username and password."""
    with APP.app_context():
        # Check if user already exists
        existing_user = User.with_name(username)
        if existing_user:
            print(f"Error: User '{username}' already exists!")
            return False

        # Create new user
        user = User(name=username)
        AuthService.set_user_password(user, password)
        DB.session.add(user)
        DB.session.commit()

        print(f"Successfully created user: {username} (id: {user.id})")
        return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/create_user.py <username> <password>")
        print("\nExample:")
        print("    python scripts/create_user.py admin mypassword123")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    if len(password) < 8:
        print("Error: Password must be at least 8 characters long")
        sys.exit(1)

    success = create_user(username, password)
    sys.exit(0 if success else 1)
