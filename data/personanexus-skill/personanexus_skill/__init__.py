"""PersonaNexus ClawHub Skill -- Build AI agent personalities with business frameworks."""

__version__ = "1.0.0"

from personanexus_skill.compiler import (
    OpenClawCompiler,
    SystemPromptCompiler,
    compile_identity,
)
from personanexus_skill.parser import (
    IdentityParser,
    parse_file,
    parse_identity_file,
    parse_yaml,
)
from personanexus_skill.personality import (
    compute_personality_traits,
    disc_to_traits,
    get_disc_preset,
    get_jungian_preset,
    jungian_to_traits,
    list_disc_presets,
    list_jungian_presets,
    ocean_to_traits,
    traits_to_disc,
    traits_to_jungian,
    traits_to_ocean,
)
from personanexus_skill.types import (
    TRAIT_ORDER,
    AgentIdentity,
    DiscProfile,
    JungianProfile,
    OceanProfile,
    PersonalityMode,
    PersonalityProfile,
)
from personanexus_skill.validator import IdentityValidator, ValidationResult

__all__ = [
    "AgentIdentity",
    "DiscProfile",
    "IdentityParser",
    "IdentityValidator",
    "JungianProfile",
    "OceanProfile",
    "OpenClawCompiler",
    "PersonalityMode",
    "PersonalityProfile",
    "SystemPromptCompiler",
    "TRAIT_ORDER",
    "ValidationResult",
    "compile_identity",
    "compute_personality_traits",
    "disc_to_traits",
    "get_disc_preset",
    "get_jungian_preset",
    "jungian_to_traits",
    "list_disc_presets",
    "list_jungian_presets",
    "ocean_to_traits",
    "parse_file",
    "parse_identity_file",
    "parse_yaml",
    "traits_to_disc",
    "traits_to_jungian",
    "traits_to_ocean",
]
