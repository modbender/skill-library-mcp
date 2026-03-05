use crate::types::enums::SearchType;
use crate::types::params::{ContentsInput, ExtrasOptions};
use crate::types::result::ExaResult;
use serde::{Deserialize, Serialize};

/// Stdin JSON input. All fields optional except context-specific required ones.
/// `action` defaults to `"search"` when absent.
#[derive(Debug, Deserialize)]
pub struct Input {
    // ── action routing ─────────────────────────────────────────────────────
    pub action: Option<String>, // "search" | "find_similar" | "get_contents"

    // ── search + find_similar ──────────────────────────────────────────────
    pub query: Option<String>,
    pub num_results: Option<u32>,
    #[serde(rename = "type")]
    pub search_type: Option<SearchType>,
    pub category: Option<String>,
    pub include_domains: Option<Vec<String>>,
    pub exclude_domains: Option<Vec<String>>,
    pub start_crawl_date: Option<String>,
    pub end_crawl_date: Option<String>,
    pub start_published_date: Option<String>,
    pub end_published_date: Option<String>,
    pub include_text: Option<Vec<String>>,
    pub exclude_text: Option<Vec<String>>,
    pub use_autoprompt: Option<bool>,
    pub moderation: Option<bool>,
    pub user_location: Option<String>,
    pub additional_queries: Option<Vec<String>>,

    // ── find_similar only ──────────────────────────────────────────────────
    pub url: Option<String>,
    pub exclude_source_domain: Option<bool>,

    // ── get_contents only ─────────────────────────────────────────────────
    pub urls: Option<Vec<String>>,

    // ── shared contents options ────────────────────────────────────────────
    pub contents: Option<ContentsInput>,

    // ── legacy compat: max_chars → contents.text.max_characters ───────────
    pub max_chars: Option<u32>,

    // ── top-level contents shorthands (applied if contents object omits them) ──
    pub filter_empty_results: Option<bool>,
    pub extras: Option<ExtrasOptions>,
    pub max_age_hours: Option<i32>,
}

#[derive(Debug, Serialize)]
#[serde(untagged)]
pub enum Output {
    SearchOk {
        ok: bool,
        action: String,
        results: Vec<ExaResult>,
        #[serde(skip_serializing_if = "Option::is_none")]
        resolved_search_type: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        auto_date: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        search_time_ms: Option<u64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        cost_dollars: Option<serde_json::Value>,
        formatted: String,
    },
    ContentsOk {
        ok: bool,
        action: String,
        results: Vec<ExaResult>,
        #[serde(skip_serializing_if = "Option::is_none")]
        cost_dollars: Option<serde_json::Value>,
    },
    Err {
        ok: bool,
        error: String,
    },
}

/// Build the markdown-formatted string from results.
pub fn format_results(results: &[ExaResult]) -> String {
    results
        .iter()
        .map(|r| {
            let title = r.title.as_deref().unwrap_or("Untitled");
            let url = &r.url;
            let body = r.summary.as_deref().or(r.text.as_deref()).unwrap_or("");
            format!("## [{title}]({url})\n\n{body}\n\n---")
        })
        .collect::<Vec<_>>()
        .join("\n\n")
}
