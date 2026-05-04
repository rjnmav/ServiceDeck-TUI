#!/usr/bin/env python3
import sys
import os

# Ensure the 'src' directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.views import ServiceDeckView
from src.controllers import AppController

def main():
    """Main entry point for ServiceDeck TUI."""
    try:
        view = ServiceDeckView()
        controller = AppController(view)
        # Link controller to view
        view.controller = controller
        
        view.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
