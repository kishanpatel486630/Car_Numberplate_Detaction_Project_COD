#!/bin/bash
# Wrapper script to launch Streamlit with proper signal handling

# Set environment variables to disable signal-heavy features
export YOLO_VERBOSE=False
export ULTRALYTICS_HUB_ENABLED=False
export PYTHONUNBUFFERED=1
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Trap signals to prevent propagation
trap '' SIGTERM SIGINT

# Launch Streamlit (this runs in foreground)
exec streamlit run streamlit_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --logger.level=error
