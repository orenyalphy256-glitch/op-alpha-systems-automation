"""
CI/CD Pipeline Simulation Script
Automates: Lint -> Test -> Build -> Deploy workflow
Agent ALO
"""

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_stage(stage_name):
    """Print pipeline stage header."""
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}STAGE: {stage_name}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")


def print_success(message):
    """Print success message."""
    print(f"{Colors.OKGREEN}SUCCESS: {message}{Colors.ENDC}")


def print_error(message):
    """Print error message."""
    print(f"{Colors.FAIL}ERROR: {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message."""
    print(f"{Colors.WARNING}WARNING: {message}{Colors.ENDC}")


def print_info(message):
    """Print informational message."""
    print(f"{Colors.OKCYAN}INFO: {message}{Colors.ENDC}")


def run_command(command, description, fail_on_error=True):
    """Run shell command and handle output.
    Returns True if command succeeds, False otherwise.
    """
    print_info(f"Running: {description}")
    print(f"Command: {' '.join(command) if isinstance(command, list) else command}\n")

    try:
        # Run command
        if isinstance(command, str):
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
                encoding="utf-8",
                errors="replace",
            )
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
                encoding="utf-8",
                errors="replace",
            )

        # Print stdout
        if result.stdout:
            print(f"{Colors.OKBLUE}OUTPUT:\n{result.stdout}{Colors.ENDC}")

        # Check result
        if result.returncode == 0:
            print_success(f"{description} completed successfully.")
            return True
        else:
            print_error(f"{description} failed with return code {result.returncode}.")
            if result.stderr:
                print(f"{Colors.FAIL}ERROR OUTPUT:\n{result.stderr}{Colors.ENDC}")

            if fail_on_error:
                print_error(f"Exiting pipeline due to failed {description}.")
                sys.exit(1)
            return False

    except subprocess.TimeoutExpired:
        print_error(f"{description} timed out.")
        if fail_on_error:
            print_error(f"Exiting pipeline due to timeout in {description}.")
            sys.exit(1)
        return False
    except Exception as e:
        print_error(f"An error occurred while running {description}: {str(e)}")
        if fail_on_error:
            print_error(f"Exiting pipeline due to error in {description}.")
            sys.exit(1)
        return False


def stage_setup():
    """Stage 1: Environment Setup."""
    print_stage("1. Environment Setup")

    # Check Python version
    python_version = sys.version.split()[0]
    print_info(f"Python version: {python_version}")

    # Check virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print_success("Virtual environment is active.")
    else:
        print_warning("Virtual environment is not active. It's recommended to use one.")

    # Check required tools
    required_tools = ["pip", "pytest", "flake8", "bandit", "black", "docker"]
    for tool in required_tools:
        try:
            if tool == "docker":
                cmd = ["docker", "--version"]
            else:
                cmd = [sys.executable, "-m", tool, "--version"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print_success(f"{tool} is installed: {result.stdout.strip().splitlines()[0]}")
            else:
                print_error(f"{tool} is not installed or not found.")
        except FileNotFoundError:
            print_error(f"{tool} is not installed or not found.")
        except Exception as e:
            print_warning(f"Could not check {tool} version: {str(e)}")

    # Install package in editable mode for coverage
    print_info("Installing package in editable mode for coverage...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            check=True,
            capture_output=True,
            text=True,
        )
        print_success("Package installed in editable mode.")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install package in editable mode: {e.stderr}")
        return False

    print_success("Setup stage completed.")
    return True


def stage_lint():
    """Stage 2: Code Linting."""
    print_stage("2. Code Quality Checks (Linting)")

    # Flake8 linting
    success = run_command(
        [sys.executable, "-m", "flake8", "autom8/", "--count", "--statistics"],
        "Flake8 Linting",
        fail_on_error=False,
    )

    if not success:
        print_warning("Flake8 found issues. Please fix them before proceeding.")
        return False

    return True


def stage_format_check():
    """Stage 3: Code formatting check."""
    print_stage("3. Code Formatting Check")

    # Black formatting check
    success = run_command(
        [sys.executable, "-m", "black", "--check", "autom8/"],
        "Black Formatting Check",
        fail_on_error=False,
    )

    if not success:
        print_warning("Black found formatting issues.")
        print_info("Run 'black autom8/' to format the code.")
        return False

    return True


def stage_security():
    """Stage 4: Security Analysis."""
    print_stage("4. Security Analysis")

    # Bandit security analysis
    success = run_command(
        [sys.executable, "-m", "bandit", "-r", "autom8/", "-ll"],
        "Bandit Security Analysis",
        fail_on_error=False,
    )

    if not success:
        print_warning("Bandit found security issues. Please review them.")

    return success


def stage_tests():
    """Stage 5: Run test suite."""
    print_stage("5. TEST - Unit and Integration Tests")

    # Run pytest with coverage
    success = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--cov=autom8",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-report=html",
            "--cov-fail-under=80",
            "--tb=short",
            "-W",
            "ignore::ResourceWarning",  # Ignore resource warnings
            "-W",
            "ignore::DeprecationWarning",
            "--disable-warnings",
        ],
        "Test suite with coverage",
        fail_on_error=True,  # This is a HARD STOP
    )

    return success


def stage_build():
    """Stage 6: Build Docker Image."""
    print_stage("6. BUILD - Docker Image Build")

    # Get current timestamp for tagging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build Docker image
    success = run_command(
        ["docker", "build", "-t", "autom8:latest", "-t", f"autom8:{timestamp}", "."],
        "Docker image build",
        fail_on_error=True,  # This is a HARD STOP
    )

    if success:
        print_info(f"Image tagged as autom8:latest and autom8:{timestamp}")

    return success


def stage_image_scan():
    """Stage 7: Scan Docker Image for Vulnerabilities."""
    print_stage("7. IMAGE SCAN - Docker Image Vulnerability Scan")

    # Check if trivy is installed
    if not shutil.which("trivy"):
        print_warning("Trivy is not installed. Skipping image scan.")
        return True

    # Scan Docker image using Trivy
    success = run_command(
        ["trivy", "image", "--severity", "HIGH,CRITICAL", "autom8:latest"],
        "Docker image vulnerability scan",
        fail_on_error=False,
    )

    if not success:
        print_warning("Vulnerabilities found in Docker image. Please review them.")

    return True


def stage_deploy_staging():
    """Stage 8: Deploy to staging (simulation)."""
    print_stage("8. DEPLOY STAGING - Test Environment")

    print_info("Would deploy to staging environment.")
    print_info("For local simulation, we'll restart Docker compose")

    # Stop existing containers
    run_command(
        ["docker", "compose", "down"], "Stopping existing staging containers", fail_on_error=False
    )

    # Start new containers
    success = run_command(
        ["docker", "compose", "up", "-d"],
        "Starting staging containers",
        fail_on_error=True,  # This is a HARD STOP
    )

    if success:
        print_success("Application redeployed to staging environment successfully.")

        # Wait for health check
        print_info("Waiting for application to become healthy (30s)...")
        time.sleep(30)

        # Check container status
        run_command(["docker", "compose", "ps"], "Checking container status", fail_on_error=False)

    return success


def stage_smoke_test():
    """Stage 9: Smoke Tests."""
    print_stage("9. SMOKE TEST - Basic Health Checks")

    print_info("Running basic health checks...")

    try:
        import requests

        # Test API health endpoint
        response = requests.get("http://localhost:5000/api/v1/health", timeout=10)

        if response.status_code == 200:
            print_success("API health check passed.")
            print(f"Response: {response.json()}")
            return True
        else:
            print_error(f"API health check failed with status code {response.status_code}.")
            return False

    except Exception as e:
        print_error(f"Smoke test failed: {str(e)}")
        print_warning("Make sure Docker containers are running and accessible.")
        return False


def generate_report(results):
    """Generate pipeline execution report."""
    print_stage("PIPELINE REPORT")

    total_stages = len(results)
    passed_stages = sum(1 for r in results.values() if r)
    failed_stages = total_stages - passed_stages

    print(f"\n{Colors.BOLD}Pipeline Execution Summary:{Colors.ENDC}")
    print(f"Total Stages: {total_stages}")
    print(f"Passed: {Colors.OKGREEN}{passed_stages}{Colors.ENDC}")
    print(f"Failed: {Colors.FAIL}{failed_stages}{Colors.ENDC}")
    success_rate = (passed_stages / total_stages) * 100
    print(f"Success Rate: {Colors.OKCYAN}{success_rate:.1f}%{Colors.ENDC}\n")

    print(f"{Colors.BOLD}Detailed Stage Results:{Colors.ENDC}")
    for stage, success in results.items():
        status = (
            f"{Colors.OKGREEN}PASSED{Colors.ENDC}"
            if success
            else f"{Colors.FAIL}FAILED{Colors.ENDC}"
        )
        print(f" {stage:<25} {status}")

    # Save to file
    report_path = (
        Path("99-Logs") / f'pipeline_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_stages": total_stages,
        "passed": passed_stages,
        "failed": failed_stages,
        "success_rate": f"{(passed_stages / total_stages) * 100:.1f}%",
        "stages": {stage: "PASSED" if success else "FAILED" for stage, success in results.items()},
    }

    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\n{Colors.OKCYAN}Pipeline report saved to {report_path}{Colors.ENDC}")

    # Overall result
    if failed_stages == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}PIPELINE COMPLETED SUCCESSFULLY!{Colors.ENDC}\n")
        return True
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}PIPELINE FAILED WITH ERRORS.{Colors.ENDC}\n")
        return False


def main():
    """Main Pipeline execution."""
    print(f"{Colors.HEADER}{Colors.BOLD}Starting CI/CD Pipeline...{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")

    start_time = time.time()

    # Execute pipeline stages
    results = {}

    try:
        results["Setup"] = stage_setup()
        results["Linting"] = stage_lint()
        results["Formatting"] = stage_format_check()
        results["Security Analysis"] = stage_security()
        results["Tests"] = stage_tests()
        results["Build"] = stage_build()
        results["Image Scan"] = stage_image_scan()
        results["Deploy Staging"] = stage_deploy_staging()
        results["Smoke Test"] = stage_smoke_test()

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Pipeline interrupted by user. Exiting...{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {str(e)}{Colors.ENDC}")
        sys.exit(1)

    # Calculate duration
    duration = time.time() - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    msg = f"\n{Colors.OKCYAN}Pipeline completed in {minutes} minutes "
    msg += f"and {seconds} seconds.{Colors.ENDC}"
    print(msg)

    # Generate report
    success = generate_report(results)

    # Exit with appropriate code
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
