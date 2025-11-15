"""
Discovery sources and keywords configuration for Agent Discovery System
"""

DISCOVERY_SOURCES = {
    "directories": [
        "https://github.com/topics/ai-agents",
        "https://huggingface.co/models",
        "https://www.langchain.com/",
        "https://www.crewai.com/",
        "https://autogpt.net/",
        "https://www.producthunt.com/topics/ai-agents",
    ],

    "communities": [
        "https://www.reddit.com/r/artificial/",
        "https://www.reddit.com/r/LocalLLaMA/",
        "https://news.ycombinator.com/",
    ],

    "social": [
        "twitter.com/search?q=AI%20agent%20launch",
        "twitter.com/search?q=LangChain%20agent",
        "twitter.com/search?q=autonomous%20agent",
    ],

    "frameworks": [
        "https://python.langchain.com/docs/use_cases/agents",
        "https://docs.crewai.com/",
        "https://www.langflow.org/",
        "https://github.com/Significant-Gravitas/AutoGPT",
    ]
}

SEARCH_KEYWORDS = [
    # General
    "AI agent",
    "autonomous agent",
    "LLM agent",

    # Framework-specific
    "LangChain agent",
    "CrewAI agent",
    "AutoGPT agent",
    "LangGraph workflow",

    # Use case specific
    "research agent",
    "coding agent",
    "data analysis agent",
    "automation agent",

    # Recent
    "new AI agent 2025",
    "agent launch",
    "agent release",
]

AGENT_CATEGORIES = [
    "research",
    "coding",
    "automation",
    "productivity",
    "creative",
    "customer service",
    "data analysis",
    "security",
    "finance",
    "marketing",
]

DISCOVERY_CONFIG = {
    "max_results_per_run": 50,
    "confidence_threshold": 0.6,
    "auto_verify_threshold": 0.9,
    "tavily_max_per_lead": 3,
    "firecrawl_enabled": True,
    "outreach_enabled": True,
}
