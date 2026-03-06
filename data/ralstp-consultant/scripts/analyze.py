import argparse
import re
import sys
from collections import defaultdict

# --- Simple PDDL Parser (Regex based for robustness without deps) ---

def clean_pddl(text):
    """Remove comments and newlines for easier parsing."""
    text = re.sub(r';.*', '', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_lisp_structure(text):
    """Parses nested parens into a list of lists."""
    stack = []
    current = []
    tokens = text.replace('(', ' ( ').replace(')', ' ) ').split()
    
    root = current
    
    for token in tokens:
        if token == '(':
            new_list = []
            current.append(new_list)
            stack.append(current)
            current = new_list
        elif token == ')':
            if not stack:
                raise ValueError("Unbalanced parentheses")
            current = stack.pop()
        else:
            current.append(token)
    
    return root[0] if root else []

def find_section(pddl_struct, keyword):
    """Finds a section like (:types ...) or (:action ...)"""
    if not isinstance(pddl_struct, list): return None
    for item in pddl_struct:
        if isinstance(item, list) and len(item) > 0 and item[0] == keyword:
            return item
    return None

def find_all_sections(pddl_struct, keyword):
    found = []
    if not isinstance(pddl_struct, list): return found
    for item in pddl_struct:
        if isinstance(item, list) and len(item) > 0 and item[0] == keyword:
            found.append(item)
    return found

# --- RALSTP Analysis Logic ---

class RALSTPAnalyzer:
    def __init__(self, domain_path, problem_path):
        with open(domain_path, 'r') as f:
            self.domain_raw = clean_pddl(f.read())
        with open(problem_path, 'r') as f:
            self.problem_raw = clean_pddl(f.read())
            
        self.domain = parse_lisp_structure(self.domain_raw)
        self.problem = parse_lisp_structure(self.problem_raw)
        
        self.types = defaultdict(list) # parent -> children
        self.objects = {} # name -> type
        self.actions = []
        self.predicates = []
        
        # Analysis results
        self.dynamic_types = set()
        self.static_types = set()
        self.agents = set()
        self.passive_objects = set()
        self.entanglement_score = 0.0

    def parse_domain(self):
        # Types
        types_node = find_section(self.domain, ':types')
        if types_node:
            # Simplistic type parsing (a b - parent)
            current_objs = []
            for token in types_node[1:]:
                if token == '-':
                    continue
                elif isinstance(token, str) and not token.startswith(':'): # Parent coming next
                    current_objs.append(token)
                else:
                    # Check if previous was '-'
                    pass 
            # Re-parsing carefully for "a b - parent"
            iterator = iter(types_node[1:])
            buffer = []
            for token in iterator:
                if token == '-':
                    parent = next(iterator)
                    for child in buffer:
                        self.types[parent].append(child)
                    buffer = []
                else:
                    buffer.append(token)
                    
        # Actions
        actions_list = find_all_sections(self.domain, ':action')
        actions_list += find_all_sections(self.domain, ':durative-action')
        for a in actions_list:
            name = a[1]
            params = find_section(a, ':parameters')
            effects = find_section(a, ':effect')
            if not effects: effects = find_section(a, ':effects') # typo check
            
            self.actions.append({
                'name': name,
                'params': params,
                'effects': effects
            })

    def parse_problem(self):
        # Objects
        objs_node = find_section(self.problem, ':objects')
        if objs_node:
            iterator = iter(objs_node[1:])
            buffer = []
            for token in iterator:
                if token == '-':
                    type_name = next(iterator)
                    for obj in buffer:
                        self.objects[obj] = type_name
                    buffer = []
                else:
                    buffer.append(token)

    def identify_agents(self):
        """
        RALSTP Logic:
        1. Dynamic Types: Types that appear in effects (their state changes).
        2. Static Types: Types that NEVER appear in effects (only preconditions).
        3. Agents: Dynamic types that are usually the FIRST parameter of actions (Subjects).
        """
        
        # 1. Identify predicates modified in effects
        modified_predicates = set()
        for act in self.actions:
            eff = act['effects']
            # Flatten effect tree to find predicates (not perfect but heuristic)
            eff_str = str(eff)
            # Find words that look like predicates? Hard without full parsing.
            # Better: Scan action parameters and see which are used in effects.
            pass

        # Heuristic approach for Agents:
        # If an object type is the first parameter of multiple actions, it's likely an Agent.
        type_subject_score = defaultdict(int)
        
        for act in self.actions:
            params = act['params']
            if params and len(params) > 1: # (:parameters (?d - driver ?t - truck))
                # extracting (?name - type)
                # flattened list: ['?d', '-', 'driver', '?t', '-', 'truck']
                
                # Try to parse typed list
                args = []
                iterator = iter(params[1:])
                buffer = []
                for token in iterator:
                    if token == '-':
                        type_name = next(iterator)
                        for var in buffer:
                            args.append((var, type_name))
                        buffer = []
                    else:
                        buffer.append(token)
                
                if args:
                    # First arg is usually the agent
                    subject_type = args[0][1]
                    type_subject_score[subject_type] += 1
                    
                    # Check if it has 'driver', 'plane', 'truck' in name
                    if 'driver' in subject_type or 'truck' in subject_type or 'plane' in subject_type:
                        type_subject_score[subject_type] += 5

        # Classify
        sorted_types = sorted(type_subject_score.items(), key=lambda x: x[1], reverse=True)
        
        print("\n--- RALSTP Agent Identification ---")
        for t, score in sorted_types:
            if score > 0:
                self.agents.add(t)
                print(f"  [Agent Candidate] Type: {t} (Score: {score})")
            else:
                self.static_types.add(t)

        # Count instances
        total_agents = 0
        for obj, type_name in self.objects.items():
            if type_name in self.agents:
                total_agents += 1
                
        self.metrics = {
            'agent_types': list(self.agents),
            'total_agent_instances': total_agents,
            'total_objects': len(self.objects)
        }

    def calculate_difficulty(self):
        """
        Buksz Difficulty Metric ~ (Agents * Entanglement)
        Entanglement: How many agents share the same Static Resources?
        """
        # Simply: Ratio of Agents to Objects
        if self.metrics['total_objects'] > 0:
            ratio = self.metrics['total_agent_instances'] / self.metrics['total_objects']
        else:
            ratio = 0
            
        print(f"\n--- Difficulty Metrics ---")
        print(f"  Agent Density: {ratio:.2f}")
        print(f"  Total Agents: {self.metrics['total_agent_instances']}")
        
        complexity = "Low"
        if self.metrics['total_agent_instances'] > 5: complexity = "Medium"
        if self.metrics['total_agent_instances'] > 10: complexity = "High"
        if self.metrics['total_agent_instances'] > 20: complexity = "Extreme (Needs RALSTP)"
        
        print(f"  Estimated Complexity: {complexity}")
        
    def suggest_strategy(self):
        print(f"\n--- RALSTP Decomposition Strategy ---")
        if not self.agents:
            print("  No clear agents identified. Standard heuristic search recommended.")
            return

        print("  1. Strategic Phase:")
        print(f"     - Ignore local goals for {list(self.agents)[:2]}...")
        print("     - Solve for high-level resource movement first.")
        print("  2. Tactical Phase:")
        print("     - For each Agent group, solve their goals independently.")
        print("     - Merge plans ensuring no time overlaps on static resources.")

def main():
    parser = argparse.ArgumentParser(description="RALSTP Consultant")
    parser.add_argument("--domain", required=True, help="Path to domain.pddl")
    parser.add_argument("--problem", required=True, help="Path to problem.pddl")
    args = parser.parse_args()

    analyzer = RALSTPAnalyzer(args.domain, args.problem)
    analyzer.parse_domain()
    analyzer.parse_problem()
    analyzer.identify_agents()
    analyzer.calculate_difficulty()
    analyzer.suggest_strategy()

if __name__ == "__main__":
    main()
