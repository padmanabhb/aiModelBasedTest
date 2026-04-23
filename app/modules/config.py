"""
Configuration Module
Manages all application-level configurations and constants
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', False)
    
    # LLM API settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    
    # Default LLM provider: 'openai' or 'claude'
    DEFAULT_LLM_PROVIDER = os.getenv('DEFAULT_LLM_PROVIDER', 'openai')
    
    # LLM model configurations
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    
    # Application settings
    TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
    STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')
    EXPORT_DIR = os.path.join(STATIC_DIR, 'exports')
    
    # Templates
    REQUIREMENT_TEMPLATE = """
## Functional Requirement Specification (FRS)

### **1. Overview**
[Provide a brief overview of the requirement]

### **2. Objectives**
- [Objective 1]
- [Objective 2]
- [Objective 3]

### **3. Scope**
[Define what is included and excluded]

### **4. User Stories**
- As a [user type], I want [action], so that [benefit]
- As a [user type], I want [action], so that [benefit]

### **5. Functional Features**
- [Feature 1]: [Description]
- [Feature 2]: [Description]

### **6. Non-Functional Requirements**
- Performance: [Details]
- Security: [Details]
- Scalability: [Details]

### **7. Acceptance Criteria**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
"""

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
