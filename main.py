#!/usr/bin/env python3
"""
FinalRound - Multi-Agent Interview System
Entry point for the CLI application.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.cli import InterviewCLI


def main():
    """Main entry point for the FinalRound interview system."""
    try:
        cli = InterviewCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()