# Quick Start Guide

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 2. Setup Steps

```bash
# Navigate to project directory
cd aiModelBasedTest

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
copy .env.example .env
# or on Mac/Linux: cp .env.example .env

# (Optional) Add your OpenAI API key to .env
# OPENAI_API_KEY=sk-xxxxx

# Run the application
python run.py
```

### 3. Access Application
Open your browser and go to: **http://localhost:5000**

## Quick Usage

1. Click "📋 Load Template" to see the format
2. Enter your requirement or test cases
3. Click "🔍 Analyze & Generate Flow"
4. View results in 4 sections:
   - Section 1: Your input
   - Section 2: Generated test flows
   - Section 3: Visual flow diagram
   - Section 4: Path analysis

## Export Your Diagram

- **Draw.io**: For editing and beautifying
- **JSON**: For integration with other tools
- **PowerPoint**: For presentations

## For Detailed Information

- See `README.md` for comprehensive user guide
- See `ARCHITECTURE.md` for technical documentation

Enjoy! 🚀
