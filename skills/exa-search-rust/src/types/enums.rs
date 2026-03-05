use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SearchType {
    Auto,
    Fast,
    Deep,
    Neural,
    Instant,
    Keyword,
}

/// Maps to Exa category strings (may contain spaces — use string passthrough).
/// Keep as a plain String in params; this enum is for documentation only.
#[allow(dead_code)]
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Category {
    Company,
    #[serde(rename = "research paper")]
    ResearchPaper,
    News,
    Pdf,
    Tweet,
    #[serde(rename = "personal site")]
    PersonalSite,
    #[serde(rename = "financial report")]
    FinancialReport,
    People,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Livecrawl {
    Always,
    Fallback,
    Never,
    Auto,
    Preferred,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Verbosity {
    Compact,
    Standard,
    Full,
}
