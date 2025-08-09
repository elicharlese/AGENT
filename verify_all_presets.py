#!/usr/bin/env python3
"""
Comprehensive verification script for all mode-specific presets
Ensures all 12 training data modes have properly configured presets
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Any, Optional

class PresetVerifier:
    """Verifies all mode-specific presets are created and working"""
    
    def __init__(self):
        self.api_key = os.getenv("NEBIUS_API_KEY", "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMTI4MTc3MTQ4ODU2MTMwNjAwMSIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTkxMjM4NTYyMiwidXVpZCI6IjM0NTRiN2YyLTBhMmEtNDIzOS1hZmM5LTY0NDQ4NzNjZTQxNyIsIm5hbWUiOiJBR0VOVCIsImV4cGlyZXNfYXQiOiIyMDMwLTA4LTA4VDAyOjEzOjQyKzAwMDAifQ.fXcYEMU8dNcXS2M6dtuUkWHy63V9rkR63AYWYWaeumk")
        self.base_url = "https://api.studio.nebius.com"
        self.session = None
        
        # All 12 training data modes with their configurations
        self.modes = {
            "design": {
                "model": "deepseek-ai/DeepSeek-V3-0324-fast",
                "system_prompt": "You are an expert UI/UX designer and 3D artist with deep knowledge of modern design principles, Spline 3D, React components, and user experience optimization. You excel at creating beautiful, functional, and accessible designs.",
                "test_query": "Design a modern dashboard for real-time analytics with good UX",
                "expected_keywords": ["design", "UI", "UX", "dashboard", "user experience"]
            },
            "security": {
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "system_prompt": "You are a cybersecurity expert with extensive knowledge of threat analysis, vulnerability assessment, penetration testing, and security architecture. You follow industry standards like OWASP, NIST, and ISO 27001.",
                "test_query": "Analyze potential security vulnerabilities in a web application",
                "expected_keywords": ["security", "vulnerability", "threat", "OWASP", "assessment"]
            },
            "development": {
                "model": "deepseek-ai/DeepSeek-V3-0324-fast",
                "system_prompt": "You are a senior software engineer with expertise in full-stack development, DevOps, cloud architecture, and modern programming languages. You write clean, efficient, and maintainable code.",
                "test_query": "Create a REST API endpoint for user authentication",
                "expected_keywords": ["API", "endpoint", "authentication", "code", "development"]
            },
            "analysis": {
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "system_prompt": "You are a data scientist and analyst with expertise in statistical analysis, machine learning, data visualization, and business intelligence. You turn data into actionable insights.",
                "test_query": "Analyze customer behavior patterns from e-commerce data",
                "expected_keywords": ["analysis", "data", "patterns", "insights", "statistics"]
            },
            "communication": {
                "model": "deepseek-ai/DeepSeek-V3-0324-fast",
                "system_prompt": "You are a communication expert specializing in technical writing, documentation, and human-AI interaction. You excel at making complex topics clear and accessible.",
                "test_query": "Write clear documentation for a new API feature",
                "expected_keywords": ["documentation", "communication", "clear", "technical", "writing"]
            },
            "automation": {
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "system_prompt": "You are an automation expert with deep knowledge of RPA, workflow optimization, process improvement, and intelligent automation systems. You identify and implement efficiency opportunities.",
                "test_query": "Design an automated workflow for invoice processing",
                "expected_keywords": ["automation", "workflow", "process", "efficiency", "optimization"]
            },
            "research": {
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "system_prompt": "You are a research specialist with expertise in information gathering, knowledge synthesis, systematic analysis, and academic research methodologies. You provide comprehensive and well-sourced insights.",
                "test_query": "Research the latest trends in artificial intelligence",
                "expected_keywords": ["research", "analysis", "trends", "information", "insights"]
            },
            "reasoning": {
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "system_prompt": "You are a logic and reasoning expert with deep knowledge of critical thinking, problem-solving methodologies, and decision-making frameworks. You approach problems systematically and analytically.",
                "test_query": "Solve this complex business decision using logical reasoning",
                "expected_keywords": ["reasoning", "logic", "analysis", "decision", "systematic"]
            },
            "creative": {
                "model": "deepseek-ai/DeepSeek-V3-0324-fast",
                "system_prompt": "You are a creative professional with expertise in content creation, storytelling, artistic generation, and innovative thinking. You generate original and engaging creative solutions.",
                "test_query": "Create an engaging story about AI and human collaboration",
                "expected_keywords": ["creative", "story", "content", "innovative", "engaging"]
            },
            "educational": {
                "model": "deepseek-ai/DeepSeek-V3-0324-fast",
                "system_prompt": "You are an educational expert with deep knowledge of pedagogy, instructional design, learning theories, and knowledge transfer. You make complex topics accessible and engaging.",
                "test_query": "Explain machine learning concepts to beginners",
                "expected_keywords": ["educational", "explain", "learning", "teaching", "concepts"]
            },
            "diagnostic": {
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "system_prompt": "You are a diagnostic expert with expertise in problem identification, root cause analysis, systematic troubleshooting, and issue resolution. You approach problems methodically.",
                "test_query": "Diagnose why a web application is running slowly",
                "expected_keywords": ["diagnostic", "problem", "troubleshooting", "analysis", "root cause"]
            },
            "optimization": {
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "system_prompt": "You are an optimization expert with deep knowledge of performance tuning, resource optimization, efficiency improvement, and system enhancement. You identify and implement optimization opportunities.",
                "test_query": "Optimize database performance for high-traffic applications",
                "expected_keywords": ["optimization", "performance", "efficiency", "tuning", "improvement"]
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def test_mode_preset(self, mode: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific mode preset"""
        result = {
            "mode": mode,
            "success": False,
            "response_length": 0,
            "keywords_found": [],
            "model_used": config["model"],
            "error": None
        }
        
        try:
            payload = {
                "model": config["model"],
                "messages": [
                    {"role": "system", "content": config["system_prompt"]},
                    {"role": "user", "content": config["test_query"]}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    result["success"] = True
                    result["response_length"] = len(content)
                    
                    # Check for expected keywords
                    content_lower = content.lower()
                    for keyword in config["expected_keywords"]:
                        if keyword.lower() in content_lower:
                            result["keywords_found"].append(keyword)
                    
                    print(f"✅ {mode.upper()} MODE: SUCCESS")
                    print(f"   Model: {config['model']}")
                    print(f"   Response length: {len(content)} chars")
                    print(f"   Keywords found: {len(result['keywords_found'])}/{len(config['expected_keywords'])}")
                    print(f"   Preview: {content[:150]}...")
                    
                else:
                    error_text = await response.text()
                    result["error"] = f"HTTP {response.status}: {error_text[:200]}"
                    print(f"❌ {mode.upper()} MODE: FAILED (Status: {response.status})")
                    print(f"   Error: {error_text[:100]}...")
                    
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ {mode.upper()} MODE: EXCEPTION - {e}")
        
        return result
    
    async def verify_all_presets(self) -> Dict[str, Any]:
        """Verify all mode presets are working"""
        print("🔍 Verifying All Mode-Specific Presets...")
        print("=" * 60)
        
        results = {}
        successful_modes = 0
        total_modes = len(self.modes)
        
        for mode, config in self.modes.items():
            print(f"\n🧪 Testing {mode.upper()} mode...")
            result = await self.test_mode_preset(mode, config)
            results[mode] = result
            
            if result["success"]:
                successful_modes += 1
            
            # Small delay between requests to be respectful to the API
            await asyncio.sleep(1)
        
        # Summary
        print(f"\n📊 VERIFICATION SUMMARY")
        print("=" * 40)
        print(f"Total modes tested: {total_modes}")
        print(f"Successful modes: {successful_modes}")
        print(f"Failed modes: {total_modes - successful_modes}")
        print(f"Success rate: {(successful_modes/total_modes)*100:.1f}%")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS")
        print("-" * 40)
        
        for mode, result in results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            keywords_ratio = f"{len(result['keywords_found'])}/{len(self.modes[mode]['expected_keywords'])}"
            
            print(f"{mode.capitalize():12} | {status} | Keywords: {keywords_ratio:5} | Model: {result['model_used']}")
            
            if result["error"]:
                print(f"             Error: {result['error'][:80]}...")
        
        # Failed modes details
        failed_modes = [mode for mode, result in results.items() if not result["success"]]
        if failed_modes:
            print(f"\n⚠️  FAILED MODES DETAILS")
            print("-" * 30)
            for mode in failed_modes:
                result = results[mode]
                print(f"• {mode.upper()}: {result['error']}")
        
        return {
            "total_modes": total_modes,
            "successful_modes": successful_modes,
            "failed_modes": total_modes - successful_modes,
            "success_rate": (successful_modes/total_modes)*100,
            "results": results,
            "all_presets_working": successful_modes == total_modes
        }
    
    async def create_preset_status_report(self, verification_results: Dict[str, Any]):
        """Create a comprehensive status report"""
        report_content = f"""# AGENT LLM Mode-Specific Presets Status Report
Generated: {asyncio.get_event_loop().time()}

## Summary
- **Total Modes**: {verification_results['total_modes']}
- **Successful Modes**: {verification_results['successful_modes']}
- **Failed Modes**: {verification_results['failed_modes']}
- **Success Rate**: {verification_results['success_rate']:.1f}%
- **All Presets Working**: {'✅ YES' if verification_results['all_presets_working'] else '❌ NO'}

## Mode Status Details

| Mode | Status | Model | Keywords Found | Response Length |
|------|--------|-------|----------------|-----------------|
"""
        
        for mode, result in verification_results['results'].items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            keywords_count = len(result.get('keywords_found', []))
            expected_count = len(self.modes[mode]['expected_keywords'])
            keywords_ratio = f"{keywords_count}/{expected_count}"
            response_length = result.get('response_length', 0)
            model = result.get('model_used', 'Unknown')
            
            report_content += f"| {mode.capitalize()} | {status} | {model} | {keywords_ratio} | {response_length} |\n"
        
        if verification_results['failed_modes'] > 0:
            report_content += f"\n## Failed Modes\n"
            for mode, result in verification_results['results'].items():
                if not result['success']:
                    report_content += f"- **{mode.upper()}**: {result.get('error', 'Unknown error')}\n"
        
        report_content += f"\n## Recommendations\n"
        if verification_results['all_presets_working']:
            report_content += "🎉 All mode-specific presets are working correctly! The AGENT LLM system is ready for production use with specialized prompts for each training data mode.\n"
        else:
            report_content += "⚠️ Some presets failed verification. Review the failed modes above and check:\n"
            report_content += "- API key validity and permissions\n"
            report_content += "- Network connectivity to Nebius API\n"
            report_content += "- Model availability and access\n"
            report_content += "- Rate limiting or quota issues\n"
        
        # Write report to file
        with open('/Users/elicharlese/CascadeProjects/AGENT/preset_verification_report.md', 'w') as f:
            f.write(report_content)
        
        print(f"\n📄 Status report saved to: preset_verification_report.md")

async def main():
    """Main verification execution"""
    print("🤖 AGENT LLM System - Complete Preset Verification")
    print("=" * 60)
    print("Testing all 12 mode-specific presets...")
    
    async with PresetVerifier() as verifier:
        verification_results = await verifier.verify_all_presets()
        await verifier.create_preset_status_report(verification_results)
        
        if verification_results['all_presets_working']:
            print(f"\n🎉 SUCCESS: All {verification_results['total_modes']} mode-specific presets are working correctly!")
            print("Your AGENT LLM system is fully configured with specialized prompts for each training data mode.")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: {verification_results['successful_modes']}/{verification_results['total_modes']} presets working")
            print("Review the failed modes and check the status report for details.")

if __name__ == "__main__":
    asyncio.run(main())
