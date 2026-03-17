# AI Model-Based Test Flow Generator - User Guide
## How to Use the Application

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Detailed Usage](#detailed-usage)
5. [Features Overview](#features-overview)
6. [Export Options](#export-options)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Getting Started

The **AI Model-Based Test Flow Generator** is a web-based tool that helps you:
- Analyze software requirements and test cases using AI
- Generate optimized test flows automatically
- Create visual flow diagrams (editable in Draw.io or PowerPoint)
- Analyze all possible paths and critical paths in your requirements

### Prerequisites
- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- (Optional) OpenAI API key or Claude API key for AI-powered analysis

---

## LLM Integration

The application now supports **multiple LLM providers** for intelligent requirement analysis:

### Supported LLM Providers
- **OpenAI** (GPT-4, GPT-4-turbo) - Default
- **Claude** (Anthropic) - Alternative provider with automatic fallback

### Configuration

#### Step 1: Set Up Environment Variables
Create or update your `.env` file:

```bash
# OpenAI Configuration (Optional)
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4-turbo

# Claude Configuration (Optional)
CLAUDE_API_KEY=sk-ant-your-claude-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Choose default provider ('openai' or 'claude')
# Application automatically falls back to alternative if primary is unavailable
DEFAULT_LLM_PROVIDER=openai
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
# or specifically for LLM support:
pip install openai>=1.3.0 anthropic>=0.25.0
```

### How It Works
1. **Primary Provider**: Uses the DEFAULT_LLM_PROVIDER setting
2. **Fallback**: Automatically tries alternative provider if primary fails
3. **Graceful Degradation**: Uses intelligent mock analysis if no LLM is configured

### Choose Your Provider
- **OpenAI (Default)**: Better for most use cases, well-established
- **Claude**: Strong alternative, different strengths in analysis

### Minimum Configuration
- Configure **at least ONE** LLM provider for AI analysis
- OR use the application with **intelligent fallback** (no API keys needed, uses pattern analysis)

---

## Installation

### Step 1: Clone/Download the Project
```bash
cd aiModelBasedTest
```

### Step 2: Create Python Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables (Optional)
Create a `.env` file in the root directory. Copy from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# LLM Providers (configure at least one for AI analysis)
OPENAI_API_KEY=your-openai-key
CLAUDE_API_KEY=your-claude-key
DEFAULT_LLM_PROVIDER=openai
```

**Note**: You only need to configure **one LLM provider** minimum. The app will work without any API keys using intelligent fallback analysis.

### Step 5: Run the Application
```bash
python run.py
```

The application will be available at: **http://localhost:5000**

---

## Quick Start

1. **Open the Application**: Navigate to http://localhost:5000
2. **Load Template**: Click "📋 Load Template" button
3. **Enter Data**: Paste or type your requirement or test cases
4. **Analyze**: Click "🔍 Analyze & Generate Flow"
5. **View Results**: See flows, diagram, and path analysis

---

## Detailed Usage

### Section 1: Input & Configuration

#### Selecting Input Type
```
┌─────────────────────────────────────────┐
│ Select Input Type:                      │
│ [Dropdown] ▼                            │
│  • Requirement (selected)               │
│  • Test Cases                           │
└─────────────────────────────────────────┘
```

**Options:**
- **Requirement**: For functional/technical specifications
- **Test Cases**: For existing test case documentation

#### Loading Templates

**For Requirement:**
When you select "Requirement" and click "📋 Load Template", you'll get:

```markdown
## Functional Requirement Specification (FRS)

### 1. Overview
[Provide a brief overview of the requirement]

### 2. Objectives
- [Objective 1]
- [Objective 2]

### 3. Scope
[Define what is included and excluded]

### 4. User Stories
- As a [user type], I want [action], so that [benefit]

### 5. Functional Features
- [Feature 1]: [Description]

### 6. Non-Functional Requirements
- Performance: [Details]
- Security: [Details]

### 7. Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

**Example Requirement:**
```
## User Authentication System

### 1. Overview
Implement a secure user authentication system with login and logout functionality.

### 2. Objectives
- Provide secure login mechanism
- Implement JWT token-based authentication
- Support logout functionality

### 3. User Stories
- As a user, I want to log in with email and password
- As a user, I want to stay logged in across sessions
- As a user, I want to log out safely

### 4. Functional Features
- Email/Password Login: Validate credentials against database
- JWT Token Generation: Create secure tokens for valid users
- Token Validation: Verify tokens for protected endpoints
- Logout: Invalidate tokens on logout

### 5. Acceptance Criteria
- [ ] Users can login with valid credentials
- [ ] System rejects invalid credentials
- [ ] JWT tokens are generated correctly
- [ ] Users can logout successfully
```

#### Entering Your Content
1. Click "Load Template" (optional, for format reference)
2. Type or paste your requirement in the text area
3. Click "🔍 Analyze & Generate Flow"

---

### Section 2: Test Flows & Analysis

#### Test Flows Tab
After analysis, you'll see generated test flows in card format:

```
┌─────────────────────────────────────────┐
│ [TF01] Flow Name                        │
│ Description of what this flow tests     │
│                                         │
│ Steps:                                  │
│  1. First action                        │
│  2. Second action                       │
│  3. Verify result                       │
│                                         │
│ Acceptance Criteria:                    │
│  • All inputs validated                 │
│  • System responds within 2 seconds     │
└─────────────────────────────────────────┘
```

**Each card shows:**
- **Flow ID**: Unique identifier (TF01, TF02, etc.)
- **Flow Name**: Descriptive name
- **Description**: What this flow tests
- **Steps**: Sequential actions to execute
- **Acceptance Criteria**: Conditions the flow must meet

#### Analysis Summary Tab
Shows high-level insights:
- **Summary**: Overview of the analysis
- **Entities Identified**: Key components/objects
- **Optimized Paths**: Recommended execution sequences

---

### Section 3: Modifiable Flow Diagram

#### Understanding the Diagram

The diagram represents your requirement as a flow with:
- **Green Circles**: Start points
- **Blue Rectangles**: Process/Action nodes
- **Yellow Diamonds**: Decision points (if any)
- **Red Circles**: End points
- **Arrows**: Flow direction with labels

#### Diagram Controls

| Control | Action |
|---------|--------|
| 📥 Export to Draw.io | Download editable Draw.io file |
| 📄 Export as JSON | Export diagram structure as JSON |
| 🎯 Export to PowerPoint | Export as PowerPoint-compatible format |
| 🔍+ Zoom In | Increase diagram size |
| 🔍- Zoom Out | Decrease diagram size |
| ⬜ Fit View | Fit entire diagram to screen |

#### Editing in Draw.io

1. **Export to Draw.io**: Click "📥 Export to Draw.io"
2. **Open draw.io**: Go to https://draw.io
3. **Import**: File → Open → Select the `.drawio` file
4. **Edit**: Modify nodes, edges, and styling
5. **Save**: Export back to your format

---

### Section 4: Path Analysis & Statistics

#### Tabs Available

**📍 All Nodes Tab:**
```
┌─────────────────────────┐
│ Node ID    │ Type      │
├─────────────────────────┤
│ START      │ Startpoint│
│ LOGIN_001  │ Process   │
│ VALIDATE   │ Decision  │
│ SUCCESS    │ Endpoint  │
└─────────────────────────┘
```

**🔗 All Edges Tab:**
```
┌─────────────────────────────────┐
│ # │ Source    │ Target        │
├─────────────────────────────────┤
│ 1 │ START     │ LOGIN_001     │
│ 2 │ LOGIN_001 │ VALIDATE      │
│ 3 │ VALIDATE  │ SUCCESS       │
└─────────────────────────────────┘
```

**↕️ In-Out Edges Tab:**
Shows incoming and outgoing connections for a specific node.

**🔀 All Pairs Tab:**
Shows all possible node pairs and number of paths between them.

**⚡ Critical Paths Tab:**
Lists the longest/most important paths through your flow:
```
┌──────────────────────────────────┐
│ # │ Path                         │
├──────────────────────────────────┤
│ 1 │ START → LOGIN → VALIDATE ... │
│ 2 │ START → VERIFY → SUCCESS     │
└──────────────────────────────────┘
```

**📈 Statistics Tab:**
```
┌──────────────────┐
│ Total Nodes: 8   │
│ Total Edges: 10  │
│ Start Points: 1  │
│ End Points: 1    │
└──────────────────┘
```

---

## Features Overview

### 1. Intelligent Analysis
- Uses OpenAI GPT-4 to understand requirements
- Extracts key test flows automatically
- Identifies entities and relationships

### 2. Visual Representation
- Interactive flow diagram
- Syntax highlighting
- Customizable colors and styles

### 3. Comprehensive Path Analysis
- Identifies all possible execution paths
- Detects critical paths
- Shows node degree analysis

### 4. Export Capabilities
- Multiple export formats
- Compatible with industry tools
- Preserves diagram structure

### 5. Mock Mode
- Works without OpenAI API key
- Provides sample data for testing
- Useful for demonstrations

---

## Export Options

### Option 1: Export to Draw.io

**Best for:** Editing diagrams, creating beautiful visuals

```
1. Click "📥 Export to Draw.io"
2. Opens in new browser or downloads .drawio file
3. Edit at https://draw.io
4. Export to PNG, JPG, SVG, or PDF
```

### Option 2: Export as JSON

**Best for:** Integration with other tools, data analysis

```json
{
  "nodes": [
    {"id": "START", "label": "Start", "type": "startpoint", ...},
    {"id": "FLOW_TF01", "label": "Requirement Validation", ...}
  ],
  "edges": [
    {"source": "START", "target": "FLOW_TF01", "label": "Initialize"}
  ]
}
```

### Option 3: Export to PowerPoint

**Best for:** Presentations, stakeholder communication

```
1. Click "🎯 Export to PowerPoint"
2. Copy the JSON data
3. Use python-pptx library to generate PPTX file
4. See code example below
```

**Example Python code to generate PPTX:**
```python
from pptx import Presentation
from pptx.util import Inches, Pt

# Load exported data
# Create presentation
# Add slides with diagram data
# Save as .pptx
```

---

## Troubleshooting

### Issue: "Analysis failed: Content cannot be empty"
**Solution:** Make sure you've entered text in the textarea before clicking analyze.

### Issue: "No API Key Set"
**Solution:** 
- For mock analysis, this is fine - sample data will be provided
- To use AI analysis, set OPENAI_API_KEY in .env file

### Issue: Diagram not displaying
**Solution:**
- Browser may not support Cytoscape.js
- Try using a newer version of Chrome/Firefox
- Check browser console for errors (F12)

### Issue: Export button not working
**Solution:**
- First run analysis to generate diagram data
- Check browser console for JavaScript errors
- Try a different export format

### Issue: "Flask not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Port 5000 already in use
**Solution:**
```bash
# Use different port
export PORT=5001
python run.py
```

---

## FAQ

### Q1: Do I need an OpenAI API key?
**A:** No, the application works with or without it. Without a key, it provides sample analysis.

### Q2: How do I get an OpenAI API key?
**A:** 
1. Visit https://platform.openai.com
2. Sign up for an account
3. Go to API keys section
4. Create new API key
5. Add to .env file

### Q3: Can I use this for real projects?
**A:** Yes! This is production-ready. Add authentication, database, and monitoring for enterprise use.

### Q4: How long does analysis take?
**A:** Usually 5-15 seconds depending on content length. Longer requirements take more time.

### Q5: Can I analyze multiple requirements at once?
**A:** Currently, process one at a time. The application stores the last analysis in session.

### Q6: What's the maximum content length?
**A:** 16MB due to Flask default. Typically you won't exceed this with text content.

### Q7: Can I run this on Windows/Mac/Linux?
**A:** Yes, it's cross-platform. Same setup for all OS.

### Q8: How do I deploy this to production?
**A:** See ARCHITECTURE.md for deployment guide. Use Gunicorn + Nginx.

### Q9: Can I modify the template?
**A:** Yes, edit `modules/config.py` and update `REQUIREMENT_TEMPLATE` string.

### Q10: Is my data saved?
**A:** Currently in browser session only. Add database to persist data.

---

## Tips & Best Practices

### 1. Template Structure
Stick to the template format for best AI analysis results.

### 2. Clear Descriptions
More detailed requirements = better test flows.

### 3. User Stories
Add "As a... I want... So that..." format for clarity.

### 4. Acceptance Criteria
Specific criteria help AI generate better test cases.

### 5. Review Results
Always review generated flows for accuracy.

### 6. Export Before Closing
Exports are not persistent - save before session ends.

### 7. Use Draw.io for Final Diagrams
Perfect for presentations with Draw.io's styling options.

### 8. Iterate
Try analyzing with different phrasings for better results.

---

## Example Workflows

### Workflow 1: From Requirements to PowerPoint Presentation
```
1. Load template
2. Enter requirement details
3. Click Analyze
4. Review flows and diagram
5. Export to Draw.io
6. Beautify diagram with colors/styles
7. Export diagram as PNG/SVG
8. Create PowerPoint with exported images
9. Present to stakeholders
```

### Workflow 2: Test Planning from Test Cases
```
1. Select "Test Cases" type
2. Load test case template
3. Enter existing test cases
4. Analyze
5. View generated flows
6. Export as JSON
7. Import into test management tool
8. Distribute to QA team
```

### Workflow 3: Path Analysis for Coverage Verification
```
1. Analyze requirement
2. Go to Section 4 - Path Analysis
3. Review Critical Paths tab
4. Ensure test coverage for all paths
5. Add missing test cases if needed
6. Re-analyze to verify
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Enter | Analyze (in textarea) |
| Escape | Close dialogs |
| F12 | Open developer console |
| Ctrl+S | Save (if in Draw.io) |

---

## Support & Contact

For issues or feature requests, create an issue in the project repository or contact your administrator.

---

## Version History

**v1.0** (2024-01-01)
- Initial release
- 4-section UI with input, flows, diagram, and path analysis
- AI-powered requirement analysis
- Multiple export formats
- Comprehensive path analysis

---

Thank you for using the AI Model-Based Test Flow Generator!

**Happy Testing! 🚀**
"# aiModelBasedTest" 
