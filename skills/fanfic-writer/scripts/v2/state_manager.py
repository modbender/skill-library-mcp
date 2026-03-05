"""
Fanfic Writer v2.0 - State Manager
Manages all state panels with evidence-based updates and confidence scoring
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict

from .atomic_io import atomic_write_json, atomic_append_jsonl
from .utils import get_timestamp_iso


# ============================================================================
# Evidence Chain Data Structure
# ============================================================================

@dataclass
class Evidence:
    """Evidence for a state change"""
    chapter: str  # e.g., "第015章"
    snippet: str  # Text snippet as evidence
    confidence: float  # 0.0 - 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'evidence_chapter': self.chapter,
            'evidence_snippet': self.snippet,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Evidence':
        return cls(
            chapter=data.get('evidence_chapter', ''),
            snippet=data.get('evidence_snippet', ''),
            confidence=data.get('confidence', 0.0)
        )


@dataclass
class StateEntry:
    """A single state entry with value, metadata, and evidence"""
    value: Any
    evidence_chapter: str
    evidence_snippet: str
    confidence: float
    update_timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'evidence_chapter': self.evidence_chapter,
            'evidence_snippet': self.evidence_snippet,
            'confidence': self.confidence,
            'update_timestamp': self.update_timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateEntry':
        return cls(
            value=data.get('value'),
            evidence_chapter=data.get('evidence_chapter', ''),
            evidence_snippet=data.get('evidence_snippet', ''),
            confidence=data.get('confidence', 0.0),
            update_timestamp=data.get('update_timestamp', get_timestamp_iso())
        )


# ============================================================================
# Base State Panel
# ============================================================================

class StatePanel:
    """
    Base class for all state panels
    Implements evidence-based updates with confidence scoring
    """
    
    CONFIDENCE_THRESHOLD = 0.7  # Below this goes to pending_changes
    
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self._data: Optional[Dict[str, Any]] = None
        self._pending_changes: List[Dict[str, Any]] = []
    
    def load(self) -> Dict[str, Any]:
        """Load state from file"""
        if self._data is not None:
            return self._data
        
        if not self.file_path.exists():
            self._data = self._create_default()
            self.save()
        else:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        
        return self._data
    
    def save(self) -> bool:
        """Save state to file atomically"""
        if self._data is None:
            return False
        return atomic_write_json(self.file_path, self._data)
    
    def _create_default(self) -> Dict[str, Any]:
        """Create default empty state - override in subclasses"""
        return {
            'entities': {},
            'pending_changes': [],
            'last_updated': get_timestamp_iso()
        }
    
    def update_entity(
        self,
        entity_name: str,
        field: str,
        value: Any,
        evidence: Evidence
    ) -> bool:
        """
        Update entity field with evidence
        
        If confidence < 0.7, goes to pending_changes instead of active_state
        """
        data = self.load()
        
        # Ensure entity exists
        if 'entities' not in data:
            data['entities'] = {}
        
        if entity_name not in data['entities']:
            data['entities'][entity_name] = {'values': {}, 'meta': {}}
        
        # Check confidence threshold
        if evidence.confidence < self.CONFIDENCE_THRESHOLD:
            # Add to pending_changes
            if 'pending_changes' not in data:
                data['pending_changes'] = []
            
            data['pending_changes'].append({
                'entity': entity_name,
                'field': field,
                'proposed_value': value,
                'evidence_chapter': evidence.chapter,
                'evidence_snippet': evidence.snippet,
                'confidence': evidence.confidence,
                'timestamp': get_timestamp_iso()
            })
        else:
            # Update active state
            entity = data['entities'][entity_name]
            entity['values'][field] = value
            entity['meta'][field] = {
                'evidence_chapter': evidence.chapter,
                'evidence_snippet': evidence.snippet,
                'confidence': evidence.confidence,
                'update_timestamp': get_timestamp_iso()
            }
        
        data['last_updated'] = get_timestamp_iso()
        return self.save()
    
    def get_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Get entity with all its values and metadata"""
        data = self.load()
        return data.get('entities', {}).get(entity_name)
    
    def get_value(self, entity_name: str, field: str) -> Any:
        """Get specific field value for entity"""
        entity = self.get_entity(entity_name)
        if entity:
            return entity.get('values', {}).get(field)
        return None
    
    def get_pending_changes(self) -> List[Dict[str, Any]]:
        """Get list of pending changes waiting for review"""
        data = self.load()
        return data.get('pending_changes', [])
    
    def confirm_pending_change(self, change_id: int) -> bool:
        """
        Confirm a pending change and move it to active state
        
        Args:
            change_id: Index in pending_changes list
        """
        data = self.load()
        pending = data.get('pending_changes', [])
        
        if change_id < 0 or change_id >= len(pending):
            return False
        
        change = pending[change_id]
        
        # Move to active state with boosted confidence
        entity_name = change['entity']
        field = change['field']
        value = change['proposed_value']
        
        if 'entities' not in data:
            data['entities'] = {}
        if entity_name not in data['entities']:
            data['entities'][entity_name] = {'values': {}, 'meta': {}}
        
        entity = data['entities'][entity_name]
        entity['values'][field] = value
        entity['meta'][field] = {
            'evidence_chapter': change['evidence_chapter'],
            'evidence_snippet': change['evidence_snippet'],
            'confidence': 0.85,  # Boosted confidence on manual confirm
            'update_timestamp': get_timestamp_iso()
        }
        
        # Remove from pending
        data['pending_changes'].pop(change_id)
        
        return self.save()
    
    def reject_pending_change(self, change_id: int) -> bool:
        """Reject and remove a pending change"""
        data = self.load()
        pending = data.get('pending_changes', [])
        
        if change_id < 0 or change_id >= len(pending):
            return False
        
        pending.pop(change_id)
        return self.save()
    
    def list_entities(self) -> List[str]:
        """List all entity names"""
        data = self.load()
        return list(data.get('entities', {}).keys())


# ============================================================================
# Specialized State Panels
# ============================================================================

class CharactersPanel(StatePanel):
    """Character state panel: motivation, status, injuries, relationships"""
    
    def _create_default(self) -> Dict[str, Any]:
        return {
            'entities': {},  # character_name -> {values, meta}
            'pending_changes': [],
            'last_updated': get_timestamp_iso(),
            'panel_type': 'characters'
        }
    
    def update_character_status(
        self,
        character_name: str,
        status: str,  # 健康|轻伤|重伤|死亡
        evidence: Evidence
    ) -> bool:
        """Update character health status"""
        return self.update_entity(character_name, 'status', status, evidence)
    
    def add_injury(
        self,
        character_name: str,
        injury_type: str,
        chapter: int,
        evidence: Evidence
    ) -> bool:
        """Add injury to character"""
        data = self.load()
        
        if 'entities' not in data:
            data['entities'] = {}
        if character_name not in data['entities']:
            data['entities'][character_name] = {'values': {}, 'meta': {}}
        
        entity = data['entities'][character_name]
        
        # Initialize injuries list if needed
        if 'injuries' not in entity['values']:
            entity['values']['injuries'] = []
        
        injury = {
            'type': injury_type,
            'chapter': chapter,
            'healed': False
        }
        
        entity['values']['injuries'].append(injury)
        entity['meta']['injuries'] = evidence.to_dict()
        
        data['last_updated'] = get_timestamp_iso()
        return self.save()
    
    def update_relationship(
        self,
        character_name: str,
        target_character: str,
        score: int,  # -5 to +5
        evidence: Evidence
    ) -> bool:
        """Update relationship score between characters"""
        data = self.load()
        
        if 'entities' not in data:
            data['entities'] = {}
        if character_name not in data['entities']:
            data['entities'][character_name] = {'values': {}, 'meta': {}}
        
        entity = data['entities'][character_name]
        
        if 'relationships' not in entity['values']:
            entity['values']['relationships'] = {}
        
        entity['values']['relationships'][target_character] = max(-5, min(5, score))
        
        rel_key = f'relationship_{target_character}'
        entity['meta'][rel_key] = evidence.to_dict()
        
        data['last_updated'] = get_timestamp_iso()
        return self.save()


class PlotThreadsPanel(StatePanel):
    """Plot thread panel:伏笔/线索状态跟踪"""
    
    def _create_default(self) -> Dict[str, Any]:
        return {
            'entities': {},  # thread_name -> thread_data
            'pending_changes': [],
            'last_updated': get_timestamp_iso(),
            'panel_type': 'plot_threads'
        }
    
    def add_thread(
        self,
        thread_name: str,
        introduced_chapter: int,
        promised_payoff: str,
        urgency: str = 'pending',  # immediate|pending|background
        evidence: Optional[Evidence] = None
    ) -> bool:
        """Add a new plot thread (伏笔)"""
        if evidence is None:
            evidence = Evidence(
                chapter=f"第{introduced_chapter:03d}章",
                snippet="初始设定",
                confidence=0.9
            )
        
        data = self.load()
        
        data['entities'][thread_name] = {
            'values': {
                'status': 'active',
                'introduced_chapter': introduced_chapter,
                'promised_payoff': promised_payoff,
                'urgency': urgency
            },
            'meta': evidence.to_dict()
        }
        
        data['last_updated'] = get_timestamp_iso()
        return self.save()
    
    def resolve_thread(
        self,
        thread_name: str,
        resolved_chapter: int,
        resolution_summary: str,
        evidence: Evidence
    ) -> bool:
        """Mark a thread as resolved"""
        return self.update_entity(
            thread_name,
            'status',
            'resolved',
            evidence
        )
    
    def drop_thread(
        self,
        thread_name: str,
        reason: str,
        evidence: Evidence
    ) -> bool:
        """Mark a thread as dropped (废弃伏笔)"""
        data = self.load()
        
        if thread_name in data.get('entities', {}):
            data['entities'][thread_name]['values']['status'] = 'dropped'
            data['entities'][thread_name]['values']['drop_reason'] = reason
            data['last_updated'] = get_timestamp_iso()
            return self.save()
        
        return False
    
    def get_active_threads(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) threads"""
        data = self.load()
        active = []
        
        for name, entity in data.get('entities', {}).items():
            if entity.get('values', {}).get('status') == 'active':
                active.append({
                    'name': name,
                    **entity['values'],
                    **entity['meta']
                })
        
        return active
    
    def get_resolution_ratio(self) -> float:
        """Get ratio of resolved threads (for ending check)"""
        data = self.load()
        entities = data.get('entities', {})
        
        if not entities:
            return 1.0  # No threads = all resolved
        
        resolved = sum(1 for e in entities.values() if e.get('values', {}).get('status') == 'resolved')
        return resolved / len(entities)


class TimelinePanel(StatePanel):
    """Timeline panel: 故事内时间线管理"""
    
    def _create_default(self) -> Dict[str, Any]:
        return {
            'current_date': '第1天',
            'total_days_passed': 0,
            'events': [],
            'last_updated': get_timestamp_iso(),
            'panel_type': 'timeline'
        }
    
    def add_event(
        self,
        chapter: int,
        event_description: str,
        day_offset: int = 0,  # 0 = same day, 1 = next day, etc.
        evidence: Optional[Evidence] = None
    ) -> bool:
        """Add event to timeline"""
        data = self.load()
        
        # Update current date
        data['total_days_passed'] += day_offset
        data['current_date'] = f"第{data['total_days_passed'] + 1}天"
        
        # Add event
        event = {
            'chapter': chapter,
            'day_offset': day_offset,
            'event': event_description,
            'story_day': data['total_days_passed'] + 1
        }
        
        if evidence:
            event.update(evidence.to_dict())
        
        data['events'].append(event)
        data['last_updated'] = get_timestamp_iso()
        
        return self.save()
    
    def get_current_day(self) -> int:
        """Get current story day"""
        data = self.load()
        return data.get('total_days_passed', 0) + 1
    
    def get_events_for_chapter(self, chapter: int) -> List[Dict[str, Any]]:
        """Get all events in a specific chapter"""
        data = self.load()
        return [e for e in data.get('events', []) if e.get('chapter') == chapter]


class InventoryPanel(StatePanel):
    """Inventory panel: 道具/物品管理"""
    
    def _create_default(self) -> Dict[str, Any]:
        return {
            'entities': {},  # item_name -> item_data
            'pending_changes': [],
            'last_updated': get_timestamp_iso(),
            'panel_type': 'inventory'
        }
    
    def add_item(
        self,
        item_name: str,
        owner: str,
        description: str,
        acquired_chapter: int,
        evidence: Evidence
    ) -> bool:
        """Add new item to inventory"""
        data = self.load()
        
        data['entities'][item_name] = {
            'values': {
                'owner': owner,
                'status': 'active',  # active|lost|consumed|destroyed
                'acquired_chapter': acquired_chapter,
                'description': description
            },
            'meta': evidence.to_dict()
        }
        
        data['last_updated'] = get_timestamp_iso()
        return self.save()
    
    def transfer_item(
        self,
        item_name: str,
        new_owner: str,
        evidence: Evidence
    ) -> bool:
        """Transfer item ownership"""
        return self.update_entity(item_name, 'owner', new_owner, evidence)
    
    def change_item_status(
        self,
        item_name: str,
        new_status: str,  # active|lost|consumed|destroyed
        evidence: Evidence
    ) -> bool:
        """Change item status"""
        return self.update_entity(item_name, 'status', new_status, evidence)
    
    def get_items_by_owner(self, owner: str) -> List[Dict[str, Any]]:
        """Get all items owned by a character"""
        data = self.load()
        items = []
        
        for name, entity in data.get('entities', {}).items():
            if entity.get('values', {}).get('owner') == owner:
                items.append({
                    'name': name,
                    **entity['values']
                })
        
        return items


# ============================================================================
# State Manager (Aggregate)
# ============================================================================

class StateManager:
    """
    Aggregates all state panels for convenient access
    """
    
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.state_dir = self.run_dir / "4-state"
        
        # Initialize all panels
        self.characters = CharactersPanel(self.state_dir / "characters.json")
        self.plot_threads = PlotThreadsPanel(self.state_dir / "plot_threads.json")
        self.timeline = TimelinePanel(self.state_dir / "timeline.json")
        self.inventory = InventoryPanel(self.state_dir / "inventory.json")
        self.locations_factions = StatePanel(self.state_dir / "locations_factions.json")
        self.pov_rules = StatePanel(self.state_dir / "pov_rules.json")
    
    def load_all(self) -> Dict[str, Any]:
        """Load all state panels"""
        return {
            'characters': self.characters.load(),
            'plot_threads': self.plot_threads.load(),
            'timeline': self.timeline.load(),
            'inventory': self.inventory.load(),
            'locations_factions': self.locations_factions.load(),
            'pov_rules': self.pov_rules.load()
        }
    
    def get_invariants(self, current_chapter: int) -> Dict[str, Any]:
        """
        Extract invariants for Sanitizer
        Returns all state that MUST be continued (confidence >= 0.7)
        """
        invariants = {
            'characters': {},
            'plot_threads': {},
            'inventory': {},
            'timeline': {}
        }
        
        # Get characters with high-confidence states
        for char_name in self.characters.list_entities():
            entity = self.characters.get_entity(char_name)
            if entity:
                high_conf_fields = {}
                for field, meta in entity.get('meta', {}).items():
                    if meta.get('confidence', 0) >= 0.7:
                        high_conf_fields[field] = entity['values'].get(field)
                if high_conf_fields:
                    invariants['characters'][char_name] = high_conf_fields
        
        # Get active plot threads
        invariants['plot_threads'] = self.plot_threads.get_active_threads()
        
        return invariants
    
    def commit_chapter_state(
        self,
        chapter_num: int,
        changes: Dict[str, Any]
    ) -> bool:
        """
        Commit state changes after chapter completion
        
        Args:
            chapter_num: Current chapter number
            changes: Dictionary of changes to apply
        """
        success = True
        
        # Apply character changes
        if 'characters' in changes:
            for char_name, char_changes in changes['characters'].items():
                for field, change_data in char_changes.items():
                    evidence = Evidence(
                        chapter=f"第{chapter_num:03d}章",
                        snippet=change_data.get('snippet', ''),
                        confidence=change_data.get('confidence', 0.8)
                    )
                    if not self.characters.update_entity(
                        char_name, field, change_data['value'], evidence
                    ):
                        success = False
        
        # Apply plot thread changes
        if 'plot_threads' in changes:
            for thread_name, thread_data in changes['plot_threads'].items():
                # Handle thread resolution
                if thread_data.get('resolved'):
                    evidence = Evidence(
                        chapter=f"第{chapter_num:03d}章",
                        snippet=thread_data.get('snippet', ''),
                        confidence=thread_data.get('confidence', 0.8)
                    )
                    if not self.plot_threads.resolve_thread(
                        thread_name, chapter_num, thread_data.get('resolution', ''), evidence
                    ):
                        success = False
        
        # Apply timeline changes
        if 'timeline' in changes:
            timeline_data = changes['timeline']
            evidence = Evidence(
                chapter=f"第{chapter_num:03d}章",
                snippet=timeline_data.get('snippet', ''),
                confidence=timeline_data.get('confidence', 0.8)
            )
            if not self.timeline.add_event(
                chapter_num,
                timeline_data.get('event', ''),
                timeline_data.get('day_offset', 0),
                evidence
            ):
                success = False
        
        return success


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== State Manager Test ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "4-state"
        state_dir.mkdir(parents=True)
        
        # Test Characters Panel
        print("[Test] Characters Panel")
        chars = CharactersPanel(state_dir / "characters.json")
        
        evidence = Evidence("第001章", "张大胆获得系统", 0.95)
        chars.update_entity("张大胆", "motivation", "还清阴债", evidence)
        chars.update_character_status("张大胆", "健康", evidence)
        chars.add_injury("张大胆", "胸口剑伤", 5, 
                        Evidence("第005章", "张大胆胸口中了一剑", 0.9))
        chars.update_relationship("张大胆", "饿死鬼", -2,
                                 Evidence("第003章", "饿死鬼想害他", 0.8))
        
        entity = chars.get_entity("张大胆")
        print(f"  Character created: {'PASS' if entity else 'FAIL'}")
        print(f"  Motivation: {entity['values'].get('motivation')}")
        
        # Test Plot Threads Panel
        print("\n[Test] Plot Threads Panel")
        threads = PlotThreadsPanel(state_dir / "plot_threads.json")
        
        threads.add_thread(
            "系统真实来源",
            introduced_chapter=1,
            promised_payoff="揭示系统是上古神器",
            urgency="pending"
        )
        
        active = threads.get_active_threads()
        print(f"  Active threads: {len(active)}")
        
        # Test Timeline Panel
        print("\n[Test] Timeline Panel")
        timeline = TimelinePanel(state_dir / "timeline.json")
        
        timeline.add_event(1, "获得系统", 0)
        timeline.add_event(2, "送第一单", 0)
        timeline.add_event(3, "遭遇恶鬼", 1)  # Next day
        
        print(f"  Current day: {timeline.get_current_day()}")
        print(f"  Total events: {len(timeline.load()['events'])}")
        
        # Test Inventory Panel
        print("\n[Test] Inventory Panel")
        inv = InventoryPanel(state_dir / "inventory.json")
        
        inv.add_item(
            "阴间外卖箱",
            owner="张大胆",
            description="系统赠送，可容纳鬼物",
            acquired_chapter=1,
            evidence=Evidence("第001章", "获得外卖箱", 0.98)
        )
        
        items = inv.get_items_by_owner("张大胆")
        print(f"  Items owned: {len(items)}")
        
        # Test StateManager aggregate
        print("\n[Test] StateManager Aggregate")
        mgr = StateManager(Path(tmpdir))
        all_state = mgr.load_all()
        print(f"  Loaded panels: {list(all_state.keys())}")
        
        invariants = mgr.get_invariants(5)
        print(f"  Invariants extracted: {'characters' in invariants}")
        
    print("\n=== All tests completed ===")
