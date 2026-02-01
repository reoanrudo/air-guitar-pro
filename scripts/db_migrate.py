#!/usr/bin/env python3
"""
Database migration script.

Run with: python scripts/db_migrate.py [command]

Commands:
    migrate  - Run pending migrations
    upgrade  - Alias for migrate
    downgrade - Rollback last migration
    current  - Show current version
    history  - Show migration history
    create   - Create a new migration
"""

import os
import sys
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def run_alembic_command(args: list[str]) -> None:
    """Run an Alembic command.

    Args:
        args: Arguments to pass to alembic
    """
    cmd = ["alembic"] + args
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/db_migrate.py [command]")
        print("\nCommands:")
        print("  migrate   - Run pending migrations")
        print("  upgrade   - Alias for migrate")
        print("  downgrade - Rollback last migration")
        print("  current   - Show current version")
        print("  history   - Show migration history")
        print("  create    - Create a new migration")
        print("  revision  - Alias for create")
        sys.exit(1)

    command = sys.argv[1]

    if command in ["migrate", "upgrade"]:
        run_alembic_command(["upgrade", "head"])
    elif command == "downgrade":
        run_alembic_command(["downgrade", "-1"])
    elif command == "current":
        run_alembic_command(["current"])
    elif command == "history":
        run_alembic_command(["history"])
    elif command in ["create", "revision"]:
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
        run_alembic_command(["revision", "--autogenerate", "-m", message])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
