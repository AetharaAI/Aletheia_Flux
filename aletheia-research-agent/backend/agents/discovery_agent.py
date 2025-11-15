"""
Agent Discovery System - Extends Aletheia Flux for AI agent discovery
"""
import asyncio
from typing import List, Dict, TypedDict, Optional
from datetime import datetime
import json

# Import existing Aletheia components
# from backend.agents.research_agent import ResearchAgent
# from backend.llm.minimax_client import MiniMaxClient
# from backend.tools.web_search import WebSearchTool

# Import new tools
from tools.grok_search import GrokSearchTool
from tools.firecrawl_scraper import FirecrawlTool


class DiscoveryState(TypedDict):
    """State for agent discovery workflow"""
    
    # Input
    search_targets: List[str]
    keywords: List[str]
    max_results: int
    
    # Discovery Phase
    grok_results: List[Dict]
    filtered_leads: List[Dict]
    
    # Research Phase
    tavily_results: List[Dict]
    scraped_content: List[Dict]
    
    # Analysis Phase
    classified_agents: List[Dict]
    
    # Output
    agents_to_store: List[Dict]
    outreach_list: List[Dict]
    
    # Metadata
    thinking_steps: List[Dict]
    sources: List[Dict]
    run_id: str
    started_at: str
    status: str


class AgentDiscoverySystem:
    """
    Extends Aletheia Flux with specialized agent discovery capabilities.
    
    Workflow:
    1. Grok Sweep - Fast bulk discovery
    2. Filter & Classify - MiniMax relevance scoring
    3. Tavily Research - Deep research on promising leads
    4. Firecrawl Extract - Full content extraction
    5. MiniMax Analysis - Structure and classify
    6. Store & Outreach - Save to DB and prepare outreach
    """
    
    def __init__(
        self,
        minimax_client,
        tavily_client,
        grok_api_key: str,
        firecrawl_api_key: str,
        supabase_client
    ):
        self.minimax = minimax_client
        self.tavily = tavily_client
        self.grok = GrokSearchTool(grok_api_key)
        self.firecrawl = FirecrawlTool(firecrawl_api_key)
        self.db = supabase_client
        
    async def discover(
        self,
        search_targets: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        max_results: int = 50
    ) -> DiscoveryState:
        """
        Run complete discovery workflow
        
        Args:
            search_targets: Specific sources to search
            keywords: Search keywords
            max_results: Maximum agents to discover
            
        Returns:
            Complete discovery state with results
        """
        
        # Initialize state
        state: DiscoveryState = {
            "search_targets": search_targets or self._get_default_targets(),
            "keywords": keywords or self._get_default_keywords(),
            "max_results": max_results,
            "grok_results": [],
            "filtered_leads": [],
            "tavily_results": [],
            "scraped_content": [],
            "classified_agents": [],
            "agents_to_store": [],
            "outreach_list": [],
            "thinking_steps": [],
            "sources": [],
            "run_id": self._generate_run_id(),
            "started_at": datetime.utcnow().isoformat(),
            "status": "running"
        }
        
        try:
            # Phase 1: Grok Sweep
            state = await self._grok_sweep(state)
            
            # Phase 2: Filter & Classify
            state = await self._filter_classify(state)
            
            # Phase 3: Tavily Deep Dive
            state = await self._tavily_research(state)
            
            # Phase 4: Firecrawl Extract
            state = await self._firecrawl_extract(state)
            
            # Phase 5: MiniMax Analysis
            state = await self._minimax_analyze(state)
            
            # Phase 6: Store Results
            state = await self._store_results(state)
            
            # Phase 7: Generate Outreach
            state = await self._generate_outreach(state)
            
            state["status"] = "completed"
            
        except Exception as e:
            state["status"] = "failed"
            state["thinking_steps"].append({
                "step": len(state["thinking_steps"]) + 1,
                "action": "error",
                "description": f"Discovery failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return state
    
    async def _grok_sweep(self, state: DiscoveryState) -> DiscoveryState:
        """Phase 1: Fast bulk discovery with Grok"""
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "grok_sweep",
            "description": f"Starting Grok sweep with {len(state['keywords'])} keywords",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Build search queries combining targets and keywords
        queries = []
        for keyword in state["keywords"]:
            queries.append(keyword)
        
        # Execute bulk search
        results = await self.grok.bulk_search(
            queries,
            max_results_per_query=20
        )
        
        # Flatten results
        all_results = []
        for query, query_results in results.items():
            all_results.extend(query_results)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        state["grok_results"] = unique_results[:state["max_results"]]
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "grok_sweep_complete",
            "description": f"Found {len(state['grok_results'])} unique results",
            "confidence": 0.7,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return state
    
    async def _filter_classify(self, state: DiscoveryState) -> DiscoveryState:
        """Phase 2: Filter and classify results with MiniMax"""
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "filter_classify",
            "description": "Classifying results for relevance",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Use MiniMax to classify each result
        filtered = []
        
        for result in state["grok_results"]:
            # Create classification prompt
            prompt = f"""
            Analyze this search result and determine if it's an AI agent.
            
            RESULT:
            Title: {result.get('title', '')}
            URL: {result.get('url', '')}
            Snippet: {result.get('snippet', '')}
            
            Is this an actual AI agent (autonomous software system)?
            Consider: Does it perform tasks, make decisions, or automate workflows?
            
            Respond with JSON:
            {{
              "is_agent": true/false,
              "confidence": 0.0-1.0,
              "reasoning": "brief explanation",
              "preliminary_category": "research/coding/automation/etc"
            }}
            """
            
            # Get MiniMax classification
            response = await self.minimax.generate(
                prompt,
                temperature=0.1,
                max_tokens=200
            )
            
            try:
                # Parse response
                classification = json.loads(response)
                
                if classification.get("is_agent") and classification.get("confidence", 0) > 0.6:
                    result["classification"] = classification
                    filtered.append(result)
                    
            except json.JSONDecodeError:
                # Skip if can't parse
                continue
        
        state["filtered_leads"] = filtered
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "filter_complete",
            "description": f"Filtered to {len(filtered)} high-confidence agent leads",
            "confidence": 0.8,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return state
    
    async def _tavily_research(self, state: DiscoveryState) -> DiscoveryState:
        """Phase 3: Deep research with Tavily on promising leads"""
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "tavily_research",
            "description": f"Deep research on {len(state['filtered_leads'])} leads",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Research each high-confidence lead
        researched = []
        
        for lead in state["filtered_leads"][:30]:  # Limit to top 30 to control costs
            # Build research query
            query = f"{lead.get('title', '')} AI agent details documentation"
            
            # Search with Tavily
            tavily_results = await self.tavily.search(
                query,
                max_results=3,
                search_depth="advanced"
            )
            
            lead["tavily_research"] = tavily_results
            researched.append(lead)
            
            # Add to sources
            state["sources"].extend([{
                "url": r.get("url"),
                "title": r.get("title"),
                "score": r.get("score")
            } for r in tavily_results])
        
        state["tavily_results"] = researched
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "tavily_complete",
            "description": f"Completed deep research on {len(researched)} agents",
            "confidence": 0.85,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return state
    
    async def _firecrawl_extract(self, state: DiscoveryState) -> DiscoveryState:
        """Phase 4: Extract full content with Firecrawl"""
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "firecrawl_extract",
            "description": "Extracting full content from agent pages",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Scrape each lead's primary URL
        scraped = []
        
        for lead in state["tavily_results"][:20]:  # Limit to top 20
            url = lead.get("url")
            
            try:
                # Scrape with contact extraction
                content = await self.firecrawl.scrape(
                    url,
                    extract_contacts=True,
                    include_markdown=True
                )
                
                lead["scraped_content"] = content
                scraped.append(lead)
                
            except Exception as e:
                # Log error but continue
                print(f"Failed to scrape {url}: {e}")
                continue
        
        state["scraped_content"] = scraped
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "firecrawl_complete",
            "description": f"Extracted content from {len(scraped)} pages",
            "confidence": 0.9,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return state
    
    async def _minimax_analyze(self, state: DiscoveryState) -> DiscoveryState:
        """Phase 5: Comprehensive analysis and structuring with MiniMax"""
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "minimax_analyze",
            "description": "Analyzing and structuring agent data",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Analyze each scraped result
        classified = []
        
        for lead in state["scraped_content"]:
            # Combine all available data
            combined_data = {
                "original_result": lead,
                "scraped_content": lead.get("scraped_content", {}).get("markdown", "")[:5000],
                "tavily_research": lead.get("tavily_research", [])
            }
            
            # Create analysis prompt
            prompt = f"""
            Analyze this AI agent and extract structured information.
            
            DATA:
            {json.dumps(combined_data, indent=2)}
            
            Extract and return JSON:
            {{
              "name": "Agent name",
              "slug": "url-friendly-slug",
              "description": "1-2 sentence description",
              "capabilities": ["list", "of", "capabilities"],
              "framework": "LangChain/CrewAI/Custom/etc",
              "category": "research/coding/automation/creative/productivity",
              "tags": ["relevant", "tags"],
              "endpoint_url": "API endpoint if available",
              "documentation_url": "Documentation URL",
              "source_url": "Original URL",
              "contacts": {{
                "email": "contact email",
                "github": "GitHub URL",
                "twitter": "Twitter handle"
              }},
              "confidence_score": 0.0-1.0
            }}
            
            Be conservative with confidence scores. Only include information you're certain about.
            """
            
            try:
                # Get MiniMax analysis
                response = await self.minimax.generate(
                    prompt,
                    temperature=0.1,
                    max_tokens=1000
                )
                
                # Parse structured data
                agent_data = json.loads(response)
                agent_data["raw_data"] = combined_data
                agent_data["discovered_at"] = datetime.utcnow().isoformat()
                
                classified.append(agent_data)
                
            except Exception as e:
                print(f"Failed to analyze lead: {e}")
                continue
        
        state["classified_agents"] = classified
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "minimax_complete",
            "description": f"Classified {len(classified)} agents with structured data",
            "confidence": 0.95,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return state
    
    async def _store_results(self, state: DiscoveryState) -> DiscoveryState:
        """Phase 6: Store results in database"""
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "store_results",
            "description": f"Storing {len(state['classified_agents'])} agents in database",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        stored = []
        
        for agent in state["classified_agents"]:
            try:
                # Insert into discovered_agents table
                result = await self.db.table("discovered_agents").insert({
                    "name": agent.get("name"),
                    "slug": agent.get("slug"),
                    "description": agent.get("description"),
                    "framework": agent.get("framework"),
                    "category": agent.get("category"),
                    "tags": agent.get("tags", []),
                    "capabilities": agent.get("capabilities", []),
                    "endpoint_url": agent.get("endpoint_url"),
                    "source_url": agent.get("source_url"),
                    "documentation_url": agent.get("documentation_url"),
                    "contact_email": agent.get("contacts", {}).get("email"),
                    "github_url": agent.get("contacts", {}).get("github"),
                    "twitter_handle": agent.get("contacts", {}).get("twitter"),
                    "confidence_score": agent.get("confidence_score"),
                    "raw_data": agent.get("raw_data"),
                    "discovered_by": "discovery_system",
                    "verified": False
                }).execute()
                
                stored.append(result.data[0])
                
            except Exception as e:
                print(f"Failed to store agent {agent.get('name')}: {e}")
                continue
        
        state["agents_to_store"] = stored
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "store_complete",
            "description": f"Successfully stored {len(stored)} agents",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return state
    
    async def _generate_outreach(self, state: DiscoveryState) -> DiscoveryState:
        """Phase 7: Generate personalized outreach for each agent"""
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "generate_outreach",
            "description": "Generating personalized outreach messages",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        outreach_list = []
        
        for agent in state["agents_to_store"]:
            # Skip if no contact info
            if not agent.get("contact_email") and not agent.get("github_url"):
                continue
            
            # Generate personalized message
            prompt = f"""
            Generate a professional, friendly outreach email to the creator of this AI agent.
            
            AGENT: {agent.get('name')}
            DESCRIPTION: {agent.get('description')}
            FRAMEWORK: {agent.get('framework')}
            
            PURPOSE: Invite them to register their agent on AetherPro.tech, the agent registry
            and communication infrastructure (like DNS for AI agents).
            
            REQUIREMENTS:
            - Acknowledge their specific work
            - Explain AetherPro as neutral infrastructure (not a competitor)
            - Keep it under 150 words
            - Professional but not salesy
            - Clear call-to-action
            
            EMAIL:
            """
            
            try:
                message = await self.minimax.generate(
                    prompt,
                    temperature=0.7,
                    max_tokens=300
                )
                
                outreach_list.append({
                    "agent_id": agent.get("id"),
                    "contact_email": agent.get("contact_email"),
                    "github_url": agent.get("github_url"),
                    "message": message,
                    "status": "pending"
                })
                
            except Exception as e:
                print(f"Failed to generate outreach for {agent.get('name')}: {e}")
                continue
        
        state["outreach_list"] = outreach_list
        
        state["thinking_steps"].append({
            "step": len(state["thinking_steps"]) + 1,
            "action": "outreach_complete",
            "description": f"Generated {len(outreach_list)} outreach messages",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return state
    
    def _get_default_targets(self) -> List[str]:
        """Get default discovery targets"""
        return [
            "github.com/topics/ai-agents",
            "huggingface.co/models",
            "langchain.com",
            "crewai.com",
            "producthunt.com AI agents"
        ]
    
    def _get_default_keywords(self) -> List[str]:
        """Get default search keywords"""
        return [
            "AI agent",
            "LangChain agent",
            "CrewAI agent",
            "autonomous agent",
            "LLM agent",
            "research agent",
            "coding agent"
        ]
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID"""
        import uuid
        return str(uuid.uuid4())


# Example usage
if __name__ == "__main__":
    async def test_discovery():
        # Initialize system (you'll need real credentials)
        system = AgentDiscoverySystem(
            minimax_client=None,  # Your MiniMax client
            tavily_client=None,   # Your Tavily client
            grok_api_key="your-grok-key",
            firecrawl_api_key="your-firecrawl-key",
            supabase_client=None  # Your Supabase client
        )
        
        # Run discovery
        result = await system.discover(
            keywords=["LangChain agents", "research agents"],
            max_results=10
        )
        
        print(f"Discovery {result['status']}")
        print(f"Found {len(result['classified_agents'])} agents")
        print(f"Stored {len(result['agents_to_store'])} agents")
        print(f"Generated {len(result['outreach_list'])} outreach messages")
    
    asyncio.run(test_discovery())
