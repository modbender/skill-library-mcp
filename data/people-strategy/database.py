import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os


class PeopleDatabase:
    """Database handler for people-strategy agent skill."""
    
    def __init__(self, db_path: str = "people.db"):
        """Initialize the database connection."""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
    
    def _create_tables(self):
        """Create the people and edges tables if they don't exist."""
        # Create people table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT,
                relation_to_me TEXT,
                organization TEXT,
                character TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create edges table for relationships between people
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_person_id INTEGER NOT NULL,
                to_person_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_person_id) REFERENCES people (id) ON DELETE CASCADE,
                FOREIGN KEY (to_person_id) REFERENCES people (id) ON DELETE CASCADE,
                UNIQUE(from_person_id, to_person_id, relationship_type)
            )
        """)
        
        # Create index for faster lookups
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_people_name ON people(name)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_person_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_person_id)
        """)
        
        self.connection.commit()
    
    # ========== PERSON OPERATIONS ==========
    
    def add_person(self, name: str, role: str = "", relation_to_me: str = "",
                   organization: str = "", character: str = "", notes: str = "") -> int:
        """
        Add a new person to the database.
        
        Args:
            name: Person's name
            role: Their role/position
            relation_to_me: How they relate to me
            organization: Their organization
            character: Character traits/description
            notes: Additional notes
        
        Returns:
            The ID of the newly created person
        """
        self.cursor.execute("""
            INSERT INTO people (name, role, relation_to_me, organization, character, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, role, relation_to_me, organization, character, notes))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_person(self, person_id: int) -> Optional[Dict]:
        """Get a person by ID."""
        self.cursor.execute("SELECT * FROM people WHERE id = ?", (person_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_person_by_name(self, name: str) -> Optional[Dict]:
        """Get a person by name (case-insensitive)."""
        self.cursor.execute("SELECT * FROM people WHERE LOWER(name) = LOWER(?)", (name,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def search_people(self, search_term: str) -> List[Dict]:
        """Search people by name, role, or organization."""
        search_pattern = f"%{search_term}%"
        self.cursor.execute("""
            SELECT * FROM people 
            WHERE LOWER(name) LIKE LOWER(?) 
               OR LOWER(role) LIKE LOWER(?)
               OR LOWER(organization) LIKE LOWER(?)
            ORDER BY name
        """, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_people(self) -> List[Dict]:
        """Get all people."""
        self.cursor.execute("SELECT * FROM people ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_people_by_organization(self, organization: str) -> List[Dict]:
        """Get all people from a specific organization."""
        self.cursor.execute("""
            SELECT * FROM people 
            WHERE LOWER(organization) = LOWER(?)
            ORDER BY name
        """, (organization,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_people_by_relation(self, relation: str) -> List[Dict]:
        """Get all people with a specific relation to me."""
        self.cursor.execute("""
            SELECT * FROM people 
            WHERE LOWER(relation_to_me) = LOWER(?)
            ORDER BY name
        """, (relation,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_person(self, person_id: int, name: Optional[str] = None,
                     role: Optional[str] = None, relation_to_me: Optional[str] = None,
                     organization: Optional[str] = None, character: Optional[str] = None,
                     notes: Optional[str] = None) -> bool:
        """
        Update a person's information.
        
        Returns:
            True if the person was updated, False otherwise
        """
        fields = []
        values = []
        
        if name is not None:
            fields.append("name = ?")
            values.append(name)
        if role is not None:
            fields.append("role = ?")
            values.append(role)
        if relation_to_me is not None:
            fields.append("relation_to_me = ?")
            values.append(relation_to_me)
        if organization is not None:
            fields.append("organization = ?")
            values.append(organization)
        if character is not None:
            fields.append("character = ?")
            values.append(character)
        if notes is not None:
            fields.append("notes = ?")
            values.append(notes)
        
        if not fields:
            return False
        
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(person_id)
        
        query = f"UPDATE people SET {', '.join(fields)} WHERE id = ?"
        self.cursor.execute(query, values)
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def delete_person(self, person_id: int) -> bool:
        """
        Delete a person from the database.
        
        Returns:
            True if the person was deleted, False otherwise
        """
        self.cursor.execute("DELETE FROM people WHERE id = ?", (person_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    # ========== EDGE/RELATIONSHIP OPERATIONS ==========
    
    def add_edge(self, from_person_id: int, to_person_id: int,
                 relationship_type: str, description: str = "") -> int:
        """
        Add a relationship edge between two people.
        
        Args:
            from_person_id: ID of the first person
            to_person_id: ID of the second person
            relationship_type: Type of relationship (e.g., 'reports_to', 'works_with', 'mentors')
            description: Additional description of the relationship
        
        Returns:
            The ID of the newly created edge
        """
        self.cursor.execute("""
            INSERT OR REPLACE INTO edges (from_person_id, to_person_id, relationship_type, description)
            VALUES (?, ?, ?, ?)
        """, (from_person_id, to_person_id, relationship_type, description))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_edge(self, edge_id: int) -> Optional[Dict]:
        """Get an edge by ID."""
        self.cursor.execute("SELECT * FROM edges WHERE id = ?", (edge_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_edges_from_person(self, person_id: int) -> List[Dict]:
        """Get all edges originating from a person."""
        self.cursor.execute("""
            SELECT e.*, p.name as to_person_name
            FROM edges e
            JOIN people p ON e.to_person_id = p.id
            WHERE e.from_person_id = ?
            ORDER BY e.relationship_type, p.name
        """, (person_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_edges_to_person(self, person_id: int) -> List[Dict]:
        """Get all edges pointing to a person."""
        self.cursor.execute("""
            SELECT e.*, p.name as from_person_name
            FROM edges e
            JOIN people p ON e.from_person_id = p.id
            WHERE e.to_person_id = ?
            ORDER BY e.relationship_type, p.name
        """, (person_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_edges_for_person(self, person_id: int) -> Dict[str, List[Dict]]:
        """Get all edges (both incoming and outgoing) for a person."""
        return {
            "outgoing": self.get_edges_from_person(person_id),
            "incoming": self.get_edges_to_person(person_id)
        }
    
    def get_all_edges(self) -> List[Dict]:
        """Get all edges with person names."""
        self.cursor.execute("""
            SELECT e.*, 
                   p1.name as from_person_name,
                   p2.name as to_person_name
            FROM edges e
            JOIN people p1 ON e.from_person_id = p1.id
            JOIN people p2 ON e.to_person_id = p2.id
            ORDER BY p1.name, p2.name
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_edge(self, edge_id: int, relationship_type: Optional[str] = None,
                   description: Optional[str] = None) -> bool:
        """
        Update an edge's information.
        
        Returns:
            True if the edge was updated, False otherwise
        """
        fields = []
        values = []
        
        if relationship_type is not None:
            fields.append("relationship_type = ?")
            values.append(relationship_type)
        if description is not None:
            fields.append("description = ?")
            values.append(description)
        
        if not fields:
            return False
        
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(edge_id)
        
        query = f"UPDATE edges SET {', '.join(fields)} WHERE id = ?"
        self.cursor.execute(query, values)
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def delete_edge(self, edge_id: int) -> bool:
        """
        Delete an edge from the database.
        
        Returns:
            True if the edge was deleted, False otherwise
        """
        self.cursor.execute("DELETE FROM edges WHERE id = ?", (edge_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def get_relationship_graph(self) -> Dict:
        """
        Get the entire relationship graph.
        
        Returns:
            Dict with 'nodes' (people) and 'edges' (relationships)
        """
        return {
            "nodes": self.get_all_people(),
            "edges": self.get_all_edges()
        }
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
