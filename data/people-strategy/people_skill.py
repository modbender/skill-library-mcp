#!/usr/bin/env python3
"""
People-Strategy Agent Skill
A command-line agent for managing people relationships with graph database.
"""

import sys
import json
from typing import Optional
from database import PeopleDatabase


class PeopleAgent:
    """Agent for managing people and their relationships."""
    
    def __init__(self, db_path: str = "people.db"):
        """Initialize the people agent."""
        self.db = PeopleDatabase(db_path)
    
    # ========== PERSON OPERATIONS ==========
    
    def add_person(self, name: str, role: str = "", relation_to_me: str = "",
                   organization: str = "", character: str = "", notes: str = "") -> dict:
        """Add a new person."""
        person_id = self.db.add_person(name, role, relation_to_me, organization, character, notes)
        return {
            "success": True,
            "person_id": person_id,
            "message": f"Person '{name}' created with ID: {person_id}"
        }
    
    def get_person(self, person_id: int) -> dict:
        """Get a specific person."""
        person = self.db.get_person(person_id)
        if person:
            return {"success": True, "person": person}
        return {"success": False, "message": f"Person {person_id} not found"}
    
    def search_people(self, search_term: str) -> dict:
        """Search for people by name, role, or organization."""
        people = self.db.search_people(search_term)
        return {
            "success": True,
            "people": people,
            "count": len(people)
        }
    
    def list_people(self, organization: Optional[str] = None,
                   relation: Optional[str] = None) -> dict:
        """List all people or filter by organization/relation."""
        if organization:
            people = self.db.get_people_by_organization(organization)
        elif relation:
            people = self.db.get_people_by_relation(relation)
        else:
            people = self.db.get_all_people()
        
        return {"success": True, "people": people, "count": len(people)}
    
    def update_person(self, person_id: int, name: Optional[str] = None,
                     role: Optional[str] = None, relation_to_me: Optional[str] = None,
                     organization: Optional[str] = None, character: Optional[str] = None,
                     notes: Optional[str] = None) -> dict:
        """Update a person."""
        updated = self.db.update_person(person_id, name, role, relation_to_me,
                                       organization, character, notes)
        if updated:
            return {"success": True, "message": f"Person {person_id} updated"}
        return {"success": False, "message": f"Person {person_id} not found or no changes made"}
    
    def delete_person(self, person_id: int) -> dict:
        """Delete a person."""
        deleted = self.db.delete_person(person_id)
        if deleted:
            return {"success": True, "message": f"Person {person_id} deleted"}
        return {"success": False, "message": f"Person {person_id} not found"}
    
    # ========== EDGE/RELATIONSHIP OPERATIONS ==========
    
    def add_relationship(self, from_person_id: int, to_person_id: int,
                        relationship_type: str, description: str = "") -> dict:
        """Add a relationship between two people."""
        edge_id = self.db.add_edge(from_person_id, to_person_id, relationship_type, description)
        return {
            "success": True,
            "edge_id": edge_id,
            "message": f"Relationship created with ID: {edge_id}"
        }
    
    def get_relationships(self, person_id: int, direction: str = "all") -> dict:
        """Get relationships for a person."""
        if direction == "outgoing":
            edges = self.db.get_edges_from_person(person_id)
            return {"success": True, "relationships": edges, "count": len(edges)}
        elif direction == "incoming":
            edges = self.db.get_edges_to_person(person_id)
            return {"success": True, "relationships": edges, "count": len(edges)}
        else:
            edges = self.db.get_all_edges_for_person(person_id)
            total = len(edges["outgoing"]) + len(edges["incoming"])
            return {"success": True, "relationships": edges, "count": total}
    
    def list_all_relationships(self) -> dict:
        """List all relationships."""
        edges = self.db.get_all_edges()
        return {"success": True, "relationships": edges, "count": len(edges)}
    
    def update_relationship(self, edge_id: int, relationship_type: Optional[str] = None,
                          description: Optional[str] = None) -> dict:
        """Update a relationship."""
        updated = self.db.update_edge(edge_id, relationship_type, description)
        if updated:
            return {"success": True, "message": f"Relationship {edge_id} updated"}
        return {"success": False, "message": f"Relationship {edge_id} not found or no changes made"}
    
    def delete_relationship(self, edge_id: int) -> dict:
        """Delete a relationship."""
        deleted = self.db.delete_edge(edge_id)
        if deleted:
            return {"success": True, "message": f"Relationship {edge_id} deleted"}
        return {"success": False, "message": f"Relationship {edge_id} not found"}
    
    # ========== GRAPH OPERATIONS ==========
    
    def get_graph(self) -> dict:
        """Get the entire relationship graph."""
        graph = self.db.get_relationship_graph()
        return {
            "success": True,
            "graph": graph,
            "nodes_count": len(graph["nodes"]),
            "edges_count": len(graph["edges"])
        }
    
    def get_person_network(self, person_id: int) -> dict:
        """Get a person's complete network (connections and their details)."""
        person = self.db.get_person(person_id)
        if not person:
            return {"success": False, "message": f"Person {person_id} not found"}
        
        edges = self.db.get_all_edges_for_person(person_id)
        
        # Get all connected people
        connected_ids = set()
        for edge in edges["outgoing"]:
            connected_ids.add(edge["to_person_id"])
        for edge in edges["incoming"]:
            connected_ids.add(edge["from_person_id"])
        
        connected_people = [self.db.get_person(pid) for pid in connected_ids]
        
        return {
            "success": True,
            "person": person,
            "relationships": edges,
            "connected_people": connected_people,
            "connections_count": len(connected_people)
        }


def format_person(person: dict) -> str:
    """Format a person for display."""
    lines = [
        f"ID: {person['id']}",
        f"Name: {person['name']}",
    ]
    if person.get('role'):
        lines.append(f"Role: {person['role']}")
    if person.get('relation_to_me'):
        lines.append(f"Relation: {person['relation_to_me']}")
    if person.get('organization'):
        lines.append(f"Organization: {person['organization']}")
    if person.get('character'):
        lines.append(f"Character: {person['character']}")
    if person.get('notes'):
        lines.append(f"Notes: {person['notes']}")
    lines.append(f"Created: {person['created_at']}")
    return "\n".join(lines)


def format_edge(edge: dict) -> str:
    """Format an edge for display."""
    lines = [
        f"ID: {edge['id']}",
        f"From: {edge.get('from_person_name', edge['from_person_id'])} (ID: {edge['from_person_id']})",
        f"To: {edge.get('to_person_name', edge['to_person_id'])} (ID: {edge['to_person_id']})",
        f"Type: {edge['relationship_type']}",
    ]
    if edge.get('description'):
        lines.append(f"Description: {edge['description']}")
    lines.append(f"Created: {edge['created_at']}")
    return "\n".join(lines)


def main():
    """Main CLI handler."""
    if len(sys.argv) < 2:
        print("Usage: python people_skill.py <command> [args]")
        print("\nPerson Commands:")
        print("  add-person <name> [--role ROLE] [--relation RELATION] [--org ORG] [--character CHAR] [--notes NOTES]")
        print("  get-person <id>")
        print("  search <term>")
        print("  list-people [--org ORG] [--relation RELATION]")
        print("  update-person <id> [--name NAME] [--role ROLE] [--relation RELATION] [--org ORG] [--character CHAR] [--notes NOTES]")
        print("  delete-person <id>")
        print("\nRelationship Commands:")
        print("  add-relationship <from_id> <to_id> <type> [--description DESC]")
        print("  get-relationships <person_id> [--direction all|incoming|outgoing]")
        print("  list-relationships")
        print("  update-relationship <edge_id> [--type TYPE] [--description DESC]")
        print("  delete-relationship <edge_id>")
        print("\nGraph Commands:")
        print("  get-graph")
        print("  get-network <person_id>")
        sys.exit(1)
    
    agent = PeopleAgent()
    command = sys.argv[1]
    
    try:
        # Person commands
        if command == "add-person":
            if len(sys.argv) < 3:
                print("Error: Name required")
                sys.exit(1)
            
            name = sys.argv[2]
            role = ""
            relation = ""
            org = ""
            character = ""
            notes = ""
            
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--role" and i + 1 < len(sys.argv):
                    role = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--relation" and i + 1 < len(sys.argv):
                    relation = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--org" and i + 1 < len(sys.argv):
                    org = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--character" and i + 1 < len(sys.argv):
                    character = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--notes" and i + 1 < len(sys.argv):
                    notes = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            result = agent.add_person(name, role, relation, org, character, notes)
            print(result["message"])
        
        elif command == "get-person":
            if len(sys.argv) < 3:
                print("Error: Person ID required")
                sys.exit(1)
            
            person_id = int(sys.argv[2])
            result = agent.get_person(person_id)
            if result["success"]:
                print(format_person(result["person"]))
            else:
                print(result["message"])
        
        elif command == "search":
            if len(sys.argv) < 3:
                print("Error: Search term required")
                sys.exit(1)
            
            search_term = sys.argv[2]
            result = agent.search_people(search_term)
            print(f"Found {result['count']} people:\n")
            for person in result["people"]:
                print(format_person(person))
                print("-" * 50)
        
        elif command == "list-people":
            org = None
            relation = None
            
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == "--org" and i + 1 < len(sys.argv):
                    org = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--relation" and i + 1 < len(sys.argv):
                    relation = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            result = agent.list_people(org, relation)
            print(f"Total: {result['count']} people\n")
            for person in result["people"]:
                print(format_person(person))
                print("-" * 50)
        
        elif command == "update-person":
            if len(sys.argv) < 3:
                print("Error: Person ID required")
                sys.exit(1)
            
            person_id = int(sys.argv[2])
            name = None
            role = None
            relation = None
            org = None
            character = None
            notes = None
            
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--name" and i + 1 < len(sys.argv):
                    name = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--role" and i + 1 < len(sys.argv):
                    role = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--relation" and i + 1 < len(sys.argv):
                    relation = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--org" and i + 1 < len(sys.argv):
                    org = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--character" and i + 1 < len(sys.argv):
                    character = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--notes" and i + 1 < len(sys.argv):
                    notes = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            result = agent.update_person(person_id, name, role, relation, org, character, notes)
            print(result["message"])
        
        elif command == "delete-person":
            if len(sys.argv) < 3:
                print("Error: Person ID required")
                sys.exit(1)
            
            person_id = int(sys.argv[2])
            result = agent.delete_person(person_id)
            print(result["message"])
        
        # Relationship commands
        elif command == "add-relationship":
            if len(sys.argv) < 5:
                print("Error: from_id, to_id, and type required")
                sys.exit(1)
            
            from_id = int(sys.argv[2])
            to_id = int(sys.argv[3])
            rel_type = sys.argv[4]
            description = ""
            
            if len(sys.argv) > 5 and sys.argv[5] == "--description":
                description = sys.argv[6] if len(sys.argv) > 6 else ""
            
            result = agent.add_relationship(from_id, to_id, rel_type, description)
            print(result["message"])
        
        elif command == "get-relationships":
            if len(sys.argv) < 3:
                print("Error: Person ID required")
                sys.exit(1)
            
            person_id = int(sys.argv[2])
            direction = "all"
            
            if len(sys.argv) > 3 and sys.argv[3] == "--direction":
                direction = sys.argv[4] if len(sys.argv) > 4 else "all"
            
            result = agent.get_relationships(person_id, direction)
            if result["success"]:
                print(f"Total: {result['count']} relationships\n")
                if direction == "all":
                    print("OUTGOING:")
                    for edge in result["relationships"]["outgoing"]:
                        print(format_edge(edge))
                        print("-" * 50)
                    print("\nINCOMING:")
                    for edge in result["relationships"]["incoming"]:
                        print(format_edge(edge))
                        print("-" * 50)
                else:
                    for edge in result["relationships"]:
                        print(format_edge(edge))
                        print("-" * 50)
        
        elif command == "list-relationships":
            result = agent.list_all_relationships()
            print(f"Total: {result['count']} relationships\n")
            for edge in result["relationships"]:
                print(format_edge(edge))
                print("-" * 50)
        
        elif command == "update-relationship":
            if len(sys.argv) < 3:
                print("Error: Edge ID required")
                sys.exit(1)
            
            edge_id = int(sys.argv[2])
            rel_type = None
            description = None
            
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                    rel_type = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--description" and i + 1 < len(sys.argv):
                    description = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            result = agent.update_relationship(edge_id, rel_type, description)
            print(result["message"])
        
        elif command == "delete-relationship":
            if len(sys.argv) < 3:
                print("Error: Edge ID required")
                sys.exit(1)
            
            edge_id = int(sys.argv[2])
            result = agent.delete_relationship(edge_id)
            print(result["message"])
        
        # Graph commands
        elif command == "get-graph":
            result = agent.get_graph()
            print(f"Graph: {result['nodes_count']} people, {result['edges_count']} relationships")
            print("\nJSON Output:")
            print(json.dumps(result["graph"], indent=2))
        
        elif command == "get-network":
            if len(sys.argv) < 3:
                print("Error: Person ID required")
                sys.exit(1)
            
            person_id = int(sys.argv[2])
            result = agent.get_person_network(person_id)
            if result["success"]:
                print("PERSON:")
                print(format_person(result["person"]))
                print("\n" + "=" * 50 + "\n")
                print(f"NETWORK: {result['connections_count']} connections\n")
                
                print("CONNECTED PEOPLE:")
                for person in result["connected_people"]:
                    print(format_person(person))
                    print("-" * 50)
                
                print("\nRELATIONSHIPS:")
                print("\nOutgoing:")
                for edge in result["relationships"]["outgoing"]:
                    print(format_edge(edge))
                    print("-" * 50)
                print("\nIncoming:")
                for edge in result["relationships"]["incoming"]:
                    print(format_edge(edge))
                    print("-" * 50)
            else:
                print(result["message"])
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
