"""LangGraph agent orchestration for research workflows."""
from typing import TypedDict, List, Dict, Annotated
import operator
from langgraph.graph import StateGraph, END
from tools.web_search import perform_search, cross_verify_sources
from llm.minimax_client import get_minimax_client


class AgentState(TypedDict):
    """State for the research agent."""
    messages: Annotated[List[Dict], operator.add]
    query: str
    search_results: List[Dict]
    verified_sources: List[Dict]
    thinking_steps: List[Dict]
    final_response: str
    error: str


class ResearchAgent:
    """LangGraph-based research agent with multi-step workflow."""
    
    def __init__(self):
        """Initialize research agent."""
        self.llm_client = None
        self.graph = self._build_graph()
    
    def _get_client(self):
        """Lazy load LLM client."""
        if self.llm_client is None:
            try:
                self.llm_client = get_minimax_client()
            except ValueError as e:
                # LLM client unavailable
                self.llm_client = None
        return self.llm_client
    
    async def reflect(self, state: AgentState) -> AgentState:
        """Reflect on the query and plan research approach."""
        thinking_steps = state.get("thinking_steps", [])
        thinking_steps.append({
            "step": len(thinking_steps) + 1,
            "action": "reflect",
            "description": f"Analyzing query: {state['query']}",
            "confidence": 0.9
        })
        
        return {
            **state,
            "thinking_steps": thinking_steps
        }
    
    async def search(self, state: AgentState) -> AgentState:
        """Perform web search."""
        query = state["query"]
        
        # Perform search
        results = await perform_search(query, max_results=5)
        
        thinking_steps = state.get("thinking_steps", [])
        thinking_steps.append({
            "step": len(thinking_steps) + 1,
            "action": "search",
            "description": f"Found {len(results)} sources",
            "confidence": 0.85
        })
        
        return {
            **state,
            "search_results": results,
            "thinking_steps": thinking_steps
        }
    
    async def verify(self, state: AgentState) -> AgentState:
        """Verify and cross-check sources."""
        results = state.get("search_results", [])
        
        if len(results) < 2:
            thinking_steps = state.get("thinking_steps", [])
            thinking_steps.append({
                "step": len(thinking_steps) + 1,
                "action": "verify",
                "description": "Insufficient sources for cross-verification",
                "confidence": 0.5
            })
            return {
                **state,
                "verified_sources": results,
                "thinking_steps": thinking_steps
            }
        
        # Extract URLs for verification
        urls = [r["url"] for r in results[:3]]
        verified = await cross_verify_sources(urls)
        
        # Filter accessible sources
        accessible_sources = [
            results[i] for i, v in enumerate(verified)
            if v.get("accessible", False)
        ]
        
        thinking_steps = state.get("thinking_steps", [])
        thinking_steps.append({
            "step": len(thinking_steps) + 1,
            "action": "verify",
            "description": f"Verified {len(accessible_sources)}/{len(results)} sources",
            "confidence": 0.8
        })
        
        return {
            **state,
            "verified_sources": accessible_sources if accessible_sources else results,
            "thinking_steps": thinking_steps
        }
    
    async def synthesize(self, state: AgentState) -> AgentState:
        """Synthesize findings using LLM."""
        client = self._get_client()
        
        if client is None:
            # Fallback without LLM
            sources = state.get("verified_sources", [])
            response = self._create_fallback_response(state["query"], sources)
            
            thinking_steps = state.get("thinking_steps", [])
            thinking_steps.append({
                "step": len(thinking_steps) + 1,
                "action": "synthesize",
                "description": "Generated response from search results (LLM unavailable)",
                "confidence": 0.6
            })
            
            return {
                **state,
                "final_response": response,
                "thinking_steps": thinking_steps
            }
        
        # Build prompt with search results
        sources = state.get("verified_sources", [])
        sources_text = "\n\n".join([
            f"[{i+1}] {s['title']}\nURL: {s['url']}\n{s['content']}"
            for i, s in enumerate(sources)
        ])
        
        messages = [
            {
                "role": "user",
                "content": f"Query: {state['query']}\n\nSources:\n{sources_text}\n\nSynthesize these sources into a comprehensive response. Cite sources with [1], [2], etc."
            }
        ]
        
        try:
            response = await client.generate_response(messages)
            
            thinking_steps = state.get("thinking_steps", [])
            thinking_steps.append({
                "step": len(thinking_steps) + 1,
                "action": "synthesize",
                "description": "Generated comprehensive response",
                "confidence": 0.95
            })
            
            return {
                **state,
                "final_response": response["content"],
                "thinking_steps": thinking_steps
            }
        except Exception as e:
            # Fallback on error
            response = self._create_fallback_response(state["query"], sources)
            return {
                **state,
                "final_response": response,
                "error": str(e)
            }
    
    def _create_fallback_response(self, query: str, sources: List[Dict]) -> str:
        """Create fallback response without LLM."""
        if not sources:
            return f"I found no reliable sources for: {query}. Please try a different query or check your internet connection."
        
        response = f"Research findings for: {query}\n\n"
        
        for i, source in enumerate(sources[:3], 1):
            response += f"[{i}] {source['title']}\n"
            response += f"{source['content'][:200]}...\n"
            response += f"Source: {source['url']}\n\n"
        
        response += "Note: Full synthesis unavailable. Please configure MINIMAX_API_KEY for enhanced responses."
        
        return response
    
    async def suggest(self, state: AgentState) -> AgentState:
        """Generate follow-up suggestions."""
        query = state["query"]
        
        # Simple follow-up generation
        suggestions = [
            f"What are the latest developments in {query}?",
            f"How does {query} compare to alternatives?",
            f"What are the practical applications of {query}?"
        ]
        
        thinking_steps = state.get("thinking_steps", [])
        thinking_steps.append({
            "step": len(thinking_steps) + 1,
            "action": "suggest",
            "description": "Generated follow-up suggestions",
            "confidence": 0.8
        })
        
        return {
            **state,
            "thinking_steps": thinking_steps
        }
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("reflect", self.reflect)
        workflow.add_node("search", self.search)
        workflow.add_node("verify", self.verify)
        workflow.add_node("synthesize", self.synthesize)
        workflow.add_node("suggest", self.suggest)
        
        # Define edges
        workflow.set_entry_point("reflect")
        workflow.add_edge("reflect", "search")
        workflow.add_edge("search", "verify")
        workflow.add_edge("verify", "synthesize")
        workflow.add_edge("synthesize", "suggest")
        workflow.add_edge("suggest", END)
        
        return workflow.compile()
    
    async def run(self, query: str, messages: List[Dict] = None) -> Dict:
        """Run the research agent workflow."""
        initial_state = {
            "messages": messages or [],
            "query": query,
            "search_results": [],
            "verified_sources": [],
            "thinking_steps": [],
            "final_response": "",
            "error": ""
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "response": final_state["final_response"],
            "sources": final_state.get("verified_sources", []),
            "thinking_trace": final_state.get("thinking_steps", []),
            "error": final_state.get("error", "")
        }


# Global agent instance
research_agent = ResearchAgent()


async def run_research_agent(query: str, messages: List[Dict] = None) -> Dict:
    """Run research agent on query."""
    return await research_agent.run(query, messages)
