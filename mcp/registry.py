#!/usr/bin/env python3
"""
MCP Registry
Manages discovery, registration, and lifecycle of MCP servers.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from .client import MCPClient, MCPServerInfo
from .server import MCPServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    server_id: str
    name: str
    description: str
    server_type: str
    endpoint: Optional[str] = None
    config: Dict[str, Any] = None
    auto_start: bool = True
    health_check_interval: int = 60
    retry_attempts: int = 3
    timeout: int = 30

class MCPRegistry:
    """
    MCP Registry manages the lifecycle of MCP servers.
    Handles discovery, registration, health monitoring, and failover.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "mcp_config.yaml"
        self.servers: Dict[str, MCPServerConfig] = {}
        self.running_servers: Dict[str, MCPServer] = {}
        self.client = MCPClient()
        self.is_running = False
        self.health_monitor_task: Optional[asyncio.Task] = None
        
        # Load configuration
        self._load_configuration()
        
        logger.info(f"Initialized MCP registry with {len(self.servers)} server configurations")
    
    async def start(self) -> None:
        """Start the MCP registry."""
        if self.is_running:
            logger.warning("MCP registry is already running")
            return
        
        logger.info("Starting MCP registry...")
        
        # Start the client
        await self.client.start()
        
        # Start configured servers
        await self._start_configured_servers()
        
        # Start health monitoring
        self.health_monitor_task = asyncio.create_task(self._health_monitor())
        
        self.is_running = True
        logger.info("MCP registry started successfully")
    
    async def stop(self) -> None:
        """Stop the MCP registry."""
        if not self.is_running:
            logger.warning("MCP registry is not running")
            return
        
        logger.info("Stopping MCP registry...")
        
        # Stop health monitoring
        if self.health_monitor_task:
            self.health_monitor_task.cancel()
            try:
                await self.health_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Stop all running servers
        await self._stop_all_servers()
        
        # Stop the client
        await self.client.stop()
        
        self.is_running = False
        logger.info("MCP registry stopped")
    
    def register_server_config(self, config: MCPServerConfig) -> None:
        """Register a server configuration."""
        self.servers[config.server_id] = config
        logger.info(f"Registered server configuration: {config.name} ({config.server_id})")
    
    def unregister_server_config(self, server_id: str) -> bool:
        """Unregister a server configuration."""
        if server_id in self.servers:
            config = self.servers[server_id]
            del self.servers[server_id]
            logger.info(f"Unregistered server configuration: {config.name} ({server_id})")
            return True
        return False
    
    async def start_server(self, server_id: str) -> bool:
        """Start a specific server."""
        if server_id not in self.servers:
            logger.error(f"Server configuration {server_id} not found")
            return False
        
        if server_id in self.running_servers:
            logger.warning(f"Server {server_id} is already running")
            return True
        
        config = self.servers[server_id]
        
        try:
            # Create server instance
            server = await self._create_server_instance(config)
            
            if server:
                # Start the server
                success = await server.start()
                
                if success:
                    self.running_servers[server_id] = server
                    
                    # Register with client
                    server_info = MCPServerInfo(
                        server_id=server_id,
                        name=config.name,
                        description=config.description,
                        endpoint=config.endpoint or f"http://localhost:8000/{server_id}",
                        capabilities=server.capabilities if hasattr(server, 'capabilities') else {}
                    )
                    self.client.register_server(server_info)
                    
                    logger.info(f"Started server: {config.name} ({server_id})")
                    return True
                else:
                    logger.error(f"Failed to start server: {config.name} ({server_id})")
                    return False
            else:
                logger.error(f"Failed to create server instance: {config.name} ({server_id})")
                return False
                
        except Exception as e:
            logger.error(f"Error starting server {server_id}: {e}")
            return False
    
    async def stop_server(self, server_id: str) -> bool:
        """Stop a specific server."""
        if server_id not in self.running_servers:
            logger.warning(f"Server {server_id} is not running")
            return True
        
        try:
            server = self.running_servers[server_id]
            success = await server.stop()
            
            if success:
                del self.running_servers[server_id]
                self.client.unregister_server(server_id)
                logger.info(f"Stopped server: {server_id}")
                return True
            else:
                logger.error(f"Failed to stop server: {server_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping server {server_id}: {e}")
            return False
    
    async def restart_server(self, server_id: str) -> bool:
        """Restart a specific server."""
        logger.info(f"Restarting server: {server_id}")
        
        # Stop the server
        stop_success = await self.stop_server(server_id)
        
        if stop_success:
            # Wait a moment before restarting
            await asyncio.sleep(1)
            
            # Start the server
            return await self.start_server(server_id)
        
        return False
    
    async def query_servers(self, query_text: str, 
                          context: Optional[Dict[str, Any]] = None,
                          server_filters: Optional[Dict[str, Any]] = None,
                          max_results: int = 10) -> List[Any]:
        """Query servers through the registry."""
        return await self.client.search_knowledge(
            query_text=query_text,
            context=context,
            max_results=max_results,
            server_filters=server_filters
        )
    
    async def get_server_health(self, server_id: Optional[str] = None) -> Dict[str, Any]:
        """Get health status of servers."""
        if server_id:
            # Get health of specific server
            server_info = self.client.get_server_info(server_id)
            if server_info:
                health_results = await self.client.health_check_all_servers()
                return health_results.get(server_id, {"status": "unknown"})
            else:
                return {"status": "not_registered"}
        else:
            # Get health of all servers
            return await self.client.health_check_all_servers()
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get overall server status."""
        return {
            "registry_running": self.is_running,
            "configured_servers": len(self.servers),
            "running_servers": len(self.running_servers),
            "available_servers": len(self.client.get_available_servers()),
            "server_details": {
                server_id: {
                    "name": config.name,
                    "type": config.server_type,
                    "running": server_id in self.running_servers,
                    "available": any(s.server_id == server_id for s in self.client.get_available_servers())
                }
                for server_id, config in self.servers.items()
            }
        }
    
    def save_configuration(self) -> None:
        """Save current configuration to file."""
        config_data = {
            "servers": {
                server_id: asdict(config)
                for server_id, config in self.servers.items()
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    # Private methods
    
    def _load_configuration(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            logger.info(f"Configuration file {self.config_file} not found, using defaults")
            self._create_default_configuration()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if "servers" in config_data:
                for server_id, server_config in config_data["servers"].items():
                    config = MCPServerConfig(**server_config)
                    self.servers[server_id] = config
            
            logger.info(f"Loaded configuration from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self) -> None:
        """Create default configuration."""
        default_servers = [
            MCPServerConfig(
                server_id="react-docs",
                name="React Documentation",
                description="Official React documentation server",
                server_type="documentation",
                config={
                    "documentation_url": "https://react.dev",
                    "api_key": None
                }
            ),
            MCPServerConfig(
                server_id="python-docs",
                name="Python Documentation",
                description="Official Python documentation server",
                server_type="documentation",
                config={
                    "documentation_url": "https://docs.python.org",
                    "api_key": None
                }
            ),
            MCPServerConfig(
                server_id="stackoverflow",
                name="Stack Overflow",
                description="Stack Overflow Q&A integration",
                server_type="community",
                config={
                    "api_key": None,
                    "rate_limit": 100
                }
            )
        ]
        
        for config in default_servers:
            self.servers[config.server_id] = config
        
        # Save default configuration
        self.save_configuration()
        
        logger.info("Created default configuration")
    
    async def _start_configured_servers(self) -> None:
        """Start all configured servers that have auto_start enabled."""
        for server_id, config in self.servers.items():
            if config.auto_start:
                logger.info(f"Auto-starting server: {config.name} ({server_id})")
                await self.start_server(server_id)
    
    async def _stop_all_servers(self) -> None:
        """Stop all running servers."""
        stop_tasks = []
        for server_id in list(self.running_servers.keys()):
            task = asyncio.create_task(self.stop_server(server_id))
            stop_tasks.append(task)
        
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
    
    async def _create_server_instance(self, config: MCPServerConfig) -> Optional[MCPServer]:
        """Create a server instance based on configuration."""
        try:
            if config.server_type == "documentation":
                from .server import DocumentationMCPServer
                return DocumentationMCPServer(
                    server_id=config.server_id,
                    name=config.name,
                    documentation_url=config.config.get("documentation_url", ""),
                    api_key=config.config.get("api_key")
                )
            elif config.server_type == "community":
                # Placeholder for community servers (Stack Overflow, etc.)
                logger.warning(f"Community server type not yet implemented: {config.server_id}")
                return None
            elif config.server_type == "codebase":
                # Placeholder for codebase servers
                logger.warning(f"Codebase server type not yet implemented: {config.server_id}")
                return None
            else:
                logger.error(f"Unknown server type: {config.server_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create server instance for {config.server_id}: {e}")
            return None
    
    async def _health_monitor(self) -> None:
        """Background health monitoring task."""
        while self.is_running:
            try:
                # Perform health checks
                health_results = await self.client.health_check_all_servers()
                
                # Check for failed servers and attempt restart
                for server_id, health in health_results.items():
                    if health.get("status") != "healthy":
                        logger.warning(f"Server {server_id} is unhealthy: {health}")
                        
                        # Attempt restart if server is configured for auto-restart
                        if server_id in self.servers and server_id in self.running_servers:
                            config = self.servers[server_id]
                            if config.retry_attempts > 0:
                                logger.info(f"Attempting to restart unhealthy server: {server_id}")
                                await self.restart_server(server_id)
                
                # Wait before next health check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)


# Example usage
async def main():
    """Example usage of MCP registry."""
    registry = MCPRegistry()
    
    try:
        # Start the registry
        await registry.start()
        
        # Get server status
        status = registry.get_server_status()
        print(f"Server status: {json.dumps(status, indent=2)}")
        
        # Query servers
        results = await registry.query_servers(
            query_text="getting started",
            context={"project_type": "web_application"}
        )
        
        print(f"Query results: {len(results)} resources found")
        
        # Wait a bit to see health monitoring
        await asyncio.sleep(5)
        
    finally:
        # Stop the registry
        await registry.stop()

if __name__ == "__main__":
    asyncio.run(main())
