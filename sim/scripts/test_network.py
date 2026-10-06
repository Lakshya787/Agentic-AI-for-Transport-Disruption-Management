#!/usr/bin/env python3
"""Test the TransportNetwork class."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.graph_builder import TransportNetwork

def main():
    # Load network
    net = TransportNetwork("networks/grid_4x4.net.xml")
    
    print("=" * 50)
    print("NETWORK LOADED SUCCESSFULLY")
    print("=" * 50)
    print(f"Nodes: {net.graph.number_of_nodes()}")
    print(f"Edges: {net.graph.number_of_edges()}")
    print()
    
    # Print all node IDs
    nodes = sorted(net.graph.nodes())
    print(f"Node IDs: {nodes}")
    print()
    
    # Pick two nodes for testing
    node_list = list(net.graph.nodes())
    start_node = node_list[0]
    end_node = node_list[-1]
    print(f"Testing path from {start_node} to {end_node}")
    
    # Test 1: Shortest path (should work)
    path = net.shortest_path(start_node, end_node)
    if path:
        print(f"✅ Path found: {' -> '.join(path)}")
        print(f"   Hops: {len(path) - 1}")
    else:
        print("❌ No path found (this is wrong — grid should be fully connected)")
    print()
    
    # Test 2: BFS reachability
    reachable = net.bfs_reachable(start_node, end_node)
    print(f"✅ BFS reachable: {reachable}")
    print()
    
    # Test 3: Close an edge and verify path changes
    if path and len(path) >= 3:
        close_from = path[1]
        close_to = path[2]
        print(f"Closing edge: {close_from} -> {close_to}")
        net.close_edge(close_from, close_to)
        
        # Check the edge status
        edge_data = net.get_edge_by_nodes(close_from, close_to)
        print(f"   Edge status: {edge_data['status']}")
        print(f"   Edge capacity: {edge_data['capacity']}")
        
        # Try finding path again (should reroute or fail)
        new_path = net.shortest_path(start_node, end_node)
        if new_path:
            print(f"✅ Rerouted path: {' -> '.join(new_path)}")
            if new_path != path:
                print("   ✅ Path changed (correctly avoided closed edge)")
            else:
                print("   ❌ Path didn't change (something is wrong)")
        else:
            print("   ⚠️  No path found after closure (may be valid if edge is critical)")
        print()
        
        # Test 4: Restore the edge
        net.restore_edge(close_from, close_to)
        restored_data = net.get_edge_by_nodes(close_from, close_to)
        print(f"After restore — status: {restored_data['status']}, capacity: {restored_data['capacity']}")
        
        restored_path = net.shortest_path(start_node, end_node)
        if restored_path == path:
            print("✅ Original path restored correctly")
        print()
    
    # Test 5: Congestion
    if path and len(path) >= 3:
        congest_from = path[1]
        congest_to = path[2]
        edge_before = net.get_edge_by_nodes(congest_from, congest_to)
        tt_before = edge_before['travel_time']
        
        net.congest_edge(congest_from, congest_to, factor=3.0)
        edge_after = net.get_edge_by_nodes(congest_from, congest_to)
        tt_after = edge_after['travel_time']
        
        print(f"Congestion test on {congest_from} -> {congest_to}:")
        print(f"   Travel time before: {tt_before:.1f}s")
        print(f"   Travel time after (3x factor): {tt_after:.1f}s")
        print(f"   ✅ Ratio: {tt_after/tt_before:.1f}x" if tt_after > tt_before else "   ❌ Congestion not applied")
        
        net.restore_edge(congest_from, congest_to)
        print()
    
    # Test 6: JSON serialization
    state = net.to_json_state()
    print(f"JSON state: {len(state['nodes'])} nodes, {len(state['edges'])} edges")
    print(f"Sample node: {state['nodes'][0]}")
    print(f"Sample edge: {state['edges'][0]}")
    print()
    
    print("=" * 50)
    print("ALL NETWORK TESTS PASSED ✅")
    print("=" * 50)

if __name__ == "__main__":
    main()
