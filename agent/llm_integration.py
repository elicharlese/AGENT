"""
AGENT LLM Integration Layer
Provides seamless integration between Python and Rust LLM backends
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import json
from .llm_manager import LLMSelfCareManager, LLMConfig, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)

@dataclass
class BackendConfig:
    """Configuration for backend services"""
    python_enabled: bool = True
    rust_enabled: bool = True
    rust_endpoint: str = "http://localhost:8001"
    fallback_to_python: bool = True
    load_balance: bool = True
    timeout_seconds: int = 30

class LLMIntegrationLayer:
    """Integration layer managing both Python and Rust LLM backends"""
    
    def __init__(self, backend_config: BackendConfig, llm_config: LLMConfig):
        self.backend_config = backend_config
        self.llm_config = llm_config
        self.python_manager = LLMSelfCareManager(llm_config) if backend_config.python_enabled else None
        self.rust_available = False
        self.request_count = 0
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup integration layer logging"""
        handler = logging.FileHandler('agent/llm_integration.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    async def initialize(self):
        """Initialize the integration layer and check backend availability"""
        logger.info("Initializing LLM Integration Layer")
        
        # Check Rust backend availability
        if self.backend_config.rust_enabled:
            self.rust_available = await self._check_rust_backend()
            if self.rust_available:
                logger.info("Rust backend is available")
            else:
                logger.warning("Rust backend is not available, falling back to Python only")
        
        logger.info("LLM Integration Layer initialized")
    
    async def _check_rust_backend(self) -> bool:
        """Check if Rust backend is available"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.backend_config.rust_endpoint}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        return health_data.get('status') == 'healthy'
            return False
        except Exception as e:
            logger.debug(f"Rust backend health check failed: {e}")
            return False
    
    async def process_request(self, request: LLMRequest) -> LLMResponse:
        """Process LLM request using the best available backend"""
        logger.info(f"Processing request {request.query[:50]}...")
        
        # Determine which backend to use
        backend_choice = await self._choose_backend(request)
        
        try:
            if backend_choice == "rust" and self.rust_available:
                return await self._process_with_rust(request)
            elif backend_choice == "python" and self.python_manager:
                return await self._process_with_python(request)
            else:
                # Fallback logic
                if self.python_manager:
                    logger.info("Using Python backend as fallback")
                    return await self._process_with_python(request)
                else:
                    raise Exception("No available backends for processing")
        
        except Exception as e:
            logger.error(f"Request processing failed with {backend_choice} backend: {e}")
            
            # Try fallback if enabled
            if self.backend_config.fallback_to_python and backend_choice != "python" and self.python_manager:
                logger.info("Attempting fallback to Python backend")
                return await self._process_with_python(request)
            else:
                raise
    
    async def _choose_backend(self, request: LLMRequest) -> str:
        """Choose the best backend for the request"""
        if not self.backend_config.load_balance:
            # Prefer Rust if available, otherwise Python
            return "rust" if self.rust_available else "python"
        
        # Load balancing logic
        self.request_count += 1
        
        # Use Rust for high-performance tasks
        if request.task_type in ["cybersecurity", "analysis", "complex"]:
            return "rust" if self.rust_available else "python"
        
        # Simple round-robin for other requests
        if self.request_count % 2 == 0 and self.rust_available:
            return "rust"
        else:
            return "python"
    
    async def _process_with_rust(self, request: LLMRequest) -> LLMResponse:
        """Process request using Rust backend"""
        logger.debug(f"Processing request {request.query[:30]}... with Rust backend")
        
        # Convert Python request to format expected by Rust
        rust_request = {
            "id": getattr(request, 'id', f"req_{self.request_count}"),
            "query": request.query,
            "context": request.context,
            "task_type": request.task_type,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "priority": 128  # Default priority
        }
        
        timeout = aiohttp.ClientTimeout(total=self.backend_config.timeout_seconds)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.backend_config.rust_endpoint}/process",
                json=rust_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Rust backend error: {response.status} - {error_text}")
                
                rust_response = await response.json()
                
                # Convert Rust response back to Python format
                return LLMResponse(
                    content=rust_response["content"],
                    model_used=rust_response["model_used"],
                    tokens_used=rust_response["tokens_used"],
                    processing_time=rust_response["processing_time_ms"] / 1000.0,
                    confidence_score=rust_response["confidence_score"],
                    reasoning_steps=rust_response["reasoning_steps"]
                )
    
    async def _process_with_python(self, request: LLMRequest) -> LLMResponse:
        """Process request using Python backend"""
        logger.debug(f"Processing request {request.query[:30]}... with Python backend")
        return await self.python_manager.process_with_self_care(request)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status from all backends"""
        status = {
            "timestamp": asyncio.get_event_loop().time(),
            "backends": {
                "python": {"enabled": self.backend_config.python_enabled, "available": self.python_manager is not None},
                "rust": {"enabled": self.backend_config.rust_enabled, "available": self.rust_available}
            },
            "configuration": asdict(self.backend_config),
            "request_count": self.request_count
        }
        
        # Get Python backend status
        if self.python_manager:
            try:
                python_status = await self.python_manager.get_system_status()
                status["backends"]["python"]["status"] = python_status
            except Exception as e:
                status["backends"]["python"]["error"] = str(e)
        
        # Get Rust backend status
        if self.rust_available:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    async with session.get(f"{self.backend_config.rust_endpoint}/health") as response:
                        if response.status == 200:
                            rust_status = await response.json()
                            status["backends"]["rust"]["status"] = rust_status
            except Exception as e:
                status["backends"]["rust"]["error"] = str(e)
        
        return status
    
    async def optimize_performance(self):
        """Optimize performance across all backends"""
        logger.info("Optimizing performance across all backends")
        
        # Optimize Python backend
        if self.python_manager:
            await self.python_manager.optimize_performance()
        
        # Optimize Rust backend
        if self.rust_available:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    async with session.post(f"{self.backend_config.rust_endpoint}/optimize") as response:
                        if response.status == 200:
                            logger.info("Rust backend optimization completed")
                        else:
                            logger.warning(f"Rust backend optimization failed: {response.status}")
            except Exception as e:
                logger.error(f"Rust backend optimization error: {e}")
        
        # Re-check backend availability
        if self.backend_config.rust_enabled:
            self.rust_available = await self._check_rust_backend()
        
        logger.info("Performance optimization completed")
    
    async def shutdown(self):
        """Gracefully shutdown the integration layer"""
        logger.info("Shutting down LLM Integration Layer")
        
        # No specific cleanup needed for Python backend (handled by manager)
        # Rust backend shutdown is handled by the Rust service itself
        
        logger.info("LLM Integration Layer shutdown completed")

# Global integration layer instance
integration_layer = None

def get_integration_layer(
    backend_config: Optional[BackendConfig] = None,
    llm_config: Optional[LLMConfig] = None
) -> LLMIntegrationLayer:
    """Get or create integration layer instance"""
    global integration_layer
    if integration_layer is None:
        integration_layer = LLMIntegrationLayer(
            backend_config or BackendConfig(),
            llm_config or LLMConfig()
        )
    return integration_layer

# Example usage and testing
async def main():
    """Example usage of the integration layer"""
    backend_config = BackendConfig(
        python_enabled=True,
        rust_enabled=True,
        fallback_to_python=True,
        load_balance=True
    )
    
    llm_config = LLMConfig(
        model_name="gpt-4",
        max_tokens=2048,
        temperature=0.7
    )
    
    # Initialize integration layer
    integration = get_integration_layer(backend_config, llm_config)
    await integration.initialize()
    
    # Test request
    request = LLMRequest(
        query="What are the latest cybersecurity threats and how can we mitigate them?",
        context=["Security is critical", "Recent attacks have increased"],
        task_type="cybersecurity"
    )
    
    try:
        response = await integration.process_request(request)
        print(f"Response: {response.content[:200]}...")
        print(f"Backend used: {response.model_used}")
        print(f"Confidence: {response.confidence_score}")
        
        # Get system status
        status = await integration.get_system_status()
        print(f"System Status: {json.dumps(status, indent=2)}")
        
        # Optimize performance
        await integration.optimize_performance()
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await integration.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
