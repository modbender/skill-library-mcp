//! ClawChain RPC client tests

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_agent_did_parse() {
        let did = AgentDID::parse("did:claw:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12").unwrap();
        assert_eq!(did.as_str(), "did:claw:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12");
    }
    
    #[test]
    fn test_agent_did_generate() {
        let metadata = "{\"name\":\"test\"}";
        let owner = "0x1234567890abcdef1234567890abcdef1234567890";
        let did = AgentDID::generate(metadata.as_bytes(), owner);
        
        assert!(did.0.starts_with("did:claw:"));
        assert_eq!(did.0.len(), 10 + 64); // "did:claw:" + 64 hex chars
    }
    
    #[test]
    fn test_agent_did_parse_invalid() {
        let result = AgentDID::parse("did:eth:123456");
        assert!(result.is_err());
    }
    
    #[tokio::test]
    #[ignore = "requires running node"]
    async fn test_client_connection() {
        let client = ClawChainClient::new("ws://localhost:9944").await.unwrap();
        assert!(client.client.connection_status().is_connected());
    }
}
