# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Autom8 Command Line Interface

Complete CLI for managing the Autom8 automation platform.
"""

import argparse
import shlex
import subprocess  # nosec B404 - subprocess used safely with input validation
import sys
from pathlib import Path
from typing import Tuple

# No license check in simple single-repo mode


try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

    # Fallback if colorama not installed
    class Fore:
        GREEN = RED = YELLOW = CYAN = ""

    class Style:
        BRIGHT = RESET_ALL = ""


__version__ = "1.0.0"


def print_success(message):
    """Print success message"""
    if HAS_COLOR:
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    else:
        print(f"✓ {message}")


def print_error(message):
    """Print error message"""
    if HAS_COLOR:
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", file=sys.stderr)
    else:
        print(f"✗ {message}", file=sys.stderr)


def print_info(message):
    """Print info message"""
    if HAS_COLOR:
        print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
    else:
        print(f"ℹ {message}")


def print_warning(message):
    """Print warning message"""
    if HAS_COLOR:
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    else:
        print(f"⚠ {message}")


def run_command(cmd, cwd=None) -> Tuple[bool, str, str]:
    """
    Run a shell command safely and return result.

    Security: Uses shlex.split() to safely parse commands.
    Never uses shell=True to prevent command injection.
    All commands are from trusted internal sources only.

    Args:
        cmd: Command string or list (from trusted internal sources)
        cwd: Optional working directory

    Returns:
        Tuple of (success: bool, stdout: str, stderr: str)
    """
    try:
        # Parse string safely or use list directly
        cmd_list = shlex.split(cmd) if isinstance(cmd, str) else cmd

        # nosec B603 - Using subprocess safely:
        # - No shell=True (prevents injection)
        # - Commands are hardcoded/trusted (not user input)
        # - Using list format (safe execution)
        # - Proper timeout prevents hanging
        result = subprocess.run(  # nosec B603
            cmd_list,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            check=False,  # Don't raise on non-zero exit
        )

        return result.returncode == 0, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", "Command execution timed out after 5 minutes"
    except FileNotFoundError as e:
        return False, "", f"Command not found: {e}"
    except Exception as e:
        return False, "", f"Unexpected error: {str(e)}"


# ============================================================================
# API Commands
# ============================================================================


def cmd_api_start(args):
    """Start the API server"""
    print_info("Starting Autom8 API server...")
    success, stdout, stderr = run_command("python -m autom8.api")
    if success:
        print_success("API server started successfully")
        print_info("API running at http://localhost:5000")
    else:
        print_error(f"Failed to start API server: {stderr}")
        return 1
    return 0


def cmd_api_stop(args):
    """Stop the API server"""
    print_info("Stopping Autom8 API server...")
    # On Windows, use taskkill; on Unix, use pkill
    if sys.platform == "win32":
        success, _, _ = run_command('taskkill /F /IM python.exe /FI "WINDOWTITLE eq autom8*"')
    else:
        success, _, _ = run_command("pkill -f 'python.*autom8.api'")

    if success:
        print_success("API server stopped")
    else:
        print_warning("No running API server found")
    return 0


def cmd_api_restart(args):
    """Restart the API server"""
    print_info("Restarting Autom8 API server...")
    cmd_api_stop(args)
    return cmd_api_start(args)


def cmd_api_status(args):
    """Check API server status"""
    print_info("Checking API server status...")
    try:
        import requests

        response = requests.get("http://localhost:5000/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API server is running (v{data.get('version', 'unknown')})")
            print_info(f"Status: {data.get('status', 'unknown')}")
            return 0
        else:
            print_error("API server is not responding correctly")
            return 1
    except Exception as e:
        print_error(f"API server is not running: {e}")
        return 1


# ============================================================================
# Scheduler Commands
# ============================================================================


def cmd_scheduler_start(args):
    """Start the scheduler"""
    print_info("Starting Autom8 scheduler...")
    success, stdout, stderr = run_command("python run_scheduler.py")
    if success:
        print_success("Scheduler started successfully")
    else:
        print_error(f"Failed to start scheduler: {stderr}")
        return 1
    return 0


def cmd_scheduler_stop(args):
    """Stop the scheduler"""
    print_info("Stopping Autom8 scheduler...")
    if sys.platform == "win32":
        success, _, _ = run_command('taskkill /F /IM python.exe /FI "WINDOWTITLE eq *scheduler*"')
    else:
        success, _, _ = run_command("pkill -f 'python.*scheduler'")

    if success:
        print_success("Scheduler stopped")
    else:
        print_warning("No running scheduler found")
    return 0


def cmd_scheduler_status(args):
    """Check scheduler status"""
    print_info("Checking scheduler status...")
    # Check if scheduler process is running
    if sys.platform == "win32":
        success, stdout, _ = run_command('tasklist /FI "IMAGENAME eq python.exe" /FO CSV')
        if "scheduler" in stdout.lower():
            print_success("Scheduler is running")
            return 0
    else:
        success, stdout, _ = run_command("ps aux | grep scheduler")
        if success and "python" in stdout:
            print_success("Scheduler is running")
            return 0

    print_error("Scheduler is not running")
    return 1


# ============================================================================
# Database Commands
# ============================================================================


def cmd_db_init(args):
    """Initialize database"""
    print_info("Initializing database...")
    success, stdout, stderr = run_command("python autom8/init_database.py")
    if success:
        print_success("Database initialized successfully")
    else:
        print_error(f"Failed to initialize database: {stderr}")
        return 1
    return 0


def cmd_db_migrate(args):
    """Run database migrations"""
    print_info("Running database migrations...")
    print_warning("Migration system not yet implemented")
    return 0


def cmd_db_seed(args):
    """Seed database with test data"""
    print_info("Seeding database with test data...")
    success, stdout, stderr = run_command("python autom8/seed_data.py")
    if success:
        print_success("Database seeded successfully")
    else:
        print_error(f"Failed to seed database: {stderr}")
        return 1
    return 0


def cmd_db_shell(args):
    """Open database shell"""
    print_info("Opening database shell...")
    success, stdout, stderr = run_command("python autom8/db_shell.py")
    return 0 if success else 1


def cmd_db_backup(args):
    """Backup database"""
    print_info("Creating database backup...")
    success, stdout, stderr = run_command("backup.bat")
    if success:
        print_success("Database backup created")
    else:
        print_error(f"Failed to create backup: {stderr}")
        return 1
    return 0


def cmd_db_restore(args):
    """Restore database from backup"""
    if not args.file:
        print_error("Backup file required. Use: autom8 db restore <file>")
        return 1

    print_info(f"Restoring database from {args.file}...")
    print_warning("Restore functionality not yet implemented")
    return 0


# ============================================================================
# System Commands
# ============================================================================


def cmd_health(args):
    """Perform system health check"""
    print_info("Performing system health check...")
    success, stdout, stderr = run_command("health-check.bat")
    if success:
        print(stdout)
        print_success("Health check completed")
    else:
        print_error(f"Health check failed: {stderr}")
        return 1
    return 0


def cmd_info(args):
    """Display system information"""
    print_info("Autom8 System Information")
    print(f"\n{Style.BRIGHT}Version:{Style.RESET_ALL} {__version__}")
    print(f"{Style.BRIGHT}Python:{Style.RESET_ALL} {sys.version.split()[0]}")
    print(f"{Style.BRIGHT}Platform:{Style.RESET_ALL} {sys.platform}")

    print(f"{Style.BRIGHT}License:{Style.RESET_ALL} Proprietary Edition")

    # Check if API is running
    try:
        import requests

        response = requests.get("http://localhost:5000/api/v1/health", timeout=2)
        if response.status_code == 200:
            print(
                f"{Style.BRIGHT}API Status:{Style.RESET_ALL} {Fore.GREEN}Running{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Style.BRIGHT}API Status:{Style.RESET_ALL} {Fore.RED}Not Running{Style.RESET_ALL}"
            )
    except Exception:
        print(f"{Style.BRIGHT}API Status:{Style.RESET_ALL} {Fore.RED}Not Running{Style.RESET_ALL}")

    return 0


def cmd_metrics(args):
    """Show system metrics"""
    print_info("Fetching system metrics...")
    try:
        import requests

        response = requests.get("http://localhost:5000/api/v1/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n{Style.BRIGHT}System Metrics:{Style.RESET_ALL}")
            print(f"  CPU Usage: {data.get('cpu_percent', 0):.1f}%")
            print(f"  Memory Usage: {data.get('memory_percent', 0):.1f}%")
            print(f"  Disk Usage: {data.get('disk_percent', 0):.1f}%")
            return 0
        else:
            print_error("Failed to fetch metrics")
            return 1
    except Exception as e:
        print_error(f"Failed to fetch metrics: {e}")
        return 1


def cmd_logs(args):
    """Display application logs"""
    log_file = Path("logs/app.log")
    if not log_file.exists():
        print_error(f"Log file not found: {log_file}")
        return 1

    print_info(f"Displaying logs from {log_file}")

    if args.tail:
        # Show last N lines
        with open(log_file, "r") as f:
            lines = f.readlines()
            for line in lines[-args.tail :]:
                print(line.rstrip())
    else:
        # Show all logs
        with open(log_file, "r") as f:
            print(f.read())

    return 0


# ============================================================================
# Testing Commands
# ============================================================================


def cmd_test(args):
    """Run tests"""
    print_info("Running tests...")

    cmd = "pytest tests/ -v"
    if args.coverage:
        cmd += " --cov=autom8 --cov-report=html --cov-report=term"

    success, stdout, stderr = run_command(cmd)
    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if success:
        print_success("All tests passed")
        if args.coverage:
            print_info("Coverage report generated in htmlcov/index.html")
    else:
        print_error("Some tests failed")
        return 1
    return 0


def cmd_test_unit(args):
    """Run unit tests only"""
    print_info("Running unit tests...")
    success, stdout, stderr = run_command("pytest tests/unit/ -v")
    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    return 0 if success else 1


def cmd_test_integration(args):
    """Run integration tests only"""
    print_info("Running integration tests...")
    success, stdout, stderr = run_command("pytest tests/integration/ -v")
    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    return 0 if success else 1


# ============================================================================
# Development Commands
# ============================================================================


def cmd_dev_setup(args):
    """Setup development environment"""
    print_info("Setting up development environment...")

    steps = [
        ("Installing dependencies", "pip install -r requirements.txt"),
        ("Installing dev dependencies", "pip install -r requirements-dev.txt"),
        ("Installing pre-commit hooks", "pre-commit install"),
        ("Initializing database", "python autom8/init_database.py"),
    ]

    for step_name, cmd in steps:
        print_info(f"{step_name}...")
        success, _, stderr = run_command(cmd)
        if success:
            print_success(f"{step_name} completed")
        else:
            print_error(f"{step_name} failed: {stderr}")
            return 1

    print_success("Development environment setup complete")
    return 0


def cmd_dev_lint(args):
    """Run linters"""
    print_info("Running linters...")
    success, stdout, stderr = run_command("flake8 autom8/ tests/")
    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    return 0 if success else 1


def cmd_dev_format(args):
    """Format code"""
    print_info("Formatting code with Black...")
    success, stdout, stderr = run_command("black autom8/ tests/")
    print(stdout)
    if success:
        print_success("Code formatted successfully")
    else:
        print_error(f"Formatting failed: {stderr}")
        return 1
    return 0


# ============================================================================
# Contact Commands
# ============================================================================


def cmd_contacts_list(args):
    """List all contacts"""
    print_info("Fetching contacts...")
    try:
        import requests

        response = requests.get("http://localhost:5000/api/v1/contacts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            contacts = data.get("contacts", [])
            if contacts:
                print(f"\n{Style.BRIGHT}Contacts:{Style.RESET_ALL}")
                for contact in contacts:
                    print(f"  [{contact['id']}] {contact['name']} - {contact['phone']}")
            else:
                print_info("No contacts found")
            return 0
        else:
            print_error("Failed to fetch contacts")
            return 1
    except Exception as e:
        print_error(f"Failed to fetch contacts: {e}")
        return 1


def cmd_contacts_add(args):
    """Add new contact (interactive)"""
    print_info("Add New Contact")

    try:
        name = input("Name: ").strip()
        phone = input("Phone: ").strip()
        email = input("Email (optional): ").strip() or None

        import requests

        response = requests.post(
            "http://localhost:5000/api/v1/contacts",
            json={"name": name, "phone": phone, "email": email},
            timeout=5,
        )

        if response.status_code == 201:
            contact = response.json()
            print_success(f"Contact created with ID: {contact['id']}")
            return 0
        else:
            print_error(
                f"Failed to create contact: {response.json().get('message', 'Unknown error')}"
            )
            return 1
    except KeyboardInterrupt:
        print_info("\nCancelled")
        return 0
    except Exception as e:
        print_error(f"Failed to create contact: {e}")
        return 1


def cmd_contacts_delete(args):
    """Delete contact by ID"""
    if not args.id:
        print_error("Contact ID required. Use: autom8 contacts delete <id>")
        return 1

    print_info(f"Deleting contact {args.id}...")
    try:
        import requests

        response = requests.delete(f"http://localhost:5000/api/v1/contacts/{args.id}", timeout=5)

        if response.status_code == 204:
            print_success(f"Contact {args.id} deleted")
            return 0
        else:
            print_error(
                f"Failed to delete contact: {response.json().get('message', 'Unknown error')}"
            )
            return 1
    except Exception as e:
        print_error(f"Failed to delete contact: {e}")
        return 1


# ============================================================================
# Main CLI Setup
# ============================================================================


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Autom8 - Enterprise Systems Automation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  autom8 api start              Start the API server
  autom8 health                 Check system health
  autom8 test --coverage        Run tests with coverage
  autom8 contacts list          List all contacts
For more information, visit: https://github.com/orenyalphy256-glitch/op-alpha-systems-automation
        """,
    )

    parser.add_argument("-v", "--version", action="version", version=f"Autom8 {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # API commands
    api_parser = subparsers.add_parser("api", help="API server management")
    api_subparsers = api_parser.add_subparsers(dest="api_command")
    api_subparsers.add_parser("start", help="Start API server").set_defaults(func=cmd_api_start)
    api_subparsers.add_parser("stop", help="Stop API server").set_defaults(func=cmd_api_stop)
    api_subparsers.add_parser("restart", help="Restart API server").set_defaults(
        func=cmd_api_restart
    )
    api_subparsers.add_parser("status", help="Check API status").set_defaults(func=cmd_api_status)

    # Scheduler commands
    scheduler_parser = subparsers.add_parser("scheduler", help="Scheduler management")
    scheduler_subparsers = scheduler_parser.add_subparsers(dest="scheduler_command")
    scheduler_subparsers.add_parser("start", help="Start scheduler").set_defaults(
        func=cmd_scheduler_start
    )
    scheduler_subparsers.add_parser("stop", help="Stop scheduler").set_defaults(
        func=cmd_scheduler_stop
    )
    scheduler_subparsers.add_parser("status", help="Check scheduler status").set_defaults(
        func=cmd_scheduler_status
    )

    # Database commands
    db_parser = subparsers.add_parser("db", help="Database management")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    db_subparsers.add_parser("init", help="Initialize database").set_defaults(func=cmd_db_init)
    db_subparsers.add_parser("migrate", help="Run migrations").set_defaults(func=cmd_db_migrate)
    db_subparsers.add_parser("seed", help="Seed test data").set_defaults(func=cmd_db_seed)
    db_subparsers.add_parser("shell", help="Open database shell").set_defaults(func=cmd_db_shell)
    db_subparsers.add_parser("backup", help="Backup database").set_defaults(func=cmd_db_backup)
    restore_parser = db_subparsers.add_parser("restore", help="Restore database")
    restore_parser.add_argument("file", help="Backup file to restore from")
    restore_parser.set_defaults(func=cmd_db_restore)

    # System commands
    subparsers.add_parser("health", help="System health check").set_defaults(func=cmd_health)
    subparsers.add_parser("info", help="System information").set_defaults(func=cmd_info)
    subparsers.add_parser("metrics", help="System metrics").set_defaults(func=cmd_metrics)
    logs_parser = subparsers.add_parser("logs", help="View logs")
    logs_parser.add_argument("--tail", type=int, metavar="N", help="Show last N lines")
    logs_parser.set_defaults(func=cmd_logs)

    # Testing commands
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    test_parser.set_defaults(func=cmd_test)

    test_subparsers = test_parser.add_subparsers(dest="test_type")
    test_subparsers.add_parser("unit", help="Run unit tests").set_defaults(func=cmd_test_unit)
    test_subparsers.add_parser("integration", help="Run integration tests").set_defaults(
        func=cmd_test_integration
    )

    # Development commands
    dev_parser = subparsers.add_parser("dev", help="Development tools")
    dev_subparsers = dev_parser.add_subparsers(dest="dev_command")
    dev_subparsers.add_parser("setup", help="Setup dev environment").set_defaults(
        func=cmd_dev_setup
    )
    dev_subparsers.add_parser("lint", help="Run linters").set_defaults(func=cmd_dev_lint)
    dev_subparsers.add_parser("format", help="Format code").set_defaults(func=cmd_dev_format)

    # Contact commands
    contacts_parser = subparsers.add_parser("contacts", help="Contact management")
    contacts_subparsers = contacts_parser.add_subparsers(dest="contacts_command")
    contacts_subparsers.add_parser("list", help="List contacts").set_defaults(
        func=cmd_contacts_list
    )
    contacts_subparsers.add_parser("add", help="Add contact").set_defaults(func=cmd_contacts_add)
    delete_parser = contacts_subparsers.add_parser("delete", help="Delete contact")
    delete_parser.add_argument("id", type=int, help="Contact ID")
    delete_parser.set_defaults(func=cmd_contacts_delete)

    # Parse arguments
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    if hasattr(args, "func"):
        try:
            return args.func(args)
        except KeyboardInterrupt:
            print_info("\nOperation cancelled")
            return 0
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
