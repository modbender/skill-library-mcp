use crate::types::{
    ContentsResponse, FindSimilarOptions, FindSimilarResponse, GetContentsOptions, SearchOptions,
    SearchResponse,
};
use anyhow::{Context, Result};
use reqwest::header::{HeaderMap, HeaderValue, CONTENT_TYPE};
use reqwest::Client;

const EXA_BASE_URL: &str = "https://api.exa.ai";

pub struct ExaClient {
    client: Client,
    api_key: String,
}

impl ExaClient {
    pub fn new(api_key: String) -> Result<Self> {
        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(60))
            .build()
            .context("Failed to build HTTP client")?;
        Ok(Self { client, api_key })
    }

    fn auth_headers(&self) -> Result<HeaderMap> {
        let mut headers = HeaderMap::new();
        let Ok(api_key_val) = HeaderValue::from_str(&self.api_key) else {
            anyhow::bail!("api_key contains invalid header characters");
        };
        headers.insert("x-api-key", api_key_val);
        headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));
        Ok(headers)
    }

    pub async fn search(&self, opts: SearchOptions) -> Result<SearchResponse> {
        let url = format!("{EXA_BASE_URL}/search");
        let resp = self
            .client
            .post(&url)
            .headers(self.auth_headers()?)
            .json(&opts)
            .send()
            .await
            .context("HTTP request failed")?;
        self.parse_response(resp).await
    }

    pub async fn find_similar(&self, opts: FindSimilarOptions) -> Result<FindSimilarResponse> {
        let url = format!("{EXA_BASE_URL}/findSimilar");
        let resp = self
            .client
            .post(&url)
            .headers(self.auth_headers()?)
            .json(&opts)
            .send()
            .await
            .context("HTTP request failed")?;
        self.parse_response(resp).await
    }

    pub async fn get_contents(&self, opts: GetContentsOptions) -> Result<ContentsResponse> {
        let url = format!("{EXA_BASE_URL}/contents");
        let resp = self
            .client
            .post(&url)
            .headers(self.auth_headers()?)
            .json(&opts)
            .send()
            .await
            .context("HTTP request failed")?;
        self.parse_response(resp).await
    }

    /// Parse a response: propagate HTTP errors, then deserialize JSON.
    async fn parse_response<T: serde::de::DeserializeOwned>(
        &self,
        resp: reqwest::Response,
    ) -> Result<T> {
        const MAX_BODY: usize = 10 * 1024 * 1024; // 10MB
        let status = resp.status();
        let bytes = resp.bytes().await.context("Failed to read response body")?;
        if bytes.len() > MAX_BODY {
            anyhow::bail!("Response too large: {} bytes (max 10MB)", bytes.len());
        }
        let body = String::from_utf8(bytes.to_vec()).context("Response body is not valid UTF-8")?;
        if !status.is_success() {
            anyhow::bail!("Exa API error {status}: {body}");
        }
        serde_json::from_str(&body).with_context(|| format!("Failed to parse API response: {body}"))
    }
}
