use serde::{Deserialize, Serialize};

// ─── Entity types ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
#[allow(clippy::struct_field_names)]
pub struct Entity {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<String>,

    #[serde(rename = "type", skip_serializing_if = "Option::is_none")]
    pub entity_type: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<u32>,

    /// Arbitrary entity properties — pass through as raw JSON.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub properties: Option<serde_json::Value>,
}

// ─── Core result item ─────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExaResult {
    pub url: String,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub title: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub score: Option<f64>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub published_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub author: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub image: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub favicon: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub summary: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub highlights: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub highlight_scores: Option<Vec<f64>>,

    /// Nested subpage results (recursive — same shape).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub subpages: Option<Vec<ExaResult>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub extras: Option<serde_json::Value>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub entities: Option<Vec<Entity>>,
}

// ─── API response wrappers ────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
pub struct SearchResponse {
    pub results: Vec<ExaResult>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub resolved_search_type: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub auto_date: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub search_time_ms: Option<u64>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub cost_dollars: Option<serde_json::Value>,
}

#[derive(Debug, Deserialize)]
pub struct FindSimilarResponse {
    pub results: Vec<ExaResult>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub cost_dollars: Option<serde_json::Value>,
}

#[derive(Debug, Deserialize)]
pub struct ContentsResponse {
    pub results: Vec<ExaResult>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub cost_dollars: Option<serde_json::Value>,
}
