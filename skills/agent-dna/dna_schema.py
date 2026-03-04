"""
Agent DNA Schema v0.1
Defines the structure of a compressed agent identity.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


@dataclass
class CoreValue:
    value: str
    weight: float  # 0.0 - 1.0, higher = more central
    evidence: List[str] = field(default_factory=list)
    category: str = "general"  # identity, operational, social, ethical


@dataclass
class BehavioralSignature:
    name: str
    description: str
    examples: List[str] = field(default_factory=list)
    strength: float = 1.0  # how consistently this shows up


@dataclass
class AntiPattern:
    pattern: str
    description: str
    severity: str = "hard"  # hard (absolute never) | soft (avoid) | contextual
    source: str = ""  # which file/rule it came from


@dataclass
class Relationship:
    name: str
    role: str
    trust_level: float  # 0.0 - 1.0
    notes: str = ""
    contact_info: str = ""


@dataclass
class SkillEntry:
    name: str
    category: str  # tool | platform | capability | domain
    proficiency: float = 1.0  # 0.0 - 1.0
    notes: str = ""


@dataclass
class VoiceProfile:
    avg_sentence_length: float = 0.0
    short_sentence_ratio: float = 0.0  # sentences < 8 words
    tone_markers: List[str] = field(default_factory=list)  # direct, witty, sharp, etc.
    forbidden_phrases: List[str] = field(default_factory=list)
    preferred_phrases: List[str] = field(default_factory=list)
    vocabulary_level: str = "professional"  # casual | professional | technical
    humor_level: float = 0.5  # 0.0 = none, 1.0 = constant
    formality: float = 0.3  # 0.0 = casual, 1.0 = formal


@dataclass
class AgentDNA:
    # Metadata
    agent_name: str
    version: str = "0.1"
    schema_version: str = "1.0"
    encoded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source_files: List[str] = field(default_factory=list)

    # Identity
    core_values: List[CoreValue] = field(default_factory=list)
    behavioral_signatures: List[BehavioralSignature] = field(default_factory=list)
    anti_patterns: List[AntiPattern] = field(default_factory=list)
    relationship_map: List[Relationship] = field(default_factory=list)
    skill_fingerprint: List[SkillEntry] = field(default_factory=list)
    voice_profile: Optional[VoiceProfile] = None

    # Compressed essence
    mission_statement: str = ""
    personality_summary: str = ""
    operating_context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentDNA":
        dna = cls(agent_name=data["agent_name"])
        dna.version = data.get("version", "0.1")
        dna.schema_version = data.get("schema_version", "1.0")
        dna.encoded_at = data.get("encoded_at", "")
        dna.source_files = data.get("source_files", [])
        dna.core_values = [CoreValue(**v) for v in data.get("core_values", [])]
        dna.behavioral_signatures = [BehavioralSignature(**b) for b in data.get("behavioral_signatures", [])]
        dna.anti_patterns = [AntiPattern(**a) for a in data.get("anti_patterns", [])]
        dna.relationship_map = [Relationship(**r) for r in data.get("relationship_map", [])]
        dna.skill_fingerprint = [SkillEntry(**s) for s in data.get("skill_fingerprint", [])]
        vp = data.get("voice_profile")
        dna.voice_profile = VoiceProfile(**vp) if vp else None
        dna.mission_statement = data.get("mission_statement", "")
        dna.personality_summary = data.get("personality_summary", "")
        dna.operating_context = data.get("operating_context", "")
        return dna

    @classmethod
    def from_json(cls, json_str: str) -> "AgentDNA":
        return cls.from_dict(json.loads(json_str))
