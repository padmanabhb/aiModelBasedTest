"""
Path Analyzer Module
Analyzes paths in the requirement model graph
"""
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, deque

class PathAnalyzer:
    """
    Analyzes all nodes, edges, and paths in a requirement model
    """
    
    def __init__(self, nodes: Dict[str, Any], edges: List[Dict[str, str]]):
        """
        Initialize the path analyzer
        
        Args:
            nodes: Dictionary of nodes
            edges: List of edge dictionaries with 'source' and 'target'
        """
        self.nodes = nodes
        self.edges = edges
        self.adjacency_list = self._build_adjacency_list()
        self.reverse_adjacency = self._build_reverse_adjacency()
    
    def _build_adjacency_list(self) -> Dict[str, List[str]]:
        """Build adjacency list for the graph"""
        adj_list = defaultdict(list)
        for edge in self.edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            if source and target:
                adj_list[source].append(target)
                # Ensure all nodes are in the list
                if target not in adj_list:
                    adj_list[target] = []
        
        # Add isolated nodes
        for node_id in self.nodes.keys():
            if node_id not in adj_list:
                adj_list[node_id] = []
        
        return dict(adj_list)
    
    def _build_reverse_adjacency(self) -> Dict[str, List[str]]:
        """Build reverse adjacency list"""
        rev_adj = defaultdict(list)
        for source, targets in self.adjacency_list.items():
            for target in targets:
                rev_adj[target].append(source)
        
        for node_id in self.nodes.keys():
            if node_id not in rev_adj:
                rev_adj[node_id] = []
        
        return dict(rev_adj)
    
    def get_all_nodes(self) -> List[str]:
        """Get all nodes in the graph"""
        return list(self.nodes.keys())
    
    def get_all_edges(self) -> List[Tuple[str, str]]:
        """Get all edges in the graph"""
        return [(edge["source"], edge["target"]) for edge in self.edges]
    
    def get_in_edges(self, node_id: str) -> List[Tuple[str, str]]:
        """Get all edges coming into a node"""
        in_edges = []
        for edge in self.edges:
            if edge["target"] == node_id:
                in_edges.append((edge["source"], edge["target"]))
        return in_edges
    
    def get_out_edges(self, node_id: str) -> List[Tuple[str, str]]:
        """Get all edges going out of a node"""
        out_edges = []
        for edge in self.edges:
            if edge["source"] == node_id:
                out_edges.append((edge["source"], edge["target"]))
        return out_edges
    
    def get_in_out_edges(self, node_id: str) -> Dict[str, List[Tuple[str, str]]]:
        """Get all in and out edges for a node"""
        return {
            "in_edges": self.get_in_edges(node_id),
            "out_edges": self.get_out_edges(node_id)
        }
    
    def get_all_paths_between(self, source: str, target: str) -> List[List[str]]:
        """
        Find all possible paths between two nodes using DFS
        
        Args:
            source: Starting node ID
            target: Ending node ID
            
        Returns:
            List of paths, each path is a list of node IDs
        """
        if source not in self.adjacency_list or target not in self.adjacency_list:
            return []
        
        all_paths = []
        visited = set()
        current_path = [source]
        
        self._dfs_find_paths(source, target, visited, current_path, all_paths)
        return all_paths
    
    def _dfs_find_paths(self, current: str, target: str, visited: Set[str], 
                       path: List[str], all_paths: List[List[str]]) -> None:
        """DFS helper to find all paths"""
        if current == target:
            all_paths.append(path.copy())
            return
        
        for neighbor in self.adjacency_list.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                self._dfs_find_paths(neighbor, target, visited, path, all_paths)
                path.pop()
                visited.remove(neighbor)
    
    def get_all_possible_paths(self) -> Dict[str, List[List[str]]]:
        """
        Get all possible paths starting from each node
        
        Returns:
            Dictionary mapping node IDs to lists of paths
        """
        paths = {}
        for start_node in self.nodes.keys():
            start_paths = []
            for end_node in self.nodes.keys():
                if start_node != end_node:
                    path_list = self.get_all_paths_between(start_node, end_node)
                    if path_list:
                        start_paths.extend(path_list)
            paths[start_node] = start_paths
        
        return paths
    
    def get_all_pairs(self) -> List[Tuple[str, str]]:
        """Get all possible node pairs"""
        nodes = self.get_all_nodes()
        pairs = []
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                pairs.append((node1, node2))
        return pairs
    
    def get_critical_paths(self) -> List[List[str]]:
        """
        Find critical paths in the flow
        Critical paths are the longest paths from start to end nodes
        
        Returns:
            List of critical paths
        """
        start_nodes = [n for n in self.nodes.keys() 
                      if self.nodes[n].get("type") == "startpoint" or len(self.reverse_adjacency.get(n, [])) == 0]
        end_nodes = [n for n in self.nodes.keys() 
                    if self.nodes[n].get("type") == "endpoint" or len(self.adjacency_list.get(n, [])) == 0]
        
        if not start_nodes:
            start_nodes = [list(self.nodes.keys())[0]]
        if not end_nodes:
            end_nodes = [list(self.nodes.keys())[-1]]
        
        all_critical_paths = []
        for start in start_nodes:
            for end in end_nodes:
                paths = self.get_all_paths_between(start, end)
                if paths:
                    # Get the longest path
                    longest = max(paths, key=len)
                    all_critical_paths.append(longest)
        
        return all_critical_paths
    
    def get_path_analysis_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive path analysis report
        
        Returns:
            Dictionary containing all path analysis data
        """
        all_pairs = self.get_all_pairs()
        pair_paths = []
        
        for source, target in all_pairs:
            paths = self.get_all_paths_between(source, target)
            pair_paths.append({
                "from": source,
                "to": target,
                "path_count": len(paths),
                "paths": paths,
                "shortest_path": min(paths, key=len) if paths else None,
                "longest_path": max(paths, key=len) if paths else None
            })
        
        # Node degree analysis
        node_degree = {}
        for node_id in self.nodes.keys():
            in_degree = len(self.get_in_edges(node_id))
            out_degree = len(self.get_out_edges(node_id))
            node_degree[node_id] = {
                "in_degree": in_degree,
                "out_degree": out_degree,
                "total_degree": in_degree + out_degree
            }
        
        return {
            "all_nodes": self.get_all_nodes(),
            "all_edges": self.get_all_edges(),
            "all_pairs": all_pairs,
            "pair_paths": pair_paths,
            "critical_paths": self.get_critical_paths(),
            "node_degree_analysis": node_degree,
            "graph_stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "total_pairs": len(all_pairs),
                "start_nodes": len([n for n in self.nodes.keys() 
                                   if self.nodes[n].get("type") == "startpoint"]),
                "end_nodes": len([n for n in self.nodes.keys() 
                                 if self.nodes[n].get("type") == "endpoint"])
            }
        }
