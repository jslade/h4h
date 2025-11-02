#!/usr/bin/env python
"""
Script to create a new user in the h4h application.

Usage:
    python scripts/create_user.py <username> <password>

Example:
    python scripts/create_user.py admin mypassword123
"""

import os
import sys

import click
import structlog

# Add the parent directory to the path so we can import hfh
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hfh.app import APP
from hfh.db import DB
from hfh.models.user import User
from hfh.services.auth_service import AuthService

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
)

logger = structlog.get_logger()


@click.command()
@click.argument("username")
@click.argument("password")
@click.option(
    "--min-password-length",
    default=4,
    help="Minimum password length (default: 4)",
    type=int,
)
def create_user(username: str, password: str, min_password_length: int):
    """Create a new user in the h4h application.

    \b
    Arguments:
        USERNAME: The username for the new user
        PASSWORD: The password for the new user

    \b
    Example:
        python scripts/create_user.py admin mypassword123
    """
    logger.info("Starting user creation", username=username)

    # Validate password length
    if len(password) < min_password_length:
        logger.error(
            "Password too short",
            password_length=len(password),
            min_length=min_password_length,
        )
        click.echo(
            click.style(
                f"Error: Password must be at least {min_password_length} characters long",
                fg="red",
            )
        )
        sys.exit(1)

    with APP.app_context():
        # Check if user already exists
        existing_user = User.with_name(username)
        if existing_user:
            logger.error(
                "User already exists", username=username, user_id=existing_user.id
            )
            click.echo(click.style(f"Error: User '{username}' already exists!", fg="red"))
            sys.exit(1)

        # Create new user
        try:
            user = User(name=username)
            AuthService.set_user_password(user, password)
            DB.session.add(user)
            DB.session.commit()

            logger.info("User created successfully", username=username, user_id=user.id)
            click.echo(
                click.style(
                    f"✓ Successfully created user: {username} (id: {user.id})", fg="green"
                )
            )
        except Exception as e:
            logger.error("Failed to create user", username=username, error=str(e))
            click.echo(click.style(f"Error: Failed to create user: {e}", fg="red"))
            sys.exit(1)


if __name__ == "__main__":
    create_user()
