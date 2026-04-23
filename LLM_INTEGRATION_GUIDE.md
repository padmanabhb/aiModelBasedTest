# LLM Integration Migration Guide

## Overview
The application has been upgraded from a **single OpenAI Copilot** integration to a **multi-LLM architecture** supporting both OpenAI and Claude (Anthropic).

## Key Changes

### 1. Module Renaming
**Old**: `copilot_integration.py`  
**New**: `llm_integration.py`

- Renamed `CopilotAnalyzer` class to `LLMAnalyzer`
- The new class maintains all previous functionality plus new multi-provider support
- Backward compatible with existing code patterns

### 2. New Features
- ✅ Support for **Claude (Anthropic) API**
- ✅ **Automatic fallback** between providers
- ✅ **Provider switching** via configuration
- ✅ **Intelligent mock analysis** when no LLM is configured
- ✅ Configurable models for both providers

### 3. Configuration Changes

#### Environment Variables (New)
```env
# Provider Selection (new)
DEFAULT_LLM_PROVIDER=openai  # 'openai' or 'claude'

# Claude API (new)
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# OpenAI (updated)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
```

### 4. Code Changes for Developers

#### Before (Old Code)
```python
from .modules.copilot_integration import CopilotAnalyzer

analyzer = CopilotAnalyzer(api_key="sk-...")
result = analyzer.analyze_requirement(text)
```

#### After (New Code)
```python
from .modules.llm_integration import LLMAnalyzer

# Method 1: Use default provider
analyzer = LLMAnalyzer()

# Method 2: Specify provider and keys
analyzer = LLMAnalyzer(
    provider='openai',          # or 'claude'
    openai_api_key='sk-...',
    claude_api_key='sk-ant-...'
)

result = analyzer.analyze_requirement(text)
```

### 5. Flask App Updates

**In `app.py`:**
```python
# Old
from .modules.copilot_integration import CopilotAnalyzer
app.copilot = CopilotAnalyzer(api_key)

# New
from .modules.llm_integration import LLMAnalyzer
app.llm_analyzer = LLMAnalyzer(
    provider=app.config.get('DEFAULT_LLM_PROVIDER'),
    openai_api_key=app.config.get('OPENAI_API_KEY'),
    claude_api_key=app.config.get('CLAUDE_API_KEY')
)
```

## Migration Steps

### For End Users
1. Update environment variables in `.env`:
   ```bash
   # Copy template
   cp .env.example .env
   
   # Edit with your keys (only one LLM needed)
   # Save changes
   ```

2. Install new dependencies:
   ```bash
   pip install -r requirements.txt
   # installs anthropic==0.25.0 in addition to existing packages
   ```

3. No application changes needed - it works as before!

### For Developers
1. Update imports:
   - Replace `from copilot_integration import CopilotAnalyzer`
   - With `from llm_integration import LLMAnalyzer`

2. Update class instantiation:
   - Update parameter passing to use new config-based approach

3. Test with both providers:
   ```bash
   # Test with OpenAI
   DEFAULT_LLM_PROVIDER=openai python run.py
   
   # Test with Claude
   DEFAULT_LLM_PROVIDER=claude python run.py
   ```

## How Provider Selection Works

### Priority Order
1. **PRIMARY**: Uses `DEFAULT_LLM_PROVIDER` setting
2. **FALLBACK**: If primary unavailable, tries alternative
3. **GRACEFUL**: Uses intelligent mock analysis if neither LLM configured

### Example Scenarios

**Scenario A: Both Configured, OpenAI Primary**
```
Input → Try OpenAI (success) → Return result ✓
```

**Scenario B: OpenAI fails, Claude available**
```
Input → Try OpenAI (fails) → Try Claude (success) → Return result ✓
```

**Scenario C: Only Claude configured, OpenAI Primary**
```
Input → Try OpenAI (unavailable) → Try Claude (success) → Return result ✓
```

**Scenario D: No LLM configured**
```
Input → No provider available → Use mock analysis → Return result ✓
```

## Configuration File Updates

### `.env.example` Changes
- ✅ Added `CLAUDE_API_KEY`
- ✅ Added `CLAUDE_MODEL`
- ✅ Added `OPENAI_MODEL`
- ✅ Added `DEFAULT_LLM_PROVIDER`
- ✅ Added setup instructions

### `requirements.txt` Changes
- ✅ Added `anthropic==0.25.0`
- All other dependencies unchanged

### `app/modules/config.py` Changes
- ✅ Added `CLAUDE_API_KEY`
- ✅ Added `CLAUDE_MODEL`
- ✅ Added `OPENAI_MODEL`
- ✅ Added `DEFAULT_LLM_PROVIDER`
- All other config unchanged

## API Key Requirements

### Minimum Configuration (Choose One)
1. **OpenAI Only**
   ```env
   OPENAI_API_KEY=sk-...
   ```

2. **Claude Only**
   ```env
   CLAUDE_API_KEY=sk-ant-...
   ```

### Recommended Configuration (Both)
```env
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
DEFAULT_LLM_PROVIDER=openai
```

## Getting API Keys

### OpenAI
- Visit: https://platform.openai.com/api-keys
- Create new API key
- Format: `sk-...`

### Claude (Anthropic)
- Visit: https://console.anthropic.com/
- Create new API key
- Format: `sk-ant-...`

## Troubleshooting

### "No LLM providers available"
- Status: Application will use intelligent fallback analysis
- Fix: Configure at least one LLM provider in `.env`

### "OpenAI analysis failed"
- First tries: Claude (if available)
- Then uses: Intelligent fallback analysis
- Fix: Check `OPENAI_API_KEY` is correct

### "Claude analysis failed"
- First tries: OpenAI (if available)
- Then uses: Intelligent fallback analysis
- Fix: Check `CLAUDE_API_KEY` is correct

### Import Error: "cannot import 'CopilotAnalyzer'"
- Cause: Old import path
- Fix: Update to `from .modules.llm_integration import LLMAnalyzer`

## Backward Compatibility

✅ The new `LLMAnalyzer` is **100% backward compatible** with the old `CopilotAnalyzer`:
- Same method signatures: `analyze_requirement()`, `analyze_test_cases()`
- Same return types: Dictionary structures unchanged
- Same internal algorithms: Mock analysis logic preserved

The only difference is under the hood with improved provider handling.

## Version Information

- **Migration Date**: March 2026
- **Old Module**: `copilot_integration.py` (deprecated, not removed)
- **New Module**: `llm_integration.py` (production ready)
- **Supported LLMs**: OpenAI (GPT-4, GPT-4-turbo), Claude (Sonnet, Opus)
- **Python Version**: 3.8+

## Questions & Support

For issues or questions regarding the LLM integration:
1. Check the `.env.example` file for all available options
2. Review the `README.md` LLM Integration section
3. Check application logs for detailed error messages
