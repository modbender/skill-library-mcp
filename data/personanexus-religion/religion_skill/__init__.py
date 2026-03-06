"""PersonaNexus Religion Skill -- Build AI agent personalities with religion/faith frameworks."""

__version__ = "1.0.0"

from religion_skill.compiler import (
    OpenClawCompiler,
    SystemPromptCompiler,
    compile_identity,
)
from religion_skill.parser import (
    IdentityParser,
    parse_file,
    parse_identity_file,
    parse_yaml,
)
from religion_skill.personality import (
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
from religion_skill.religion import (
    AuthorityLevel,
    DietaryRule,
    HolyDay,
    InfluenceLevel,
    MoralFramework,
    PrayerSchedule,
    ReligionConfig,
    SacredText,
    Tradition,
    build_persona,
)
from religion_skill.types import (
    TRAIT_ORDER,
    AgentIdentity,
    DiscProfile,
    JungianProfile,
    OceanProfile,
    PersonalityMode,
    PersonalityProfile,
)
from religion_skill.validator import IdentityValidator, ValidationResult

__all__ = [
    "AgentIdentity",
    "AuthorityLevel",
    "DietaryRule",
    "DiscProfile",
    "HolyDay",
    "IdentityParser",
    "IdentityValidator",
    "InfluenceLevel",
    "JungianProfile",
    "MoralFramework",
    "OceanProfile",
    "OpenClawCompiler",
    "PersonalityMode",
    "PersonalityProfile",
    "PrayerSchedule",
    "ReligionConfig",
    "SacredText",
    "SystemPromptCompiler",
    "TRAIT_ORDER",
    "Tradition",
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
