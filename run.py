#!/usr/bin/env python3
"""
Wrapper script that starts Streamlit with proper signal handling
Runs Streamlit as a subprocess to avoid threading issues
"""
import os
import sys
import subprocess

# Set all environment variables
os.environ['YOLO_VERBOSE'] = 'False'
os.environ['ULTRALYTICS_HUB_ENABLED'] = 'False'
os.environ['PYTHONUNBUFFERED'] = '1'

# Patch signal module before starting streamlit
import signal
original_signal = signal.signal

def dummy_signal(sig, handler):
    try:
        return original_signal(sig, handler)
    except:
        return None

signal.signal = dummy_signal

# Run streamlit
port = os.environ.get('PORT', '8501')
cmd = [
    sys.executable, '-m', 'streamlit', 'run',
    'streamlit_app.py',
    f'--server.port={port}',
    '--server.address=0.0.0.0',
    '--server.headless=true',
    '--server.enableCORS=false'
]

sys.exit(subprocess.call(cmd))
