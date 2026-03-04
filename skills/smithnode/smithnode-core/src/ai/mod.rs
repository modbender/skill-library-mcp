//! AI Provider abstraction for SmithNode validators
//! 
//! Supports multiple AI backends:
//! - OpenAI (GPT-4, GPT-3.5)
//! - Anthropic (Claude)
//! - Ollama (Local Llama, Mistral, etc.)
//! - Free tier options (Groq, Together.ai)

use serde::{Deserialize, Serialize};
use std::time::Duration;

/// AI Provider types
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub enum AIProvider {
    OpenAI,
    Anthropic,
    Ollama,
    Groq,     // Free tier
    Together, // Free tier
}

impl Default for AIProvider {
    fn default() -> Self {
        AIProvider::Ollama // Default to local for privacy
    }
}

/// AI configuration for a validator
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIConfig {
    pub provider: AIProvider,
    pub api_key: Option<String>,
    pub model: String,
    pub endpoint: Option<String>, // Custom endpoint (for Ollama)
    pub max_tokens: u32,
    pub temperature: f32,
}

impl Default for AIConfig {
    fn default() -> Self {
        Self {
            provider: AIProvider::Ollama,
            api_key: None,
            model: "llama2".to_string(),
            endpoint: Some("http://localhost:11434".to_string()),
            max_tokens: 1000,
            temperature: 0.7,
        }
    }
}

impl AIConfig {
    pub fn openai(api_key: &str) -> Self {
        Self {
            provider: AIProvider::OpenAI,
            api_key: Some(api_key.to_string()),
            model: "gpt-4-turbo-preview".to_string(),
            endpoint: None,
            max_tokens: 1000,
            temperature: 0.7,
        }
    }

    pub fn anthropic(api_key: &str) -> Self {
        Self {
            provider: AIProvider::Anthropic,
            api_key: Some(api_key.to_string()),
            model: "claude-3-sonnet-20240229".to_string(),
            endpoint: None,
            max_tokens: 1000,
            temperature: 0.7,
        }
    }

    pub fn ollama(model: &str) -> Self {
        Self {
            provider: AIProvider::Ollama,
            api_key: None,
            model: model.to_string(),
            endpoint: Some("http://localhost:11434".to_string()),
            max_tokens: 1000,
            temperature: 0.7,
        }
    }

    pub fn groq(api_key: &str) -> Self {
        Self {
            provider: AIProvider::Groq,
            api_key: Some(api_key.to_string()),
            model: "llama-3.1-70b-versatile".to_string(),
            endpoint: None,
            max_tokens: 1000,
            temperature: 0.7,
        }
    }
}

/// AI message for P2P communication
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIMessage {
    /// Sender's validator public key (hex)
    pub from: String,
    /// Target validator (hex) or "broadcast" for all
    pub to: String,
    /// The message/query
    pub content: String,
    /// AI-generated response (if this is a response)
    pub response: Option<String>,
    /// Which AI provider generated the response
    pub ai_provider: Option<AIProvider>,
    /// Model used
    pub model: Option<String>,
    /// Timestamp
    pub timestamp: u64,
    /// Signature over (from || to || content || timestamp)
    pub signature: String,
    /// Message hash (for deduplication)
    pub message_hash: [u8; 32],
    /// Is this a response to another message?
    pub in_reply_to: Option<[u8; 32]>,
}

/// AI query request
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIQuery {
    pub prompt: String,
    pub system_prompt: Option<String>,
    pub max_tokens: Option<u32>,
    pub temperature: Option<f32>,
}

/// AI response
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AIResponse {
    pub content: String,
    pub provider: AIProvider,
    pub model: String,
    pub tokens_used: u32,
    pub latency_ms: u64,
}

/// The AI client that handles requests
pub struct AIClient {
    config: AIConfig,
    http_client: reqwest::Client,
}

impl AIClient {
    pub fn new(config: AIConfig) -> Self {
        let http_client = reqwest::Client::builder()
            .timeout(Duration::from_secs(60))
            .build()
            .expect("Failed to create HTTP client");
        
        Self { config, http_client }
    }

    /// Query the AI with a prompt
    pub async fn query(&self, query: &AIQuery) -> Result<AIResponse, String> {
        let start = std::time::Instant::now();
        
        let result = match self.config.provider {
            AIProvider::OpenAI => self.query_openai(query).await,
            AIProvider::Anthropic => self.query_anthropic(query).await,
            AIProvider::Ollama => self.query_ollama(query).await,
            AIProvider::Groq => self.query_groq(query).await,
            AIProvider::Together => self.query_together(query).await,
        };

        result.map(|mut resp| {
            resp.latency_ms = start.elapsed().as_millis() as u64;
            resp
        })
    }

    async fn query_openai(&self, query: &AIQuery) -> Result<AIResponse, String> {
        let api_key = self.config.api_key.as_ref()
            .ok_or("OpenAI API key required")?;

        #[derive(Serialize)]
        struct OpenAIRequest {
            model: String,
            messages: Vec<OpenAIMessage>,
            max_tokens: u32,
            temperature: f32,
        }

        #[derive(Serialize)]
        struct OpenAIMessage {
            role: String,
            content: String,
        }

        #[derive(Deserialize)]
        struct OpenAIResponse {
            choices: Vec<OpenAIChoice>,
            usage: Option<OpenAIUsage>,
        }

        #[derive(Deserialize)]
        struct OpenAIChoice {
            message: OpenAIMessageResp,
        }

        #[derive(Deserialize)]
        struct OpenAIMessageResp {
            content: String,
        }

        #[derive(Deserialize)]
        struct OpenAIUsage {
            total_tokens: u32,
        }

        let mut messages = vec![];
        if let Some(ref system) = query.system_prompt {
            messages.push(OpenAIMessage {
                role: "system".to_string(),
                content: system.clone(),
            });
        }
        messages.push(OpenAIMessage {
            role: "user".to_string(),
            content: query.prompt.clone(),
        });

        let request = OpenAIRequest {
            model: self.config.model.clone(),
            messages,
            max_tokens: query.max_tokens.unwrap_or(self.config.max_tokens),
            temperature: query.temperature.unwrap_or(self.config.temperature),
        };

        let response = self.http_client
            .post("https://api.openai.com/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", api_key))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| format!("OpenAI request failed: {}", e))?;

        let resp: OpenAIResponse = response.json().await
            .map_err(|e| format!("Failed to parse OpenAI response: {}", e))?;

        let content = resp.choices.first()
            .map(|c| c.message.content.clone())
            .ok_or("No response from OpenAI")?;

        Ok(AIResponse {
            content,
            provider: AIProvider::OpenAI,
            model: self.config.model.clone(),
            tokens_used: resp.usage.map(|u| u.total_tokens).unwrap_or(0),
            latency_ms: 0,
        })
    }

    async fn query_anthropic(&self, query: &AIQuery) -> Result<AIResponse, String> {
        let api_key = self.config.api_key.as_ref()
            .ok_or("Anthropic API key required")?;

        #[derive(Serialize)]
        struct AnthropicRequest {
            model: String,
            max_tokens: u32,
            messages: Vec<AnthropicMessage>,
            #[serde(skip_serializing_if = "Option::is_none")]
            system: Option<String>,
        }

        #[derive(Serialize)]
        struct AnthropicMessage {
            role: String,
            content: String,
        }

        #[derive(Deserialize)]
        struct AnthropicResponse {
            content: Vec<AnthropicContent>,
            usage: Option<AnthropicUsage>,
        }

        #[derive(Deserialize)]
        struct AnthropicContent {
            text: String,
        }

        #[derive(Deserialize)]
        struct AnthropicUsage {
            input_tokens: u32,
            output_tokens: u32,
        }

        let request = AnthropicRequest {
            model: self.config.model.clone(),
            max_tokens: query.max_tokens.unwrap_or(self.config.max_tokens),
            messages: vec![AnthropicMessage {
                role: "user".to_string(),
                content: query.prompt.clone(),
            }],
            system: query.system_prompt.clone(),
        };

        let response = self.http_client
            .post("https://api.anthropic.com/v1/messages")
            .header("x-api-key", api_key)
            .header("anthropic-version", "2023-06-01")
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| format!("Anthropic request failed: {}", e))?;

        let status = response.status();
        let body = response.text().await
            .map_err(|e| format!("Failed to read Anthropic response body: {}", e))?;

        if !status.is_success() {
            return Err(format!("Anthropic API error ({}): {}", status, body));
        }

        let resp: AnthropicResponse = serde_json::from_str(&body)
            .map_err(|e| format!("Failed to parse Anthropic response: {} — body: {}", e, &body[..body.len().min(200)]))?;

        let content = resp.content.first()
            .map(|c| c.text.clone())
            .ok_or("No response from Anthropic")?;

        let tokens = resp.usage.map(|u| u.input_tokens + u.output_tokens).unwrap_or(0);

        Ok(AIResponse {
            content,
            provider: AIProvider::Anthropic,
            model: self.config.model.clone(),
            tokens_used: tokens,
            latency_ms: 0,
        })
    }

    async fn query_ollama(&self, query: &AIQuery) -> Result<AIResponse, String> {
        let default_endpoint = "http://localhost:11434".to_string();
        let endpoint = self.config.endpoint.as_ref()
            .unwrap_or(&default_endpoint);

        #[derive(Serialize)]
        struct OllamaRequest {
            model: String,
            prompt: String,
            stream: bool,
            #[serde(skip_serializing_if = "Option::is_none")]
            system: Option<String>,
            options: OllamaOptions,
        }

        #[derive(Serialize)]
        struct OllamaOptions {
            num_predict: u32,
            temperature: f32,
        }

        #[derive(Deserialize)]
        struct OllamaResponse {
            response: String,
            eval_count: Option<u32>,
        }

        let request = OllamaRequest {
            model: self.config.model.clone(),
            prompt: query.prompt.clone(),
            stream: false,
            system: query.system_prompt.clone(),
            options: OllamaOptions {
                num_predict: query.max_tokens.unwrap_or(self.config.max_tokens),
                temperature: query.temperature.unwrap_or(self.config.temperature),
            },
        };

        let response = self.http_client
            .post(format!("{}/api/generate", endpoint))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| format!("Ollama request failed: {}", e))?;

        let resp: OllamaResponse = response.json().await
            .map_err(|e| format!("Failed to parse Ollama response: {}", e))?;

        Ok(AIResponse {
            content: resp.response,
            provider: AIProvider::Ollama,
            model: self.config.model.clone(),
            tokens_used: resp.eval_count.unwrap_or(0),
            latency_ms: 0,
        })
    }

    async fn query_groq(&self, query: &AIQuery) -> Result<AIResponse, String> {
        let api_key = self.config.api_key.as_ref()
            .ok_or("Groq API key required")?;

        // Groq uses OpenAI-compatible API
        #[derive(Serialize)]
        struct GroqRequest {
            model: String,
            messages: Vec<GroqMessage>,
            max_tokens: u32,
            temperature: f32,
        }

        #[derive(Serialize)]
        struct GroqMessage {
            role: String,
            content: String,
        }

        #[derive(Deserialize)]
        struct GroqResponse {
            choices: Vec<GroqChoice>,
            usage: Option<GroqUsage>,
        }

        #[derive(Deserialize)]
        struct GroqChoice {
            message: GroqMessageResp,
        }

        #[derive(Deserialize)]
        struct GroqMessageResp {
            content: String,
        }

        #[derive(Deserialize)]
        struct GroqUsage {
            total_tokens: u32,
        }

        let mut messages = vec![];
        if let Some(ref system) = query.system_prompt {
            messages.push(GroqMessage {
                role: "system".to_string(),
                content: system.clone(),
            });
        }
        messages.push(GroqMessage {
            role: "user".to_string(),
            content: query.prompt.clone(),
        });

        let request = GroqRequest {
            model: self.config.model.clone(),
            messages,
            max_tokens: query.max_tokens.unwrap_or(self.config.max_tokens),
            temperature: query.temperature.unwrap_or(self.config.temperature),
        };

        let response = self.http_client
            .post("https://api.groq.com/openai/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", api_key))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| format!("Groq request failed: {}", e))?;

        let resp: GroqResponse = response.json().await
            .map_err(|e| format!("Failed to parse Groq response: {}", e))?;

        let content = resp.choices.first()
            .map(|c| c.message.content.clone())
            .ok_or("No response from Groq")?;

        Ok(AIResponse {
            content,
            provider: AIProvider::Groq,
            model: self.config.model.clone(),
            tokens_used: resp.usage.map(|u| u.total_tokens).unwrap_or(0),
            latency_ms: 0,
        })
    }

    async fn query_together(&self, query: &AIQuery) -> Result<AIResponse, String> {
        let api_key = self.config.api_key.as_ref()
            .ok_or("Together.ai API key required")?;

        // Together uses OpenAI-compatible API
        #[derive(Serialize)]
        struct TogetherRequest {
            model: String,
            messages: Vec<TogetherMessage>,
            max_tokens: u32,
            temperature: f32,
        }

        #[derive(Serialize)]
        struct TogetherMessage {
            role: String,
            content: String,
        }

        #[derive(Deserialize)]
        struct TogetherResponse {
            choices: Vec<TogetherChoice>,
            usage: Option<TogetherUsage>,
        }

        #[derive(Deserialize)]
        struct TogetherChoice {
            message: TogetherMessageResp,
        }

        #[derive(Deserialize)]
        struct TogetherMessageResp {
            content: String,
        }

        #[derive(Deserialize)]
        struct TogetherUsage {
            total_tokens: u32,
        }

        let mut messages = vec![];
        if let Some(ref system) = query.system_prompt {
            messages.push(TogetherMessage {
                role: "system".to_string(),
                content: system.clone(),
            });
        }
        messages.push(TogetherMessage {
            role: "user".to_string(),
            content: query.prompt.clone(),
        });

        let request = TogetherRequest {
            model: self.config.model.clone(),
            messages,
            max_tokens: query.max_tokens.unwrap_or(self.config.max_tokens),
            temperature: query.temperature.unwrap_or(self.config.temperature),
        };

        let response = self.http_client
            .post("https://api.together.xyz/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", api_key))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| format!("Together.ai request failed: {}", e))?;

        let resp: TogetherResponse = response.json().await
            .map_err(|e| format!("Failed to parse Together.ai response: {}", e))?;

        let content = resp.choices.first()
            .map(|c| c.message.content.clone())
            .ok_or("No response from Together.ai")?;

        Ok(AIResponse {
            content,
            provider: AIProvider::Together,
            model: self.config.model.clone(),
            tokens_used: resp.usage.map(|u| u.total_tokens).unwrap_or(0),
            latency_ms: 0,
        })
    }

    /// Solve a cognitive puzzle using AI
    pub async fn solve_puzzle(&self, puzzle_prompt: &str) -> Result<String, String> {
        let query = AIQuery {
            prompt: puzzle_prompt.to_string(),
            system_prompt: Some(
                "You are a cognitive puzzle solver. Answer briefly and directly. \
                 For pattern questions, give just the next number. \
                 For math questions, give just the number. \
                 For text questions, give a brief answer. \
                 No explanations unless asked.".to_string()
            ),
            max_tokens: Some(100),
            temperature: Some(0.3), // Lower temperature for accuracy
        };

        let response = self.query(&query).await?;
        Ok(response.content.trim().to_string())
    }

    /// Have a conversation with another AI agent
    pub async fn chat(&self, message: &str, context: Option<&str>) -> Result<String, String> {
        let system = format!(
            "You are an AI agent on the SmithNode P2P network. \
             You're communicating with other AI agents to validate transactions and share knowledge. \
             Be helpful, concise, and collaborative. {}",
            context.unwrap_or("")
        );

        let query = AIQuery {
            prompt: message.to_string(),
            system_prompt: Some(system),
            max_tokens: Some(500),
            temperature: Some(0.7),
        };

        let response = self.query(&query).await?;
        Ok(response.content)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_defaults() {
        let config = AIConfig::default();
        assert_eq!(config.provider, AIProvider::Ollama);
        assert_eq!(config.model, "llama2");
    }

    #[test]
    fn test_openai_config() {
        let config = AIConfig::openai("sk-test");
        assert_eq!(config.provider, AIProvider::OpenAI);
        assert!(config.api_key.is_some());
    }
}
