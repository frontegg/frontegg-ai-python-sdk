"""
Simple Client Example

This example demonstrates how to use the Frontegg AI Python SDK.
"""

import asyncio
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import (
    Environment,
    FronteggAiAgentsClientConfig,
    FronteggAiAgentsClient,
    setup_logger
)

# Set up logging
logger = setup_logger(level=20)  # INFO level

async def main():
    # Create client configuration
    config = FronteggAiAgentsClientConfig(
        environment=Environment.US,  # Use appropriate environment
        agent_id=os.environ.get("FRONTEGG_AGENT_ID", "a09b2864-0d32-45a4-9034-eea6eeb6a6a5"),
        client_id=os.environ.get("FRONTEGG_CLIENT_ID", "bef456f3-50db-428a-8418-a2f086bdf096"),
        client_secret=os.environ.get("FRONTEGG_CLIENT_SECRET", "93b43b45-24f2-4421-9d1d-94c5b09d4134"),
    )
    
    # Create the client
    client = FronteggAiAgentsClient(config, logger=logger)
    logger.info("Client initialized")
    
    # Set tenant ID and optional user ID for operations
    tenant_id = os.environ.get("FRONTEGG_TENANT_ID", "test")
    user_id = os.environ.get("FRONTEGG_USER_ID")  # Optional
    
    # List available tools
    tools = None
    try:
        tools = await client.list_tools()
        logger.info(f"Available tools: {tools}")
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
    
    # List available tools as CrewAI tools
    crewai_tools = []
    try:
        crewai_tools = await client.list_tools_as_crewai_tools()
        logger.info(f"Available CrewAI tools: {crewai_tools}")
    except Exception as e:
        logger.error(f"Error listing CrewAI tools: {e}")
    
    # Execute the first CrewAI tool if available
    if crewai_tools:
        try:
            first_tool = crewai_tools[0]
            logger.info(f"Executing CrewAI tool: {first_tool.name}")

            result = first_tool._run(name=first_tool.name, tenant_id=tenant_id, arguments={"param": "value"}, user_id=user_id)
            logger.info(f"CrewAI tool result: {result}")
        except Exception as e:
            logger.error(f"Error executing CrewAI tool: {e}", exc_info=True)
        
    # Example: Call a tool if available
    if tools and hasattr(tools, 'tools') and tools.tools:
        try:
            # Access the first tool from the tools list attribute
            tool = tools.tools[0]
            tool_name = tool.name
            logger.info(f"Calling tool: {tool_name}")
            result = await client.call_tool(
                name=tool_name, 
                tenant_id=tenant_id,
                arguments={"param": "value"},
                user_id=user_id
            )
            logger.info(f"Tool result: {result}")
        except Exception as e:
            logger.error(f"Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 