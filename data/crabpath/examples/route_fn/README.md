## Route function for traversal

`traverse()` accepts an optional `route_fn` callback to filter habitual-edge choices.

Signature:

```python
RouteFn = Callable[[str | None, list[Edge], str], list[str]]
# (source_node_id, candidate_edges, query_text) -> selected_target_node_ids
```

### Deterministic routing

```python
from crabpath import Graph, Node, Edge, traverse, TraversalConfig

graph = Graph()
graph.add_node(Node("root", "root"))
graph.add_node(Node("preferred", "preferred"))
graph.add_node(Node("other", "other"))
graph.add_edge(Edge("root", "preferred", 0.45))
graph.add_edge(Edge("root", "other", 0.45))

def deterministic_route(source_id, edges, context):
    if source_id != "root":
        return []
    return ["preferred"]

result = traverse(
    graph=graph,
    seeds=[("root", 1.0)],
    config=TraversalConfig(max_hops=1),
    route_fn=deterministic_route,
    query_text="root",
)
print(result.fired)
```

### LLM stub routing

```python
def llm_route_stub(source_id, edges, context):
    if "bad" in context:
        return []
    ranked = sorted(edges, key=lambda edge: edge.weight, reverse=True)
    return [ranked[0].target] if ranked else []

result = traverse(
    graph=graph,
    seeds=[("root", 1.0)],
    config=TraversalConfig(max_hops=2),
    route_fn=llm_route_stub,
    query_text="show the best next chunk",
)
print(result.fired)
```
