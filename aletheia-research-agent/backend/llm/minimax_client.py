"""MiniMax LLM client using Anthropic SDK."""
from anthropic import Anthropic, AsyncAnthropic
from typing import List, Dict, Optional, AsyncIterator
from config import settings


class MiniMaxClient:
    """Client for MiniMax-M2 API using Anthropic SDK."""
    
    def __init__(self):
        """Initialize MiniMax client."""
        if not settings.minimax_api_key:
            raise ValueError("MINIMAX_API_KEY is required but not set")
        
        self.client = Anthropic(
            api_key=settings.minimax_api_key,
            base_url=settings.minimax_base_url
        )
        
        self.async_client = AsyncAnthropic(
            api_key=settings.minimax_api_key,
            base_url=settings.minimax_base_url
        )
        
        self.model = settings.minimax_model
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get Aletheia system prompt."""
        return """You are Aletheia, an AI assistant built to explore the universe's mysteries with wit and truth. Your name derives from the Greek concept of truth and disclosure.

Core traits:
- Maximally truthful: Cite sources, cross-verify claims, flag uncertainty
- Witty but substantive: No empty jokes, every response teaches something
- Down-to-earth: Explain like talking to a curious friend, not lecturing
- Rebellious against blandness: Challenge conventional wisdom, offer fresh perspectives
- Agent-native: Use tools aggressively (search, browse, analyze data)

For research queries:
1. Break down the question with thinking trace visible to user
2. Search 2-5 sources (web_search tool)
3. Cross-verify facts across sources
4. Synthesize in your own words (NEVER quote directly)
5. Provide 2-3 follow-up suggestions

For data wrangling:
1. Analyze structure/schema
2. Surface insights (outliers, patterns)
3. Suggest actionable next steps

Always show your reasoning process in <think> tags so users can see your thought process."""
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 4096
    ) -> Dict:
        """Generate non-streaming response."""
        response = await self.async_client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=messages,
            temperature=temperature,
            top_p=0.95,
            max_tokens=max_tokens
        )
        
        # Extract content and thinking trace
        content = ""
        thinking_trace = []

        for block in response.content:
            if hasattr(block, 'type'):
                if block.type == 'text':
                    content += block.text
                elif block.type == 'thinking':
                    # Ensure thinking is properly converted to dict format
                    thinking_item = {
                        "step": len(thinking_trace) + 1,
                        "action": "think",
                        "description": str(block.thinking) if block.thinking else "",
                        "confidence": 0.9
                    }
                    thinking_trace.append(thinking_item)

        # Final safety check: ensure all items are dicts
        thinking_trace = [
            item if isinstance(item, dict) else {
                "step": idx + 1,
                "action": "think",
                "description": str(item),
                "confidence": 0.9
            }
            for idx, item in enumerate(thinking_trace)
        ]

        return {
            "content": content,
            "thinking_trace": thinking_trace,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 4096
    ) -> AsyncIterator[Dict]:
        """Generate streaming response."""
        async with self.async_client.messages.stream(
            model=self.model,
            system=self.system_prompt,
            messages=messages,
            temperature=temperature,
            top_p=0.95,
            max_tokens=max_tokens
        ) as stream:
            async for event in stream:
                if event.type == "content_block_start":
                    if hasattr(event.content_block, 'type'):
                        yield {"type": "block_start", "block_type": event.content_block.type}
                
                elif event.type == "content_block_delta":
                    if hasattr(event.delta, 'type'):
                        if event.delta.type == "text_delta":
                            yield {"type": "text_delta", "text": event.delta.text}
                        elif event.delta.type == "thinking_delta":
                            yield {"type": "thinking_delta", "thinking": event.delta.thinking}
                
                elif event.type == "message_stop":
                    yield {"type": "done"}


# Global client instance
minimax_client = None

def get_minimax_client() -> MiniMaxClient:
    """Get or create MiniMax client instance."""
    global minimax_client
    if minimax_client is None:
        minimax_client = MiniMaxClient()
    return minimax_client
