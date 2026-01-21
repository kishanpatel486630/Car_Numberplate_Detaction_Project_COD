# Vercel serverless function entry point
import sys
import os

# Set environment variables before importing heavy libraries
os.environ['YOLO_VERBOSE'] = 'False'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
    
    # Vercel expects 'app' or 'handler'
    handler = app
    
except Exception as e:
    # Fallback error handler for debugging
    from flask import Flask, jsonify
    
    fallback_app = Flask(__name__)
    
    @fallback_app.route('/')
    @fallback_app.route('/<path:path>')
    def error_handler(path=''):
        return jsonify({
            'error': 'Application failed to initialize',
            'message': str(e),
            'type': type(e).__name__
        }), 500
    
    handler = fallback_app
