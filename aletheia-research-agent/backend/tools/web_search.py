"""Web search tools for research agent."""
import aiohttp
import asyncio
from typing import List, Dict, Optional
from config import settings


class WebSearchTool:
    """Web search using Tavily API with fallback."""
    
    def __init__(self):
        """Initialize search tool."""
        self.tavily_api_key = settings.tavily_api_key
        self.tavily_url = "https://api.tavily.com/search"
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced"
    ) -> List[Dict]:
        """
        Perform web search using Tavily API.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            search_depth: "basic" or "advanced"
        
        Returns:
            List of search results with title, url, content
        """
        if not self.tavily_api_key:
            return self._mock_search_results(query, max_results)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": search_depth,
                    "include_answer": True,
                    "include_raw_content": False
                }
                
                async with session.post(
                    self.tavily_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for item in data.get("results", []):
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "content": item.get("content", ""),
                                "score": item.get("score", 0.0)
                            })
                        
                        return results
                    else:
                        return self._mock_search_results(query, max_results)
        
        except Exception as e:
            print(f"Search error: {e}")
            return self._mock_search_results(query, max_results)
    
    def _mock_search_results(self, query: str, max_results: int) -> List[Dict]:
        """
        Return empty results when API is unavailable.
        Note: This is for development only. Production requires valid API key.
        """
        return [{
            "title": f"Search unavailable: {query}",
            "url": "https://example.com",
            "content": "Web search is currently unavailable. Please configure TAVILY_API_KEY.",
            "score": 0.0
        }]
    
    async def verify_source(self, url: str) -> Dict:
        """Verify and fetch metadata from a source URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=5),
                    headers={"User-Agent": "Aletheia-Research-Agent/1.0"}
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        return {
                            "url": url,
                            "status": "verified",
                            "accessible": True,
                            "content_length": len(text)
                        }
                    else:
                        return {
                            "url": url,
                            "status": "failed",
                            "accessible": False,
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "accessible": False,
                "error": str(e)
            }


# Global search tool instance
search_tool = WebSearchTool()


async def perform_search(query: str, max_results: int = 5) -> List[Dict]:
    """Perform web search."""
    return await search_tool.search(query, max_results)


async def cross_verify_sources(sources: List[str]) -> List[Dict]:
    """Cross-verify multiple sources."""
    tasks = [search_tool.verify_source(url) for url in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    verified = []
    for result in results:
        if isinstance(result, dict) and not isinstance(result, Exception):
            verified.append(result)
    
    return verified
