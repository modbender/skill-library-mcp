import networkx as nx
import json
import os

GRAPH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory_graph.json")

class MemoryGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.load()

    def add_node(self, name, type="concept", **metadata):
        self.graph.add_node(name, type=type, **metadata)

    def add_edge(self, source, target, relation="related_to"):
        if source in self.graph and target in self.graph:
            self.graph.add_edge(source, target, relation=relation)

    def get_related(self, node_name, relation=None):
        if node_name not in self.graph:
            return []
        
        related = []
        # Outgoing edges
        for neighbor in self.graph.successors(node_name):
            edge_data = self.graph.get_edge_data(node_name, neighbor)
            if relation is None or edge_data.get('relation') == relation:
                related.append({"node": neighbor, "relation": edge_data.get('relation'), "direction": "out"})
        
        # Incoming edges
        for neighbor in self.graph.predecessors(node_name):
            edge_data = self.graph.get_edge_data(neighbor, node_name)
            if relation is None or edge_data.get('relation') == relation:
                related.append({"node": neighbor, "relation": edge_data.get('relation'), "direction": "in"})
                
        return related

    def save(self):
        data = nx.node_link_data(self.graph)
        with open(GRAPH_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"🕸️  Graph saved to {GRAPH_FILE} ({self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges)")

    def load(self):
        if os.path.exists(GRAPH_FILE):
            with open(GRAPH_FILE, 'r') as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data)
        else:
            print("🕸️  New graph initialized")

    def build_from_chunks(self, chunks):
        """
        Auto-extracts nodes and relations from text chunks.
        Nodes = Section Headers + **Bolded Concepts**.
        Edges = Hierarchical (Structure) + Semantic (Mentions).
        """
        print("🕸️  Building Knowledge Graph from Memory Chunks...")
        self.graph.clear() # Rebuild fresh from current state
        import re
        
        # 1. Identify Nodes
        # Headers -> Section Nodes
        section_nodes = set()
        for c in chunks:
            h = c['metadata']['section']
            self.add_node(h, type="section")
            section_nodes.add(h)

        # Bolded Terms -> Concept Nodes
        concept_nodes = set()
        for c in chunks:
            # Extract **Term** pattern
            concepts = re.findall(r'\*\*(.*?)\*\*', c['content'])
            for concept in concepts:
                if len(concept) < 3 or len(concept) > 50: continue # Filter noise
                if concept in section_nodes: continue
                
                self.add_node(concept, type="concept")
                concept_nodes.add(concept)
                # Link Section -> Concept (structural)
                self.add_edge(c['metadata']['section'], concept, relation="contains")

        all_nodes = section_nodes.union(concept_nodes)

        # 2. Extract Relations (Cross-References)
        # Keywords for typed relations
        RELATION_MAP = {
            "depends on": "depends_on",
            "blocked by": "blocked_by",
            "enables": "enables",
            "improves": "improves",
            "replaces": "replaces",
            "uses": "uses",
            "alternative to": "alternative_to",
            "related to": "related_to",
            "see": "refer_to",
            "reference": "refer_to"
        }

        for chunk in chunks:
            current_header = chunk['metadata']['section']
            text = chunk['content']
            text_lower = text.lower()
            
            # Check for mentions of ANY other node (Section or Concept)
            for target_node in all_nodes:
                if target_node == current_header: continue
                
                # Avoid self-referential concept loops (e.g. Section contains Concept, don't link Concept -> Section just because it's there)
                # We want mentions in the TEXT flow.
                
                # Check if target is in text
                if target_node in text:
                    # If it's a concept *inside* this section, we already added 'contains'.
                    # We want to find if this text *relates* to it.
                    
                    relation = "mentions"
                    
                    # Try to infer stricter relation from context around the mention
                    sentences = text.split('.')
                    for s in sentences:
                        if target_node in s:
                            s_lower = s.lower()
                            for keyword, rel_type in RELATION_MAP.items():
                                if keyword in s_lower:
                                    relation = rel_type
                                    break
                    
                    # If it's just a mention of a concept defined locally, 'contains' covers it.
                    # But if we found a specific relation keyword, overwrite/add it.
                    if target_node in concept_nodes and relation == "mentions":
                        # Skip implicit mentions of local concepts to reduce noise
                        # unless it's a cross-section mention? 
                        # Actually, let's keep it simple: Link if keyword found, or if it's a Section node.
                        continue
                    
                    self.add_edge(current_header, target_node, relation=relation)

        self.save()

if __name__ == "__main__":
    # Test
    g = MemoryGraph()
    print("Graph module ready.")
