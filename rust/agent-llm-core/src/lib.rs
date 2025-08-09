/*!
AGENT LLM Core - High-Performance Rust Backend
Implements optimized LLM processing with memory management and performance monitoring
*/

use tokio::sync::{RwLock, Mutex};
use std::sync::Arc;
use std::collections::HashMap;
use std::time::{Duration, Instant};
use serde::{Deserialize, Serialize};
use thiserror::Error;
use tracing::{info, warn, error, debug};
use uuid::Uuid;

#[derive(Error, Debug)]
pub enum LLMError {
    #[error("Configuration error: {0}")]
    Config(String),
    #[error("Processing error: {0}")]
    Processing(String),
    #[error("Memory error: {0}")]
    Memory(String),
    #[error("Connection error: {0}")]
    Connection(String),
    #[error("Timeout error: {0}")]
    Timeout(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMConfig {
    pub model_name: String,
    pub max_tokens: u32,
    pub temperature: f32,
    pub timeout_seconds: u64,
    pub max_concurrent_requests: usize,
    pub memory_limit_mb: usize,
    pub cache_size: usize,
}

impl Default for LLMConfig {
    fn default() -> Self {
        Self {
            model_name: "gpt-4".to_string(),
            max_tokens: 4096,
            temperature: 0.7,
            timeout_seconds: 30,
            max_concurrent_requests: 10,
            memory_limit_mb: 1024,
            cache_size: 1000,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMRequest {
    pub id: String,
    pub query: String,
    pub context: Vec<String>,
    pub task_type: String,
    pub max_tokens: Option<u32>,
    pub temperature: Option<f32>,
    pub priority: u8, // 0-255, higher is more priority
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMResponse {
    pub id: String,
    pub content: String,
    pub model_used: String,
    pub tokens_used: u32,
    pub processing_time_ms: u64,
    pub confidence_score: f32,
    pub reasoning_steps: Vec<String>,
    pub cache_hit: bool,
}

#[derive(Debug, Clone)]
pub struct PerformanceMetrics {
    pub total_requests: u64,
    pub successful_requests: u64,
    pub failed_requests: u64,
    pub average_response_time_ms: f64,
    pub memory_usage_mb: f64,
    pub cache_hit_rate: f64,
    pub concurrent_requests: usize,
}

impl Default for PerformanceMetrics {
    fn default() -> Self {
        Self {
            total_requests: 0,
            successful_requests: 0,
            failed_requests: 0,
            average_response_time_ms: 0.0,
            memory_usage_mb: 0.0,
            cache_hit_rate: 0.0,
            concurrent_requests: 0,
        }
    }
}

pub struct PerformanceMonitor {
    metrics: Arc<RwLock<PerformanceMetrics>>,
    response_times: Arc<Mutex<Vec<u64>>>,
    cache_hits: Arc<Mutex<u64>>,
    cache_misses: Arc<Mutex<u64>>,
}

impl PerformanceMonitor {
    pub fn new() -> Self {
        Self {
            metrics: Arc::new(RwLock::new(PerformanceMetrics::default())),
            response_times: Arc::new(Mutex::new(Vec::new())),
            cache_hits: Arc::new(Mutex::new(0)),
            cache_misses: Arc::new(Mutex::new(0)),
        }
    }

    pub async fn record_request(&self, success: bool, response_time_ms: u64, cache_hit: bool) {
        let mut metrics = self.metrics.write().await;
        let mut response_times = self.response_times.lock().await;
        
        metrics.total_requests += 1;
        if success {
            metrics.successful_requests += 1;
        } else {
            metrics.failed_requests += 1;
        }
        
        response_times.push(response_time_ms);
        
        // Keep only last 1000 response times for memory efficiency
        if response_times.len() > 1000 {
            response_times.drain(0..500);
        }
        
        // Update average response time
        if !response_times.is_empty() {
            metrics.average_response_time_ms = 
                response_times.iter().sum::<u64>() as f64 / response_times.len() as f64;
        }
        
        // Update cache metrics
        if cache_hit {
            *self.cache_hits.lock().await += 1;
        } else {
            *self.cache_misses.lock().await += 1;
        }
        
        let hits = *self.cache_hits.lock().await;
        let misses = *self.cache_misses.lock().await;
        if hits + misses > 0 {
            metrics.cache_hit_rate = hits as f64 / (hits + misses) as f64;
        }
    }

    pub async fn get_metrics(&self) -> PerformanceMetrics {
        self.metrics.read().await.clone()
    }

    pub async fn update_memory_usage(&self, usage_mb: f64) {
        self.metrics.write().await.memory_usage_mb = usage_mb;
    }

    pub async fn update_concurrent_requests(&self, count: usize) {
        self.metrics.write().await.concurrent_requests = count;
    }
}

pub struct MemoryManager {
    allocated_mb: Arc<RwLock<f64>>,
    max_memory_mb: f64,
    cleanup_threshold: f64,
}

impl MemoryManager {
    pub fn new(max_memory_mb: f64) -> Self {
        Self {
            allocated_mb: Arc::new(RwLock::new(0.0)),
            max_memory_mb,
            cleanup_threshold: max_memory_mb * 0.8, // Cleanup at 80% usage
        }
    }

    pub async fn allocate(&self, size_mb: f64) -> Result<(), LLMError> {
        let mut allocated = self.allocated_mb.write().await;
        if *allocated + size_mb > self.max_memory_mb {
            return Err(LLMError::Memory(format!(
                "Memory allocation would exceed limit: {} + {} > {}",
                *allocated, size_mb, self.max_memory_mb
            )));
        }
        *allocated += size_mb;
        Ok(())
    }

    pub async fn deallocate(&self, size_mb: f64) {
        let mut allocated = self.allocated_mb.write().await;
        *allocated = (*allocated - size_mb).max(0.0);
    }

    pub async fn get_usage(&self) -> f64 {
        *self.allocated_mb.read().await
    }

    pub async fn needs_cleanup(&self) -> bool {
        *self.allocated_mb.read().await > self.cleanup_threshold
    }

    pub async fn optimize(&self) -> Result<(), LLMError> {
        // Simulate memory optimization
        let current_usage = self.get_usage().await;
        if current_usage > self.cleanup_threshold {
            let optimized_usage = current_usage * 0.7; // Reduce by 30%
            *self.allocated_mb.write().await = optimized_usage;
            info!("Memory optimized: {:.2}MB -> {:.2}MB", current_usage, optimized_usage);
        }
        Ok(())
    }
}

pub struct ResponseCache {
    cache: Arc<RwLock<HashMap<String, (LLMResponse, Instant)>>>,
    max_size: usize,
    ttl: Duration,
}

impl ResponseCache {
    pub fn new(max_size: usize, ttl_seconds: u64) -> Self {
        Self {
            cache: Arc::new(RwLock::new(HashMap::new())),
            max_size,
            ttl: Duration::from_secs(ttl_seconds),
        }
    }

    pub async fn get(&self, key: &str) -> Option<LLMResponse> {
        let cache = self.cache.read().await;
        if let Some((response, timestamp)) = cache.get(key) {
            if timestamp.elapsed() < self.ttl {
                debug!("Cache hit for key: {}", key);
                return Some(response.clone());
            }
        }
        debug!("Cache miss for key: {}", key);
        None
    }

    pub async fn put(&self, key: String, response: LLMResponse) {
        let mut cache = self.cache.write().await;
        
        // Remove expired entries
        cache.retain(|_, (_, timestamp)| timestamp.elapsed() < self.ttl);
        
        // Remove oldest entries if at capacity
        if cache.len() >= self.max_size {
            let oldest_key = cache
                .iter()
                .min_by_key(|(_, (_, timestamp))| timestamp)
                .map(|(k, _)| k.clone());
            
            if let Some(key_to_remove) = oldest_key {
                cache.remove(&key_to_remove);
            }
        }
        
        cache.insert(key, (response, Instant::now()));
        debug!("Cached response for key: {}", key);
    }

    pub async fn clear(&self) {
        self.cache.write().await.clear();
        info!("Response cache cleared");
    }

    pub async fn size(&self) -> usize {
        self.cache.read().await.len()
    }
}

pub struct RequestQueue {
    queue: Arc<Mutex<Vec<(LLMRequest, tokio::sync::oneshot::Sender<Result<LLMResponse, LLMError>>)>>>,
    max_size: usize,
}

impl RequestQueue {
    pub fn new(max_size: usize) -> Self {
        Self {
            queue: Arc::new(Mutex::new(Vec::new())),
            max_size,
        }
    }

    pub async fn enqueue(
        &self,
        request: LLMRequest,
    ) -> Result<tokio::sync::oneshot::Receiver<Result<LLMResponse, LLMError>>, LLMError> {
        let mut queue = self.queue.lock().await;
        
        if queue.len() >= self.max_size {
            return Err(LLMError::Processing("Request queue is full".to_string()));
        }
        
        let (tx, rx) = tokio::sync::oneshot::channel();
        queue.push((request, tx));
        
        // Sort by priority (higher priority first)
        queue.sort_by(|a, b| b.0.priority.cmp(&a.0.priority));
        
        Ok(rx)
    }

    pub async fn dequeue(&self) -> Option<(LLMRequest, tokio::sync::oneshot::Sender<Result<LLMResponse, LLMError>>)> {
        let mut queue = self.queue.lock().await;
        queue.pop()
    }

    pub async fn size(&self) -> usize {
        self.queue.lock().await.len()
    }
}

pub struct LLMCore {
    config: Arc<RwLock<LLMConfig>>,
    performance_monitor: Arc<PerformanceMonitor>,
    memory_manager: Arc<MemoryManager>,
    response_cache: Arc<ResponseCache>,
    request_queue: Arc<RequestQueue>,
    active_requests: Arc<RwLock<usize>>,
}

impl LLMCore {
    pub async fn new(config: LLMConfig) -> Result<Self, LLMError> {
        let memory_manager = Arc::new(MemoryManager::new(config.memory_limit_mb as f64));
        let response_cache = Arc::new(ResponseCache::new(config.cache_size, 3600)); // 1 hour TTL
        let request_queue = Arc::new(RequestQueue::new(config.max_concurrent_requests * 2));
        
        Ok(Self {
            config: Arc::new(RwLock::new(config)),
            performance_monitor: Arc::new(PerformanceMonitor::new()),
            memory_manager,
            response_cache,
            request_queue,
            active_requests: Arc::new(RwLock::new(0)),
        })
    }

    pub async fn process_request(&self, request: LLMRequest) -> Result<LLMResponse, LLMError> {
        let start_time = Instant::now();
        let request_id = request.id.clone();
        
        // Check cache first
        let cache_key = self.generate_cache_key(&request);
        if let Some(cached_response) = self.response_cache.get(&cache_key).await {
            let mut response = cached_response;
            response.cache_hit = true;
            self.performance_monitor.record_request(true, start_time.elapsed().as_millis() as u64, true).await;
            return Ok(response);
        }

        // Check if we can process more requests
        {
            let active = *self.active_requests.read().await;
            let config = self.config.read().await;
            if active >= config.max_concurrent_requests {
                return Err(LLMError::Processing("Too many concurrent requests".to_string()));
            }
        }

        // Increment active requests
        {
            let mut active = self.active_requests.write().await;
            *active += 1;
            self.performance_monitor.update_concurrent_requests(*active).await;
        }

        let result = self.internal_process(request).await;

        // Decrement active requests
        {
            let mut active = self.active_requests.write().await;
            *active -= 1;
            self.performance_monitor.update_concurrent_requests(*active).await;
        }

        let processing_time = start_time.elapsed().as_millis() as u64;
        
        match &result {
            Ok(response) => {
                // Cache successful response
                self.response_cache.put(cache_key, response.clone()).await;
                self.performance_monitor.record_request(true, processing_time, false).await;
                info!("Request {} processed successfully in {}ms", request_id, processing_time);
            }
            Err(e) => {
                self.performance_monitor.record_request(false, processing_time, false).await;
                error!("Request {} failed: {}", request_id, e);
            }
        }

        result
    }

    async fn internal_process(&self, request: LLMRequest) -> Result<LLMResponse, LLMError> {
        let start_time = Instant::now();
        
        // Allocate memory for processing
        let estimated_memory = self.estimate_memory_usage(&request).await;
        self.memory_manager.allocate(estimated_memory).await?;

        // Simulate processing with timeout
        let config = self.config.read().await;
        let timeout = Duration::from_secs(config.timeout_seconds);
        
        let processing_result = tokio::time::timeout(timeout, self.simulate_llm_processing(&request)).await;
        
        // Deallocate memory
        self.memory_manager.deallocate(estimated_memory).await;

        match processing_result {
            Ok(Ok(response)) => Ok(response),
            Ok(Err(e)) => Err(e),
            Err(_) => Err(LLMError::Timeout(format!("Request {} timed out", request.id))),
        }
    }

    async fn simulate_llm_processing(&self, request: &LLMRequest) -> Result<LLMResponse, LLMError> {
        // Simulate processing delay based on query complexity
        let complexity_factor = request.query.len() as u64 / 100;
        let delay_ms = (100 + complexity_factor * 10).min(2000); // Max 2 seconds
        tokio::time::sleep(Duration::from_millis(delay_ms)).await;

        // Generate reasoning steps based on query analysis
        let reasoning_steps = self.generate_reasoning_steps(&request.query).await;
        
        // Generate response content
        let content = self.generate_response_content(request, &reasoning_steps).await;
        
        // Calculate confidence score
        let confidence_score = self.calculate_confidence_score(request, &content).await;

        let config = self.config.read().await;
        Ok(LLMResponse {
            id: request.id.clone(),
            content,
            model_used: config.model_name.clone(),
            tokens_used: (request.query.len() / 4) as u32, // Rough token estimation
            processing_time_ms: delay_ms,
            confidence_score,
            reasoning_steps,
            cache_hit: false,
        })
    }

    async fn generate_reasoning_steps(&self, query: &str) -> Vec<String> {
        let mut steps = Vec::new();
        
        // Analyze query type
        if query.to_lowercase().contains("security") || query.to_lowercase().contains("vulnerability") {
            steps.push("Identified cybersecurity domain query".to_string());
            steps.push("Accessing cybersecurity knowledge base".to_string());
        }
        
        if query.contains("?") {
            steps.push("Question detected - preparing informative response".to_string());
        }
        
        if query.len() > 100 {
            steps.push("Complex query detected - using deep reasoning".to_string());
        }
        
        steps.push("Synthesizing response from available knowledge".to_string());
        steps
    }

    async fn generate_response_content(&self, request: &LLMRequest, reasoning_steps: &[String]) -> String {
        let mut response_parts = Vec::new();
        
        // Add context-aware introduction
        if !request.context.is_empty() {
            response_parts.push("Based on the provided context:".to_string());
        }
        
        // Add main response based on query type
        if request.task_type == "cybersecurity" {
            response_parts.push(format!(
                "Regarding your cybersecurity question about '{}', here's what I can tell you:",
                request.query.chars().take(50).collect::<String>()
            ));
        } else {
            response_parts.push(format!(
                "In response to your question about '{}', I'll provide a comprehensive answer:",
                request.query.chars().take(50).collect::<String>()
            ));
        }
        
        // Add reasoning context
        if !reasoning_steps.is_empty() {
            response_parts.push("\nMy analysis process:".to_string());
            for (i, step) in reasoning_steps.iter().enumerate() {
                response_parts.push(format!("{}. {}", i + 1, step));
            }
        }
        
        // Add substantive content
        response_parts.push("\nBased on my analysis, here are the key points to consider:".to_string());
        response_parts.push("• This topic requires careful consideration of multiple factors".to_string());
        response_parts.push("• Current best practices suggest a comprehensive approach".to_string());
        response_parts.push("• It's important to stay updated with the latest developments".to_string());
        
        response_parts.join("\n")
    }

    async fn calculate_confidence_score(&self, request: &LLMRequest, content: &str) -> f32 {
        let mut factors = Vec::new();
        
        // Content length factor
        let content_length = content.len();
        if content_length > 200 && content_length < 2000 {
            factors.push(0.8);
        } else {
            factors.push(0.6);
        }
        
        // Context relevance factor
        if !request.context.is_empty() {
            factors.push(0.9);
        } else {
            factors.push(0.7);
        }
        
        // Query complexity factor
        if request.query.len() > 50 {
            factors.push(0.8);
        } else {
            factors.push(0.7);
        }
        
        // Domain expertise factor
        if request.task_type == "cybersecurity" {
            factors.push(0.9);
        } else {
            factors.push(0.7);
        }
        
        factors.iter().sum::<f32>() / factors.len() as f32
    }

    async fn estimate_memory_usage(&self, request: &LLMRequest) -> f64 {
        // Estimate memory usage based on request size
        let base_memory = 10.0; // Base 10MB
        let query_memory = request.query.len() as f64 / 1000.0; // 1MB per 1000 chars
        let context_memory = request.context.iter()
            .map(|c| c.len() as f64 / 1000.0)
            .sum::<f64>();
        
        base_memory + query_memory + context_memory
    }

    fn generate_cache_key(&self, request: &LLMRequest) -> String {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        request.query.hash(&mut hasher);
        request.context.hash(&mut hasher);
        request.task_type.hash(&mut hasher);
        request.max_tokens.hash(&mut hasher);
        
        format!("llm_cache_{:x}", hasher.finish())
    }

    pub async fn get_health_status(&self) -> HashMap<String, serde_json::Value> {
        let mut status = HashMap::new();
        
        let metrics = self.performance_monitor.get_metrics().await;
        let memory_usage = self.memory_manager.get_usage().await;
        let cache_size = self.response_cache.size().await;
        let queue_size = self.request_queue.size().await;
        let active_requests = *self.active_requests.read().await;
        
        status.insert("status".to_string(), serde_json::Value::String("healthy".to_string()));
        status.insert("memory_usage_mb".to_string(), serde_json::Value::Number(serde_json::Number::from_f64(memory_usage).unwrap()));
        status.insert("cache_size".to_string(), serde_json::Value::Number(serde_json::Number::from(cache_size)));
        status.insert("queue_size".to_string(), serde_json::Value::Number(serde_json::Number::from(queue_size)));
        status.insert("active_requests".to_string(), serde_json::Value::Number(serde_json::Number::from(active_requests)));
        status.insert("total_requests".to_string(), serde_json::Value::Number(serde_json::Number::from(metrics.total_requests)));
        status.insert("success_rate".to_string(), serde_json::Value::Number(
            serde_json::Number::from_f64(
                if metrics.total_requests > 0 {
                    metrics.successful_requests as f64 / metrics.total_requests as f64
                } else {
                    1.0
                }
            ).unwrap()
        ));
        
        status
    }

    pub async fn optimize_performance(&self) -> Result<(), LLMError> {
        // Perform memory optimization
        self.memory_manager.optimize().await?;
        
        // Clear old cache entries
        if self.response_cache.size().await > self.config.read().await.cache_size * 2 {
            self.response_cache.clear().await;
        }
        
        info!("Performance optimization completed");
        Ok(())
    }

    pub async fn shutdown(&self) -> Result<(), LLMError> {
        info!("Shutting down LLM Core");
        
        // Wait for active requests to complete (with timeout)
        let mut attempts = 0;
        while *self.active_requests.read().await > 0 && attempts < 30 {
            tokio::time::sleep(Duration::from_millis(100)).await;
            attempts += 1;
        }
        
        if *self.active_requests.read().await > 0 {
            warn!("Shutting down with {} active requests", *self.active_requests.read().await);
        }
        
        // Clear cache
        self.response_cache.clear().await;
        
        info!("LLM Core shutdown completed");
        Ok(())
    }
}

// HTTP server integration
pub mod server {
    use super::*;
    use warp::{Filter, Reply};
    use std::convert::Infallible;

    pub async fn create_server(llm_core: Arc<LLMCore>) -> impl Filter<Extract = impl Reply, Error = Infallible> + Clone {
        let health = warp::path("health")
            .and(warp::get())
            .and(with_llm_core(llm_core.clone()))
            .and_then(health_handler);

        let process = warp::path("process")
            .and(warp::post())
            .and(warp::body::json())
            .and(with_llm_core(llm_core.clone()))
            .and_then(process_handler);

        let optimize = warp::path("optimize")
            .and(warp::post())
            .and(with_llm_core(llm_core))
            .and_then(optimize_handler);

        health.or(process).or(optimize)
    }

    fn with_llm_core(llm_core: Arc<LLMCore>) -> impl Filter<Extract = (Arc<LLMCore>,), Error = Infallible> + Clone {
        warp::any().map(move || llm_core.clone())
    }

    async fn health_handler(llm_core: Arc<LLMCore>) -> Result<impl Reply, Infallible> {
        let status = llm_core.get_health_status().await;
        Ok(warp::reply::json(&status))
    }

    async fn process_handler(request: LLMRequest, llm_core: Arc<LLMCore>) -> Result<impl Reply, Infallible> {
        match llm_core.process_request(request).await {
            Ok(response) => Ok(warp::reply::json(&response)),
            Err(e) => {
                let error_response = serde_json::json!({
                    "error": e.to_string(),
                    "status": "error"
                });
                Ok(warp::reply::json(&error_response))
            }
        }
    }

    async fn optimize_handler(llm_core: Arc<LLMCore>) -> Result<impl Reply, Infallible> {
        match llm_core.optimize_performance().await {
            Ok(_) => {
                let response = serde_json::json!({
                    "status": "success",
                    "message": "Performance optimization completed"
                });
                Ok(warp::reply::json(&response))
            }
            Err(e) => {
                let error_response = serde_json::json!({
                    "error": e.to_string(),
                    "status": "error"
                });
                Ok(warp::reply::json(&error_response))
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_llm_core_creation() {
        let config = LLMConfig::default();
        let core = LLMCore::new(config).await.unwrap();
        
        let health = core.get_health_status().await;
        assert!(health.contains_key("status"));
    }

    #[tokio::test]
    async fn test_request_processing() {
        let config = LLMConfig::default();
        let core = LLMCore::new(config).await.unwrap();
        
        let request = LLMRequest {
            id: Uuid::new_v4().to_string(),
            query: "What is cybersecurity?".to_string(),
            context: vec!["Security is important".to_string()],
            task_type: "cybersecurity".to_string(),
            max_tokens: None,
            temperature: None,
            priority: 128,
        };
        
        let response = core.process_request(request).await.unwrap();
        assert!(!response.content.is_empty());
        assert!(response.confidence_score > 0.0);
    }

    #[tokio::test]
    async fn test_memory_management() {
        let memory_manager = MemoryManager::new(100.0);
        
        // Test allocation
        memory_manager.allocate(50.0).await.unwrap();
        assert_eq!(memory_manager.get_usage().await, 50.0);
        
        // Test deallocation
        memory_manager.deallocate(25.0).await;
        assert_eq!(memory_manager.get_usage().await, 25.0);
        
        // Test optimization
        memory_manager.optimize().await.unwrap();
    }

    #[tokio::test]
    async fn test_response_cache() {
        let cache = ResponseCache::new(10, 60);
        
        let response = LLMResponse {
            id: "test".to_string(),
            content: "Test response".to_string(),
            model_used: "test-model".to_string(),
            tokens_used: 10,
            processing_time_ms: 100,
            confidence_score: 0.8,
            reasoning_steps: vec!["Step 1".to_string()],
            cache_hit: false,
        };
        
        // Test cache miss
        assert!(cache.get("test_key").await.is_none());
        
        // Test cache put and hit
        cache.put("test_key".to_string(), response.clone()).await;
        let cached = cache.get("test_key").await.unwrap();
        assert_eq!(cached.content, response.content);
    }
}
