/*!
AGENT LLM Core Server
High-performance Rust backend for LLM processing with RAISE framework integration
*/

use agent_llm_core::{LLMCore, LLMConfig, LLMRequest};
use std::sync::Arc;
use tracing::{info, error};
use uuid::Uuid;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt::init();
    
    info!("Starting AGENT LLM Core Server");
    
    // Load configuration
    let config = LLMConfig {
        model_name: "gpt-4".to_string(),
        max_tokens: 4096,
        temperature: 0.7,
        timeout_seconds: 30,
        max_concurrent_requests: 10,
        memory_limit_mb: 1024,
        cache_size: 1000,
    };
    
    // Initialize LLM Core
    let llm_core = match LLMCore::new(config).await {
        Ok(core) => Arc::new(core),
        Err(e) => {
            error!("Failed to initialize LLM Core: {}", e);
            return Err(e.into());
        }
    };
    
    info!("LLM Core initialized successfully");
    
    // Create HTTP server
    let server = agent_llm_core::server::create_server(llm_core.clone()).await;
    
    // Add CORS support
    let cors = warp::cors()
        .allow_any_origin()
        .allow_headers(vec!["content-type", "authorization"])
        .allow_methods(vec!["GET", "POST", "PUT", "DELETE", "OPTIONS"]);
    
    let routes = server
        .with(cors)
        .with(warp::log("agent_llm_core"));
    
    // Start server
    let port = std::env::var("LLM_SERVER_PORT")
        .unwrap_or_else(|_| "8001".to_string())
        .parse::<u16>()
        .unwrap_or(8001);
    
    info!("Starting LLM server on port {}", port);
    
    // Graceful shutdown handling
    let (shutdown_tx, shutdown_rx) = tokio::sync::oneshot::channel();
    
    // Handle shutdown signals
    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.expect("Failed to listen for ctrl+c");
        info!("Received shutdown signal");
        let _ = shutdown_tx.send(());
    });
    
    // Start the server with graceful shutdown
    let server_future = warp::serve(routes)
        .bind_with_graceful_shutdown(([127, 0, 0, 1], port), async {
            shutdown_rx.await.ok();
        });
    
    // Run server
    server_future.await;
    
    // Perform cleanup
    info!("Shutting down LLM Core");
    if let Err(e) = llm_core.shutdown().await {
        error!("Error during shutdown: {}", e);
    }
    
    info!("AGENT LLM Core Server stopped");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_server_initialization() {
        let config = LLMConfig::default();
        let llm_core = LLMCore::new(config).await.unwrap();
        
        // Test that the core can process a simple request
        let request = LLMRequest {
            id: Uuid::new_v4().to_string(),
            query: "Test query".to_string(),
            context: vec![],
            task_type: "test".to_string(),
            max_tokens: None,
            temperature: None,
            priority: 128,
        };
        
        let response = llm_core.process_request(request).await.unwrap();
        assert!(!response.content.is_empty());
    }
}
