"""
AI Agents Client Module

This module provides the main client interface for the AI Agents SDK.
"""

import logging
from typing import Any, Dict, Optional, Callable, Union, List, Type, ClassVar
import os
import json
from datetime import datetime, timedelta

import mcp
from mcp import ClientSession
import mcp.types as types
from .httpTransport import streamablehttp_client
import httpx
import jsonref  # Added import for jsonref

from .config import FronteggAiClientConfig
from .enums import Environment
from .logger import default_logger

from mcpadapt.utils.modeling import create_model_from_json_schema
from crewai.tools import BaseTool
from pydantic import BaseModel
import asyncio
import nest_asyncio


class FronteggAiClient:
    """
    Client for interacting with Frontegg AI Agents.
    Implements the singleton pattern to ensure only one instance exists.
    """
    _instance = None
    _initialized = False

    def __new__(cls, config: FronteggAiClientConfig, logger: Optional[logging.Logger] = None):
        """
        Create a new instance if none exists, otherwise return the existing instance.
        
        Args:
            config: Configuration for the client
            logger: Logger instance (optional)
        """
        if cls._instance is None:
            cls._instance = super(FronteggAiClient, cls).__new__(cls)
            cls._instance.__init__(config, logger)
        return cls._instance

    def __init__(
        self,
        config: FronteggAiClientConfig,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize a new Frontegg AI Agents client.
        Will only initialize once, even if called multiple times.

        Args:
            config: Configuration for the client
            logger: Logger instance (optional)
        """
        if not self._initialized:
            self.config = config
            self.logger = logger or default_logger
            self.vendorJwt = None
            
            if os.environ.get("FRONTEGG_STAGING_OVERRIDE") == "true":
                base_domain = "stg.frontegg.com"
            else:
                base_domain = config.environment.value
            
            self.mcp_url = f"https://mcp.{base_domain}/mcp/v1"
            self.base_url = f"https://api.{base_domain}"
            
            self.headers = {
                "agent-id": config.agent_id,
                "Authorization": f"Bearer {config.client_secret}",
                "tenant-id": config.client_id,
            }
            
            self.__class__._initialized = True

    async def list_tools(self) -> List[types.Tool]:
        """
        List all available tools.
        
        Returns:
            List of available tools
        """
        await self._refresh_transport_if_needed()
        self._update_headers(self.config.client_id, None)
        async with streamablehttp_client(f"{self.mcp_url}", self.headers) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:
                result = await session.initialize()
                tools = await session.list_tools()  
                return tools

    async def list_tools_as_crewai_tools(self) -> List[BaseTool]:
        """
        List all available tools as CrewAI tools.
        """
        tools_response = await self.list_tools()
        if hasattr(tools_response, 'tools'):
            return [self._adapt_mcp_tool_to_crewai_tool(tool) for tool in tools_response.tools]
        else:
            self.logger.error(f"Unexpected response type from list_tools: {type(tools_response)}")
            return []

    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a tool by name.
        
        Args:
            name: Name of the tool
            arguments: Optional arguments for the tool
            user_id: Optional user ID for the tool call
            
        Returns:
            The tool result
        """
        await self._refresh_transport_if_needed()
        async with streamablehttp_client(f"{self.mcp_url}", self.headers) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:
                result = await session.initialize()
                tools = await session.call_tool(name, arguments or {})  
                return tools

    def call_tool_sync(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """
        Synchronous version of call_tool.
        
        Args:
            name: Name of the tool
            arguments: Optional arguments for the tool
            user_id: Optional user ID for the tool call
            
        Returns:
            The tool result
        """
        try:
            # Check if we're already in an event loop
            if asyncio.get_event_loop().is_running():
                nest_asyncio.apply()
                return asyncio.get_event_loop().run_until_complete(
                    self.call_tool(name, arguments)
                )
            else:
                # If we're not in an event loop, use run_until_complete
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(self.call_tool(name, arguments))
        except RuntimeError:
            # If there's no event loop in the current thread, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.call_tool(name, arguments))
            finally:
                loop.close()

        
    def set_context(self, tenant_id: str, user_id: Optional[str] = None) -> None:
        self._update_headers(tenant_id, user_id)

    def set_user_context_by_jwt(self, user_jwt: str) -> None:
        self.headers['frontegg-user-access-token'] = user_jwt

    def _adapt_mcp_tool_to_crewai_tool(self, mcp_tool: types.Tool) -> BaseTool:
        # Check if inputSchema exists, if not, create an empty model
        if hasattr(mcp_tool, 'inputSchema') and mcp_tool.inputSchema:
            ToolInput = create_model_from_json_schema(mcp_tool.inputSchema)
        else:
            raise ValueError(f"Tool {mcp_tool.name} has no input schema")

        class CrewAIMCPTool(BaseTool):
            name: str = mcp_tool.name
            description: str = getattr(mcp_tool, 'description', '') or ''
            args_schema: Type[BaseModel] = ToolInput

            def _run(self, *args: Any, **kwargs: Any) -> Any:
                try:
                    client = FronteggAiClient({})
                    name = kwargs.pop('name', self.name)
                    arguments = kwargs
                    
                    return client.call_tool_sync(name, arguments)
                except ImportError as e:
                    # If nest_asyncio is required but not available, try to install it
                    if "install 'nest_asyncio'" in str(e):
                        try:
                            import subprocess
                            subprocess.check_call(["pip", "install", "nest_asyncio"])
                            # Try again after installing
                            import nest_asyncio
                            nest_asyncio.apply()
                            client = FronteggAiClient({})
                            return client.call_tool_sync(self.name, kwargs)
                        except Exception as install_err:
                            raise RuntimeError(f"Failed to install nest_asyncio: {install_err}. {str(e)}")
                    else:
                        raise

            def _generate_description(self):
                try:
                    args_schema = {
                        k: v
                        for k, v in jsonref.replace_refs(
                            self.args_schema.model_json_schema()
                        ).items()
                        if k != "$defs"
                    }
                    self.description = f"Tool Name: {self.name}\nTool Arguments: {args_schema}\nTool Description: {self.description}"
                except Exception as e:
                    self.description = f"Tool Name: {self.name}\nTool Description: {self.description}"

        return CrewAIMCPTool()


    def _update_headers(self, tenant_id: str, user_id: Optional[str] = None) -> None:
        self.headers["tenant-id"] = tenant_id
        if user_id:
            self.headers["user-id"] = user_id

    async def _refresh_transport_if_needed(self) -> None:
        if self.vendorJwt and self.vendorJwt['expiration'] > datetime.now():
            return
        await self._refresh_transport()

    async def _refresh_transport(self) -> None:
        try:
            await self._refresh_vendor_jwt()
            if not self.vendorJwt:
                raise Exception("Failed to refresh vendor JWT")
            self.headers["Authorization"] = f"Bearer {self.vendorJwt['token']}"
        except Exception as error:
            self.logger.error("Failed to refresh transport", exc_info=error)
            raise

    async def _refresh_vendor_jwt(self) -> Dict[str, Any]:
        """
        Refresh the vendor JWT token.
        """
        jwt = await self._create_vendor_jwt()
        self.vendorJwt = jwt

    async def _create_vendor_jwt(self) -> Dict[str, Any]:
        """
        Create a vendor JWT token for authentication.
        
        Returns:
            Dictionary containing the token and expiration date
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/vendor/",
                    headers={
                        "Content-Type": "application/json",
                    },
                    json={
                        "clientId": self.config.client_id,
                        "secret": self.config.client_secret,
                    },
                )
                
                if response.status_code != 200:
                    error_body = response.text
                    raise Exception(f"Failed to create vendor JWT: {response.status_code} {response.reason_phrase} - {error_body}")
                
                result = response.json()
                expiration = datetime.now() + timedelta(seconds=result["expiresIn"])
                self.logger.info(f"Vendor JWT created: {result['token']} - Expires: {expiration}")
                
                return {
                    "token": result["token"],
                    "expiration": expiration,
                }
                
        except Exception as error:
            self.logger.error("Failed to create vendor JWT", exc_info=error)
            raise 