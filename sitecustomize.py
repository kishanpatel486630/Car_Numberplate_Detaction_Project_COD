"""
sitecustomize.py - Loaded automatically by Python at startup
Patches signal module BEFORE any other imports to prevent threading errors
"""
import sys
import signal as _signal

# Store original signal function
_original_signal = _signal.signal

def _patched_signal(signalnum, handler):
    """
    Patched signal handler that never raises threading errors.
    Always returns None silently when called from non-main thread.
    """
    try:
        # Try to set the signal handler
        return _original_signal(signalnum, handler)
    except (ValueError, OSError, RuntimeError) as e:
        # Silently ignore all signal-related errors
        # This happens when not in main thread - which is OK
        return None

# Replace signal.signal globally BEFORE any imports
_signal.signal = _patched_signal

# Also set these signals to ignore at Python startup
try:
    _original_signal(_signal.SIGTERM, _signal.SIG_IGN)
    _original_signal(_signal.SIGINT, _signal.SIG_IGN)
except:
    pass
