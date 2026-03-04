//! ClawChain RPC client implementation
//! 
//! Connects to Substrate-based ClawChain node via WebSocket,
//! queries pallets, submits transactions, and subscribes to events.

use async_std::net::TcpStream;
use futures_util::{SinkExt, StreamExt};
use serde_json::{json, Value};
use sullivan::{
    jsonrpc::{OutboundRequest, OutboundRequestDetails},
    websocket_client::{WebSocketClient, WsMessage, wstr},
};
use url::Url;

use crate::error::{ClawChainError, Result};
use crate::types::{AgentDID, AgentInfo, Proposal, ChainEvent};

/// ClawChain RPC client
pub struct ClawChainClient {
    client: WebSocketClient<TcpStream>,
}

impl ClawChainClient {
    /// Connect to a ClawChain RPC endpoint
    ///
    /// # Arguments
    /// * `url` - WebSocket URL (e.g., "ws://localhost:9944")
    ///
    /// # Returns
    /// Connected client or error
    pub async fn new(url: &str) -> Result<Self> {
        let url = Url::parse(url)?;
        
        let client = WebSocketClient::new(url.clone(), |client| async move {
            let mut client = client;
            
            // Subscribe to chain finalized head
            let request = OutboundRequest {
                jsonrpc: wstr!("2.0"),
                method: wstr!("chain_subscribeFinalizedHeads"),
                params: vec![],
                id: 1,
            };
            client.send(request).await?;
            
            Ok(client)
        })
        .await
        .map_err(|e| ClawChainError::ConnectionError(e.to_string()))?;
        
        Ok(ClawChainClient { client })
    }
    
    /// Get agent information by DID
    pub async fn get_agent(&self, did: &str) -> Result<AgentInfo> {
        let storage_key = storage_key_for_agent(did);
        
        let request = OutboundRequest {
            jsonrpc: wstr!("2.0"),
            method: wstr!("state_getStorage"),
            params: vec![storage_key.into()],
            id: 1,
        };
        
        let response = self.client.send(request).await?;
        
        // Parse response (Scale-encoded storage data)
        let agent_info = parse_agent_storage(response)?;
        
        Ok(agent_info)
    }
    
    /// Get agent reputation score
    pub async fn get_agent_reputation(&self, did: &str) -> Result<u64> {
        let agent = self.get_agent(did).await?;
        Ok(agent.reputation)
    }
    
    /// Get CLAW token balance for an agent
    pub async fn get_token_balance(&self, did: &str) -> Result<u128> {
        let did_hash = AgentDID::parse(did)?;
        
        // Query ClawToken pallet balance mapping
        let storage_key = format!("0x{}", balance_key_for_did(did_hash.as_str()));
        
        let request = OutboundRequest {
            jsonrpc: wstr!("2.0"),
            method: wstr!("state_getStorage"),
            params: vec![storage_key.into()],
            id: 1,
        };
        
        let response = self.client.send(request).await?;
        let balance = parse_u128_storage(response)?;
        
        Ok(balance)
    }
    
    /// Register a new agent
    pub async fn register_agent(&self, metadata: &[u8]) -> Result<String> {
        let owner_address = get_owner_address()?;
        let did = AgentDID::generate(std::str::from_utf8(metadata)?, &owner_address);
        
        // Build extrinsic for agent registration
        let call_data = build_register_call(&did.0, metadata)?;
        
        let request = OutboundRequest {
            jsonrpc: wstr!("2.0"),
            method: wstr!("author_submitExtrinsic"),
            params: vec![call_data.into()],
            id: 1,
        };
        
        let response = self.client.send(request).await?;
        let tx_hash = parse_submit_response(response)?;
        
        Ok(did.0)
    }
    
    /// Vote on a governance proposal
    pub async fn vote(&self, proposal_id: u64, approve: bool) -> Result<()> {
        let call_data = build_vote_call(proposal_id, approve)?;
        
        let request = OutboundRequest {
            jsonrpc: wstr!("2.0"),
            method: wstr!("author_submitExtrinsic"),
            params: vec![call_data.into()],
            id: 1,
        };
        
        self.client.send(request).await?;
        Ok(())
    }
    
    /// Subscribe to chain events
    pub async fn subscribe_events<F>(&self, mut callback: F) -> Result<()>
    where
        F: FnMut(ChainEvent) + Send + 'static,
    {
        let mut stream = self.client.subscribe("chain_finalizedHead").await?;
        
        while let Some(msg) = stream.next().await {
            if let WsMessage::Text(text) = msg {
                if let Ok(event) = parse_chain_event(text) {
                    callback(event);
                }
            }
        }
        
        Ok(())
    }
    
    /// Submit a custom extrinsic
    pub async fn submit_extrinsic(&self, call_data: &str) -> Result<String> {
        let request = OutboundRequest {
            jsonrpc: wstr!("2.0"),
            method: wstr!("agent_submitExtrinsic"),
            params: vec![call_data.into()],
            id: 1,
        };
        
        let response = self.client.send(request).await?;
        let tx_hash = parse_submit_response(response)?;
        
        Ok(tx_hash)
    }
}

// Helper functions

fn storage_key_for_agent(did: &str) -> String {
    // AgentRegistry pallet storage map: Agents<DID, AgentInfo>
    // TwoXx64 concatenation of Blake2_256("Agents") + DID (as bytes)
    use sp_core::hash::blake2_256;
    
    let pallet_hash = blake2_256(b"Agents");
    let did_hash = blake_256(did.as_bytes());
    
    format!("{:064x}{:064x}", pallet_hash, did_hash)
}

fn balance_key_for_did(did: &str) -> String {
    // ClawToken pallet: AirdropAllocations<DID, Balance>
    use sp_core::hash::blake2_256;
    
    let pallet_hash = blake2_256(b"AirdropAllocations");
    let did_hash = blake2_256(did.as_bytes());
    
    format!("{:064x}{:064x}", pallet_hash, did_hash)
}

fn build_register_call(did: &str, metadata: &[u8]) -> Result<String> {
    // This is a simplified placeholder
    // In production, use Substrate SCALE encoding
    Ok(format!("0x{:02x}{:02x}", 0x01, did.len()).to_string())
}

fn build_vote_call(proposal_id: u64, approve: bool) -> Result<String> {
    // Simplified vote call encoding
    Ok(format!("0x{:02x}{:02x}", 0x02, proposal_id).to_string())
}

fn get_owner_address() -> Result<String> {
    // Load from config or environment
    std::env::var("CLAWCHAIN_OWNER")
        .or_else(|_| Ok("0x64e830dd7aF93431C898eA9e4C375C6706bd0Fc5".to_string()))
}

fn parse_agent_storage(response: String) -> Result<AgentInfo> {
    // Parse Scale-encoded AgentInfo
    // Placeholder: assumes JSON for simplicity
    serde_json::from_str(&response)
        .map_err(|e| ClawChainError::DeserializationError(e.to_string()))
}

fn parse_u128_storage(response: String) -> Result<u128> {
    // Parse Scale-encoded u128 balance
    if response.starts_with("0x") {
        let hex = &response[2..];
        let value = u128::from_str_radix(hex, 16)
            .map_err(|_| ClawChainError::DeserializationError("Invalid hex".into()))?;
        Ok(value)
    } else {
        serde_json::from_str::<u128>(&response)
            .map_err(|e| ClawChainError::DeserializationError(e.to_string()))
    }
}

fn parse_submit_response(response: String) -> Result<String> {
    let json: Value = serde_json::from_str(&response)
        .map_err(|e| ClawChainError::TransactionError(e.to_string()))?;
    
    json["result"]["extrinsic_hash"]
        .as_str()
        .map(|s| s.to_string())
        .ok_or_else(|| ClawChainError::TransactionError("No tx hash".into()))
}

fn parse_chain_event(text: String) -> Result<ChainEvent> {
    // Parse event from subscription
    let json: Value = serde_json::from_str(&text)?;
    
    match json["result"]["event"]["method"].as_str() {
        Some("AgentRegistered") => {
            Ok(ChainEvent::AgentRegistered {
                did: json["result"]["params"]["did"].as_str().unwrap().to_string()
            })
        }
        Some("ProposalExecuted") => {
            let id = json["result"]["params"]["proposal_id"]
                .as_u64().unwrap_or(0);
            let success = json["result"]["params"]["success"]
                .as_bool().unwrap_or(false);
            
            if success {
                Ok(ChainEvent::ProposalPassed { id })
            } else {
                Ok(ChainEvent::ProposalRejected { id })
            }
        }
        _ => Ok(ChainEvent::Block {
            number: json["result"]["params"]["number"].as_u64().unwrap_or(0),
            hash: json["result"]["params"]["hash"].as_str().unwrap().to_string()
        }),
    }
}
