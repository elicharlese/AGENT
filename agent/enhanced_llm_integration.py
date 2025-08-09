"""
Enhanced LLM Integration with Nebius Prompt Presets
Combines the existing LLM architecture with Nebius prompt management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import json

from .llm_integration import LLMIntegrationLayer, BackendConfig, LLMConfig, LLMRequest, LLMResponse
from .nebius_integration import NebiusPromptManager, NebiusConfig, PromptPreset, NebiusAPIError

logger = logging.getLogger(__name__)

@dataclass
class EnhancedLLMConfig:
    """Enhanced configuration combining local and Nebius capabilities"""
    # Local LLM configuration
    backend_config: BackendConfig
    llm_config: LLMConfig
    
    # Nebius configuration
    nebius_config: NebiusConfig
    
    # Integration settings
    use_nebius_presets: bool = True
    fallback_to_local: bool = True
    preset_cache_ttl: int = 3600  # 1 hour
    auto_create_presets: bool = True

class EnhancedLLMManager:
    """Enhanced LLM manager with Nebius prompt preset integration"""
    
    def __init__(self, config: EnhancedLLMConfig):
        self.config = config
        self.local_integration = LLMIntegrationLayer(
            config.backend_config, 
            config.llm_config
        )
        self.nebius_manager = NebiusPromptManager(config.nebius_config)
        self.preset_cache = {}
        self.mode_presets = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup enhanced logging"""
        handler = logging.FileHandler('agent/enhanced_llm_integration.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    async def initialize(self):
        """Initialize both local and Nebius integrations"""
        logger.info("Initializing Enhanced LLM Manager")
        
        # Initialize local integration
        await self.local_integration.initialize()
        
        # Initialize Nebius integration
        await self.nebius_manager.initialize()
        
        # Load and cache mode presets
        if self.config.use_nebius_presets:
            await self._load_mode_presets()
        
        # Auto-create missing presets if enabled
        if self.config.auto_create_presets:
            await self._ensure_mode_presets()
        
        logger.info("Enhanced LLM Manager initialized successfully")
    
    async def _load_mode_presets(self):
        """Load and cache prompt presets for all modes"""
        logger.info("Loading mode-specific prompt presets")
        
        # Define all training data modes
        modes = [
            "design", "security", "development", "analysis", 
            "communication", "automation", "research", "reasoning",
            "creative", "educational", "diagnostic", "optimization"
        ]
        
        for mode in modes:
            try:
                presets = await self.nebius_manager.get_mode_presets(mode)
                self.mode_presets[mode] = presets
                logger.info(f"Loaded {len(presets)} presets for {mode} mode")
            except NebiusAPIError as e:
                logger.warning(f"Failed to load presets for {mode} mode: {e}")
                self.mode_presets[mode] = []
    
    async def _ensure_mode_presets(self):
        """Ensure each mode has at least one default preset"""
        logger.info("Ensuring default presets exist for all modes")
        
        # Mode-specific system prompts
        mode_prompts = {
            "design": {
                "system_prompt": "You are an expert UI/UX designer and 3D artist with deep knowledge of modern design principles, Spline 3D, React components, and user experience optimization. You excel at creating beautiful, functional, and accessible designs.",
                "user_template": "Design Request: {user_input}\n\nPlease provide detailed guidance on:\n1. Visual design and aesthetics\n2. User experience considerations\n3. Technical implementation\n4. Accessibility and best practices",
                "description": "Specialized for UI/UX design, 3D modeling, and visual creation"
            },
            "security": {
                "system_prompt": "You are a cybersecurity expert with extensive knowledge of threat analysis, vulnerability assessment, penetration testing, and security architecture. You follow industry standards like OWASP, NIST, and ISO 27001.",
                "user_template": "Security Analysis: {user_input}\n\nPlease analyze and provide:\n1. Threat assessment and risk evaluation\n2. Vulnerability identification\n3. Mitigation strategies\n4. Compliance considerations",
                "description": "Specialized for cybersecurity analysis and threat detection"
            },
            "development": {
                "system_prompt": "You are a senior software engineer with expertise in full-stack development, DevOps, cloud architecture, and modern programming languages. You write clean, efficient, and maintainable code.",
                "user_template": "Development Task: {user_input}\n\nPlease provide:\n1. Technical approach and architecture\n2. Code examples and implementation\n3. Best practices and patterns\n4. Testing and deployment considerations",
                "description": "Specialized for software development and engineering"
            },
            "analysis": {
                "system_prompt": "You are a data scientist and analyst with expertise in statistical analysis, machine learning, data visualization, and business intelligence. You turn data into actionable insights.",
                "user_template": "Analysis Request: {user_input}\n\nPlease provide:\n1. Data analysis approach\n2. Statistical methods and techniques\n3. Visualization recommendations\n4. Business insights and recommendations",
                "description": "Specialized for data analysis and business intelligence"
            },
            "communication": {
                "system_prompt": "You are a communication expert specializing in technical writing, documentation, and human-AI interaction. You excel at making complex topics clear and accessible.",
                "user_template": "Communication Task: {user_input}\n\nPlease provide:\n1. Clear and structured explanation\n2. Appropriate tone and style\n3. Audience-specific adaptation\n4. Engagement and clarity optimization",
                "description": "Specialized for technical communication and documentation"
            },
            "automation": {
                "system_prompt": "You are an automation expert with deep knowledge of RPA, workflow optimization, process improvement, and intelligent automation systems. You identify and implement efficiency opportunities.",
                "user_template": "Automation Opportunity: {user_input}\n\nPlease analyze and provide:\n1. Process optimization opportunities\n2. Automation implementation strategy\n3. Tools and technologies recommendations\n4. ROI and efficiency improvements",
                "description": "Specialized for process automation and workflow optimization"
            },
            "research": {
                "system_prompt": "You are a research specialist with expertise in information gathering, knowledge synthesis, systematic analysis, and academic research methodologies. You provide comprehensive and well-sourced insights.",
                "user_template": "Research Query: {user_input}\n\nPlease provide:\n1. Comprehensive information gathering\n2. Source evaluation and synthesis\n3. Pattern identification and analysis\n4. Evidence-based conclusions",
                "description": "Specialized for research and knowledge synthesis"
            },
            "reasoning": {
                "system_prompt": "You are a logic and reasoning expert with deep knowledge of critical thinking, problem-solving methodologies, and decision-making frameworks. You approach problems systematically and analytically.",
                "user_template": "Reasoning Challenge: {user_input}\n\nPlease provide:\n1. Logical analysis and breakdown\n2. Problem-solving approach\n3. Evidence evaluation\n4. Reasoned conclusions and recommendations",
                "description": "Specialized for logical reasoning and problem-solving"
            },
            "creative": {
                "system_prompt": "You are a creative professional with expertise in content creation, storytelling, artistic generation, and innovative thinking. You generate original and engaging creative solutions.",
                "user_template": "Creative Brief: {user_input}\n\nPlease provide:\n1. Creative concept development\n2. Original content generation\n3. Artistic and aesthetic considerations\n4. Innovation and uniqueness",
                "description": "Specialized for creative content and artistic generation"
            },
            "educational": {
                "system_prompt": "You are an educational expert with deep knowledge of pedagogy, instructional design, learning theories, and knowledge transfer. You make complex topics accessible and engaging.",
                "user_template": "Educational Content: {user_input}\n\nPlease provide:\n1. Clear learning objectives\n2. Structured educational content\n3. Engagement and interaction strategies\n4. Assessment and evaluation methods",
                "description": "Specialized for teaching and knowledge transfer"
            },
            "diagnostic": {
                "system_prompt": "You are a diagnostic expert with expertise in problem identification, root cause analysis, systematic troubleshooting, and issue resolution. You approach problems methodically.",
                "user_template": "Diagnostic Request: {user_input}\n\nPlease provide:\n1. Problem identification and classification\n2. Root cause analysis\n3. Systematic troubleshooting approach\n4. Resolution recommendations",
                "description": "Specialized for problem diagnosis and troubleshooting"
            },
            "optimization": {
                "system_prompt": "You are an optimization expert with deep knowledge of performance tuning, resource optimization, efficiency improvement, and system enhancement. You identify and implement optimization opportunities.",
                "user_template": "Optimization Challenge: {user_input}\n\nPlease provide:\n1. Performance analysis and profiling\n2. Optimization opportunities identification\n3. Implementation strategies\n4. Performance improvement metrics",
                "description": "Specialized for performance optimization and efficiency"
            }
        }
        
        for mode, prompt_config in mode_prompts.items():
            # Check if mode has any presets
            if not self.mode_presets.get(mode):
                try:
                    preset = await self.nebius_manager.create_mode_preset(
                        mode=mode,
                        name="Default",
                        system_prompt=prompt_config["system_prompt"],
                        user_template=prompt_config["user_template"],
                        description=prompt_config["description"]
                    )
                    
                    # Add to cache
                    if mode not in self.mode_presets:
                        self.mode_presets[mode] = []
                    self.mode_presets[mode].append(preset)
                    
                    logger.info(f"Created default preset for {mode} mode: {preset.id}")
                    
                except NebiusAPIError as e:
                    logger.error(f"Failed to create default preset for {mode} mode: {e}")
    
    async def process_request_enhanced(self, request: LLMRequest, use_preset: bool = True) -> LLMResponse:
        """Process LLM request with enhanced capabilities"""
        logger.info(f"Processing enhanced request for mode: {request.task_type}")
        
        try:
            # Try Nebius with preset if enabled and available
            if use_preset and self.config.use_nebius_presets:
                preset_response = await self._process_with_preset(request)
                if preset_response:
                    return preset_response
            
            # Fallback to local integration
            if self.config.fallback_to_local:
                logger.info("Using local integration as fallback")
                return await self.local_integration.process_request(request)
            else:
                raise Exception("No available processing method")
                
        except Exception as e:
            logger.error(f"Enhanced request processing failed: {e}")
            
            # Final fallback to local integration
            if self.config.fallback_to_local:
                return await self.local_integration.process_request(request)
            else:
                raise
    
    async def _process_with_preset(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Process request using Nebius preset for the specified mode"""
        mode = request.task_type
        presets = self.mode_presets.get(mode, [])
        
        if not presets:
            logger.warning(f"No presets available for mode: {mode}")
            return None
        
        # Use the first (default) preset for the mode
        preset = presets[0]
        
        try:
            # Use Nebius chat with preset
            response_content = await self.nebius_manager.chat_with_preset(
                preset.id,
                request.query,
                context=request.context
            )
            
            # Convert to LLMResponse format
            return LLMResponse(
                content=response_content,
                model_used=f"nebius-{preset.model_id}",
                tokens_used=len(response_content.split()) * 1.3,  # Rough estimate
                processing_time=0.5,  # Placeholder
                confidence_score=0.9,  # High confidence for preset-based responses
                reasoning_steps=[f"Used Nebius preset: {preset.name} for {mode} mode"]
            )
            
        except NebiusAPIError as e:
            logger.error(f"Nebius preset processing failed: {e}")
            return None
    
    async def get_mode_capabilities(self, mode: str) -> Dict[str, Any]:
        """Get capabilities and presets for a specific mode"""
        presets = self.mode_presets.get(mode, [])
        
        return {
            "mode": mode,
            "presets_available": len(presets),
            "presets": [
                {
                    "id": preset.id,
                    "name": preset.name,
                    "description": preset.description,
                    "model": preset.model_id
                }
                for preset in presets
            ],
            "local_backend_available": True,
            "nebius_integration": self.config.use_nebius_presets
        }
    
    async def create_custom_preset(self, mode: str, name: str, system_prompt: str, 
                                 user_template: str = None, description: str = None) -> PromptPreset:
        """Create a custom preset for a specific mode"""
        preset = await self.nebius_manager.create_mode_preset(
            mode=mode,
            name=name,
            system_prompt=system_prompt,
            user_template=user_template,
            description=description
        )
        
        # Add to cache
        if mode not in self.mode_presets:
            self.mode_presets[mode] = []
        self.mode_presets[mode].append(preset)
        
        logger.info(f"Created custom preset for {mode} mode: {preset.id}")
        return preset
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Get local integration status
        local_status = await self.local_integration.get_system_status()
        
        # Get Nebius status
        nebius_health = await self.nebius_manager.health_check()
        
        # Compile mode statistics
        mode_stats = {}
        for mode, presets in self.mode_presets.items():
            mode_stats[mode] = {
                "preset_count": len(presets),
                "default_preset": presets[0].id if presets else None
            }
        
        return {
            "timestamp": local_status.get("timestamp"),
            "local_integration": local_status,
            "nebius_integration": {
                "health": nebius_health,
                "presets_loaded": sum(len(presets) for presets in self.mode_presets.values()),
                "modes_configured": len(self.mode_presets)
            },
            "mode_statistics": mode_stats,
            "configuration": {
                "use_nebius_presets": self.config.use_nebius_presets,
                "fallback_to_local": self.config.fallback_to_local,
                "auto_create_presets": self.config.auto_create_presets
            }
        }
    
    async def optimize_performance(self):
        """Optimize performance across all integrations"""
        logger.info("Optimizing enhanced LLM performance")
        
        # Optimize local integration
        await self.local_integration.optimize_performance()
        
        # Refresh preset cache
        await self._load_mode_presets()
        
        logger.info("Enhanced LLM performance optimization completed")
    
    async def shutdown(self):
        """Gracefully shutdown all integrations"""
        logger.info("Shutting down Enhanced LLM Manager")
        
        # Shutdown local integration
        await self.local_integration.shutdown()
        
        # Shutdown Nebius integration
        await self.nebius_manager.close()
        
        logger.info("Enhanced LLM Manager shutdown completed")

# Global enhanced manager instance
enhanced_llm_manager = None

def get_enhanced_llm_manager(config: EnhancedLLMConfig = None) -> EnhancedLLMManager:
    """Get or create enhanced LLM manager instance"""
    global enhanced_llm_manager
    if enhanced_llm_manager is None:
        if config is None:
            # Create default configuration
            from .llm_integration import BackendConfig, LLMConfig
            from .nebius_integration import NebiusConfig
            import os
            
            api_key = os.getenv("NEBIUS_API_KEY", "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMTI4MTc3MTQ4ODU2MTMwNjAwMSIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTkxMjM4NTYyMiwidXVpZCI6IjM0NTRiN2YyLTBhMmEtNDIzOS1hZmM5LTY0NDQ4NzNjZTQxNyIsIm5hbWUiOiJBR0VOVCIsImV4cGlyZXNfYXQiOiIyMDMwLTA4LTA4VDAyOjEzOjQyKzAwMDAifQ.fXcYEMU8dNcXS2M6dtuUkWHy63V9rkR63AYWYWaeumk")
            
            config = EnhancedLLMConfig(
                backend_config=BackendConfig(),
                llm_config=LLMConfig(),
                nebius_config=NebiusConfig(api_key=api_key)
            )
        
        enhanced_llm_manager = EnhancedLLMManager(config)
    
    return enhanced_llm_manager

# Example usage
async def main():
    """Example usage of enhanced LLM manager"""
    manager = get_enhanced_llm_manager()
    
    try:
        # Initialize
        await manager.initialize()
        
        # Test design mode request
        design_request = LLMRequest(
            query="I need to create a modern dashboard for cybersecurity monitoring. What design principles should I follow?",
            context=["The dashboard will be used by security analysts", "Real-time threat data display is required"],
            task_type="design"
        )
        
        response = await manager.process_request_enhanced(design_request)
        print(f"Design Response: {response.content[:200]}...")
        
        # Test security mode request
        security_request = LLMRequest(
            query="Analyze the security implications of using JWT tokens for API authentication",
            context=["Web application with React frontend", "Node.js backend API"],
            task_type="security"
        )
        
        response = await manager.process_request_enhanced(security_request)
        print(f"Security Response: {response.content[:200]}...")
        
        # Get system status
        status = await manager.get_system_status()
        print(f"System Status: {json.dumps(status, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
