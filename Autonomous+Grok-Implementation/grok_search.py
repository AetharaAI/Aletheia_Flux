"""
Grok Search Tool - Fast web search for initial discovery sweep
"""
import os
import httpx
from typing import List, Dict, Optional
from datetime import datetime


class GrokSearchTool:
    """
    Grok web search integration for fast bulk discovery.
    Uses X.AI's Grok model with native web search capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable not set")
        
        self.base_url = "https://api.x.ai/v1"
        self.model = "grok-beta"
        
    async def search(
        self, 
        query: str, 
        max_results: int = 20,
        include_snippets: bool = True
    ) -> List[Dict]:
        """
        Fast web search using Grok's native capabilities
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            include_snippets: Include content snippets
            
        Returns:
            List of search results with URLs, titles, and snippets
        """
        
        # Construct search prompt
        search_prompt = f"""
        Search the web for: {query}
        
        Return the top {max_results} most relevant results.
        For each result, provide:
        1. URL
        2. Title
        3. Brief description/snippet
        4. Relevance score (0-1)
        
        Format as JSON array:
        [
          {{
            "url": "https://...",
            "title": "...",
            "snippet": "...",
            "relevance_score": 0.95
          }}
        ]
        
        Focus on authoritative sources. Prioritize:
        - Official documentation
        - GitHub repositories
        - Technical blogs
        - Product pages
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a web search specialist. Use your web search capabilities to find relevant results."
                        },
                        {
                            "role": "user",
                            "content": search_prompt
                        }
                    ],
                    "temperature": 0.1,  # Low temperature for factual search
                },
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract results from response
            content = data["choices"][0]["message"]["content"]
            
            # Parse JSON from response
            import json
            import re
            
            # Extract JSON array from markdown code blocks if present
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                results = json.loads(json_match.group(1))
            else:
                # Try parsing directly
                results = json.loads(content)
            
            # Add metadata
            for result in results:
                result['search_query'] = query
                result['discovered_at'] = datetime.utcnow().isoformat()
                result['source'] = 'grok'
            
            return results[:max_results]
    
    async def bulk_search(
        self,
        queries: List[str],
        max_results_per_query: int = 20
    ) -> Dict[str, List[Dict]]:
        """
        Execute multiple searches in parallel
        
        Args:
            queries: List of search queries
            max_results_per_query: Max results per query
            
        Returns:
            Dictionary mapping queries to their results
        """
        import asyncio
        
        async def search_with_query(query: str):
            return query, await self.search(query, max_results_per_query)
        
        # Execute searches concurrently
        tasks = [search_with_query(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build results dictionary
        search_results = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"Search failed: {result}")
                continue
            
            query, data = result
            search_results[query] = data
        
        return search_results
    
    async def targeted_agent_search(
        self,
        framework: Optional[str] = None,
        category: Optional[str] = None,
        recent: bool = True
    ) -> List[Dict]:
        """
        Specialized search for AI agents with specific criteria
        
        Args:
            framework: Filter by framework (LangChain, CrewAI, etc.)
            category: Filter by category (research, coding, etc.)
            recent: Only include recent releases (2024-2025)
            
        Returns:
            List of agent search results
        """
        
        # Build targeted query
        query_parts = ["AI agent"]
        
        if framework:
            query_parts.append(framework)
        
        if category:
            query_parts.append(category)
        
        if recent:
            query_parts.append("2024 OR 2025")
        
        query = " ".join(query_parts)
        
        results = await self.search(query, max_results=50)
        
        # Filter results for agent-specific content
        agent_results = []
        agent_keywords = [
            'agent', 'autonomous', 'llm', 'ai assistant',
            'workflow', 'automation', 'chatbot', 'assistant'
        ]
        
        for result in results:
            content = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
            
            if any(keyword in content for keyword in agent_keywords):
                agent_results.append(result)
        
        return agent_results


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_grok_search():
        tool = GrokSearchTool()
        
        # Single search
        print("Testing single search...")
        results = await tool.search("LangChain AI agents GitHub", max_results=5)
        print(f"Found {len(results)} results")
        for r in results[:3]:
            print(f"  - {r['title']}: {r['url']}")
        
        # Targeted agent search
        print("\nTesting targeted agent search...")
        agents = await tool.targeted_agent_search(
            framework="LangChain",
            category="research",
            recent=True
        )
        print(f"Found {len(agents)} agent results")
        
        # Bulk search
        print("\nTesting bulk search...")
        queries = [
            "CrewAI agents",
            "AutoGPT agents",
            "LangGraph workflows"
        ]
        bulk_results = await tool.bulk_search(queries, max_results_per_query=5)
        for query, results in bulk_results.items():
            print(f"{query}: {len(results)} results")
    
    asyncio.run(test_grok_search())
