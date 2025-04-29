# Frontegg AI Python SDK

The Frontegg AI Python SDK provides AI Agent developers with tools and utilities to easily empower AI agents within their applications. This SDK seamlessly integrates with the Frontegg platform, enabling advanced tool authentication, authorization, and identity management capabilities for AI Agents.

## Installation

```bash
pip install frontegg-ai-sdk
```

## Features

- Secure integration with Frontegg authentication

- Easy integration with Frontegg built-in and 3rd party application tools

- User identity context for agent throught Frontegg's identity platform

- Seamless integration with CrewAI agent tools

## Quick Start

```python
import asyncio
import os
from frontegg_ai_python_sdk import (
    Environment,
    FronteggAiClientConfig,
    FronteggAiClient
)

# Async usage
async def async_example():
    # Create client configuration
    config = FronteggAiClientConfig(
        environment=Environment.US,
        agent_id=os.environ.get("FRONTEGG_AGENT_ID"),
        client_id=os.environ.get("FRONTEGG_CLIENT_ID"),
        client_secret=os.environ.get("FRONTEGG_CLIENT_SECRET"),
    )

    # Create client
    client = FronteggAiClient(config)

    # Set Context manually
    tenant_id = os.getenv("FRONTEGG_TENANT_ID")
    user_id = os.getenv("FRONTEGG_USER_ID")
    client.set_context(tenant_id=tenant_id, user_id=user_id)

    # Or set the context using the user JWT
    user_jwt = "Bearer eyJ..."
    client.set_user_context_by_jwt(user_jwt)

    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {tools}")

    # Call a tool with arguments
    result = await client.call_tool(
        name="your_tool_name",
        arguments={"param1": "value1"},
    )
    print(f"Tool result: {result}")

if __name__ == "__main__":
    # Run async example
    asyncio.run(async_example())
```

## CrewAI Integration

The SDK supports integration with CrewAI for tool usage:

```python
import asyncio
from crewai import Agent, Crew, Task
from frontegg_ai_python_sdk import (
    Environment,
    FronteggAiClientConfig,
    FronteggAiClient
)

async def get_crewai_tools():
    # Configure Frontegg client
    config = FronteggAiClientConfig(
        environment=Environment.US,
        agent_id=os.environ.get("FRONTEGG_AGENT_ID"),
        client_id=os.environ.get("FRONTEGG_CLIENT_ID"),
        client_secret=os.environ.get("FRONTEGG_CLIENT_SECRET"),
    )

    # Create client
    client = FronteggAiClient(config)

    # Set Context manually
    tenant_id = os.getenv("FRONTEGG_TENANT_ID")
    user_id = os.getenv("FRONTEGG_USER_ID")
    client.set_context(tenant_id=tenant_id, user_id=user_id)

    # Or set the context using the user JWT
    user_jwt = "Bearer eyJ..."
    client.set_user_context_by_jwt(user_jwt)

    # Get tools as CrewAI tools
    tools = await client.list_tools_as_crewai_tools()
    return tools

# Get CrewAI tools
tools = asyncio.run(get_crewai_tools())

# Create an agent with Frontegg tools
agent = Agent(
    role="Research Assistant",
    goal="Find and analyze information",
    backstory="I am an AI research assistant with access to various tools.",
    tools=tools,
    verbose=True
)

# Create tasks for the agent
task = Task(
    description="Research topic X and provide insights",
    expected_output="A comprehensive report",
    agent=agent
)

# Create and run the crew
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

## Environment Configuration

The SDK supports multiple Frontegg environments:

```python
from frontegg_ai_python_sdk import Environment

# Available environments
Environment.EU # European servers: 'eu.frontegg.com'
Environment.US # US servers: 'us.frontegg.com'
Environment.CA # Canadian servers: 'ca.frontegg.com'
Environment.AU # Australian servers: 'au.frontegg.com'
Environment.UK # UK servers: 'uk.frontegg.com'
```

## Custom Logging

```python
from frontegg_ai_python_sdk import setup_logger
import logging

# Set up a custom logger
logger = setup_logger(
    name="my_custom_logger",
    level=logging.DEBUG,
    format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    file_handler="app.log"  # Also log to a file
)

# Use the custom logger with the client
client = FronteggAiClient(config, logger=logger)
```

## Requirements

- Python 3.8+

- asyncio

- httpx

- anyio

- nest_asyncio (for nested event loops)

- pydantic

- modelcontextprotocol

- crewai (optional, for CrewAI integration)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
