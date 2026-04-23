# Architecture Documentation
## AI Model-Based Test Flow Generator

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture Design](#architecture-design)
3. [Module Structure](#module-structure)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Patterns](#design-patterns)
7. [Scalability Considerations](#scalability-considerations)

---

## Overview

The **AI Model-Based Test Flow Generator** is a sophisticated web application that uses AI (OpenAI GPT-4) to analyze software requirements and test cases, generating optimized test flows, UML diagrams, and comprehensive path analysis.

### Key Features:
- **Intelligent Requirement Analysis**: Uses OpenAI API to interpret requirements and extract test flows
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Flow Diagram Generation**: Creates visual, editable flow diagrams
- **Path Analysis**: Comprehensive graph analysis including nodes, edges, paths, and critical paths
- **Multiple Export Formats**: Support for Draw.io (mxGraph), JSON, and PowerPoint

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/CSS/JS)                   │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │   Section 1  │   Section 2  │   Section 3  │ Section 4  │ │
│  │   (Input)    │   (Flows)    │  (Diagram)   │  (Paths)   │ │
│  └──────────────┴──────────────┴──────────────┴────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    FLASK WEB SERVER                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                  Route Handlers                          ││
│  │  • /api/template  • /api/analyze  • /api/export/*       ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  ┌──────────────────────────────────────────────────────────┐
│  │                                                           │
│  │  ┌─────────────────────────────────────────────────────┐ │
│  │  │           LLMAnalyzer Module                       │ │
│  │  │  • Requirement analysis                             │ │
│  │  │  • Test case extraction                             │ │
│  │  │  • Flow generation (via OpenAI GPT-4)              │ │
│  │  └─────────────────────────────────────────────────────┘ │
│  │                                                           │
│  │  ┌─────────────────────────────────────────────────────┐ │
│  │  │        FlowDiagramGenerator Module                  │ │
│  │  │  • Graph structure creation                         │ │
│  │  │  • Node/Edge management                            │ │
│  │  │  • Export to multiple formats (mxGraph, JSON)       │ │
│  │  │  • Position calculation & layout                    │ │
│  │  └─────────────────────────────────────────────────────┘ │
│  │                                                           │
│  │  ┌─────────────────────────────────────────────────────┐ │
│  │  │           PathAnalyzer Module                       │ │
│  │  │  • Graph traversal algorithms                       │ │
│  │  │  • Path finding (DFS)                               │ │
│  │  │  • Critical path identification                     │ │
│  │  │  • Node/Edge degree analysis                        │ │
│  │  └─────────────────────────────────────────────────────┘ │
│  │                                                           │
│  └──────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│  • OpenAI API (GPT-4) for intelligent analysis               │
│  • Cytoscape.js (Frontend visualization)                    │
│  • draw.io/mxGraph (Diagram export)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### Directory Layout

```
aiModelBasedTest/
├── app/
│   ├── __init__.py                 # Package initialization
│   ├── app.py                      # Main Flask application
│   ├── modules/                    # Business logic modules
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management
│   │   ├── llm_integration.py      # Multi-LLM AI analysis engine
│   │   ├── flow_diagram.py         # Diagram generation
│   │   ├── test_case_generator.py  # Test case generation
│   │   ├── path_analyzer.py        # Path analysis engine
│   │   └── __pycache__/
│   ├── templates/                  # HTML templates
│   │   └── index.html              # Main UI
│   └── static/                     # Static assets
│       ├── css/
│       │   └── style.css           # Styling
│       ├── js/
│       │   └── main.js             # Frontend logic
│       └── exports/                # Export directory
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── ARCHITECTURE.md                 # This file
├── README.md                       # Usage guide
├── LLM_INTEGRATION_GUIDE.md        # LLM setup and migration guide
├── LLM_USAGE_EXAMPLES.md           # Practical usage examples
└── REFACTORING_SUMMARY.md          # Technical refactoring overview
```

### Module Descriptions

#### 1. **config.py** - Configuration Management
- Centralized configuration management
- Environment-specific settings (Development, Production, Testing)
- Template management for requirements
- Multi-LLM API credentials handling (OpenAI, Claude)
- Provider selection configuration

**Key Classes:**
- `Config`: Base configuration
- `DevelopmentConfig`: Development settings
- `ProductionConfig`: Production settings
- `TestingConfig`: Testing settings

#### 2. **llm_integration.py** - Multi-LLM AI Analysis Engine
- Supports multiple LLM providers: OpenAI (GPT-4, GPT-4-turbo) and Claude (Anthropic)
- Automatic provider failover mechanism
- Analyzes requirements and test cases
- Extracts test flows with steps and acceptance criteria
- Provides entity and relationship identification
- Intelligent fallback analysis for testing without LLM APIs

**Key Classes:**
- `LLMAnalyzer`: Main analyzer with multi-provider support
- `LLMProvider`: Enum for supported providers
- `TestFlow`: Data class for test flow representation

**Methods:**
- `analyze_requirement()`: Analyzes requirement text using configured provider
- `analyze_test_cases()`: Analyzes test case text
- `get_active_provider()`: Returns currently active LLM provider
- `_analyze_requirement_openai()`: OpenAI-specific analysis
- `_analyze_requirement_claude()`: Claude-specific analysis
- `_mock_analysis()`: Intelligent fallback analysis

#### 3. **flow_diagram.py** - Diagram Generation
- Creates graph structures from test flows
- Manages nodes and edges
- Calculates optimal node positions
- Exports to multiple formats (mxGraph XML, JSON, PowerPoint-compatible)

**Key Classes:**
- `Node`: Represents a diagram node
- `Edge`: Represents a connection between nodes
- `FlowDiagramGenerator`: Main generator

**Methods:**
- `create_diagram_from_flows()`: Generates diagram from test flows
- `create_diagram_from_entities()`: Generates diagram from entities
- `export_to_mxgraph()`: Export as Draw.io compatible XML
- `export_to_json()`: Export as JSON
- `generate_pptx_compatible_data()`: Generate PowerPoint data

#### 4. **path_analyzer.py** - Path Analysis Engine
- Analyzes the requirement model graph
- Finds all possible paths between nodes
- Identifies critical paths
- Computes node degree analysis
- Generates comprehensive reports

**Key Classes:**
- `PathAnalyzer`: Main analyzer

**Methods:**
- `get_all_nodes()`: Returns all nodes
- `get_all_edges()`: Returns all edges
- `get_all_paths_between()`: Finds all paths from source to target
- `get_critical_paths()`: Identifies critical (longest) paths
- `get_path_analysis_report()`: Generates comprehensive analysis

---

## Data Flow

### 1. Input Phase
```
User Input (Text Area)
    ↓
Frontend Validation
    ↓
Send to Backend (/api/analyze)
```

### 2. Analysis Phase
```
LLM Analyzer (OpenAI/Claude with Fallback)
    ↓
    ├─→ Parse Requirement/Test Cases
    ├─→ Call LLM API (OpenAI or Claude)
    ├─→ Extract Test Flows
    ├─→ Identify Entities & Relationships
    └─→ Return Analysis JSON
```

### 3. Diagram Generation Phase
```
Flow Diagram Generator
    ↓
    ├─→ Create Nodes from Test Flows
    ├─→ Create Edges from Relationships
    ├─→ Calculate Node Positions
    └─→ Return Diagram Data (JSON)
```

### 4. Path Analysis Phase
```
Path Analyzer
    ↓
    ├─→ Build Adjacency List
    ├─→ Find All Paths (DFS)
    ├─→ Calculate Degree Analysis
    ├─→ Identify Critical Paths
    └─→ Generate Report
```

### 5. Output Phase
```
Aggregate Results
    ↓
    ├─→ Return to Frontend
    ├─→ Display in UI
    └─→ Enable Exports
```

---

## Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Language**: Python 3.8+
- **AI Integration**: OpenAI GPT-4
- **Configuration**: python-dotenv

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Flexbox/Grid
- **JavaScript (ES6+)**: Dynamic interactions
- **Cytoscape.js**: Graph visualization
- **mxGraph**: Diagram format support

### Visualization
- **Cytoscape.js**: Interactive graph rendering
- **Draw.io/mxGraph XML**: Import/export format
- **Custom Layouts**: DAG layout using Cytoscape Dagre

---

## Design Patterns

### 1. **Model-View-Controller (MVC)**
- **Model**: Business logic modules (LLMAnalyzer, PathAnalyzer, FlowDiagramGenerator, TestCaseGenerator)
- **View**: HTML templates and CSS
- **Controller**: Flask routes in app.py

### 2. **Factory Pattern**
- `create_app()` function creates configured Flask application
- Configuration classes for different environments

### 3. **Singleton Pattern**
- LLM analyzer and diagram generator initialized once per app

### 4. **Data Transfer Object (DTO)**
- `Node` and `Edge` dataclasses for data encapsulation

### 5. **Repository Pattern**
- Separate data access layer (PathAnalyzer graph operations)

### 6. **Strategy Pattern**
- Multiple export strategies (mxGraph, JSON, PPTX)

---

## Scalability Considerations

### 1. **Horizontal Scaling**
- Stateless Flask application
- Session data stored in Flask session (can be moved to Redis/Cache)
- Can be deployed behind load balancer

### 2. **Performance Optimization**
- **Caching**: Implement Redis caching for frequently analyzed patterns
- **Async Processing**: Use Celery for long-running AI analysis
- **Database**: Add persistent storage for historical analyses

### 3. **API Rate Limiting**
- Implement rate limiting for OpenAI API calls
- Queue system for managing concurrent analyses

### 4. **Frontend Optimization**
- Lazy loading for large diagrams
- Virtual scrolling for large path lists
- Service Workers for offline capability

### 5. **Database Schema** (Future)
```sql
-- Analyses Table
CREATE TABLE analyses (
    id UUID PRIMARY KEY,
    user_id UUID,
    type ENUM('requirement', 'test_case'),
    content TEXT,
    test_flows JSON,
    diagram_data JSON,
    path_analysis JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- User Exports Table
CREATE TABLE exports (
    id UUID PRIMARY KEY,
    analysis_id UUID,
    format ENUM('mxgraph', 'json', 'pptx'),
    file_path VARCHAR(255),
    created_at TIMESTAMP
);
```

---

## Security Considerations

### 1. **API Key Management**
- OpenAI API key stored in environment variables
- Never commit credentials to version control

### 2. **Input Validation**
- Validate user input on both frontend and backend
- Sanitize content before processing

### 3. **CORS Security**
- Configure CORS headers appropriately
- Validate session tokens

### 4. **Data Privacy**
- Consider data encryption for stored analyses
- Implement user authentication/authorization

---

## Error Handling

The application implements comprehensive error handling:

1. **API Errors**: Graceful fallback to mock data
2. **Validation Errors**: User-friendly error messages
3. **Parse Errors**: JSON validation and error reporting
4. **Network Errors**: Retry mechanisms and timeouts

---

## Testing Strategy

### Unit Tests
- Test individual module functions
- Mock external API calls

### Integration Tests
- Test Flask routes
- Test module interactions

### E2E Tests
- Test complete user workflows
- Test all export formats

---

## Future Enhancements

1. **Multi-user Support**: Add authentication and user management
2. **Collaboration**: Real-time collaboration on diagrams
3. **Advanced Analytics**: ML-based optimization suggestions
4. **Custom Models**: Allow users to define custom analysis rules
5. **API Documentation**: Swagger/OpenAPI integration
6. **Performance Monitoring**: Add APM and analytics
7. **Plugin System**: Extensible architecture for custom modules

---

## Deployment Guide

### Development
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

### Production
```bash
export FLASK_ENV=production
export OPENAI_API_KEY=<your-api-key>
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

---

## Support & Maintenance

For issues, enhancements, or questions, please refer to the usage guide in `README.md`.

Last Updated: 2024-01-01
Version: 1.0
