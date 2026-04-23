#!/usr/bin/env python
"""
AI Model-Based Test Flow Generator
Main entry point
"""
import os
import sys
from app.app import create_app
from app.modules.config import DevelopmentConfig, ProductionConfig

if __name__ == '__main__':
    # Determine environment
    env = os.getenv('FLASK_ENV', 'development')
    
    # Select config
    if env == 'production':
        config = ProductionConfig
    else:
        config = DevelopmentConfig
    
    # Create app
    app = create_app(config)
    
    # Run app
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode
    )
