# run.py
import streamlit as st
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from app.ui import main

if __name__ == "__main__":
    main()