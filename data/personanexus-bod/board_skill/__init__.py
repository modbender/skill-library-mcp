"""PersonaNexus Board Skill -- Build AI agent personalities with a Board of Directors advisory panel."""

__version__ = "1.0.0"

from board_skill.board import (
    BoardConfig,
    BoardMember,
    DiscStyle,
    MemberPersonality,
    OceanScores,
    build_persona,
)
from board_skill.compiler import (
    OpenClawCompiler,
    SystemPromptCompiler,
    compile_identity,
)
from board_skill.parser import (
    IdentityParser,
    parse_file,
    parse_identity_file,
    parse_yaml,
)
from board_skill.personality import (
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
from board_skill.types import (
    TRAIT_ORDER,
    AgentIdentity,
    DiscProfile,
    JungianProfile,
    OceanProfile,
    PersonalityMode,
    PersonalityProfile,
)
from board_skill.validator import IdentityValidator, ValidationResult

__all__ = [
    "AgentIdentity",
    "BoardConfig",
    "BoardMember",
    "DiscProfile",
    "DiscStyle",
    "IdentityParser",
    "IdentityValidator",
    "JungianProfile",
    "MemberPersonality",
    "OceanProfile",
    "OceanScores",
    "OpenClawCompiler",
    "PersonalityMode",
    "PersonalityProfile",
    "SystemPromptCompiler",
    "TRAIT_ORDER",
    "ValidationResult",
    "build_persona",
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
