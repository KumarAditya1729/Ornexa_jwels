import argparse
import os
import json

class OrnexaKnowledgeExplorer:
    def __init__(self, graph_path="knowledge_graph.json"):
        # Resolve path relative to this script
        base_dir = os.path.dirname(__file__)
        self.graph_path = os.path.join(base_dir, graph_path)
        self.kb = self._load_graph()

    def _load_graph(self):
        try:
            with open(self.graph_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load knowledge graph ({e}).")
            return {}

    def explain(self, query: str) -> str:
        query_lower = query.lower()
        
        # Check for comparison
        if "difference" in query_lower or "vs" in query_lower:
            keys_found = [k for k in self.kb.keys() if k in query_lower]
            if len(keys_found) >= 2:
                response = f"Comparing {keys_found[0].title()} and {keys_found[1].title()}:\n\n"
                response += f"- {self.kb[keys_found[0]]['definition']}\n"
                response += f"- {self.kb[keys_found[1]]['definition']}"
                return response
                
        # Check for direct matches
        for key, node in self.kb.items():
            if key in query_lower:
                definition = node.get("definition", "")
                related = node.get("related", [])
                
                response = definition
                if related:
                    response += f"\n\nRelated Concepts: {', '.join(related)}"
                return response
                
        return "I'm sorry, I don't have knowledge about that specific term in the current ORNEXA taxonomy."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORNEXA Knowledge Explorer")
    parser.add_argument("query", type=str, nargs="+", help="The question to ask ORNEXA (e.g., 'What is Kundan?')")
    
    args = parser.parse_args()
    query_str = " ".join(args.query)
    
    explorer = OrnexaKnowledgeExplorer()
    print(f"\n[ORNEXA Explorer] Question: {query_str}")
    print(f"\n{explorer.explain(query_str)}\n")
