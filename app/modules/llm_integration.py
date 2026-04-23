"""
LLM Integration Module
Handles communication with multiple LLM providers (OpenAI, Claude) for requirement analysis
"""
import os
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

# LLM Provider imports
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class LLMProvider(Enum):
    """Enum for supported LLM providers"""
    OPENAI = "openai"
    CLAUDE = "claude"


@dataclass
class TestFlow:
    """Represents a test flow extracted from requirements"""
    flow_id: str
    name: str
    description: str
    steps: List[str]
    acceptance_criteria: List[str]


class LLMAnalyzer:
    """
    Analyzes requirements and test cases using multiple LLM providers
    Supports OpenAI and Claude APIs
    """
    
    def __init__(self, provider: str = None, openai_api_key: str = None, claude_api_key: str = None,
                 openai_model: str = "gpt-4-turbo", claude_model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize LLM Analyzer with specified provider
        
        Args:
            provider: 'openai', 'claude', or None (uses DEFAULT_LLM_PROVIDER from config)
            openai_api_key: OpenAI API key (uses env var if not provided)
            claude_api_key: Claude API key (uses env var if not provided)
            openai_model: OpenAI model to use
            claude_model: Claude model to use
        """
        # Get API keys from environment if not provided
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.claude_api_key = claude_api_key or os.getenv('CLAUDE_API_KEY')
        
        # Get default provider from env or use openai as fallback
        default_provider = os.getenv('DEFAULT_LLM_PROVIDER', 'openai')
        self.provider = provider or default_provider
        
        # Store model names
        self.openai_model = os.getenv('OPENAI_MODEL', openai_model)
        self.claude_model = os.getenv('CLAUDE_MODEL', claude_model)
        
        # Initialize clients
        self.openai_client = None
        self.claude_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients"""
        # Initialize OpenAI client
        if OpenAI and self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                print("✓ OpenAI integration initialized")
            except Exception as e:
                print(f"✗ Failed to initialize OpenAI: {e}")
        else:
            if not OpenAI:
                print("⚠ OpenAI library not available. Install with: pip install openai")
            elif not self.openai_api_key:
                print("⚠ OpenAI API key not configured. Set OPENAI_API_KEY environment variable")
        
        # Initialize Claude client
        if Anthropic and self.claude_api_key:
            try:
                self.claude_client = Anthropic(api_key=self.claude_api_key)
                print("✓ Claude (Anthropic) integration initialized")
            except Exception as e:
                print(f"✗ Failed to initialize Claude: {e}")
        else:
            if not Anthropic:
                print("⚠ Anthropic library not available. Install with: pip install anthropic")
            elif not self.claude_api_key:
                print("⚠ Claude API key not configured. Set CLAUDE_API_KEY environment variable")
    
    def get_active_provider(self) -> str:
        """Get the active LLM provider"""
        if self.provider.lower() == 'claude':
            if not self.claude_client:
                print("⚠ Claude not available, falling back to OpenAI")
                return 'openai'
            return 'claude'
        else:
            if not self.openai_client:
                print("⚠ OpenAI not available, falling back to Claude")
                if not self.claude_client:
                    print("⚠ No LLM providers available, using fallback analysis")
                    return 'fallback'
                return 'claude'
            return 'openai'
    
    def analyze_requirement(self, requirement_text: str) -> Dict[str, Any]:
        """
        Analyze requirement and extract test flows
        
        Args:
            requirement_text: The requirement specification text
            
        Returns:
            Dictionary containing test flows and analysis
        """
        provider = self.get_active_provider()
        
        if provider == 'claude':
            return self._analyze_requirement_claude(requirement_text)
        elif provider == 'openai':
            return self._analyze_requirement_openai(requirement_text)
        else:
            print("ℹ Using intelligent fallback analysis")
            return self._mock_analysis(requirement_text)
    
    def _analyze_requirement_openai(self, requirement_text: str) -> Dict[str, Any]:
        """Analyze requirement using OpenAI"""
        try:
            print(f"📡 Sending requirement to OpenAI ({self.openai_model}) for analysis...")
            prompt = self._build_analysis_prompt(requirement_text)
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert test analyst specializing in creating optimized test flows and UML diagrams from requirements. Respond in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            analysis = json.loads(response_text)
            print(f"✓ OpenAI analysis completed successfully")
            return analysis
            
        except Exception as e:
            print(f"✗ OpenAI analysis failed: {e}")
            print(f"  Falling back to alternative provider or mock analysis")
            return self.analyze_requirement(requirement_text)  # Try next provider
    
    def _analyze_requirement_claude(self, requirement_text: str) -> Dict[str, Any]:
        """Analyze requirement using Claude"""
        try:
            print(f"📡 Sending requirement to Claude ({self.claude_model}) for analysis...")
            prompt = self._build_analysis_prompt(requirement_text)
            
            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=2048,
                system="You are an expert test analyst specializing in creating optimized test flows and UML diagrams from requirements. Respond in JSON format.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            analysis = json.loads(response_text)
            print(f"✓ Claude analysis completed successfully")
            return analysis
            
        except Exception as e:
            print(f"✗ Claude analysis failed: {e}")
            print(f"  Falling back to alternative provider or mock analysis")
            return self.analyze_requirement(requirement_text)  # Try next provider
    
    def _build_analysis_prompt(self, requirement_text: str) -> str:
        """Build the analysis prompt for LLM"""
        return f"""
Analyze the following requirement and extract USER FLOWS and NAVIGATION PATTERNS:

FOCUS ON:
1. **User Screens/Pages**: Identify all distinct screens or pages users interact with
2. **User Flows**: Map out complete user journeys from entry to completion
3. **Navigation Paths**: How users move between screens (buttons, links, menu options)
4. **Shared Navigation**: Identify screens accessed from multiple flows
5. **User Actions**: What actions trigger navigation
6. **Decision Points**: Where flows diverge based on user choice/conditions
7. **Alternative Paths**: Multiple ways to reach the same destination

Requirement:
{requirement_text}

Return a JSON object with this structure:
{{
    "user_screens": [
        {{
            "screen_id": "SCREEN_ID",
            "screen_name": "Screen Name",
            "description": "Screen description",
            "screen_type": "landing|list|detail|form|confirmation"
        }}
    ],
    "user_flows": [
        {{
            "flow_id": "UF01",
            "name": "Flow Name",
            "description": "Flow description",
            "screens": ["SCREEN_ID1", "SCREEN_ID2"],
            "entry_screen": "SCREEN_ID1",
            "exit_screen": "SCREEN_ID2"
        }}
    ],
    "navigation_paths": [
        {{
            "from_screen": "SCREEN_ID1",
            "to_screen": "SCREEN_ID2",
            "action": "User action",
            "flows": ["UF01"]
        }}
    ],
    "shared_screens": {{"SCREEN_ID": ["UF01", "UF02"]}},
    "decision_points": [
        {{
            "screen_id": "SCREEN_ID",
            "decision": "Decision description",
            "paths": ["Path A", "Path B"]
        }}
    ],
    "test_flows": [
        {{
            "flow_id": "TF01",
            "name": "Test Flow Name",
            "description": "Description",
            "steps": ["Step 1", "Step 2"],
            "acceptance_criteria": ["Criterion 1"]
        }}
    ],
    "entities": ["Entity names from requirement"],
    "relationships": {{"Entity1": ["Entity2"]}},
    "optimized_paths": [["Path array"]],
    "summary": "Analysis summary"
}}
"""
    
    def _mock_analysis(self, requirement_text: str) -> Dict[str, Any]:
        """
        Intelligent fallback analysis that parses requirement text.
        Extracts screens, flows, and navigation patterns from the requirement.
        Supports:
        - Multiple navigation paths (e.g., "Header > Account > Order History")
        - Overlapping flows that converge at common screens
        - Complex customer journeys with multiple entry points
        """
        import re
        
        text_lower = requirement_text.lower()
        
        # Screen keyword mapping for normalization
        screen_keywords = {
            r'\bhome\b|\blanding\b|\bdashboard\b|\bmain\b': ('HOME', 'Home Screen', 'landing'),
            r'\bproduct\b|\bproducts\b|\bcatalog\b|\bbrowse\b|\bshop\b': ('PRODUCTS', 'Product Listing', 'list'),
            r'\bsearch\b|\bfind\b|\bquery\b': ('SEARCH', 'Search', 'list'),
            r'\bdetail\b|\bview\b|\bshow\b': ('DETAIL', 'Product Detail', 'detail'),
            r'\bcart\b|\bbasket\b|\bshopping\b': ('CART', 'Shopping Cart', 'form'),
            r'\bcheckout\b|\bpayment\b|\bpurchase\b|\bpay\b': ('CHECKOUT', 'Checkout', 'form'),
            r'\bconfirm\b|\bconfirmation\b|\bsuccess\b|\bcompleted\b': ('CONFIRMATION', 'Confirmation', 'confirmation'),
            r'\bhistory\b|\bpast\b|\bprevious\b|\border\b': ('HISTORY', 'Order History', 'list'),
            r'\baccount\b|\bprofile\b|\buser\b|\bsettings\b|\bdashboard\b': ('ACCOUNT', 'Account', 'form'),
            r'\blogin\b|\bsignin\b|\bauthent\b': ('LOGIN', 'Login', 'form'),
            r'\bheader\b|\bnavigation\b|\bmenu\b': ('HEADER', 'Header/Navigation', 'landing'),
            r'\bmobile\b|\bapp\b': ('MOBILE', 'Mobile App', 'landing'),
        }
        
        # Step 1: Parse explicit navigation paths (e.g., "Header > Account > Order History")
        navigation_path_pattern = r'([^>\n]+)\s*>\s*([^>\n]+)(?:\s*>\s*([^>\n]+))?(?:\s*>\s*([^>\n]+))?'
        explicit_paths = []
        
        for match in re.finditer(navigation_path_pattern, requirement_text):
            path_parts = [p.strip() for p in match.groups() if p and p.strip()]
            if len(path_parts) >= 2:
                explicit_paths.append(path_parts)
        
        # Step 2: Normalize screen names
        def normalize_screen_name(name: str) -> tuple:
            """Normalize a screen name to screen_id, screen_name, screen_type"""
            name_lower = name.lower()
            
            for pattern, (screen_id, screen_name, screen_type) in screen_keywords.items():
                if re.search(pattern, name_lower):
                    return (screen_id, screen_name, screen_type)
            
            screen_id = name.upper().replace(' ', '_').replace('&', 'AND')[:20]
            return (screen_id, name, 'form')
        
        # Step 3: Build screens from explicit paths
        identified_screens = {}
        user_flows = []
        all_screen_sequences = []
        
        if explicit_paths:
            for flow_idx, path in enumerate(explicit_paths):
                screen_ids = []
                screen_sequence = []
                
                for screen_name in path:
                    screen_id, normalized_name, screen_type = normalize_screen_name(screen_name)
                    
                    if screen_id not in identified_screens:
                        identified_screens[screen_id] = {
                            "screen_id": screen_id,
                            "screen_name": normalized_name,
                            "description": f"Accessed via {screen_name}",
                            "screen_type": screen_type
                        }
                    
                    screen_ids.append(screen_id)
                    screen_sequence.append(screen_id)
                
                all_screen_sequences.append(screen_sequence)
                
                if len(screen_ids) >= 2:
                    user_flows.append({
                        "flow_id": f"UF{flow_idx+1:02d}",
                        "name": f"Flow: {' → '.join(path[:2])}",
                        "description": f"Navigation via {' → '.join(path)}",
                        "screens": screen_ids,
                        "entry_screen": screen_ids[0],
                        "exit_screen": screen_ids[-1]
                    })
        
        # If no explicit paths, use keyword detection
        if not identified_screens:
            for pattern, (screen_id, screen_name, screen_type) in screen_keywords.items():
                if re.search(pattern, text_lower):
                    if screen_id not in identified_screens:
                        identified_screens[screen_id] = {
                            "screen_id": screen_id,
                            "screen_name": screen_name,
                            "description": f"{screen_name} - extracted from requirement",
                            "screen_type": screen_type
                        }
                        all_screen_sequences.append([screen_id])
        
        # Fallback if no screens found
        if not identified_screens:
            identified_screens = {
                "HOME": {"screen_id": "HOME", "screen_name": "Home", "description": "Entry point", "screen_type": "landing"},
                "MAIN": {"screen_id": "MAIN", "screen_name": "Main Screen", "description": "Main processing", "screen_type": "form"},
                "RESULT": {"screen_id": "RESULT", "screen_name": "Result", "description": "Result display", "screen_type": "confirmation"}
            }
            all_screen_sequences = [["HOME", "MAIN", "RESULT"]]
        
        # Fallback flows
        if not user_flows:
            screen_order = list(identified_screens.keys())
            if len(screen_order) >= 2:
                user_flows.append({
                    "flow_id": "UF01",
                    "name": "Primary User Flow",
                    "description": "Main user journey through the system",
                    "screens": screen_order,
                    "entry_screen": screen_order[0],
                    "exit_screen": screen_order[-1]
                })
        
        # Build navigation paths
        navigation_paths = []
        flow_paths_set = set()
        
        for flow in user_flows:
            screens = flow['screens']
            for i in range(len(screens) - 1):
                from_screen = screens[i]
                to_screen = screens[i + 1]
                path_key = (from_screen, to_screen)
                
                if path_key not in flow_paths_set:
                    flows_using = [f["flow_id"] for f in user_flows 
                                   if from_screen in f["screens"] and to_screen in f["screens"]]
                    
                    navigation_paths.append({
                        "from_screen": from_screen,
                        "to_screen": to_screen,
                        "action": f"Navigate to {identified_screens[to_screen]['screen_name']}",
                        "flows": flows_using
                    })
                    flow_paths_set.add(path_key)
        
        # Identify shared screens
        shared_screens = {}
        for screen_id in identified_screens.keys():
            flows_accessing = [f["flow_id"] for f in user_flows if screen_id in f["screens"]]
            if len(flows_accessing) > 1:
                shared_screens[screen_id] = flows_accessing
        
        # Identify decision points
        decision_points = []
        for flow in user_flows:
            screens = flow['screens']
            for i, screen_id in enumerate(screens[:-1]):
                outgoing_screens = set()
                for f in user_flows:
                    if screen_id in f['screens']:
                        idx = f['screens'].index(screen_id)
                        if idx + 1 < len(f['screens']):
                            outgoing_screens.add(f['screens'][idx + 1])
                
                if len(outgoing_screens) > 1:
                    existing = [dp for dp in decision_points if dp["screen_id"] == screen_id]
                    if not existing:
                        decision_points.append({
                            "screen_id": screen_id,
                            "decision": f"Decision: Choose between {len(outgoing_screens)} options",
                            "paths": sorted(list(outgoing_screens))
                        })
        
        # Extract entities
        entities = []
        entity_patterns = {
            'user': 'User',
            'customer': 'Customer',
            'product': 'Product',
            'order': 'Order',
            'payment': 'Payment',
            'account': 'Account',
            'cart': 'Cart',
            'inventory': 'Inventory'
        }
        
        for keyword, entity in entity_patterns.items():
            if keyword in text_lower:
                entities.append(entity)
        
        if not entities:
            entities = ["User", "System"]
        
        # Create test flows
        test_flows = []
        for idx, flow in enumerate(user_flows):
            steps = [f"Step {i+1}: Access {identified_screens[sid]['screen_name']}" 
                     for i, sid in enumerate(flow['screens'])]
            test_flows.append({
                "flow_id": f"TF{idx+1:02d}",
                "name": f"Test {flow['name']}",
                "description": f"Execute {flow['name']}",
                "steps": steps,
                "acceptance_criteria": [
                    "All screens accessible",
                    "Navigation successful",
                    "No errors encountered"
                ]
            })
        
        # Create summary
        summary_parts = [
            f"Identified {len(identified_screens)} screens",
            f"{len(user_flows)} user flows",
            f"{len(navigation_paths)} navigation paths"
        ]
        if shared_screens:
            summary_parts.append(f"{len(shared_screens)} shared/convergent screens")
        
        return {
            "user_screens": list(identified_screens.values()),
            "user_flows": user_flows,
            "navigation_paths": navigation_paths,
            "shared_screens": shared_screens,
            "decision_points": decision_points,
            "test_flows": test_flows,
            "entities": entities,
            "relationships": {entities[0]: entities[1:]} if len(entities) > 1 else {},
            "optimized_paths": all_screen_sequences,
            "summary": f"Analyzed requirement: {', '.join(summary_parts)}. Created {len(user_flows)} overlapping flows that converge at shared screens."
        }
    
    def analyze_test_cases(self, test_cases_text: str) -> Dict[str, Any]:
        """
        Analyze test cases and extract flow information
        
        Args:
            test_cases_text: The test cases specification
            
        Returns:
            Dictionary containing flow analysis
        """
        provider = self.get_active_provider()
        
        if provider == 'claude':
            return self._analyze_test_cases_claude(test_cases_text)
        elif provider == 'openai':
            return self._analyze_test_cases_openai(test_cases_text)
        else:
            print("ℹ Using intelligent fallback analysis")
            return self._mock_test_analysis(test_cases_text)
    
    def _analyze_test_cases_openai(self, test_cases_text: str) -> Dict[str, Any]:
        """Analyze test cases using OpenAI"""
        try:
            print(f"📡 Sending test cases to OpenAI ({self.openai_model}) for analysis...")
            prompt = f"""
Analyze the following test cases and provide:
1. Identified test scenarios and their dependencies
2. Critical paths through the test flow
3. Node and edge analysis
4. Recommended optimization points

Test Cases:
{test_cases_text}

Return JSON with: scenarios, dependencies, critical_paths, nodes, edges, optimization_points
"""
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert QA analyst. Return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis = json.loads(response.choices[0].message.content)
            print(f"✓ OpenAI test analysis completed successfully")
            return analysis
            
        except Exception as e:
            print(f"✗ OpenAI analysis failed: {e}")
            print(f"  Falling back to alternative provider or mock analysis")
            return self.analyze_test_cases(test_cases_text)
    
    def _analyze_test_cases_claude(self, test_cases_text: str) -> Dict[str, Any]:
        """Analyze test cases using Claude"""
        try:
            print(f"📡 Sending test cases to Claude ({self.claude_model}) for analysis...")
            prompt = f"""
Analyze the following test cases and provide:
1. Identified test scenarios and their dependencies
2. Critical paths through the test flow
3. Node and edge analysis
4. Recommended optimization points

Test Cases:
{test_cases_text}

Return JSON with: scenarios, dependencies, critical_paths, nodes, edges, optimization_points
"""
            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=1536,
                system="You are an expert QA analyst. Return valid JSON only.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            analysis = json.loads(message.content[0].text)
            print(f"✓ Claude test analysis completed successfully")
            return analysis
            
        except Exception as e:
            print(f"✗ Claude analysis failed: {e}")
            print(f"  Falling back to alternative provider or mock analysis")
            return self.analyze_test_cases(test_cases_text)
    
    def _mock_test_analysis(self, test_cases_text: str) -> Dict[str, Any]:
        """
        Intelligent fallback test analysis that parses test case text.
        Extracts scenarios, dependencies, and critical paths from the test cases.
        """
        import re
        
        text_lower = test_cases_text.lower()
        
        # Extract test case identifiers and names
        test_case_patterns = [
            r'(?:test case|tc)\s*#?(\d+)[:\s-]+([^\n]+)',
            r'(?:scenario)\s*#?(\d+)[:\s-]+([^\n]+)',
            r'(?:test)\s+([a-z_]+)',
        ]
        
        scenarios = []
        test_cases = []
        
        for pattern in test_case_patterns:
            matches = re.finditer(pattern, test_cases_text)
            for match in matches:
                if len(match.groups()) >= 2:
                    scenario_name = match.group(2).strip()
                elif len(match.groups()) >= 1:
                    scenario_name = match.group(1).strip()
                else:
                    scenario_name = f"Test Scenario {len(test_cases) + 1}"
                
                if scenario_name not in test_cases:
                    test_cases.append(scenario_name)
        
        if not test_cases:
            scenario_keywords = ['happy path', 'error handling', 'edge case', 'boundary', 'validation']
            for keyword in scenario_keywords:
                if keyword in text_lower:
                    test_cases.append(keyword.title())
        
        if not test_cases:
            test_cases = ["Positive Test", "Negative Test", "Edge Case Test"]
        
        for i, tc in enumerate(test_cases[:5]):
            scenarios.append({
                "id": f"SC{i+1:02d}",
                "name": tc,
                "description": f"Automated test for {tc}"
            })
        
        nodes = ["Setup"]
        dependencies = {"Setup": []}
        
        scenario_names = [s["name"] for s in scenarios]
        nodes.extend(scenario_names)
        
        for i, scenario in enumerate(scenario_names):
            if i == 0:
                dependencies[scenario] = ["Setup"]
            else:
                dependencies[scenario] = ["Setup", scenario_names[i-1]]
        
        nodes.extend(["Verification", "Cleanup"])
        dependencies["Verification"] = scenario_names if scenario_names else ["Setup"]
        dependencies["Cleanup"] = ["Verification"]
        
        edges = []
        for i in range(len(nodes) - 1):
            edges.append([nodes[i], nodes[i + 1]])
        
        critical_paths = [nodes]
        
        if len(nodes) > 4:
            quick_path = ["Setup"] + nodes[2::2] + ["Verification", "Cleanup"]
            critical_paths.append(quick_path)
        
        optimization_points = []
        if len(scenario_names) > 3:
            optimization_points.append("Parallelize independent test scenarios")
        optimization_points.extend([
            "Cache setup results between tests",
            "Optimize verification steps",
            "Group related test cases"
        ])
        
        return {
            "scenarios": scenarios,
            "dependencies": dependencies,
            "critical_paths": critical_paths,
            "nodes": nodes,
            "edges": edges,
            "optimization_points": optimization_points,
            "summary": f"Analyzed test cases and identified {len(scenarios)} scenarios: {', '.join(scenario_names)}. Created {len(critical_paths)} critical paths with {len(edges)} flow connections."
        }
