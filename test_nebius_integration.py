#!/usr/bin/env python3
"""
Simple test script for Nebius integration
Tests the basic functionality without complex imports
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, Optional

class SimpleNebiusTest:
    """Simple test class for Nebius API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("NEBIUS_API_KEY", "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMTI4MTc3MTQ4ODU2MTMwNjAwMSIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTkxMjM4NTYyMiwidXVpZCI6IjM0NTRiN2YyLTBhMmEtNDIzOS1hZmM5LTY0NDQ4NzNjZTQxNyIsIm5hbWUiOiJBR0VOVCIsImV4cGlyZXNfYXQiOiIyMDMwLTA4LTA4VDAyOjEzOjQyKzAwMDAifQ.fXcYEMU8dNcXS2M6dtuUkWHy63V9rkR63AYWYWaeumk")
        self.base_url = "https://api.studio.nebius.com"
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> bool:
        """Test basic connectivity to Nebius API"""
        try:
            # Test with a simple chat completion
            payload = {
                "model": "deepseek-ai/DeepSeek-V3-0324-fast",
                "messages": [
                    {"role": "user", "content": "Hello, this is a connectivity test."}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
            
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Nebius API Health Check: SUCCESS")
                    print(f"   Response: {data.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:100]}...")
                    return True
                else:
                    print(f"❌ Nebius API Health Check: FAILED (Status: {response.status})")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
                    return False
                    
        except Exception as e:
            print(f"❌ Nebius API Health Check: EXCEPTION - {e}")
            return False
    
    async def test_design_mode_prompt(self) -> bool:
        """Test design mode with specialized prompt"""
        try:
            system_prompt = """You are an expert UI/UX designer and 3D artist with deep knowledge of modern design principles, Spline 3D, React components, and user experience optimization. You excel at creating beautiful, functional, and accessible designs."""
            
            user_query = "I need to design a modern cybersecurity dashboard. What design principles should I follow for displaying real-time threat data?"
            
            payload = {
                "model": "deepseek-ai/DeepSeek-V3-0324-fast",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"✅ Design Mode Test: SUCCESS")
                    print(f"   Query: {user_query[:80]}...")
                    print(f"   Response: {content[:200]}...")
                    return True
                else:
                    print(f"❌ Design Mode Test: FAILED (Status: {response.status})")
                    return False
                    
        except Exception as e:
            print(f"❌ Design Mode Test: EXCEPTION - {e}")
            return False
    
    async def test_security_mode_prompt(self) -> bool:
        """Test security mode with specialized prompt"""
        try:
            system_prompt = """You are a cybersecurity expert with extensive knowledge of threat analysis, vulnerability assessment, penetration testing, and security architecture. You follow industry standards like OWASP, NIST, and ISO 27001."""
            
            user_query = "Analyze the security implications of using JWT tokens for API authentication in a React/Node.js application"
            
            payload = {
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"✅ Security Mode Test: SUCCESS")
                    print(f"   Query: {user_query[:80]}...")
                    print(f"   Response: {content[:200]}...")
                    return True
                else:
                    print(f"❌ Security Mode Test: FAILED (Status: {response.status})")
                    return False
                    
        except Exception as e:
            print(f"❌ Security Mode Test: EXCEPTION - {e}")
            return False
    
    async def test_development_mode_prompt(self) -> bool:
        """Test development mode with specialized prompt"""
        try:
            system_prompt = """You are a senior software engineer with expertise in full-stack development, DevOps, cloud architecture, and modern programming languages. You write clean, efficient, and maintainable code."""
            
            user_query = "Create a TypeScript React component for a responsive navigation bar with mobile hamburger menu"
            
            payload = {
                "model": "deepseek-ai/DeepSeek-V3-0324-fast",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "max_tokens": 800,
                "temperature": 0.2
            }
            
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"✅ Development Mode Test: SUCCESS")
                    print(f"   Query: {user_query[:80]}...")
                    print(f"   Response: {content[:200]}...")
                    return True
                else:
                    print(f"❌ Development Mode Test: FAILED (Status: {response.status})")
                    return False
                    
        except Exception as e:
            print(f"❌ Development Mode Test: EXCEPTION - {e}")
            return False

async def main():
    """Main test execution"""
    print("🤖 AGENT LLM System - Nebius Integration Test")
    print("=" * 60)
    
    async with SimpleNebiusTest() as tester:
        # Test basic connectivity
        health_ok = await tester.health_check()
        
        if not health_ok:
            print("\n❌ Basic connectivity failed. Check your API key and network connection.")
            return
        
        print("\n🧪 Testing Mode-Specific Prompts...")
        
        # Test different modes
        design_ok = await tester.test_design_mode_prompt()
        security_ok = await tester.test_security_mode_prompt()
        development_ok = await tester.test_development_mode_prompt()
        
        # Summary
        print(f"\n📊 Test Results Summary:")
        print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"   Design Mode: {'✅ PASS' if design_ok else '❌ FAIL'}")
        print(f"   Security Mode: {'✅ PASS' if security_ok else '❌ FAIL'}")
        print(f"   Development Mode: {'✅ PASS' if development_ok else '❌ FAIL'}")
        
        total_tests = 4
        passed_tests = sum([health_ok, design_ok, security_ok, development_ok])
        
        print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Nebius integration is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
