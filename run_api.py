"""
run_api.py - Flask API Server Launcher
Usage:  python run_api.py
"""

import os

from autom8.api import app
from autom8.core import log


def main():
    """Run Flask development server."""

    # Configuration
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 5000))
    debug = os.getenv("API_DEBUG", "True").lower() == "true"

    log.info(f"Starting Flask API server on {host}:{port}")
    log.info(f"Debug mode: {debug}")
    log.info(f"Access API at: http://{host}:{port}/")

    # Run server
    app.run(host=host, port=port, debug=debug, use_reloader=debug)


if __name__ == "__main__":
    main()
