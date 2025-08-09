#!/usr/bin/env python3
"""
Nebius Integration Example for AGENT LLM System
Demonstrates how to use the enhanced LLM manager with Nebius prompt presets
"""

import asyncio
import os
import json
from typing import Dict, Any

# Import AGENT LLM components
from agent.enhanced_llm_integration import (
    EnhancedLLMManager, 
    EnhancedLLMConfig,
    get_enhanced_llm_manager
)
from agent.llm_integration import LLMRequest, BackendConfig, LLMConfig
from agent.nebius_integration import NebiusConfig

async def setup_enhanced_llm() -> EnhancedLLMManager:
    """Setup and initialize the enhanced LLM manager"""
    print("🚀 Setting up Enhanced LLM Manager with Nebius Integration...")
    
    # Load API key from environment
    api_key = os.getenv("NEBIUS_API_KEY")
    if not api_key:
        print("⚠️  NEBIUS_API_KEY not found in environment variables")
        print("   Using default key for demo purposes")
        api_key = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMTI4MTc3MTQ4ODU2MTMwNjAwMSIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTkxMjM4NTYyMiwidXVpZCI6IjM0NTRiN2YyLTBhMmEtNDIzOS1hZmM5LTY0NDQ4NzNjZTQxNyIsIm5hbWUiOiJBR0VOVCIsImV4cGlyZXNfYXQiOiIyMDMwLTA4LTA4VDAyOjEzOjQyKzAwMDAifQ.fXcYEMU8dNcXS2M6dtuUkWHy63V9rkR63AYWYWaeumk"
    
    # Create configuration
    config = EnhancedLLMConfig(
        backend_config=BackendConfig(
            python_enabled=True,
            rust_enabled=True,
            python_host="localhost",
            python_port=8000,
            rust_host="localhost",
            rust_port=8001
        ),
        llm_config=LLMConfig(
            model_name="deepseek-ai/DeepSeek-V3-0324-fast",
            max_tokens=2000,
            temperature=0.7
        ),
        nebius_config=NebiusConfig(
            api_key=api_key,
            base_url="https://api.studio.nebius.com"
        ),
        use_nebius_presets=True,
        fallback_to_local=True,
        auto_create_presets=True
    )
    
    # Create and initialize manager
    manager = EnhancedLLMManager(config)
    await manager.initialize()
    
    print("✅ Enhanced LLM Manager initialized successfully!")
    return manager

async def demonstrate_mode_capabilities(manager: EnhancedLLMManager):
    """Demonstrate capabilities for different modes"""
    print("\n🎯 Demonstrating Mode-Specific Capabilities...")
    
    modes = ["design", "security", "development", "analysis"]
    
    for mode in modes:
        print(f"\n--- {mode.upper()} MODE ---")
        capabilities = await manager.get_mode_capabilities(mode)
        print(f"Presets available: {capabilities['presets_available']}")
        print(f"Nebius integration: {capabilities['nebius_integration']}")
        print(f"Local backend: {capabilities['local_backend_available']}")
        
        if capabilities['presets']:
            preset = capabilities['presets'][0]
            print(f"Default preset: {preset['name']} ({preset['id'][:8]}...)")

async def test_design_mode(manager: EnhancedLLMManager):
    """Test design mode with UI/UX request"""
    print("\n🎨 Testing Design Mode...")
    
    request = LLMRequest(
        query="I need to design a modern cybersecurity dashboard. What design principles should I follow for displaying real-time threat data?",
        context=[
            "Target users: Security analysts and SOC teams",
            "Real-time data updates required",
            "Must work on large monitors and tablets",
            "Dark theme preferred for 24/7 monitoring"
        ],
        task_type="design"
    )
    
    print("📝 Request:", request.query[:80] + "...")
    response = await manager.process_request_enhanced(request)
    
    print("🤖 Response Preview:", response.content[:200] + "...")
    print(f"📊 Model: {response.model_used}")
    print(f"⏱️  Processing time: {response.processing_time:.2f}s")
    print(f"🎯 Confidence: {response.confidence_score:.2f}")

async def test_security_mode(manager: EnhancedLLMManager):
    """Test security mode with threat analysis"""
    print("\n🔒 Testing Security Mode...")
    
    request = LLMRequest(
        query="Analyze the security implications of using JWT tokens for API authentication in a React/Node.js application",
        context=[
            "Web application with React frontend",
            "Node.js Express backend",
            "RESTful API architecture",
            "User authentication required"
        ],
        task_type="security"
    )
    
    print("📝 Request:", request.query[:80] + "...")
    response = await manager.process_request_enhanced(request)
    
    print("🤖 Response Preview:", response.content[:200] + "...")
    print(f"📊 Model: {response.model_used}")
    print(f"⏱️  Processing time: {response.processing_time:.2f}s")
    print(f"🎯 Confidence: {response.confidence_score:.2f}")

async def test_development_mode(manager: EnhancedLLMManager):
    """Test development mode with code generation"""
    print("\n💻 Testing Development Mode...")
    
    request = LLMRequest(
        query="Create a TypeScript React component for a responsive navigation bar with mobile hamburger menu",
        context=[
            "Using React 18 with TypeScript",
            "Tailwind CSS for styling",
            "Mobile-first responsive design",
            "Accessibility considerations required"
        ],
        task_type="development"
    )
    
    print("📝 Request:", request.query[:80] + "...")
    response = await manager.process_request_enhanced(request)
    
    print("🤖 Response Preview:", response.content[:200] + "...")
    print(f"📊 Model: {response.model_used}")
    print(f"⏱️  Processing time: {response.processing_time:.2f}s")
    print(f"🎯 Confidence: {response.confidence_score:.2f}")

async def test_analysis_mode(manager: EnhancedLLMManager):
    """Test analysis mode with data analysis"""
    print("\n📊 Testing Analysis Mode...")
    
    request = LLMRequest(
        query="Analyze user engagement patterns from web analytics data and provide actionable insights",
        context=[
            "E-commerce website analytics",
            "Monthly active users: 50K",
            "Conversion rate: 2.3%",
            "High bounce rate on product pages"
        ],
        task_type="analysis"
    )
    
    print("📝 Request:", request.query[:80] + "...")
    response = await manager.process_request_enhanced(request)
    
    print("🤖 Response Preview:", response.content[:200] + "...")
    print(f"📊 Model: {response.model_used}")
    print(f"⏱️  Processing time: {response.processing_time:.2f}s")
    print(f"🎯 Confidence: {response.confidence_score:.2f}")

async def demonstrate_custom_preset_creation(manager: EnhancedLLMManager):
    """Demonstrate creating custom presets"""
    print("\n🛠️  Creating Custom Preset...")
    
    try:
        custom_preset = await manager.create_custom_preset(
            mode="development",
            name="React TypeScript Expert",
            system_prompt="""You are a React TypeScript expert with deep knowledge of modern React patterns, 
            TypeScript best practices, and component architecture. You write clean, type-safe, and performant code.""",
            user_template="""Development Request: {user_input}

Please provide:
1. Complete TypeScript React implementation
2. Type definitions and interfaces
3. Best practices and patterns used
4. Testing considerations

Context: {context}""",
            description="Specialized for React TypeScript development with modern patterns"
        )
        
        print(f"✅ Created custom preset: {custom_preset.name}")
        print(f"   ID: {custom_preset.id}")
        print(f"   Model: {custom_preset.model_id}")
        
    except Exception as e:
        print(f"❌ Failed to create custom preset: {e}")

async def show_system_status(manager: EnhancedLLMManager):
    """Display comprehensive system status"""
    print("\n📈 System Status...")
    
    status = await manager.get_system_status()
    
    print("\n--- LOCAL INTEGRATION ---")
    local_status = status.get("local_integration", {})
    print(f"Python Backend: {'✅ Active' if local_status.get('python_backend_active') else '❌ Inactive'}")
    print(f"Rust Backend: {'✅ Active' if local_status.get('rust_backend_active') else '❌ Inactive'}")
    
    print("\n--- NEBIUS INTEGRATION ---")
    nebius_status = status.get("nebius_integration", {})
    print(f"Health: {'✅ Healthy' if nebius_status.get('health') else '❌ Unhealthy'}")
    print(f"Presets Loaded: {nebius_status.get('presets_loaded', 0)}")
    print(f"Modes Configured: {nebius_status.get('modes_configured', 0)}")
    
    print("\n--- MODE STATISTICS ---")
    mode_stats = status.get("mode_statistics", {})
    for mode, stats in mode_stats.items():
        preset_count = stats.get("preset_count", 0)
        print(f"{mode.capitalize()}: {preset_count} presets")
    
    print("\n--- CONFIGURATION ---")
    config = status.get("configuration", {})
    print(f"Nebius Presets: {'✅ Enabled' if config.get('use_nebius_presets') else '❌ Disabled'}")
    print(f"Local Fallback: {'✅ Enabled' if config.get('fallback_to_local') else '❌ Disabled'}")
    print(f"Auto-Create Presets: {'✅ Enabled' if config.get('auto_create_presets') else '❌ Disabled'}")

async def performance_benchmark(manager: EnhancedLLMManager):
    """Run performance benchmark across different modes"""
    print("\n⚡ Performance Benchmark...")
    
    test_requests = [
        ("design", "Design a modern login form with good UX"),
        ("security", "Analyze password security best practices"),
        ("development", "Create a REST API endpoint in Node.js"),
        ("analysis", "Analyze website performance metrics")
    ]
    
    total_time = 0
    successful_requests = 0
    
    for mode, query in test_requests:
        print(f"\n🧪 Testing {mode} mode...")
        
        try:
            request = LLMRequest(
                query=query,
                context=["Benchmark test request"],
                task_type=mode
            )
            
            import time
            start_time = time.time()
            response = await manager.process_request_enhanced(request)
            end_time = time.time()
            
            processing_time = end_time - start_time
            total_time += processing_time
            successful_requests += 1
            
            print(f"   ⏱️  {processing_time:.2f}s")
            print(f"   🎯 Confidence: {response.confidence_score:.2f}")
            print(f"   📊 Model: {response.model_used}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    if successful_requests > 0:
        avg_time = total_time / successful_requests
        print(f"\n📊 Benchmark Results:")
        print(f"   Successful requests: {successful_requests}/{len(test_requests)}")
        print(f"   Average response time: {avg_time:.2f}s")
        print(f"   Total processing time: {total_time:.2f}s")

async def main():
    """Main example execution"""
    print("🤖 AGENT LLM System - Nebius Integration Example")
    print("=" * 60)
    
    try:
        # Setup enhanced LLM manager
        manager = await setup_enhanced_llm()
        
        # Demonstrate capabilities
        await demonstrate_mode_capabilities(manager)
        
        # Test different modes
        await test_design_mode(manager)
        await test_security_mode(manager)
        await test_development_mode(manager)
        await test_analysis_mode(manager)
        
        # Create custom preset
        await demonstrate_custom_preset_creation(manager)
        
        # Show system status
        await show_system_status(manager)
        
        # Run performance benchmark
        await performance_benchmark(manager)
        
        # Optimize performance
        print("\n🔧 Optimizing performance...")
        await manager.optimize_performance()
        print("✅ Performance optimization completed!")
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'manager' in locals():
            print("\n🧹 Shutting down Enhanced LLM Manager...")
            await manager.shutdown()
            print("✅ Shutdown completed!")
    
    print("\n🎉 Example execution completed!")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
