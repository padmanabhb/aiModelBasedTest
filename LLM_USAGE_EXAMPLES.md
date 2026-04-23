# LLM Integration - Practical Usage Examples

## Overview
This document provides practical code examples showing how to use the new multi-LLM integration in different scenarios.

---

## Example 1: Basic Usage (Default Configuration)

### Code
```python
from app.modules.llm_integration import LLMAnalyzer

# Use default provider from config
analyzer = LLMAnalyzer()

# Analyze a requirement
requirement = """
Users can Add items to shopping cart by:
- Scanning product barcode
- Selecting from product list
After adding, confirm purchase to proceed to checkout.
"""

result = analyzer.analyze_requirement(requirement)

# Access results
print(f"Found {len(result['user_screens'])} screens")
print(f"Identified {len(result['user_flows'])} flows")
print(f"Decision points: {len(result['decision_points'])}")
```

### Output
```
Found 5 screens
Identified 2 flows
Decision points: 1
```

---

## Example 2: Explicitly Specify Provider

### Using OpenAI
```python
from app.modules.llm_integration import LLMAnalyzer

# Use OpenAI explicitly
analyzer = LLMAnalyzer(provider='openai')
result = analyzer.analyze_requirement(requirement_text)
```

### Using Claude
```python
from app.modules.llm_integration import LLMAnalyzer

# Use Claude explicitly
analyzer = LLMAnalyzer(provider='claude')
result = analyzer.analyze_requirement(requirement_text)
```

---

## Example 3: Override API Keys and Models

### Custom Configuration
```python
from app.modules.llm_integration import LLMAnalyzer

analyzer = LLMAnalyzer(
    provider='openai',
    openai_api_key='sk-your-custom-key',
    openai_model='gpt-4',  # Use cheaper/faster GPT-4 instead of turbo
    claude_api_key='sk-ant-fallback-key'  # Fallback provider
)

result = analyzer.analyze_requirement(requirement_text)
```

---

## Example 4: Test Cases Analysis

### Code
```python
from app.modules.llm_integration import LLMAnalyzer

analyzer = LLMAnalyzer()

test_cases = """
Test Case 1: Happy Path
- User adds item by scanning barcode
- Confirms purchase
- Receives confirmation

Test Case 2: Alternative Path
- User selects item from list
- Confirms purchase
- Receives confirmation

Test Case 3: Error Handling
- User cancels operation
- Cart is cleared
- Returns to home screen
"""

result = analyzer.analyze_test_cases(test_cases)

print(f"Scenarios: {result['scenarios']}")
print(f"Create {len(result['critical_paths'])} critical paths")
```

---

## Example 5: Error Handling and Fallback

### Graceful Error Handling
```python
from app.modules.llm_integration import LLMAnalyzer

analyzer = LLMAnalyzer(provider='openai')

try:
    result = analyzer.analyze_requirement(requirement_text)
    print(f"✓ Analysis complete: {result['summary']}")
except Exception as e:
    print(f"⚠ Analysis failed: {e}")
    print("  Application automatically attempted fallback providers")
    # Still returns a result from fallback/mock analysis
```

### What Happens
```
Attempt 1: OpenAI API (fails)
    ↓
Attempt 2: Claude API (fails)
    ↓
Attempt 3: Mock Analysis (succeeds - always available)
```

---

## Example 6: Check Active Provider

### Code
```python
from app.modules.llm_integration import LLMAnalyzer

analyzer = LLMAnalyzer()

# Get the active provider being used
active = analyzer.get_active_provider()
print(f"Active LLM Provider: {active}")
# Output: Active LLM Provider: openai

# Check availability of specific providers
if analyzer.openai_client:
    print("✓ OpenAI is available")

if analyzer.claude_client:
    print("✓ Claude is available")
```

---

## Example 7: Requirement Analysis with Decision Points

### Code
```python
from app.modules.llm_integration import LLMAnalyzer

analyzer = LLMAnalyzer()

# Requirement with decision points (branching)
requirement = """
Product Selection Process:
- User navigates to Products catalog
- User can Add product by scanning barcode OR Select from on-screen list
- If barcode: Scan barcode → Product added
- If list: Browse catalog → Click product → Product added
- After product added, show confirmation
"""

result = analyzer.analyze_requirement(requirement)

# Check decision points
print("Decision Points Found:")
for dp in result['decision_points']:
    print(f"  - Screen: {dp['screen_id']}")
    print(f"    Decision: {dp['decision']}")
    print(f"    Options: {dp['paths']}")

# Check navigation paths
print("\nNavigation Paths:")
for path in result['navigation_paths']:
    print(f"  {path['from_screen']} → {path['to_screen']}")
    print(f"    Action: {path['action']}")
```

### Output
```
Decision Points Found:
  - Screen: PRODUCTS
    Decision: Decision: Choose between 2 options
    Options: ['BARCODE_SCAN', 'PRODUCT_LISTING']

Navigation Paths:
  HOME → PRODUCTS
    Action: Navigate to Product Listing
  PRODUCTS → BARCODE_SCAN
    Action: Navigate to Barcode Scan
  PRODUCTS → PRODUCT_LISTING
    Action: Navigate to Product Listing
```

---

## Example 8: Flask Integration (Web Application)

### Code
```python
# In app.py or Flask route handler

from flask import Flask, request, jsonify
from app.modules.llm_integration import LLMAnalyzer

app = Flask(__name__)

# Initialize analyzer with config
app.llm_analyzer = LLMAnalyzer(
    provider=app.config.get('DEFAULT_LLM_PROVIDER'),
    openai_api_key=app.config.get('OPENAI_API_KEY'),
    claude_api_key=app.config.get('CLAUDE_API_KEY'),
    openai_model=app.config.get('OPENAI_MODEL'),
    claude_model=app.config.get('CLAUDE_MODEL')
)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze requirement or test cases"""
    try:
        data = request.get_json()
        input_type = data.get('type', 'requirement')
        content = data.get('content', '')
        
        if input_type == 'requirement':
            result = app.llm_analyzer.analyze_requirement(content)
        else:
            result = app.llm_analyzer.analyze_test_cases(content)
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
```

---

## Example 9: Environment Variable Configuration

### .env File
```bash
# Use OpenAI only
OPENAI_API_KEY=sk-your-key
DEFAULT_LLM_PROVIDER=openai
```

### Configure at Runtime
```python
import os

# Override environment before creating analyzer
os.environ['DEFAULT_LLM_PROVIDER'] = 'claude'
os.environ['CLAUDE_API_KEY'] = 'sk-ant-your-key'

from app.modules.llm_integration import LLMAnalyzer

analyzer = LLMAnalyzer()
# Now uses Claude as primary provider
```

---

## Example 10: Provider Fallback Demonstration

### Code
```python
from app.modules.llm_integration import LLMAnalyzer
import os

print("=== Scenario A: Both Providers Available ===")
analyzer_a = LLMAnalyzer(
    openai_api_key='sk-real-key',
    claude_api_key='sk-ant-real-key',
    provider='openai'
)
print(f"Primary: {analyzer_a.provider}")
print(f"Active: {analyzer_a.get_active_provider()}")  # ✓ openai

print("\n=== Scenario B: Only Claude Available ===")
analyzer_b = LLMAnalyzer(
    openai_api_key=None,  # Not configured
    claude_api_key='sk-ant-real-key',
    provider='openai'  # Primary is openai, but not available
)
print(f"Primary: {analyzer_b.provider}")
print(f"Active: {analyzer_b.get_active_provider()}")  # → claude

print("\n=== Scenario C: No Providers Available ===")
analyzer_c = LLMAnalyzer(
    openai_api_key=None,
    claude_api_key=None,
    provider='openai'
)
print(f"Primary: {analyzer_c.provider}")
print(f"Active: {analyzer_c.get_active_provider()}")  # → fallback
# Still works - uses intelligent pattern analysis
```

---

## Example 11: Compare Results from Different Providers

### Code
```python
from app.modules.llm_integration import LLMAnalyzer

requirement = "User can browse products and add to cart"

# Analyze with OpenAI
print("=== OpenAI Analysis ===")
analyzer_openai = LLMAnalyzer(provider='openai')
result_openai = analyzer_openai.analyze_requirement(requirement)
print(f"Screens: {len(result_openai['user_screens'])}")
print(f"Flows: {len(result_openai['user_flows'])}")

# Analyze with Claude
print("\n=== Claude Analysis ===")
analyzer_claude = LLMAnalyzer(provider='claude')
result_claude = analyzer_claude.analyze_requirement(requirement)
print(f"Screens: {len(result_claude['user_screens'])}")
print(f"Flows: {len(result_claude['user_flows'])}")

# Compare
if result_openai['summary'] == result_claude['summary']:
    print("\n✓ Both providers gave identical results")
else:
    print("\n⚠ Results differ - review for additional insights")
```

---

## Example 12: Batch Processing

### Code
```python
from app.modules.llm_integration import LLMAnalyzer

requirements = [
    "User authentication flow",
    "User can search products",
    "User can checkout and pay"
]

analyzer = LLMAnalyzer()
results = []

for idx, req in enumerate(requirements, 1):
    print(f"Processing requirement {idx}...")
    result = analyzer.analyze_requirement(req)
    results.append({
        "requirement": req,
        "summary": result['summary'],
        "flows": len(result['user_flows']),
        "screens": len(result['user_screens'])
    })
    print(f"  ✓ Complete: {result['summary']}")

# Generate report
print("\n=== Analysis Report ===")
for r in results:
    print(f"• {r['requirement']}: {r['flows']} flows, {r['screens']} screens")
```

---

## Example 13: Advanced: Custom Analysis with Provider Switching

### Code
```python
from app.modules.llm_integration import LLMAnalyzer

class SmartAnalyzer:
    """Wrapper for smart provider selection and retry logic"""
    
    def __init__(self, primary='openai', fallback='claude'):
        self.primary = LLMAnalyzer(provider=primary)
        self.fallback = LLMAnalyzer(provider=fallback)
    
    def analyze_with_retry(self, text, analysis_type='requirement'):
        """Analyze with explicit fallback"""
        try:
            if analysis_type == 'requirement':
                return self.primary.analyze_requirement(text)
            else:
                return self.primary.analyze_test_cases(text)
        except Exception as e:
            print(f"⚠ Primary failed: {e}, trying fallback...")
            try:
                if analysis_type == 'requirement':
                    return self.fallback.analyze_requirement(text)
                else:
                    return self.fallback.analyze_test_cases(text)
            except Exception as e2:
                print(f"⚠ Fallback failed: {e2}, results may be limited")
                raise

# Usage
smart = SmartAnalyzer(primary='openai', fallback='claude')
result = smart.analyze_with_retry("Your requirement text")
```

---

## Example 14: Health Check

### Code
```python
from app.modules.llm_integration import LLMAnalyzer

def check_llm_health():
    """Check availability of LLM providers"""
    analyzer = LLMAnalyzer()
    
    status = {
        "openai": analyzer.openai_client is not None,
        "claude": analyzer.claude_client is not None,
        "active_provider": analyzer.get_active_provider(),
        "fallback_available": True  # Mock analysis is always available
    }
    
    print("LLM Health Check:")
    print(f"  OpenAI: {'✓' if status['openai'] else '✗'}")
    print(f"  Claude: {'✓' if status['claude'] else '✗'}")
    print(f"  Active: {status['active_provider']}")
    print(f"  Fallback: {'✓' if status['fallback_available'] else '✗'}")
    
    return status

check_llm_health()
```

---

## Best Practices

### 1. ✅ Always Use Fallback
```python
# Good - uses intelligent fallback if no LLM available
analyzer = LLMAnalyzer()
result = analyzer.analyze_requirement(text)
```

### 2. ✅ Configure Both Providers for Production
```python
# Good - resilient setup
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
DEFAULT_LLM_PROVIDER=openai
```

### 3. ✅ Log Active Provider
```python
analyzer = LLMAnalyzer()
print(f"Using provider: {analyzer.get_active_provider()}")
```

### 4. ❌ Don't Hardcode API Keys
```python
# Bad - never do this
analyzer = LLMAnalyzer(openai_api_key='sk-xxx')  # ❌

# Good - use environment variables
analyzer = LLMAnalyzer()  # ✅
```

### 5. ✅ Handle Potential Failures
```python
try:
    result = analyzer.analyze_requirement(text)
except Exception as e:
    print(f"Analysis failed: {e}")
    # Use fallback or display error to user
```

---

## Troubleshooting Examples

### Issue: "OpenAI analysis failed"
```python
# Check if OpenAI is properly configured
analyzer = LLMAnalyzer()
if not analyzer.openai_client:
    print("OpenAI not configured, using Claude or fallback")
```

### Issue: "No LLM providers available"
```python
# Application still works with intelligent fallback
analyzer = LLMAnalyzer()
result = analyzer.analyze_requirement(text)
# May be less comprehensive than with LLM, but still functional
```

### Issue: "Claude rate limited"
```python
# Automatically falls back to OpenAI
analyzer = LLMAnalyzer(provider='claude')
result = analyzer.analyze_requirement(text)
# Switches to OpenAI if Claude rate limit reached
```

---

## Summary

The new LLM integration provides:
- ✅ Flexible provider selection
- ✅ Automatic failover
- ✅ Graceful degradation
- ✅ Configuration-based setup
- ✅ Always-working fallback analysis

Choose the approach that best fits your use case!

