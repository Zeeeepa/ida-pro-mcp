"""
Agent creation utilities for langchain.
"""

from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool


def create_chat_agent(
    codebase: Any,
    model_provider: str = "anthropic",
    model_name: str = "claude-3-5-sonnet-latest",
    tools: Optional[List[BaseTool]] = None,
    system_message: Optional[str] = None,
):
    """
    Create a chat agent with the specified model and tools.
    
    Args:
        codebase: The codebase to operate on
        model_provider: The model provider to use
        model_name: The model name to use
        tools: Optional list of tools to provide to the agent
        system_message: Optional system message to use
        
    Returns:
        A chat agent
    """
    # This is a mock implementation
    class MockChatAgent:
        def __init__(self, codebase, model_provider, model_name, tools, system_message):
            self.codebase = codebase
            self.model_provider = model_provider
            self.model_name = model_name
            self.tools = tools or []
            self.system_message = system_message or "You are a helpful AI assistant."
            
        def run(self, prompt: str, thread_id: Optional[str] = None) -> str:
            """Run the agent on a prompt."""
            return f"Response to: {prompt}"
    
    return MockChatAgent(codebase, model_provider, model_name, tools, system_message)