"""
Signal handler fix for Render deployment
Monkey-patches signal module to prevent threading errors
Must be imported FIRST before any other imports
"""
import signal
import sys

# Store original signal function
_original_signal = signal.signal

def _dummy_signal(signalnum, handler):
    """Dummy signal handler that does nothing to prevent threading errors"""
    try:
        return _original_signal(signalnum, handler)
    except (ValueError, OSError) as e:
        # Ignore "signal only works in main thread" errors
        return None

# Replace signal.signal with our dummy version
signal.signal = _dummy_signal

# Also disable these for good measure
try:
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
except:
    pass
