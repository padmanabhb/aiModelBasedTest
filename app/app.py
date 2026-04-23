"""
Main Flask Application
Entry point for the AI Model-Based Test Flow Generator
"""
import os
import json
from flask import Flask, render_template, request, jsonify, session, send_file
from datetime import datetime
from .modules.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from .modules.llm_integration import LLMAnalyzer
from .modules.flow_diagram import FlowDiagramGenerator
from .modules.path_analyzer import PathAnalyzer
from .modules.test_case_generator import TestCaseGenerator

def create_app(config_class=DevelopmentConfig):
    """
    Application factory function
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    # Get the absolute path to the app package
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(app_dir, 'templates'),
                static_folder=os.path.join(app_dir, 'static'),
                static_url_path='/static')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Ensure export directory exists
    os.makedirs(app.config['EXPORT_DIR'], exist_ok=True)
    
    # Initialize extensions
    app.llm_analyzer = LLMAnalyzer(
        provider=app.config.get('DEFAULT_LLM_PROVIDER', 'openai'),
        openai_api_key=app.config.get('OPENAI_API_KEY'),
        claude_api_key=app.config.get('CLAUDE_API_KEY'),
        openai_model=app.config.get('OPENAI_MODEL'),
        claude_model=app.config.get('CLAUDE_MODEL')
    )
    app.diagram_generator = FlowDiagramGenerator()
    
    # Register routes
    register_routes(app)
    
    return app

def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Main application page"""
        return render_template('index.html')
    
    @app.route('/api/template', methods=['GET'])
    def get_template():
        """Get requirement template"""
        template_type = request.args.get('type', 'requirement')
        
        if template_type == 'requirement':
            template = app.config['REQUIREMENT_TEMPLATE']
        else:
            template = """
## Test Cases Specification

### **Test Case 1: Basic Functionality**
- **Objective**: Verify basic functionality works as expected
- **Preconditions**: System is initialized
- **Steps**:
  1. Step 1
  2. Step 2
  3. Step 3
- **Expected Result**: Expected outcome
- **Actual Result**: [To be filled during execution]
- **Status**: [Pass/Fail]

### **Test Case 2: Error Handling**
- **Objective**: Verify error handling
- **Preconditions**: System is initialized
- **Steps**:
  1. Trigger error condition
  2. Verify error handling
- **Expected Result**: Error is handled gracefully
- **Status**: [Pass/Fail]
"""
        
        return jsonify({
            "success": True,
            "template": template,
            "type": template_type
        })
    
    @app.route('/api/analyze', methods=['POST'])
    def analyze_input():
        """
        Analyze requirement or test cases
        
        Request JSON:
        {
            "type": "requirement" or "test_case",
            "content": "The actual content"
        }
        """
        try:
            data = request.get_json()
            input_type = data.get('type', 'requirement')
            content = data.get('content', '')
            
            if not content:
                return jsonify({
                    "success": False,
                    "error": "Content cannot be empty"
                }), 400
            
            # Analyze based on type
            if input_type == 'requirement':
                analysis = app.llm_analyzer.analyze_requirement(content)
            else:
                analysis = app.llm_analyzer.analyze_test_cases(content)
            
            # Extract user flows and screens for diagram generation
            test_flows = analysis.get('test_flows', [])
            
            # Prepare enriched flow data with navigation info
            enriched_flows = test_flows.copy()
            if analysis.get('user_screens'):
                enriched_flows.insert(0, {
                    '__user_screens__': analysis.get('user_screens', []),
                    '__navigation_paths__': analysis.get('navigation_paths', []),
                    '__shared_screens__': analysis.get('shared_screens', {}),
                    '__user_flows__': analysis.get('user_flows', [])
                })
            
            # Generate flow diagram from analysis
            diagram_data = app.diagram_generator.create_diagram_from_flows(enriched_flows)
            
            # Analyze paths
            nodes_dict = {n['id']: n for n in diagram_data.get('nodes', [])}
            edges_list = diagram_data.get('edges', [])
            path_analyzer = PathAnalyzer(nodes_dict, edges_list)
            path_analysis = path_analyzer.get_path_analysis_report()
            
            # Store in session for later use
            session['last_analysis'] = {
                'type': input_type,
                'timestamp': datetime.now().isoformat(),
                'content': content[:200],  # Store first 200 chars
                'analysis': analysis,
                'diagram': diagram_data,
                'path_analysis': path_analysis
            }
            session.modified = True
            
            return jsonify({
                "success": True,
                "analysis": analysis,
                "diagram": diagram_data,
                "path_analysis": path_analysis
            })
        
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/export/mxgraph', methods=['POST'])
    def export_mxgraph():
        """Export diagram as mxGraph XML"""
        try:
            data = request.get_json()
            nodes = data.get('nodes', {})
            edges = data.get('edges', [])
            
            if not nodes or not edges:
                # Use session data if available
                if 'last_analysis' not in session:
                    return jsonify({
                        "success": False,
                        "error": "No diagram data available"
                    }), 400
                
                last_data = session['last_analysis']
                diagram = last_data.get('diagram', {})
                nodes = {n['id']: n for n in diagram.get('nodes', [])}
                edges = diagram.get('edges', [])
            
            # Create temporary generator with this data
            generator = FlowDiagramGenerator()
            xml_content = generator.export_to_mxgraph("diagram.drawio")
            
            return jsonify({
                "success": True,
                "format": "mxgraph",
                "content": xml_content,
                "filename": "requirement_flow.drawio"
            })
        
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/export/json', methods=['POST'])
    def export_json():
        """Export diagram as JSON"""
        try:
            if 'last_analysis' not in session:
                return jsonify({
                    "success": False,
                    "error": "No diagram data available"
                }), 400
            
            last_data = session['last_analysis']
            diagram = last_data.get('diagram', {})
            
            return jsonify({
                "success": True,
                "format": "json",
                "content": diagram,
                "filename": "requirement_flow.json"
            })
        
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/export/pptx', methods=['POST'])
    def export_pptx():
        """Generate and return a real PowerPoint file"""
        try:
            if 'last_analysis' not in session:
                return jsonify({
                    "success": False,
                    "error": "No diagram data available"
                }), 400
            
            last_data = session['last_analysis']
            diagram = last_data.get('diagram', {})
            
            # Create generator with diagram data
            generator = FlowDiagramGenerator()
            
            # Properly reconstruct Node objects from diagram data
            from .modules.flow_diagram import Node, Edge
            from io import BytesIO
            
            generator.nodes = {}
            for n in diagram.get('nodes', []):
                position = n.get('position', {})
                node = Node(
                    id=n.get('id'),
                    label=n.get('label'),
                    node_type=n.get('type', 'process'),  # Map 'type' to 'node_type'
                    x=position.get('x', 0),
                    y=position.get('y', 0)
                )
                generator.nodes[n.get('id')] = node
            
            # Reconstruct Edge objects from diagram data
            generator.edges = []
            for e in diagram.get('edges', []):
                edge = Edge(
                    source=e.get('source'),
                    target=e.get('target'),
                    label=e.get('label', ''),
                    condition=e.get('condition', '')
                )
                generator.edges.append(edge)
            
            # Generate actual PPTX file
            pptx_bytes = generator.create_pptx_file()
            
            # Return as file download
            output = BytesIO(pptx_bytes)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                as_attachment=True,
                download_name='requirement_flow.pptx'
            )
        
        except Exception as e:
            print(f"Error generating PPTX: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/history', methods=['GET'])
    def get_history():
        """Get analysis history from session"""
        if 'last_analysis' in session:
            return jsonify({
                "success": True,
                "data": session['last_analysis']
            })
        
        return jsonify({
            "success": False,
            "data": None
        })
    
    @app.route('/api/testcases/generate', methods=['POST'])
    def generate_test_cases():
        """Generate test cases based on coverage type"""
        try:
            if 'last_analysis' not in session:
                return jsonify({
                    "success": False,
                    "error": "No diagram data available"
                }), 400
            
            data = request.get_json()
            coverage_type = data.get('coverage_type', 'nodes')  # nodes, edges, pairs, in-out
            
            last_data = session['last_analysis']
            diagram = last_data.get('diagram', {})
            
            # Reconstruct nodes and edges
            nodes_dict = {}
            for n in diagram.get('nodes', []):
                nodes_dict[n.get('id')] = n
            
            edges_list = diagram.get('edges', [])
            
            # Generate test cases
            generator = TestCaseGenerator(nodes_dict, edges_list)
            
            if coverage_type == 'nodes':
                test_cases = generator.generate_node_coverage_tests()
            elif coverage_type == 'edges':
                test_cases = generator.generate_edge_coverage_tests()
            elif coverage_type == 'pairs':
                test_cases = generator.generate_pair_coverage_tests()
            elif coverage_type == 'in-out':
                test_cases = generator.generate_in_out_coverage_tests()
            else:
                test_cases = generator.generate_node_coverage_tests()
            
            # Convert to serializable format
            test_cases_data = [
                {
                    "test_number": tc.test_number,
                    "description": tc.description,
                    "expected_result": tc.expected_result,
                    "coverage_type": tc.coverage_type,
                    "nodes_covered": tc.nodes_covered,
                    "edges_covered": [(str(e[0]), str(e[1])) for e in tc.edges_covered]
                }
                for tc in test_cases
            ]
            
            # Store in session for later export
            session['test_cases'] = test_cases_data
            session['test_cases_type'] = coverage_type
            session.modified = True
            
            return jsonify({
                "success": True,
                "test_cases": test_cases_data,
                "coverage_type": coverage_type,
                "count": len(test_cases_data)
            })
        
        except Exception as e:
            print(f"Error generating test cases: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/testcases/export/csv', methods=['GET'])
    def export_testcases_csv():
        """Export test cases as CSV"""
        try:
            if 'test_cases' not in session:
                return jsonify({
                    "success": False,
                    "error": "No test cases available"
                }), 400
            
            test_cases_data = session['test_cases']
            coverage_type = session.get('test_cases_type', 'general')
            
            # Reconstruct test case objects
            test_cases = []
            for tc_data in test_cases_data:
                from .modules.test_case_generator import TestCase
                tc = TestCase(
                    test_number=tc_data['test_number'],
                    description=tc_data['description'],
                    expected_result=tc_data['expected_result'],
                    coverage_type=tc_data['coverage_type'],
                    nodes_covered=tc_data['nodes_covered'],
                    edges_covered=[(e[0], e[1]) for e in tc_data['edges_covered']]
                )
                test_cases.append(tc)
            
            # Generate CSV
            generator = TestCaseGenerator({}, [])
            csv_content = generator.export_to_csv(test_cases)
            
            # Return as file download
            from flask import make_response
            response = make_response(csv_content)
            response.headers["Content-Disposition"] = f"attachment; filename=test_cases_{coverage_type}.csv"
            response.headers["Content-Type"] = "text/csv"
            return response
        
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/testcases/export/excel', methods=['GET'])
    def export_testcases_excel():
        """Export test cases as Excel"""
        try:
            if 'test_cases' not in session:
                return jsonify({
                    "success": False,
                    "error": "No test cases available"
                }), 400
            
            test_cases_data = session['test_cases']
            coverage_type = session.get('test_cases_type', 'general')
            
            # Reconstruct test case objects
            test_cases = []
            for tc_data in test_cases_data:
                from .modules.test_case_generator import TestCase
                tc = TestCase(
                    test_number=tc_data['test_number'],
                    description=tc_data['description'],
                    expected_result=tc_data['expected_result'],
                    coverage_type=tc_data['coverage_type'],
                    nodes_covered=tc_data['nodes_covered'],
                    edges_covered=[(e[0], e[1]) for e in tc_data['edges_covered']]
                )
                test_cases.append(tc)
            
            # Generate Excel
            generator = TestCaseGenerator({}, [])
            excel_bytes = generator.export_to_excel(test_cases)
            
            # Return as file download
            from io import BytesIO
            output = BytesIO(excel_bytes)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'test_cases_{coverage_type}.xlsx'
            )
        
        except Exception as e:
            print(f"Error exporting Excel: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        })

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
