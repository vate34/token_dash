#!/usr/bin/env python3
"""Entry point for py2app packaging."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_dash.app import main
if __name__ == "__main__":
    main()
