#!/usr/bin/env python3
"""
AutoCLI launcher script
Quick start: python run.py
"""
import os
os.environ.pop("OLLAMA_NO_GPU", None)

if __name__ == "__main__":
    from core.cli import main
    main()
