# src/network/graph_builder.py

import sumolib
import networkx as nx
from typing import Dict, Tuple, Optional

class TransportNetwork:
    """Dual representation: SUMO network + NetworkX graph."""
    
    def __init__(self, net_file: str):
        self.net_file = net_file
        self.sumo_net = sumolib.net.readNet(net_file)
        self.graph = self._build_networkx_graph()
        self._base_capacities: Dict[str, float] = {}
        self._initialize_capacities()
    
    def _build_networkx_graph(self) -> nx.DiGraph:
        """Convert SUMO network to NetworkX DiGraph."""
        G = nx.DiGraph()
        
        for node in self.sumo_net.getNodes():
            x, y = node.getCoord()
            G.add_node(node.getID(), pos=(x, y), type=str(node.getType()))
        
        for edge in self.sumo_net.getEdges():
            if not edge.isSpecial():  # Skip internal junction edges
                G.add_edge(
                    edge.getFromNode().getID(),
                    edge.getToNode().getID(),
                    edge_id=edge.getID(),
                    length=edge.getLength(),
                    speed_limit=edge.getSpeed(),
                    lanes=edge.getLaneNumber(),
                    travel_time=edge.getLength() / edge.getSpeed(),
                    capacity=1.0,  # Normalized: 1.0 = full capacity
                    status="open"
                )
        return G
    
    def _initialize_capacities(self):
        """Store baseline edge capacities for disruption simulation."""
        for u, v, data in self.graph.edges(data=True):
            self._base_capacities[data['edge_id']] = data['capacity']
    
    def get_edge_by_nodes(self, from_node: str, to_node: str) -> Optional[dict]:
        """Get edge data between two nodes."""
        if self.graph.has_edge(from_node, to_node):
            return dict(self.graph[from_node][to_node])
        return None
    
    def close_edge(self, from_node: str, to_node: str):
        """Simulate road closure: set capacity to 0."""
        if self.graph.has_edge(from_node, to_node):
            self.graph[from_node][to_node]['capacity'] = 0.0
            self.graph[from_node][to_node]['status'] = "closed"
            self.graph[from_node][to_node]['travel_time'] = float('inf')
    
    def congest_edge(self, from_node: str, to_node: str, factor: float):
        """Simulate congestion: multiply travel time by factor."""
        if self.graph.has_edge(from_node, to_node):
            base_tt = self.graph[from_node][to_node]['length'] / self.graph[from_node][to_node]['speed_limit']
            self.graph[from_node][to_node]['travel_time'] = base_tt * factor
            self.graph[from_node][to_node]['capacity'] = max(0.1, 1.0 / factor)
            self.graph[from_node][to_node]['status'] = "congested"
    
    def restore_edge(self, from_node: str, to_node: str):
        """Restore edge to original capacity."""
        if self.graph.has_edge(from_node, to_node):
            edge_id = self.graph[from_node][to_node]['edge_id']
            self.graph[from_node][to_node]['capacity'] = self._base_capacities[edge_id]
            self.graph[from_node][to_node]['status'] = "open"
            self.graph[from_node][to_node]['travel_time'] = (
                self.graph[from_node][to_node]['length'] / 
                self.graph[from_node][to_node]['speed_limit']
            )
    
    def get_open_subgraph(self) -> nx.DiGraph:
        """Return subgraph containing only open/operational edges."""
        open_edges = [
            (u, v) for u, v, d in self.graph.edges(data=True)
            if d['capacity'] > 0
        ]
        return self.graph.edge_subgraph(open_edges).copy()
    
    def shortest_path(self, origin: str, destination: str, weight: str = 'travel_time') -> Optional[list]:
        """Find shortest path on the open subgraph."""
        open_graph = self.get_open_subgraph()
        try:
            return nx.shortest_path(open_graph, origin, destination, weight=weight)
        except nx.NetworkXNoPath:
            return None
    
    def bfs_reachable(self, origin: str, destination: str) -> bool:
        """BFS reachability check on open edges only (for Safety Guard)."""
        open_graph = self.get_open_subgraph()
        try:
            path = nx.shortest_path(open_graph, origin, destination)
            return True
        except nx.NetworkXNoPath:
            return False
    
    def to_json_state(self) -> dict:
        """Serialize network state for LLM context / scenario files."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({"id": node_id, "pos": data.get("pos", (0, 0))})
        
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "from": u, "to": v,
                "edge_id": data['edge_id'],
                "length": round(data['length'], 2),
                "speed_limit": round(data['speed_limit'], 2),
                "travel_time": round(data['travel_time'], 2),
                "capacity": round(data['capacity'], 2),
                "status": data['status'],
                "lanes": data['lanes']
            })
        
        return {"nodes": nodes, "edges": edges}
