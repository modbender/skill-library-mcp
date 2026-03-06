use super::enums::{Livecrawl, SearchType, Verbosity};
use serde::{Deserialize, Serialize};

// ─── Text contents option ─────────────────────────────────────────────────────

/// Sent to Exa when the caller requests text extraction.
/// `true` in input → serialize as `{}` (all defaults); object → full struct.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct TextOptions {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_characters: Option<u32>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_html_tags: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub verbosity: Option<Verbosity>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_sections: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub exclude_sections: Option<Vec<String>>,
}

// ─── Summary contents option ──────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SummaryOptions {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub query: Option<String>,

    /// Arbitrary JSON Schema object — pass through as raw Value.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub schema: Option<serde_json::Value>,
}

// ─── Highlights contents option ───────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct HighlightsOptions {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub query: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_characters: Option<u32>,
}

// ─── Extras contents option ───────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ExtrasOptions {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub links: Option<u32>,
}

// ─── ContentsOptions (shared: search / find_similar / get_contents) ──────────

/// Mirrors the `contents` key in the stdin protocol.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ContentsOptions {
    /// `true` → send `{}` (defaults); object → send full struct.
    /// Represented in protocol as `true | { ... }` — use `ContentsTextInput` below.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<TextOptions>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub summary: Option<SummaryOptions>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub highlights: Option<HighlightsOptions>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub livecrawl: Option<Livecrawl>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub livecrawl_timeout: Option<u32>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_age_hours: Option<i32>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub filter_empty_results: Option<bool>,

    /// Number of subpages to fetch.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub subpages: Option<u32>,

    /// Target path(s) for subpages — string or array of strings.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub subpage_target: Option<serde_json::Value>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub extras: Option<ExtrasOptions>,
}

// ─── Protocol-level Contents input ────────────────────────────────────────────

/// In stdin, `contents.text` can be `true` (enable with defaults) or an object.
/// Deserialize using an untagged enum then flatten to `TextOptions`.
#[allow(dead_code)]
#[derive(Debug, Clone, Deserialize)]
#[serde(untagged)]
pub enum BoolOrTextOptions {
    Bool(bool),
    Options(TextOptions),
}

#[allow(dead_code)]
#[derive(Debug, Clone, Deserialize)]
#[serde(untagged)]
pub enum BoolOrSummaryOptions {
    Bool(bool),
    Options(SummaryOptions),
}

#[allow(dead_code)]
#[derive(Debug, Clone, Deserialize)]
#[serde(untagged)]
pub enum BoolOrHighlightsOptions {
    Bool(bool),
    Options(HighlightsOptions),
}

/// The `contents` field as it arrives from stdin.
#[derive(Debug, Clone, Deserialize, Default)]
pub struct ContentsInput {
    #[serde(default)]
    pub text: Option<BoolOrTextOptions>,

    #[serde(default)]
    pub summary: Option<BoolOrSummaryOptions>,

    #[serde(default)]
    pub highlights: Option<BoolOrHighlightsOptions>,

    #[serde(default)]
    pub livecrawl: Option<Livecrawl>,

    #[serde(default)]
    pub livecrawl_timeout: Option<u32>,

    #[serde(default)]
    pub max_age_hours: Option<i32>,

    #[serde(default)]
    pub filter_empty_results: Option<bool>,

    #[serde(default)]
    pub subpages: Option<u32>,

    #[serde(default)]
    pub subpage_target: Option<serde_json::Value>,

    #[serde(default)]
    pub extras: Option<ExtrasOptions>,
}

impl ContentsInput {
    /// Convert protocol input to the API-ready struct.
    pub fn into_options(self) -> ContentsOptions {
        ContentsOptions {
            text: self.text.map(|t| match t {
                BoolOrTextOptions::Bool(_) => TextOptions::default(),
                BoolOrTextOptions::Options(o) => o,
            }),
            summary: self.summary.map(|s| match s {
                BoolOrSummaryOptions::Bool(_) => SummaryOptions::default(),
                BoolOrSummaryOptions::Options(o) => o,
            }),
            highlights: self.highlights.map(|h| match h {
                BoolOrHighlightsOptions::Bool(_) => HighlightsOptions::default(),
                BoolOrHighlightsOptions::Options(o) => o,
            }),
            livecrawl: self.livecrawl,
            livecrawl_timeout: self.livecrawl_timeout,
            max_age_hours: self.max_age_hours,
            filter_empty_results: self.filter_empty_results,
            subpages: self.subpages,
            subpage_target: self.subpage_target,
            extras: self.extras,
        }
    }
}

// ─── SearchOptions (POST /search body) ───────────────────────────────────────

#[derive(Debug, Clone, Serialize)]
pub struct SearchOptions {
    pub query: String,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub num_results: Option<u32>,

    #[serde(rename = "type", skip_serializing_if = "Option::is_none")]
    pub search_type: Option<SearchType>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub category: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_domains: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub exclude_domains: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub start_crawl_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub end_crawl_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub start_published_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub end_published_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_text: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub exclude_text: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub use_autoprompt: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub moderation: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub user_location: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub additional_queries: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub contents: Option<ContentsOptions>,
}

// ─── FindSimilarOptions (POST /findSimilar body) ─────────────────────────────

#[derive(Debug, Clone, Serialize)]
pub struct FindSimilarOptions {
    pub url: String,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub num_results: Option<u32>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_domains: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub exclude_domains: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub start_crawl_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub end_crawl_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub start_published_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub end_published_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_text: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub exclude_text: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub exclude_source_domain: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub category: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub contents: Option<ContentsOptions>,
}

// ─── GetContentsOptions (POST /contents body) ─────────────────────────────────

#[derive(Debug, Clone, Serialize)]
pub struct GetContentsOptions {
    pub urls: Vec<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<TextOptions>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub summary: Option<SummaryOptions>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub highlights: Option<HighlightsOptions>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub livecrawl: Option<Livecrawl>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub livecrawl_timeout: Option<u32>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_age_hours: Option<i32>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub filter_empty_results: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub subpages: Option<u32>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub subpage_target: Option<serde_json::Value>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub extras: Option<ExtrasOptions>,
}
