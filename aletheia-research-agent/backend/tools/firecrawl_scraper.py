"""
Firecrawl Tool - Deep content extraction from web pages
"""
import os
import httpx
import re
from typing import List, Dict, Optional
from datetime import datetime


class FirecrawlTool:
    """
    Firecrawl integration for deep web scraping and content extraction.
    Handles JavaScript-heavy sites, structured data extraction, and contact info.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable not set")
        
        self.base_url = "https://api.firecrawl.dev/v1"
        
    async def scrape(
        self,
        url: str,
        extract_contacts: bool = True,
        include_markdown: bool = True,
        include_html: bool = False
    ) -> Dict:
        """
        Scrape full content from a single URL
        
        Args:
            url: URL to scrape
            extract_contacts: Extract contact information
            include_markdown: Include markdown version of content
            include_html: Include raw HTML
            
        Returns:
            Scraped content with metadata and contacts
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/scrape",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": url,
                    "formats": ["markdown"] if include_markdown else [],
                    "onlyMainContent": True,
                    "waitFor": 2000  # Wait for JS to load
                },
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract base data
            result = {
                "url": url,
                "markdown": data.get("markdown", ""),
                "metadata": data.get("metadata", {}),
                "scraped_at": datetime.utcnow().isoformat()
            }
            
            # Extract contacts if requested
            if extract_contacts:
                result["contacts"] = self._extract_contacts(
                    data.get("markdown", ""),
                    data.get("metadata", {})
                )
            
            return result
    
    def _extract_contacts(self, content: str, metadata: Dict) -> Dict:
        """
        Extract contact information from scraped content
        
        Args:
            content: Markdown content
            metadata: Page metadata
            
        Returns:
            Dictionary of extracted contacts
        """
        
        contacts = {
            "emails": [],
            "github": None,
            "twitter": None,
            "linkedin": None,
            "website": None
        }
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        contacts["emails"] = list(set(emails))  # Remove duplicates
        
        # Extract GitHub URLs
        github_pattern = r'github\.com/([a-zA-Z0-9_-]+)'
        github_matches = re.findall(github_pattern, content)
        if github_matches:
            contacts["github"] = f"https://github.com/{github_matches[0]}"
        
        # Extract Twitter handles
        twitter_pattern = r'(?:twitter\.com/|@)([a-zA-Z0-9_]+)'
        twitter_matches = re.findall(twitter_pattern, content)
        if twitter_matches:
            contacts["twitter"] = f"https://twitter.com/{twitter_matches[0]}"
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/(?:in|company)/([a-zA-Z0-9_-]+)'
        linkedin_matches = re.findall(linkedin_pattern, content)
        if linkedin_matches:
            contacts["linkedin"] = f"https://linkedin.com/in/{linkedin_matches[0]}"
        
        return contacts
    
    async def crawl_site(
        self,
        base_url: str,
        max_pages: int = 10,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Crawl multiple pages from a website
        
        Args:
            base_url: Base URL to start crawling from
            max_pages: Maximum number of pages to crawl
            include_paths: Only crawl URLs matching these patterns
            exclude_paths: Skip URLs matching these patterns
            
        Returns:
            List of scraped pages
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/crawl",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": base_url,
                    "limit": max_pages,
                    "scrapeOptions": {
                        "formats": ["markdown"],
                        "onlyMainContent": True
                    },
                    "includePaths": include_paths or [],
                    "excludePaths": exclude_paths or []
                },
                timeout=180.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Get crawl ID
            crawl_id = data.get("id")
            
            # Poll for completion
            max_attempts = 30
            for _ in range(max_attempts):
                import asyncio
                await asyncio.sleep(5)  # Wait 5 seconds between polls
                
                status_response = await client.get(
                    f"{self.base_url}/crawl/{crawl_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                status_data = status_response.json()
                
                if status_data.get("status") == "completed":
                    pages = status_data.get("data", [])
                    
                    # Process each page
                    results = []
                    for page in pages:
                        results.append({
                            "url": page.get("url"),
                            "markdown": page.get("markdown", ""),
                            "metadata": page.get("metadata", {}),
                            "contacts": self._extract_contacts(
                                page.get("markdown", ""),
                                page.get("metadata", {})
                            ),
                            "scraped_at": datetime.utcnow().isoformat()
                        })
                    
                    return results
            
            raise TimeoutError("Crawl did not complete in time")
    
    async def extract_github_repo_info(self, github_url: str) -> Dict:
        """
        Extract detailed information from a GitHub repository
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Repository information including README, topics, etc.
        """
        
        # Scrape the main repo page
        repo_data = await self.scrape(github_url)
        
        # Extract repo-specific information
        repo_info = {
            "url": github_url,
            "name": None,
            "description": None,
            "topics": [],
            "readme": repo_data.get("markdown", ""),
            "stars": None,
            "language": None,
            "last_updated": None,
            "contacts": repo_data.get("contacts", {})
        }
        
        # Parse metadata
        metadata = repo_data.get("metadata", {})
        repo_info["description"] = metadata.get("description")
        
        # Extract repo name from URL
        match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
        if match:
            owner, name = match.groups()
            repo_info["owner"] = owner
            repo_info["name"] = name
        
        return repo_info
    
    async def extract_docs_site(self, docs_url: str) -> Dict:
        """
        Extract information from a documentation site
        
        Args:
            docs_url: Documentation site URL
            
        Returns:
            Documentation content and structure
        """
        
        # Crawl the docs site
        pages = await self.crawl_site(
            docs_url,
            max_pages=20,
            include_paths=["/docs", "/api", "/guide"],
            exclude_paths=["/blog", "/community"]
        )
        
        # Aggregate information
        docs_info = {
            "base_url": docs_url,
            "pages_count": len(pages),
            "content": "",
            "api_endpoints": [],
            "examples": [],
            "contacts": {}
        }
        
        # Combine content from all pages
        for page in pages:
            docs_info["content"] += f"\n\n## {page['url']}\n\n{page['markdown']}"
            
            # Merge contacts
            for key, value in page.get("contacts", {}).items():
                if value and not docs_info["contacts"].get(key):
                    docs_info["contacts"][key] = value
        
        return docs_info


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_firecrawl():
        tool = FirecrawlTool()
        
        # Test single page scrape
        print("Testing single page scrape...")
        result = await tool.scrape(
            "https://python.langchain.com/docs/use_cases/agents",
            extract_contacts=True
        )
        print(f"Scraped {len(result['markdown'])} characters")
        print(f"Contacts: {result['contacts']}")
        
        # Test GitHub repo extraction
        print("\nTesting GitHub repo extraction...")
        repo_info = await tool.extract_github_repo_info(
            "https://github.com/langchain-ai/langchain"
        )
        print(f"Repo: {repo_info['name']}")
        print(f"Description: {repo_info['description']}")
        
        # Test site crawl
        print("\nTesting site crawl...")
        pages = await tool.crawl_site(
            "https://www.crewai.com",
            max_pages=5
        )
        print(f"Crawled {len(pages)} pages")
        for page in pages:
            print(f"  - {page['url']}")
    
    asyncio.run(test_firecrawl())
