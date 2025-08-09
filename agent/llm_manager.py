"""
AGENT LLM Manager with Self-Care Architecture
Implements robust connection management and RAISE framework integration
"""

import asyncio
import logging
import time
import sqlite3
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import backoff

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM operations"""
    model_name: str = "gpt-4"
    fallback_model: str = "gpt-3.5-turbo"
    max_tokens: int = 4096
    temperature: float = 0.7
    connection_timeout: int = 30
    retry_attempts: int = 3
    pool_size: int = 10

@dataclass
class LLMRequest:
    """LLM request structure"""
    query: str
    context: List[str]
    task_type: str = "general"
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str
    model_used: str
    tokens_used: int
    processing_time: float
    confidence_score: float
    reasoning_steps: List[str]

class PerformanceTracker:
    """Track LLM performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'response_times': [],
            'error_types': {}
        }
    
    def record_request(self, success: bool, response_time: float, error_type: str = None):
        """Record request metrics"""
        self.metrics['total_requests'] += 1
        self.metrics['response_times'].append(response_time)
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
            if error_type:
                self.metrics['error_types'][error_type] = self.metrics['error_types'].get(error_type, 0) + 1
        
        # Update average response time
        self.metrics['average_response_time'] = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        total = self.metrics['total_requests']
        if total == 0:
            return {'status': 'healthy', 'success_rate': 1.0}
        
        success_rate = self.metrics['successful_requests'] / total
        status = 'healthy' if success_rate > 0.95 else 'degraded' if success_rate > 0.8 else 'unhealthy'
        
        return {
            'status': status,
            'success_rate': success_rate,
            'average_response_time': self.metrics['average_response_time'],
            'total_requests': total,
            'recent_errors': list(self.metrics['error_types'].keys())[-5:]
        }

class HealthMonitor:
    """Monitor system health and auto-recovery"""
    
    def __init__(self):
        self.connection_status = {'python': True, 'rust': True, 'database': True}
        self.last_health_check = time.time()
        self.health_check_interval = 60  # seconds
    
    @asynccontextmanager
    async def track_request(self):
        """Context manager for request tracking"""
        start_time = time.time()
        try:
            yield
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
        finally:
            end_time = time.time()
            logger.info(f"Request completed in {end_time - start_time:.2f}s")
    
    async def check_health(self) -> Dict[str, bool]:
        """Perform comprehensive health check"""
        current_time = time.time()
        if current_time - self.last_health_check < self.health_check_interval:
            return self.connection_status
        
        # Check database connection
        try:
            conn = sqlite3.connect('cybersec_knowledge.db', timeout=5)
            conn.execute('SELECT 1')
            conn.close()
            self.connection_status['database'] = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            self.connection_status['database'] = False
        
        # Check Rust backend (if available)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get('http://localhost:8001/health') as response:
                    self.connection_status['rust'] = response.status == 200
        except Exception:
            self.connection_status['rust'] = False
        
        self.last_health_check = current_time
        return self.connection_status

class RAISEFramework:
    """Implementation of RAISE framework components"""
    
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.working_memory = {}
        self.example_pool = []
        self.task_trajectory = []
    
    async def reason(self, query: str, context: List[str]) -> Dict[str, Any]:
        """Reasoning component - analyze query and generate reasoning steps"""
        reasoning_steps = []
        
        # Analyze query complexity
        query_analysis = {
            'complexity': 'high' if len(query.split()) > 20 else 'medium' if len(query.split()) > 10 else 'low',
            'domain': self._identify_domain(query),
            'requires_tools': self._requires_tools(query),
            'context_relevance': self._assess_context_relevance(query, context)
        }
        
        reasoning_steps.append(f"Query analysis: {query_analysis}")
        
        # Generate reasoning strategy
        strategy = self._generate_reasoning_strategy(query_analysis)
        reasoning_steps.append(f"Reasoning strategy: {strategy}")
        
        return {
            'reasoning_steps': reasoning_steps,
            'strategy': strategy,
            'analysis': query_analysis
        }
    
    async def act(self, reasoning_result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Acting component - execute actions based on reasoning"""
        actions_taken = []
        results = {}
        
        strategy = reasoning_result.get('strategy', {})
        
        # Execute knowledge base search if needed
        if strategy.get('search_knowledge_base', False):
            kb_results = await self._search_knowledge_base(query)
            results['knowledge_base'] = kb_results
            actions_taken.append('knowledge_base_search')
        
        # Execute tool usage if needed
        if strategy.get('use_tools', False):
            tool_results = await self._use_tools(query, reasoning_result)
            results['tools'] = tool_results
            actions_taken.append('tool_usage')
        
        return {
            'actions_taken': actions_taken,
            'results': results
        }
    
    async def iterate(self, previous_results: Dict[str, Any]) -> bool:
        """Iterating component - determine if more iterations are needed"""
        # Simple iteration logic - can be enhanced
        confidence = previous_results.get('confidence_score', 0.8)
        return confidence < 0.7
    
    async def synthesize(self, reasoning: Dict[str, Any], actions: Dict[str, Any], query: str) -> str:
        """Synthesizing component - combine results into coherent response"""
        synthesis_parts = []
        
        # Add reasoning context
        if reasoning.get('reasoning_steps'):
            synthesis_parts.append("Based on my analysis:")
            for step in reasoning['reasoning_steps'][:2]:  # Limit to key steps
                synthesis_parts.append(f"- {step}")
        
        # Add action results
        if actions.get('results', {}).get('knowledge_base'):
            kb_results = actions['results']['knowledge_base']
            if kb_results:
                synthesis_parts.append(f"\nFrom the knowledge base, I found {len(kb_results)} relevant entries:")
                for result in kb_results[:3]:  # Limit to top 3
                    synthesis_parts.append(f"- {result.get('summary', result.get('content', '')[:100])}...")
        
        # Generate final response
        response = "\n".join(synthesis_parts)
        if not response:
            response = f"I understand your query: '{query}'. Let me provide a comprehensive response based on available information."
        
        return response
    
    async def evaluate(self, response: str, original_query: str) -> float:
        """Evaluating component - assess response quality"""
        # Simple evaluation metrics - can be enhanced with ML models
        factors = []
        
        # Length appropriateness
        response_length = len(response)
        if 50 <= response_length <= 2000:
            factors.append(0.8)
        else:
            factors.append(0.5)
        
        # Query relevance (simple keyword matching)
        query_words = set(original_query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words.intersection(response_words))
        relevance_score = min(overlap / len(query_words) if query_words else 0, 1.0)
        factors.append(relevance_score)
        
        # Structure quality
        has_structure = any(marker in response for marker in [':', '-', '1.', '2.', '\n'])
        factors.append(0.8 if has_structure else 0.6)
        
        return sum(factors) / len(factors)
    
    def _identify_domain(self, query: str) -> str:
        """Identify the domain of the query"""
        cybersec_keywords = ['security', 'vulnerability', 'attack', 'malware', 'encryption', 'firewall']
        tech_keywords = ['programming', 'code', 'software', 'development', 'algorithm']
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in cybersec_keywords):
            return 'cybersecurity'
        elif any(keyword in query_lower for keyword in tech_keywords):
            return 'technology'
        else:
            return 'general'
    
    def _requires_tools(self, query: str) -> bool:
        """Determine if query requires tool usage"""
        tool_indicators = ['calculate', 'search', 'find', 'analyze', 'generate', 'create']
        return any(indicator in query.lower() for indicator in tool_indicators)
    
    def _assess_context_relevance(self, query: str, context: List[str]) -> float:
        """Assess how relevant the context is to the query"""
        if not context:
            return 0.0
        
        query_words = set(query.lower().split())
        context_words = set()
        for ctx in context:
            context_words.update(ctx.lower().split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(context_words))
        return overlap / len(query_words)
    
    def _generate_reasoning_strategy(self, analysis: Dict[str, Any]) -> Dict[str, bool]:
        """Generate reasoning strategy based on analysis"""
        strategy = {
            'search_knowledge_base': analysis['domain'] in ['cybersecurity', 'technology'],
            'use_tools': analysis['requires_tools'],
            'deep_reasoning': analysis['complexity'] == 'high',
            'context_integration': analysis['context_relevance'] > 0.3
        }
        return strategy
    
    async def _search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information"""
        try:
            conn = sqlite3.connect(self.knowledge_base_path)
            cursor = conn.cursor()
            
            # Simple text search - can be enhanced with vector search
            cursor.execute("""
                SELECT title, content, category 
                FROM knowledge_entries 
                WHERE content LIKE ? OR title LIKE ?
                LIMIT 5
            """, (f'%{query}%', f'%{query}%'))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'title': row[0],
                    'content': row[1],
                    'category': row[2],
                    'summary': row[1][:200] + '...' if len(row[1]) > 200 else row[1]
                })
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            return []
    
    async def _use_tools(self, query: str, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Use appropriate tools based on query and reasoning"""
        # Placeholder for tool usage - integrate with existing tool system
        return {
            'tools_used': ['knowledge_search'],
            'results': 'Tool execution completed'
        }

class LLMSelfCareManager:
    """Main LLM manager with self-care capabilities"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.health_monitor = HealthMonitor()
        self.performance_tracker = PerformanceTracker()
        self.raise_framework = RAISEFramework('cybersec_knowledge.db')
        self.executor = ThreadPoolExecutor(max_workers=config.pool_size)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        handler = logging.FileHandler('agent/llm_manager.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def process_with_self_care(self, request: LLMRequest) -> LLMResponse:
        """Process request with full self-care monitoring"""
        start_time = time.time()
        
        async with self.health_monitor.track_request():
            try:
                # Check system health
                health_status = await self.health_monitor.check_health()
                if not health_status['python']:
                    raise Exception("Python backend unhealthy")
                
                # Process using RAISE framework
                response = await self._process_with_raise(request)
                
                # Record successful processing
                processing_time = time.time() - start_time
                self.performance_tracker.record_request(True, processing_time)
                
                return response
                
            except Exception as e:
                # Handle error and attempt recovery
                processing_time = time.time() - start_time
                self.performance_tracker.record_request(False, processing_time, str(type(e).__name__))
                
                logger.error(f"Request processing failed: {e}")
                return await self._fallback_response(request)
    
    async def _process_with_raise(self, request: LLMRequest) -> LLMResponse:
        """Process request using RAISE framework"""
        # Reasoning phase
        reasoning_result = await self.raise_framework.reason(request.query, request.context)
        
        # Acting phase
        action_result = await self.raise_framework.act(reasoning_result, request.query)
        
        # Iterating phase (simplified)
        needs_iteration = await self.raise_framework.iterate({
            'reasoning': reasoning_result,
            'actions': action_result
        })
        
        # Synthesizing phase
        response_content = await self.raise_framework.synthesize(
            reasoning_result, action_result, request.query
        )
        
        # Evaluating phase
        confidence_score = await self.raise_framework.evaluate(response_content, request.query)
        
        return LLMResponse(
            content=response_content,
            model_used=self.config.model_name,
            tokens_used=len(response_content.split()) * 1.3,  # Rough estimate
            processing_time=time.time(),
            confidence_score=confidence_score,
            reasoning_steps=reasoning_result.get('reasoning_steps', [])
        )
    
    async def _fallback_response(self, request: LLMRequest) -> LLMResponse:
        """Generate fallback response when primary processing fails"""
        fallback_content = f"""I understand you're asking about: "{request.query}"

I'm currently experiencing some technical difficulties with my primary processing systems, but I can still provide a basic response. 

For the most accurate and comprehensive information, please try your request again in a few moments when my systems have recovered.

If this is urgent, you might want to:
1. Check the system status
2. Try a simpler version of your question
3. Contact system administrators if the issue persists
"""
        
        return LLMResponse(
            content=fallback_content,
            model_used=self.config.fallback_model,
            tokens_used=len(fallback_content.split()),
            processing_time=0.1,
            confidence_score=0.3,
            reasoning_steps=["Fallback response generated due to system issues"]
        )
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        health_status = await self.health_monitor.check_health()
        performance_status = self.performance_tracker.get_health_status()
        
        return {
            'timestamp': time.time(),
            'health': health_status,
            'performance': performance_status,
            'config': asdict(self.config),
            'uptime': time.time() - getattr(self, '_start_time', time.time())
        }
    
    async def optimize_performance(self):
        """Perform performance optimization"""
        # Clear old metrics
        if len(self.performance_tracker.metrics['response_times']) > 1000:
            self.performance_tracker.metrics['response_times'] = \
                self.performance_tracker.metrics['response_times'][-500:]
        
        # Log optimization
        logger.info("Performance optimization completed")

# Global instance
llm_manager = None

def get_llm_manager(config: Optional[LLMConfig] = None) -> LLMSelfCareManager:
    """Get or create LLM manager instance"""
    global llm_manager
    if llm_manager is None:
        llm_manager = LLMSelfCareManager(config or LLMConfig())
    return llm_manager

# Example usage
async def main():
    """Example usage of the LLM manager"""
    manager = get_llm_manager()
    
    request = LLMRequest(
        query="What are the latest cybersecurity threats?",
        context=["Security is important", "Recent attacks have increased"],
        task_type="cybersecurity"
    )
    
    response = await manager.process_with_self_care(request)
    print(f"Response: {response.content}")
    print(f"Confidence: {response.confidence_score}")
    
    # Get system status
    status = await manager.get_system_status()
    print(f"System Status: {status}")

if __name__ == "__main__":
    asyncio.run(main())
