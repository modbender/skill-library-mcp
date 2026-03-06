#!/usr/bin/env python3
"""
Obsidian-Ontology Sync Script

Extracts entities and relationships from Obsidian markdown files
and maintains a structured ontology graph.
"""

import os
import re
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class ObsidianOntologySync:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.load_config(config_path)
        self.vault_path = Path(self.config['obsidian']['vault_path'])
        self.ontology_path = Path(self.config['ontology']['storage_path'])
        self.ontology_path.mkdir(parents=True, exist_ok=True)
        
        self.graph_file = self.ontology_path / 'graph.jsonl'
        self.entities = {}
        self.relations = []
        
    def load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration file"""
        if config_path is None:
            # Try default locations
            possible_paths = [
                '/root/life/pkm/ontology-sync/config.yaml',
                '/root/.openclaw/workspace/skills/obsidian-ontology-sync/config.yaml',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                return yaml.safe_load(f)
        else:
            # Return default config
            return {
                'obsidian': {
                    'vault_path': '/root/life/pkm',
                    'sources': {
                        'contacts': {
                            'path': 'references/contacts',
                            'entity_type': 'Person'
                        },
                        'clients': {
                            'path': 'references/clients',
                            'entity_type': 'Organization'
                        },
                        'team': {
                            'path': 'references/team',
                            'entity_type': 'Person'
                        },
                        'daily_status': {
                            'path': 'daily-status',
                            'extract': ['response_times', 'behavioral_patterns']
                        }
                    }
                },
                'ontology': {
                    'storage_path': '/root/life/pkm/memory/ontology',
                    'format': 'jsonl'
                }
            }
    
    def extract(self, dry_run=False, verbose=False):
        """Extract entities from Obsidian notes"""
        print(f"🔍 Extracting entities from {self.vault_path}")
        
        sources = self.config['obsidian']['sources']
        
        # Extract from each source
        for source_name, source_config in sources.items():
            source_path = self.vault_path / source_config['path']
            if not source_path.exists():
                if verbose:
                    print(f"  ⚠️  {source_name}: path not found - {source_path}")
                continue
            
            print(f"\n📂 Processing {source_name} ({source_path})")
            
            # Find all markdown files
            md_files = list(source_path.rglob('*.md'))
            print(f"  Found {len(md_files)} files")
            
            for md_file in md_files:
                try:
                    self.extract_from_file(md_file, source_config, verbose)
                except Exception as e:
                    if verbose:
                        print(f"  ❌ Error in {md_file.name}: {e}")
        
        # Write to ontology
        if not dry_run:
            self.write_ontology()
            print(f"\n✅ Extracted {len(self.entities)} entities, {len(self.relations)} relations")
        else:
            print(f"\n🔍 DRY RUN: Would extract {len(self.entities)} entities, {len(self.relations)} relations")
    
    def extract_from_file(self, file_path: Path, source_config: Dict, verbose: bool):
        """Extract entity from a single file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        entity_type = source_config.get('entity_type', 'Unknown')
        
        # Extract title (first H1 or filename)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = title_match.group(1) if title_match else file_path.stem
        
        # Generate ID
        entity_id = self.generate_id(entity_type, name)
        
        # Extract properties
        properties = {
            'name': name,
            'source_file': str(file_path.relative_to(self.vault_path))
        }
        
        # Extract email
        email_match = re.search(r'\*\*Email:\*\*\s+([^\s\n]+)', content)
        if email_match:
            properties['email'] = email_match.group(1)
        
        # Extract phone
        phone_match = re.search(r'\*\*Phone:\*\*\s+([^\s\n]+)', content)
        if phone_match:
            properties['phone'] = phone_match.group(1)
        
        # Extract company/organization
        company_match = re.search(r'\*\*Company:\*\*\s+(.+)', content)
        if company_match:
            company_name = company_match.group(1).strip()
            company_id = self.generate_id('Organization', company_name)
            
            # Create organization entity if not exists
            if company_id not in self.entities:
                self.entities[company_id] = {
                    'id': company_id,
                    'type': 'Organization',
                    'properties': {'name': company_name}
                }
            
            # Create works_at relation
            self.relations.append({
                'from': entity_id,
                'rel': 'works_at',
                'to': company_id
            })
        
        # Extract projects from links
        project_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in project_links:
            if 'project' in link.lower() or any(proj in link for proj in ['ValueChain', 'BytePlus', 'Benow', 'Wirerr']):
                project_id = self.generate_id('Project', link)
                
                # Create project entity if not exists
                if project_id not in self.entities:
                    self.entities[project_id] = {
                        'id': project_id,
                        'type': 'Project',
                        'properties': {'name': link}
                    }
                
                # Create assigned_to relation
                self.relations.append({
                    'from': entity_id,
                    'rel': 'assigned_to',
                    'to': project_id
                })
        
        # Add entity
        self.entities[entity_id] = {
            'id': entity_id,
            'type': entity_type,
            'properties': properties,
            'updated': datetime.now().isoformat()
        }
        
        if verbose:
            print(f"  ✓ {name} ({entity_type})")
    
    def generate_id(self, entity_type: str, name: str) -> str:
        """Generate consistent entity ID"""
        # Normalize name: lowercase, replace spaces/special chars
        normalized = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
        return f"{entity_type.lower()}_{normalized}"
    
    def write_ontology(self):
        """Write entities and relations to ontology file"""
        with open(self.graph_file, 'a') as f:
            # Write entities
            for entity in self.entities.values():
                f.write(json.dumps({
                    'op': 'upsert',
                    'entity': entity
                }) + '\n')
            
            # Write relations
            for relation in self.relations:
                f.write(json.dumps({
                    'op': 'relate',
                    **relation
                }) + '\n')
        
        print(f"📝 Wrote to {self.graph_file}")
    
    def analyze(self):
        """Run analytics on the ontology"""
        print("📊 Running analysis...")
        
        # Load current ontology
        entities, relations = self.load_ontology()
        
        print(f"\n📈 Statistics:")
        print(f"  Total entities: {len(entities)}")
        
        # Count by type
        by_type = {}
        for entity in entities.values():
            etype = entity.get('type', 'Unknown')
            by_type[etype] = by_type.get(etype, 0) + 1
        
        for etype, count in sorted(by_type.items()):
            print(f"    {etype}: {count}")
        
        print(f"\n  Total relations: {len(relations)}")
        
        # Count by relation type
        by_rel = {}
        for rel in relations:
            rtype = rel.get('rel', 'unknown')
            by_rel[rtype] = by_rel.get(rtype, 0) + 1
        
        for rtype, count in sorted(by_rel.items()):
            print(f"    {rtype}: {count}")
        
        # Find issues
        print(f"\n⚠️  Issues found:")
        
        # People without email
        no_email = [e for e in entities.values() 
                    if e.get('type') == 'Person' and not e.get('properties', {}).get('email')]
        if no_email:
            print(f"  {len(no_email)} people without email")
        
        # Orphaned entities (no relations)
        entity_ids_in_rels = set()
        for rel in relations:
            entity_ids_in_rels.add(rel.get('from'))
            entity_ids_in_rels.add(rel.get('to'))
        
        orphaned = [e for e in entities.values() if e.get('id') not in entity_ids_in_rels]
        if orphaned:
            print(f"  {len(orphaned)} orphaned entities (no relations)")
    
    def feedback(self):
        """Generate feedback for improving PKM"""
        print("💡 Generating feedback...")
        
        entities, relations = self.load_ontology()
        
        feedback_path = self.vault_path / 'ontology-sync' / 'feedback'
        feedback_path.mkdir(parents=True, exist_ok=True)
        
        feedback_file = feedback_path / f'feedback-{datetime.now().strftime("%Y-%m-%d")}.md'
        
        with open(feedback_file, 'w') as f:
            f.write(f"# Ontology Sync Feedback - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            
            # Missing information
            f.write("## Missing Information\n\n")
            no_email = [e for e in entities.values() 
                        if e.get('type') == 'Person' and not e.get('properties', {}).get('email')]
            for entity in no_email[:10]:  # Top 10
                name = entity['properties'].get('name', 'Unknown')
                source = entity['properties'].get('source_file', '')
                f.write(f"- [ ] `{name}` missing email (`{source}`)\n")
            
            f.write("\n## Relationship Insights\n\n")
            # Group people by organization
            org_people = {}
            for rel in relations:
                if rel.get('rel') == 'works_at':
                    org_id = rel.get('to')
                    if org_id not in org_people:
                        org_people[org_id] = []
                    org_people[org_id].append(rel.get('from'))
            
            for org_id, people_ids in org_people.items():
                if len(people_ids) > 1:
                    org = entities.get(org_id, {})
                    org_name = org.get('properties', {}).get('name', org_id)
                    f.write(f"- **{org_name}** has {len(people_ids)} contacts\n")
        
        print(f"✅ Feedback written to {feedback_file}")
    
    def load_ontology(self):
        """Load ontology from file"""
        entities = {}
        relations = []
        
        if not self.graph_file.exists():
            return entities, relations
        
        with open(self.graph_file) as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                    op = record.get('op')
                    
                    if op in ('create', 'upsert'):
                        entity = record.get('entity', {})
                        entities[entity['id']] = entity
                    
                    elif op == 'relate':
                        relations.append({
                            'from': record.get('from'),
                            'rel': record.get('rel'),
                            'to': record.get('to')
                        })
                except json.JSONDecodeError:
                    pass
        
        return entities, relations


def main():
    parser = argparse.ArgumentParser(description='Obsidian-Ontology Sync')
    parser.add_argument('action', choices=['extract', 'analyze', 'feedback'],
                       help='Action to perform')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t write)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    sync = ObsidianOntologySync(args.config)
    
    if args.action == 'extract':
        sync.extract(dry_run=args.dry_run, verbose=args.verbose)
    elif args.action == 'analyze':
        sync.analyze()
    elif args.action == 'feedback':
        sync.feedback()


if __name__ == '__main__':
    main()
