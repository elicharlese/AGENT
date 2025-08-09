"""
Nebius Prompt Presets API Integration
Provides prompt management and optimization for AGENT LLM system
"""

import asyncio
import aiohttp
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import os
from datetime import datetime, timedelta
import jwt

logger = logging.getLogger(__name__)

@dataclass
class NebiusConfig:
    """Configuration for Nebius API integration"""
    api_key: str
    base_url: str = "https://api.studio.nebius.com"
    public_backend_url: str = "https://api.studio.nebius.com/v1"
    timeout_seconds: int = 30
    max_retries: int = 3
    default_model: str = "deepseek-ai/DeepSeek-V3-0324-fast"

@dataclass
class PromptPreset:
    """Nebius prompt preset structure"""
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    system_prompt: str = ""
    user_prompt_template: str = ""
    model_id: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    mode: str = "general"  # Maps to our training data modes
    tags: List[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ChatMessage:
    """Chat message structure for Nebius API"""
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class ChatRequest:
    """Chat completion request structure"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False

@dataclass
class ChatResponse:
    """Chat completion response structure"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class NebiusAPIError(Exception):
    """Custom exception for Nebius API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class NebiusPromptManager:
    """Manages Nebius prompt presets and chat completions"""
    
    def __init__(self, config: NebiusConfig):
        self.config = config
        self.session = None
        self._setup_logging()
        self._validate_api_key()
    
    def _setup_logging(self):
        """Setup logging for Nebius integration"""
        handler = logging.FileHandler('agent/nebius_integration.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    def _validate_api_key(self):
        """Validate and decode the JWT API key"""
        try:
            # Decode JWT without verification to inspect payload
            decoded = jwt.decode(self.config.api_key, options={"verify_signature": False})
            logger.info(f"API key valid for user: {decoded.get('name', 'Unknown')}")
            logger.info(f"API key expires at: {decoded.get('expires_at', 'Unknown')}")
            
            # Check if key is expired
            exp_timestamp = decoded.get('exp')
            if exp_timestamp and datetime.utcnow().timestamp() > exp_timestamp:
                logger.warning("API key appears to be expired")
                
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid API key format: {e}")
            raise NebiusAPIError(f"Invalid API key: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self):
        """Initialize the HTTP session"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "AGENT-LLM-System/1.0"
                }
            )
        logger.info("Nebius API session initialized")
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("Nebius API session closed")
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to Nebius API with error handling and retries"""
        if not self.session:
            await self.initialize()
        
        url = f"{self.config.base_url}{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.request(method, url, json=data) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return response_data
                    elif response.status == 401:
                        raise NebiusAPIError("Authentication failed - check API key", response.status, response_data)
                    elif response.status == 429:
                        # Rate limiting - wait and retry
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise NebiusAPIError(f"API request failed: {response_data}", response.status, response_data)
                        
            except aiohttp.ClientError as e:
                if attempt == self.config.max_retries - 1:
                    raise NebiusAPIError(f"Network error: {e}")
                await asyncio.sleep(2 ** attempt)
        
        raise NebiusAPIError("Max retries exceeded")
    
    # Prompt Preset Management
    async def create_prompt_preset(self, preset: PromptPreset) -> PromptPreset:
        """Create a new prompt preset"""
        logger.info(f"Creating prompt preset: {preset.name}")
        
        preset_data = {
            "name": preset.name,
            "description": preset.description,
            "system_prompt": preset.system_prompt,
            "user_prompt_template": preset.user_prompt_template,
            "model_id": preset.model_id or self.config.default_model,
            "temperature": preset.temperature,
            "max_tokens": preset.max_tokens,
            "top_p": preset.top_p,
            "frequency_penalty": preset.frequency_penalty,
            "presence_penalty": preset.presence_penalty,
            "tags": preset.tags + [f"mode:{preset.mode}"]
        }
        
        try:
            response = await self._make_request("POST", "/v1/prompt-presets", preset_data)
            
            # Update preset with response data
            preset.id = response.get("id")
            preset.created_at = response.get("created_at")
            preset.updated_at = response.get("updated_at")
            
            logger.info(f"Prompt preset created successfully: {preset.id}")
            return preset
            
        except NebiusAPIError as e:
            logger.error(f"Failed to create prompt preset: {e}")
            raise
    
    async def get_prompt_preset(self, preset_id: str) -> PromptPreset:
        """Retrieve a prompt preset by ID"""
        logger.info(f"Retrieving prompt preset: {preset_id}")
        
        try:
            response = await self._make_request("GET", f"/v1/prompt-presets/{preset_id}")
            
            preset = PromptPreset(
                id=response.get("id"),
                name=response.get("name", ""),
                description=response.get("description", ""),
                system_prompt=response.get("system_prompt", ""),
                user_prompt_template=response.get("user_prompt_template", ""),
                model_id=response.get("model_id", ""),
                temperature=response.get("temperature", 0.7),
                max_tokens=response.get("max_tokens", 2048),
                top_p=response.get("top_p", 0.9),
                frequency_penalty=response.get("frequency_penalty", 0.0),
                presence_penalty=response.get("presence_penalty", 0.0),
                tags=response.get("tags", []),
                created_at=response.get("created_at"),
                updated_at=response.get("updated_at")
            )
            
            # Extract mode from tags
            for tag in preset.tags:
                if tag.startswith("mode:"):
                    preset.mode = tag.split(":", 1)[1]
                    break
            
            return preset
            
        except NebiusAPIError as e:
            logger.error(f"Failed to retrieve prompt preset: {e}")
            raise
    
    async def list_prompt_presets(self, mode: str = None, limit: int = 50) -> List[PromptPreset]:
        """List prompt presets, optionally filtered by mode"""
        logger.info(f"Listing prompt presets (mode: {mode}, limit: {limit})")
        
        params = {"limit": limit}
        if mode:
            params["tags"] = f"mode:{mode}"
        
        try:
            # Build query string
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"/v1/prompt-presets?{query_string}"
            
            response = await self._make_request("GET", endpoint)
            presets = []
            
            for item in response.get("data", []):
                preset = PromptPreset(
                    id=item.get("id"),
                    name=item.get("name", ""),
                    description=item.get("description", ""),
                    system_prompt=item.get("system_prompt", ""),
                    user_prompt_template=item.get("user_prompt_template", ""),
                    model_id=item.get("model_id", ""),
                    temperature=item.get("temperature", 0.7),
                    max_tokens=item.get("max_tokens", 2048),
                    top_p=item.get("top_p", 0.9),
                    frequency_penalty=item.get("frequency_penalty", 0.0),
                    presence_penalty=item.get("presence_penalty", 0.0),
                    tags=item.get("tags", []),
                    created_at=item.get("created_at"),
                    updated_at=item.get("updated_at")
                )
                
                # Extract mode from tags
                for tag in preset.tags:
                    if tag.startswith("mode:"):
                        preset.mode = tag.split(":", 1)[1]
                        break
                
                presets.append(preset)
            
            logger.info(f"Retrieved {len(presets)} prompt presets")
            return presets
            
        except NebiusAPIError as e:
            logger.error(f"Failed to list prompt presets: {e}")
            raise
    
    async def update_prompt_preset(self, preset: PromptPreset) -> PromptPreset:
        """Update an existing prompt preset"""
        if not preset.id:
            raise NebiusAPIError("Preset ID is required for updates")
        
        logger.info(f"Updating prompt preset: {preset.id}")
        
        preset_data = {
            "name": preset.name,
            "description": preset.description,
            "system_prompt": preset.system_prompt,
            "user_prompt_template": preset.user_prompt_template,
            "model_id": preset.model_id,
            "temperature": preset.temperature,
            "max_tokens": preset.max_tokens,
            "top_p": preset.top_p,
            "frequency_penalty": preset.frequency_penalty,
            "presence_penalty": preset.presence_penalty,
            "tags": preset.tags + [f"mode:{preset.mode}"]
        }
        
        try:
            response = await self._make_request("PUT", f"/v1/prompt-presets/{preset.id}", preset_data)
            preset.updated_at = response.get("updated_at")
            
            logger.info(f"Prompt preset updated successfully: {preset.id}")
            return preset
            
        except NebiusAPIError as e:
            logger.error(f"Failed to update prompt preset: {e}")
            raise
    
    async def delete_prompt_preset(self, preset_id: str) -> bool:
        """Delete a prompt preset"""
        logger.info(f"Deleting prompt preset: {preset_id}")
        
        try:
            await self._make_request("DELETE", f"/v1/prompt-presets/{preset_id}")
            logger.info(f"Prompt preset deleted successfully: {preset_id}")
            return True
            
        except NebiusAPIError as e:
            logger.error(f"Failed to delete prompt preset: {e}")
            raise
    
    # Chat Completions
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Perform chat completion using Nebius API"""
        logger.info(f"Performing chat completion with model: {request.model}")
        
        request_data = {
            "model": request.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
            "stream": request.stream
        }
        
        try:
            response = await self._make_request("POST", "/v1/chat/completions", request_data)
            
            chat_response = ChatResponse(
                id=response.get("id", ""),
                object=response.get("object", ""),
                created=response.get("created", 0),
                model=response.get("model", ""),
                choices=response.get("choices", []),
                usage=response.get("usage", {})
            )
            
            logger.info(f"Chat completion successful, tokens used: {chat_response.usage.get('total_tokens', 0)}")
            return chat_response
            
        except NebiusAPIError as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def chat_with_preset(self, preset_id: str, user_message: str, context: List[str] = None) -> str:
        """Perform chat completion using a specific prompt preset"""
        logger.info(f"Chat with preset: {preset_id}")
        
        try:
            # Get the prompt preset
            preset = await self.get_prompt_preset(preset_id)
            
            # Build messages
            messages = []
            
            # Add system prompt if available
            if preset.system_prompt:
                messages.append(ChatMessage(role="system", content=preset.system_prompt))
            
            # Add context if provided
            if context:
                context_message = "Context:\n" + "\n".join(context)
                messages.append(ChatMessage(role="system", content=context_message))
            
            # Format user message with template if available
            if preset.user_prompt_template:
                formatted_message = preset.user_prompt_template.format(user_input=user_message)
            else:
                formatted_message = user_message
            
            messages.append(ChatMessage(role="user", content=formatted_message))
            
            # Create chat request
            chat_request = ChatRequest(
                model=preset.model_id or self.config.default_model,
                messages=messages,
                temperature=preset.temperature,
                max_tokens=preset.max_tokens,
                top_p=preset.top_p,
                frequency_penalty=preset.frequency_penalty,
                presence_penalty=preset.presence_penalty
            )
            
            # Perform chat completion
            response = await self.chat_completion(chat_request)
            
            # Extract response content
            if response.choices and len(response.choices) > 0:
                return response.choices[0].get("message", {}).get("content", "")
            else:
                raise NebiusAPIError("No response content received")
                
        except NebiusAPIError as e:
            logger.error(f"Chat with preset failed: {e}")
            raise
    
    # Mode-specific preset management
    async def get_mode_presets(self, mode: str) -> List[PromptPreset]:
        """Get all prompt presets for a specific mode"""
        return await self.list_prompt_presets(mode=mode)
    
    async def create_mode_preset(self, mode: str, name: str, system_prompt: str, 
                               user_template: str = None, description: str = None) -> PromptPreset:
        """Create a prompt preset for a specific mode"""
        preset = PromptPreset(
            name=f"{mode.title()} - {name}",
            description=description or f"Prompt preset for {mode} mode",
            system_prompt=system_prompt,
            user_prompt_template=user_template or "{user_input}",
            model_id=self.config.default_model,
            mode=mode,
            tags=[f"mode:{mode}", "agent-generated"]
        )
        
        return await self.create_prompt_preset(preset)
    
    # Health and status
    async def health_check(self) -> Dict[str, Any]:
        """Check API health and connectivity"""
        try:
            # Simple API call to check connectivity
            await self._make_request("GET", "/v1/models")
            return {
                "status": "healthy",
                "api_accessible": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Global instance management
nebius_manager = None

def get_nebius_manager(config: NebiusConfig = None) -> NebiusPromptManager:
    """Get or create Nebius manager instance"""
    global nebius_manager
    if nebius_manager is None:
        if config is None:
            # Use environment variables or default config
            api_key = os.getenv("NEBIUS_API_KEY")
            if not api_key:
                raise NebiusAPIError("NEBIUS_API_KEY environment variable not set")
            config = NebiusConfig(api_key=api_key)
        nebius_manager = NebiusPromptManager(config)
    return nebius_manager

# Example usage and testing
async def main():
    """Example usage of Nebius integration"""
    # Initialize with provided API key
    api_key = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMTI4MTc3MTQ4ODU2MTMwNjAwMSIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTkxMjM4NTYyMiwidXVpZCI6IjM0NTRiN2YyLTBhMmEtNDIzOS1hZmM5LTY0NDQ4NzNjZTQxNyIsIm5hbWUiOiJBR0VOVCIsImV4cGlyZXNfYXQiOiIyMDMwLTA4LTA4VDAyOjEzOjQyKzAwMDAifQ.fXcYEMU8dNcXS2M6dtuUkWHy63V9rkR63AYWYWaeumk"
    
    config = NebiusConfig(api_key=api_key)
    
    async with NebiusPromptManager(config) as nebius:
        try:
            # Health check
            health = await nebius.health_check()
            print(f"Health Status: {health}")
            
            # Create a design mode preset
            design_preset = await nebius.create_mode_preset(
                mode="design",
                name="UI/UX Analysis",
                system_prompt="You are an expert UI/UX designer with deep knowledge of modern design principles, accessibility, and user experience optimization. Analyze designs with attention to visual hierarchy, usability, and aesthetic appeal.",
                user_template="Please analyze the following design request: {user_input}\n\nProvide specific, actionable feedback on:\n1. Visual hierarchy and layout\n2. User experience considerations\n3. Accessibility compliance\n4. Modern design best practices",
                description="Specialized prompt for UI/UX design analysis and feedback"
            )
            
            print(f"Created design preset: {design_preset.id}")
            
            # Test chat with preset
            response = await nebius.chat_with_preset(
                design_preset.id,
                "I'm designing a dashboard for a cybersecurity monitoring system. What are the key design principles I should follow?",
                context=["The dashboard will be used by security analysts", "It needs to display real-time threat data"]
            )
            
            print(f"Response: {response}")
            
        except NebiusAPIError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
