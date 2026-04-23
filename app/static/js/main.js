// Main JavaScript - Frontend Logic

let currentAnalysis = null;
let cy = null;

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application loaded');
    // Initialize any required components
});

/**
 * Handle input type change
 */
function handleTypeChange() {
    const type = document.getElementById('inputType').value;
    const textarea = document.getElementById('contentInput');
    
    if (type === 'requirement') {
        textarea.placeholder = 'Enter requirement here... Click "Load Template" for format';
    } else {
        textarea.placeholder = 'Enter test cases here... Click "Load Template" for format';
    }
}

/**
 * Load template for the selected type
 */
function loadTemplate() {
    const type = document.getElementById('inputType').value;
    
    fetch(`/api/template?type=${type}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('contentInput').value = data.template;
                showToast(`${type} template loaded successfully`, 'info');
            }
        })
        .catch(error => {
            console.error('Error loading template:', error);
            showToast('Failed to load template', 'error');
        });
}

/**
 * Analyze the input content
 */
function analyzeInput() {
    const inputType = document.getElementById('inputType').value;
    const content = document.getElementById('contentInput').value;

    if (!content.trim()) {
        showToast('Please enter content before analyzing', 'warning');
        return;
    }

    // Show loading indicator
    document.getElementById('loadingIndicator').classList.remove('hidden');

    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type: inputType,
            content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loadingIndicator').classList.add('hidden');
        
        if (data.success) {
            currentAnalysis = data;
            displayFlows(data.analysis.test_flows);
            displayAnalysisSummary(data.analysis);
            displayDiagram(data.diagram);
            displayPathAnalysis(data.path_analysis);
            showToast('Analysis completed successfully', 'success');
            
            // Scroll to results
            setTimeout(() => {
                document.getElementById('section-flows').scrollIntoView({ behavior: 'smooth' });
            }, 300);
        } else {
            showToast('Analysis failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        document.getElementById('loadingIndicator').classList.add('hidden');
        console.error('Error:', error);
        showToast('Error during analysis: ' + error.message, 'error');
    });
}

/**
 * Display test flows
 */
function displayFlows(flows) {
    const flowsList = document.getElementById('flowsList');
    
    if (!flows || flows.length === 0) {
        flowsList.innerHTML = '<p class="placeholder">No flows generated</p>';
        return;
    }

    let html = '';
    flows.forEach((flow, index) => {
        const stepsHtml = (flow.steps || []).map(step => `<li>${step}</li>`).join('');
        html += `
            <div class="flow-card">
                <div class="flow-id">${flow.flow_id || 'FLOW-' + (index + 1)}</div>
                <h3>${flow.name || 'Flow ' + (index + 1)}</h3>
                <p class="flow-description">${flow.description || 'Test flow'}</p>
                <div style="margin: 10px 0;">
                    <strong>Steps:</strong>
                    <ul class="flow-steps">${stepsHtml}</ul>
                </div>
                ${flow.acceptance_criteria ? `
                <div style="margin: 10px 0;">
                    <strong>Acceptance Criteria:</strong>
                    <ul style="margin-left: 20px; font-size: 0.85rem;">
                        ${(flow.acceptance_criteria || []).map(c => `<li>${c}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        `;
    });

    flowsList.innerHTML = html;
}

/**
 * Display analysis summary
 */
function displayAnalysisSummary(analysis) {
    const summary = document.getElementById('analysisSummary');
    
    let html = `
        <h4>Analysis Summary</h4>
        <p>${analysis.summary || 'Analysis completed'}</p>
        
        <h4>User Flows Identified</h4>
    `;
    
    // Display user flows if available
    if (analysis.user_flows && analysis.user_flows.length > 0) {
        html += '<div style="margin-left: 20px;">';
        analysis.user_flows.forEach(flow => {
            html += `
                <div style="margin-bottom: 15px; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                    <strong>${flow.flow_id}: ${flow.name}</strong>
                    <p style="margin: 5px 0; font-size: 0.9rem; color: #666;">${flow.description}</p>
                    <div style="font-size: 0.85rem;">
                        <strong>Screens:</strong> ${flow.screens.join(' → ')}
                    </div>
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += '<ul style="margin-left: 20px;"></ul>';
    }
    
    html += '<h4>Entities Identified</h4>';
    html += '<ul style="margin-left: 20px;">';
    (analysis.entities || []).forEach(e => {
        html += `<li>${e}</li>`;
    });
    html += '</ul>';
    
    // Display shared screens if available
    if (analysis.shared_screens && Object.keys(analysis.shared_screens).length > 0) {
        html += '<h4>Shared Screens (Multi-Flow Access)</h4>';
        html += '<ul style="margin-left: 20px;">';
        Object.entries(analysis.shared_screens).forEach(([screen, flows]) => {
            html += `<li><strong>${screen}:</strong> Used by ${flows.length} flows (${flows.join(', ')})</li>`;
        });
        html += '</ul>';
    }
    
    html += '<h4>Optimized Paths</h4>';
    html += '<ul style="margin-left: 20px;">';
    (analysis.optimized_paths || []).forEach(p => {
        const pathStr = Array.isArray(p) ? p.join(' → ') : p;
        html += `<li>${pathStr}</li>`;
    });
    html += '</ul>';

    summary.innerHTML = html;
}

/**
 * Display flow diagram
 */
function displayDiagram(diagramData) {
    const container = document.getElementById('diagramContainer');
    
    if (!diagramData || !diagramData.nodes || diagramData.nodes.length === 0) {
        container.innerHTML = '<p class="placeholder">No diagram data available</p>';
        return;
    }

    // Create container for Cytoscape
    if (document.getElementById('cy')) {
        document.getElementById('cy').remove();
    }
    
    const cyDiv = document.createElement('div');
    cyDiv.id = 'cy';
    cyDiv.style.width = '100%';
    cyDiv.style.height = '900px';  // Increased height for better spacing
    container.innerHTML = '';
    container.appendChild(cyDiv);

    // Prepare data for Cytoscape
    const cyNodes = diagramData.nodes.map(node => ({
        data: {
            id: node.id,
            label: node.label,
            type: node.type
        }
    }));

    const cyEdges = diagramData.edges.map(edge => ({
        data: {
            source: edge.source,
            target: edge.target,
            label: edge.label || ''
        }
    }));

    // Initialize Cytoscape with standard block diagram styling
    cy = cytoscape({
        container: cyDiv,
        elements: [...cyNodes, ...cyEdges],
        style: [
            {
                selector: 'node',
                style: {
                    'content': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'background-color': '#0066cc',
                    'width': 130,
                    'height': 80,
                    'color': '#fff',
                    'font-size': 12,
                    'font-weight': 'bold',
                    'text-wrap': 'wrap',
                    'padding': '8px',
                    'border-width': 2,
                    'border-color': '#004d99',
                    'shape': 'rectangle'
                }
            },
            {
                selector: 'node[type="startpoint"]',
                style: {
                    'background-color': '#28a745',
                    'border-color': '#1e7e34',
                    'shape': 'rectangle',
                    'width': 110,
                    'height': 60
                }
            },
            {
                selector: 'node[type="endpoint"]',
                style: {
                    'background-color': '#dc3545',
                    'border-color': '#bd2130',
                    'shape': 'rectangle',
                    'width': 110,
                    'height': 60
                }
            },
            {
                selector: 'node[type="decision"]',
                style: {
                    'shape': 'diamond',
                    'background-color': '#ffc107',
                    'color': '#000',
                    'border-color': '#e0a800',
                    'width': 120,
                    'height': 120,
                    'font-size': 11
                }
            },
            {
                selector: 'edge',
                style: {
                    'curve-style': 'taxi',
                    'taxi-direction': 'downward',
                    'target-arrow-shape': 'triangle',
                    'line-color': '#333',
                    'target-arrow-color': '#333',
                    'line-width': 2,
                    'label': 'data(label)',
                    'font-size': 10,
                    'font-weight': 'bold',
                    'text-wrap': 'wrap',
                    'text-max-width': '120px',
                    'text-background-color': '#fff',
                    'text-background-opacity': 1.0,
                    'text-background-padding': '6px',
                    'text-background-border-width': '1px',
                    'text-background-border-color': '#333',
                    'text-margin-y': '-25px',
                    'text-margin-x': '0px',
                    'text-valign': 'center',
                    'text-halign': 'center'
                }
            }
        ],
        layout: {
            name: 'grid',
            rows: 1,
            cols: 1
        }
    });

    // Apply hierarchical layout with proper flow spacing
    applyAlignedHierarchicalLayout(cyNodes, diagramData.edges);

    // Auto fit on load
    setTimeout(() => {
        if (cy) {
            cy.fit(cyDiv, 20);
        }
    }, 300);
}

/**
 * Apply aligned hierarchical layout for top-to-bottom flow with vertical/horizontal edges
 * Handles multiple parallel flows without overlap
 */
function applyAlignedHierarchicalLayout(nodes, edges) {
    if (!cy || nodes.length === 0) return;
    
    // Build adjacency information from edges
    const adjacency = {};
    const inDegree = {};
    
    nodes.forEach(n => {
        adjacency[n.data.id] = [];
        inDegree[n.data.id] = 0;
    });
    
    edges.forEach(e => {
        adjacency[e.source] = adjacency[e.source] || [];
        adjacency[e.source].push(e.target);
        inDegree[e.target] = (inDegree[e.target] || 0) + 1;
    });
    
    // Find all root nodes (START or startpoint type or in-degree = 0)
    const rootNodes = nodes.filter(n => 
        n.data.id.includes('START') || 
        n.data.type === 'startpoint' || 
        inDegree[n.data.id] === 0
    );
    
    const startX = 200;
    const startY = 60;
    const nodeWidth = 160;
    const nodeHeight = 120;
    const verticalGap = 160;
    const flowHorizontalGap = 240;  // Space between parallel flows
    
    let levelMap = {};      // level -> list of nodes at that level
    let nodePositions = {}; // nodeId -> {x, y}
    let visited = new Set();
    let flowMap = {};       // Track which flow each node belongs to
    let flowCounter = 0;
    
    // BFS from each root to map levels and flows
    const processQueue = [];
    
    rootNodes.forEach((rootNode, flowIdx) => {
        processQueue.push({
            nodeId: rootNode.data.id,
            level: 0,
            flowId: flowIdx,
            pathDepth: 0
        });
    });
    
    while (processQueue.length > 0) {
        const { nodeId, level, flowId, pathDepth } = processQueue.shift();
        
        // Assign to level
        if (!levelMap[level]) levelMap[level] = [];
        if (!levelMap[level].find(n => n.id === nodeId)) {
            levelMap[level].push({ 
                id: nodeId, 
                flowId: flowId,
                pathDepth: pathDepth 
            });
        }
        
        // Avoid infinite loops
        if (visited.has(`${nodeId}-${flowId}-${level}`)) continue;
        visited.add(`${nodeId}-${flowId}-${level}`);
        
        // Process successors
        if (adjacency[nodeId]) {
            adjacency[nodeId].forEach(successor => {
                processQueue.push({
                    nodeId: successor,
                    level: level + 1,
                    flowId: flowId,
                    pathDepth: pathDepth + 1
                });
            });
        }
    }
    
    // Calculate positions based on levels and flows
    Object.entries(levelMap).forEach(([level, nodesAtLevel]) => {
        const y = startY + (parseInt(level)) * verticalGap;
        
        // Group nodes by flowId to position them side-by-side
        const flowGroups = {};
        nodesAtLevel.forEach(node => {
            if (!flowGroups[node.flowId]) flowGroups[node.flowId] = [];
            flowGroups[node.flowId].push(node);
        });
        
        let xOffset = startX;
        
        Object.entries(flowGroups).forEach(([flowId, flowNodes]) => {
            flowNodes.forEach((node, idx) => {
                // Get or create position
                if (!nodePositions[node.id]) {
                    nodePositions[node.id] = {
                        x: xOffset + (idx * nodeWidth),
                        y: y
                    };
                } else {
                    // If node already has position but we're seeing it again,
                    // it's a convergence point - keep original position
                }
            });
            
            xOffset += (flowNodes.length * nodeWidth) + flowHorizontalGap;
        });
    });
    
    // Apply positions to nodes
    Object.entries(nodePositions).forEach(([nodeId, pos]) => {
        const cyNode = cy.getElementById(nodeId);
        if (cyNode && cyNode.isNode()) {
            cyNode.position(pos);
        }
    });
    
    // Handle nodes that appear in multiple flows (convergence points)
    // Recenter them if needed for better visualization
    const nodeFlowCount = {};
    Object.values(levelMap).forEach(nodesAtLevel => {
        nodesAtLevel.forEach(node => {
            nodeFlowCount[node.id] = (nodeFlowCount[node.id] || 0) + 1;
        });
    });
    
    // For convergence points, adjust position to be more centered
    Object.entries(nodeFlowCount).forEach(([nodeId, count]) => {
        if (count > 1 && nodePositions[nodeId]) {
            // Node appears in multiple flows - highlight this
            const cyNode = cy.getElementById(nodeId);
            if (cyNode && cyNode.isNode()) {
                cyNode.style('border-width', 3);
                cyNode.style('border-color', '#ff6b35');
            }
        }
    });
}

/**
 * Display path analysis data
 */
function displayPathAnalysis(pathAnalysis) {
    if (!pathAnalysis) return;

    // Display navigation paths if available (from analysis)
    if (currentAnalysis && currentAnalysis.analysis && currentAnalysis.analysis.navigation_paths) {
        displayNavigationPaths(currentAnalysis.analysis.navigation_paths);
    }

    // Display All Nodes
    displayNodesList(pathAnalysis.all_nodes);

    // Display All Edges
    displayEdgesList(pathAnalysis.all_edges);

    // Display In-Out Edges (for first node as example)
    if (pathAnalysis.all_nodes && pathAnalysis.all_nodes.length > 0) {
        displayInOutEdges(pathAnalysis.all_nodes[0], pathAnalysis);
    }

    // Display All Pairs
    displayAllPairs(pathAnalysis.all_pairs, pathAnalysis.pair_paths);

    // Display Critical Paths
    displayCriticalPaths(pathAnalysis.critical_paths);

    // Display Statistics
    displayStatistics(pathAnalysis.graph_stats, pathAnalysis.node_degree_analysis);
}

/**
 * Display navigation paths
 */
function displayNavigationPaths(navigationPaths) {
    const navContainer = document.getElementById('navigationContainer');
    if (!navContainer) {
        // Create container if it doesn't exist
        const pathsTab = document.getElementById('statsTab');
        if (pathsTab && !document.getElementById('navigationContainer')) {
            const navDiv = document.createElement('div');
            navDiv.id = 'navigationContainer';
            navDiv.style.marginBottom = '20px';
            pathsTab.parentNode.insertBefore(navDiv, pathsTab);
        }
    }
    
    if (!navigationPaths || navigationPaths.length === 0) return;
    
    let html = '<h4>Navigation Paths</h4>';
    html += '<table class="nav-table" style="width: 100%; border-collapse: collapse;">';
    html += '<thead><tr style="background: #f0f0f0;"><th style="padding: 8px; border: 1px solid #ddd;">From Screen</th><th style="padding: 8px; border: 1px solid #ddd;">To Screen</th><th style="padding: 8px; border: 1px solid #ddd;">Action</th><th style="padding: 8px; border: 1px solid #ddd;">Used By Flows</th></tr></thead>';
    html += '<tbody>';
    
    navigationPaths.forEach((path, index) => {
        const fromScreen = path.from_screen || path[0] || '';
        const toScreen = path.to_screen || path[1] || '';
        const action = path.action || 'Navigate';
        const flows = path.flows ? path.flows.join(', ') : 'N/A';
        
        html += `<tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; border: 1px solid #ddd; background: #e8f4f8;"><strong>${fromScreen}</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd; background: #f0f8e8;"><strong>${toScreen}</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${action}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; font-size: 0.85rem;"><code>${flows}</code></td>
                </tr>`;
    });
    
    html += '</tbody></table>';
    
    if (document.getElementById('navigationContainer')) {
        document.getElementById('navigationContainer').innerHTML = html;
    }
}

/**
 * Display all nodes
 */
function displayNodesList(nodes) {
    const list = document.getElementById('nodesList');
    
    if (!nodes || nodes.length === 0) {
        list.innerHTML = '<p class="placeholder">No nodes found</p>';
        return;
    }

    let html = '<table class="node-table"><thead><tr><th>Node ID</th><th>Type</th></tr></thead><tbody>';
    nodes.forEach(node => {
        html += `<tr><td>${node}</td><td><span style="padding: 3px 8px; background: #e0e0e0; border-radius: 3px; font-size: 0.85rem;">${node}</span></td></tr>`;
    });
    html += '</tbody></table>';
    
    list.innerHTML = html;
}

/**
 * Display all edges
 */
function displayEdgesList(edges) {
    const list = document.getElementById('edgesList');
    
    if (!edges || edges.length === 0) {
        list.innerHTML = '<p class="placeholder">No edges found</p>';
        return;
    }

    let html = '<table class="edge-table"><thead><tr><th>#</th><th>Source</th><th>Target</th></tr></thead><tbody>';
    edges.forEach((edge, index) => {
        html += `<tr><td>${index + 1}</td><td>${edge[0]}</td><td>${edge[1]}</td></tr>`;
    });
    html += '</tbody></table>';
    
    list.innerHTML = html;
}

/**
 * Display in and out edges for a node
 */
function displayInOutEdges(nodeId, pathAnalysis) {
    const list = document.getElementById('inoutList');
    let html = `<h4>Edges for Node: ${nodeId}</h4>`;

    // Find in-edges
    const inEdges = pathAnalysis.all_edges.filter(e => e[1] === nodeId);
    const outEdges = pathAnalysis.all_edges.filter(e => e[0] === nodeId);

    html += '<h5 style="margin-top: 15px;">Incoming Edges:</h5>';
    if (inEdges.length > 0) {
        html += '<table class="inout-table"><tbody>';
        inEdges.forEach(edge => {
            html += `<tr><td>${edge[0]}</td><td style="text-align: center;">→</td><td>${edge[1]}</td></tr>`;
        });
        html += '</tbody></table>';
    } else {
        html += '<p style="color: #999;">No incoming edges</p>';
    }

    html += '<h5 style="margin-top: 15px;">Outgoing Edges:</h5>';
    if (outEdges.length > 0) {
        html += '<table class="inout-table"><tbody>';
        outEdges.forEach(edge => {
            html += `<tr><td>${edge[0]}</td><td style="text-align: center;">→</td><td>${edge[1]}</td></tr>`;
        });
        html += '</tbody></table>';
    } else {
        html += '<p style="color: #999;">No outgoing edges</p>';
    }

    list.innerHTML = html;
}

/**
 * Display all pairs and their paths
 */
function displayAllPairs(pairs, pairPaths) {
    const list = document.getElementById('pairsList');
    
    if (!pairs || pairs.length === 0) {
        list.innerHTML = '<p class="placeholder">No pairs found</p>';
        return;
    }

    let html = '<table class="pair-table"><thead><tr><th>#</th><th>From</th><th>To</th><th>Paths</th></tr></thead><tbody>';
    pairs.forEach((pair, index) => {
        const pairData = pairPaths.find(p => p.from === pair[0] && p.to === pair[1]);
        const pathCount = pairData ? pairData.path_count : 0;
        html += `<tr><td>${index + 1}</td><td>${pair[0]}</td><td>${pair[1]}</td><td>${pathCount}</td></tr>`;
    });
    html += '</tbody></table>';
    
    list.innerHTML = html;
}

/**
 * Display critical paths
 */
function displayCriticalPaths(paths) {
    const list = document.getElementById('criticalList');
    
    if (!paths || paths.length === 0) {
        list.innerHTML = '<p class="placeholder">No critical paths found</p>';
        return;
    }

    let html = '<table class="critical-table"><thead><tr><th>#</th><th>Path</th><th>Length</th></tr></thead><tbody>';
    paths.forEach((path, index) => {
        const pathStr = path.join(' → ');
        html += `<tr><td>${index + 1}</td><td>${pathStr}</td><td>${path.length}</td></tr>`;
    });
    html += '</tbody></table>';
    
    list.innerHTML = html;
}

/**
 * Display statistics
 */
function displayStatistics(stats, nodeAnalysis) {
    const grid = document.getElementById('statsDisplay');
    
    if (!stats) {
        grid.innerHTML = '<p class="placeholder">No statistics available</p>';
        return;
    }

    let html = `
        <div class="stat-card">
            <div class="stat-value">${stats.total_nodes}</div>
            <div class="stat-label">Total Nodes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.total_edges}</div>
            <div class="stat-label">Total Edges</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.total_pairs}</div>
            <div class="stat-label">All Pairs</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.start_nodes}</div>
            <div class="stat-label">Start Nodes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.end_nodes}</div>
            <div class="stat-label">End Nodes</div>
        </div>
    `;

    // Add node degree analysis if available
    if (nodeAnalysis) {
        const avgInDegree = Object.values(nodeAnalysis).reduce((sum, n) => sum + n.in_degree, 0) / Object.keys(nodeAnalysis).length;
        const avgOutDegree = Object.values(nodeAnalysis).reduce((sum, n) => sum + n.out_degree, 0) / Object.keys(nodeAnalysis).length;
        
        html += `
            <div class="stat-card">
                <div class="stat-value">${avgInDegree.toFixed(2)}</div>
                <div class="stat-label">Avg In-Degree</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${avgOutDegree.toFixed(2)}</div>
                <div class="stat-label">Avg Out-Degree</div>
            </div>
        `;
    }

    grid.innerHTML = html;
}

/**
 * Clear input
 */
function clearInput() {
    document.getElementById('contentInput').value = '';
    showToast('Input cleared', 'info');
}

/**
 * Export diagram
 */
function exportDiagram(format) {
    if (!currentAnalysis) {
        showToast('No diagram available. Please run analysis first.', 'warning');
        return;
    }

    let endpoint = '';
    let filename = '';

    if (format === 'mxgraph') {
        endpoint = '/api/export/mxgraph';
        filename = 'flow_diagram.drawio';
    } else if (format === 'json') {
        endpoint = '/api/export/json';
        filename = 'flow_diagram.json';
    } else if (format === 'pptx') {
        endpoint = '/api/export/pptx';
        filename = 'flow_diagram.pptx';
    }

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(currentAnalysis.diagram)
    })
    .then(response => {
        // Handle PPTX binary file download
        if (format === 'pptx') {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Export failed');
                });
            }
            return response.blob().then(blob => ({
                blob: blob,
                format: 'pptx'
            }));
        }
        // Handle JSON responses for other formats
        return response.json().then(data => ({
            data: data,
            format: format
        }));
    })
    .then(result => {
        if (result.format === 'pptx') {
            // Handle binary PPTX file
            const url = window.URL.createObjectURL(result.blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
            showToast('PowerPoint exported successfully', 'success');
        } else {
            // Handle JSON data for other formats
            const data = result.data;
            if (data.success) {
                if (format === 'mxgraph') {
                    const blob = new Blob([data.content], { type: 'application/xml' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    a.click();
                    window.URL.revokeObjectURL(url);
                    showToast('Draw.io file exported successfully', 'success');
                } else if (format === 'json') {
                    const blob = new Blob([JSON.stringify(data.content, null, 2)], { type: 'application/json' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    a.click();
                    window.URL.revokeObjectURL(url);
                    showToast('JSON exported successfully', 'success');
                }
            } else {
                showToast('Export failed: ' + data.error, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Export error: ' + error.message, 'error');
    });
}

/**
 * Diagram zoom controls
 */
function zoomDiagram(direction) {
    if (!cy) return;
    
    if (direction === 'in') {
        cy.zoom(cy.zoom() * 1.2);
    } else if (direction === 'out') {
        cy.zoom(cy.zoom() / 1.2);
    }
}

/**
 * Fit diagram to view
 */
function fitDiagram() {
    if (cy) {
        cy.fit();
    }
}

/**
 * Switch tab in section 2
 */
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    if (tabName === 'flows') {
        document.getElementById('flowsTab').classList.add('active');
    } else if (tabName === 'analysis') {
        document.getElementById('analysisTab').classList.add('active');
    }

    // Mark button as active
    event.target.classList.add('active');
}

/**
 * Switch path tab in section 4
 */
function switchPathTab(tabName) {
    // Hide all panels
    document.querySelectorAll('.path-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.querySelectorAll('.path-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected panel
    const panelMap = {
        'navigation': 'navigationTab',
        'nodes': 'nodesTab',
        'edges': 'edgesTab',
        'inout': 'inoutTab',
        'pairs': 'pairsTab',
        'critical': 'criticalTab',
        'stats': 'statsTab'
    };

    if (panelMap[tabName]) {
        document.getElementById(panelMap[tabName]).classList.add('active');
    }

    // Mark button as active
    event.target.classList.add('active');
}

/**
 * Generate test cases for a specific coverage type
 */
function generateTestCases(coverageType) {
    fetch('/api/testcases/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            coverage_type: coverageType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayTestCases(data.test_cases, coverageType);
            showToast(`Generated ${data.count} test cases for ${coverageType} coverage`, 'success');
        } else {
            showToast('Failed to generate test cases: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error generating test cases: ' + error.message, 'error');
    });
}

/**
 * Display test cases in a table format
 */
function displayTestCases(testCases, coverageType) {
    // Determine which container to use
    const containerMap = {
        'nodes': 'nodesCoverageTestCases',
        'edges': 'edgesCoverageTestCases',
        'in-out': 'inoutCoverageTestCases',
        'pairs': 'pairsCoverageTestCases'
    };
    
    const containerId = containerMap[coverageType] || 'nodesCoverageTestCases';
    const container = document.getElementById(containerId);
    
    if (!testCases || testCases.length === 0) {
        container.innerHTML = '<p class="placeholder">No test cases generated</p>';
        return;
    }
    
    let html = '<table class="test-cases-table" style="width: 100%; border-collapse: collapse; margin-top: 10px;">';
    html += '<thead><tr style="background: #4472C4; color: white;">';
    html += '<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Test #</th>';
    html += '<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Test Description (Gherkin)</th>';
    html += '<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Expected Result</th>';
    html += '<th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Nodes Covered</th>';
    html += '</tr></thead><tbody>';
    
    testCases.forEach((tc) => {
        const nodesCovered = tc.nodes_covered.join(' → ');
        const description = tc.description.replace(/\n/g, '<br>');
        
        html += `<tr style="border: 1px solid #ddd; background: ${tc.test_number % 2 === 0 ? '#f9f9f9' : '#ffffff'};">`;
        html += `<td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">${tc.test_number}</td>`;
        html += `<td style="padding: 10px; border: 1px solid #ddd; font-family: monospace; font-size: 0.9rem; white-space: pre-wrap;">${description}</td>`;
        html += `<td style="padding: 10px; border: 1px solid #ddd;"><code style="background: #f0f0f0; padding: 3px 6px; border-radius: 3px;">${tc.expected_result}</code></td>`;
        html += `<td style="padding: 10px; border: 1px solid #ddd; font-size: 0.85rem;"><code style="background: #f0f0f0; padding: 3px 6px; border-radius: 3px;">${nodesCovered}</code></td>`;
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Export test cases to CSV or Excel
 */
function exportTestCases(format) {
    const endpoint = format === 'csv' ? '/api/testcases/export/csv' : '/api/testcases/export/excel';
    
    fetch(endpoint, {
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Export failed with status ${response.status}`);
        }
        
        if (format === 'excel') {
            // Handle binary Excel file
            return response.blob().then(blob => ({
                blob: blob,
                format: 'excel'
            }));
        } else {
            // Handle text CSV
            return response.text().then(text => ({
                text: text,
                format: 'csv'
            }));
        }
    })
    .then(result => {
        if (result.format === 'excel') {
            const url = window.URL.createObjectURL(result.blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `test_cases_${new Date().toISOString().split('T')[0]}.xlsx`;
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const url = window.URL.createObjectURL(new Blob([result.text], { type: 'text/csv' }));
            const a = document.createElement('a');
            a.href = url;
            a.download = `test_cases_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
        showToast(`Test cases exported as ${format.toUpperCase()}`, 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Export error: ' + error.message, 'error');
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

