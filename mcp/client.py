#!/usr/bin/env python3
"""
MCP Client
Provides client functionality to interact with MCP servers.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import hashlib

from .server import MCPQuery, MCPResponse, MCPResource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServerInfo:
    """Information about an MCP server."""
    server_id: str
    name: str
    description: str
    endpoint: str
    is_available: bool = True
    last_health_check: Optional[datetime] = None
    capabilities: Dict[str, bool] = None
    metadata: Dict[str, Any] = None

class MCPClient:
    """
    MCP Client for interacting with MCP servers.
    Provides high-level interface for querying and managing MCP servers.
    """
    
    def __init__(self, timeout: int = 30):
        self.servers: Dict[str, MCPServerInfo] = {}
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.query_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes default
        
        logger.info("Initialized MCP client")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    async def start(self) -> None:
        """Start the MCP client."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        logger.info("MCP client started")
    
    async def stop(self) -> None:
        """Stop the MCP client."""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("MCP client stopped")
    
    def register_server(self, server_info: MCPServerInfo) -> None:
        """Register an MCP server."""
        self.servers[server_info.server_id] = server_info
        logger.info(f"Registered MCP server: {server_info.name} ({server_info.server_id})")
    
    def unregister_server(self, server_id: str) -> bool:
        """Unregister an MCP server."""
        if server_id in self.servers:
            server_name = self.servers[server_id].name
            del self.servers[server_id]
            logger.info(f"Unregistered MCP server: {server_name} ({server_id})")
            return True
        return False
    
    async def query_server(self, server_id: str, query: MCPQuery) -> Optional[MCPResponse]:
        """Query a specific MCP server."""
        if server_id not in self.servers:
            logger.error(f"Server {server_id} not registered")
            return None
        
        server_info = self.servers[server_id]
        
        if not server_info.is_available:
            logger.warning(f"Server {server_id} is not available")
            return None
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(server_id, query)
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result:
                logger.info(f"Returning cached result for server {server_id}")
                return cached_result
            
            # Make request to server
            response = await self._make_server_request(server_info, query)
            
            if response:
                # Cache successful response
                self._cache_result(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to query server {server_id}: {e}")
            # Mark server as potentially unavailable
            server_info.is_available = False
            return None
    
    async def query_all_servers(self, query: MCPQuery, 
                              server_filters: Optional[Dict[str, Any]] = None) -> List[MCPResponse]:
        """Query all available servers and return combined results."""
        results = []
        
        # Filter servers if criteria provided
        servers_to_query = self._filter_servers(server_filters) if server_filters else self.servers.values()
        
        # Create tasks for concurrent queries
        tasks = []
        for server_info in servers_to_query:
            if server_info.is_available:
                task = asyncio.create_task(
                    self.query_server(server_info.server_id, query)
                )
                tasks.append((server_info.server_id, task))
        
        # Wait for all queries to complete
        for server_id, task in tasks:
            try:
                response = await task
                if response and not response.error:
                    results.append(response)
            except Exception as e:
                logger.error(f"Query to server {server_id} failed: {e}")
        
        logger.info(f"Queried {len(tasks)} servers, got {len(results)} successful responses")
        return results
    
    async def search_knowledge(self, query_text: str, 
                             context: Optional[Dict[str, Any]] = None,
                             max_results: int = 10,
                             server_filters: Optional[Dict[str, Any]] = None) -> List[MCPResource]:
        """
        High-level knowledge search across all servers.
        Returns aggregated and ranked results.
        """
        # Create query
        query = MCPQuery(
            query_id=str(uuid.uuid4()),
            query_text=query_text,
            context=context or {},
            filters={},
            max_results=max_results
        )
        
        # Query all servers
        responses = await self.query_all_servers(query, server_filters)
        
        # Aggregate results
        all_resources = []
        for response in responses:
            for resource in response.resources:
                # Add server information to resource metadata
                resource.metadata["source_server"] = response.metadata.get("server_name", "unknown")
                resource.metadata["server_id"] = response.metadata.get("server_id", "unknown")
                all_resources.append(resource)
        
        # Rank and deduplicate results
        ranked_resources = self._rank_and_deduplicate(all_resources, query_text)
        
        return ranked_resources[:max_results]
    
    async def get_resource(self, server_id: str, uri: str) -> Optional[MCPResource]:
        """Retrieve a specific resource from a server."""
        if server_id not in self.servers:
            logger.error(f"Server {server_id} not registered")
            return None
        
        server_info = self.servers[server_id]
        
        try:
            # Make request to get resource
            response = await self._make_resource_request(server_info, uri)
            return response
            
        except Exception as e:
            logger.error(f"Failed to get resource {uri} from server {server_id}: {e}")
            return None
    
    async def health_check_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all registered servers."""
        health_results = {}
        
        tasks = []
        for server_id, server_info in self.servers.items():
            task = asyncio.create_task(
                self._health_check_server(server_info)
            )
            tasks.append((server_id, task))
        
        for server_id, task in tasks:
            try:
                health_status = await task
                health_results[server_id] = health_status
                
                # Update server availability
                self.servers[server_id].is_available = health_status.get("status") == "healthy"
                self.servers[server_id].last_health_check = datetime.now()
                
            except Exception as e:
                logger.error(f"Health check failed for server {server_id}: {e}")
                health_results[server_id] = {"status": "error", "error": str(e)}
                self.servers[server_id].is_available = False
        
        return health_results
    
    def get_server_info(self, server_id: str) -> Optional[MCPServerInfo]:
        """Get information about a registered server."""
        return self.servers.get(server_id)
    
    def list_servers(self) -> List[MCPServerInfo]:
        """List all registered servers."""
        return list(self.servers.values())
    
    def get_available_servers(self) -> List[MCPServerInfo]:
        """Get list of available servers."""
        return [server for server in self.servers.values() if server.is_available]
    
    # Private helper methods
    
    async def _make_server_request(self, server_info: MCPServerInfo, 
                                 query: MCPQuery) -> Optional[MCPResponse]:
        """Make a request to an MCP server."""
        if not self.session:
            await self.start()
        
        try:
            # Prepare request data
            request_data = {
                "query_id": query.query_id,
                "query_text": query.query_text,
                "context": query.context,
                "filters": query.filters,
                "max_results": query.max_results
            }
            
            # Make HTTP request
            async with self.session.post(
                f"{server_info.endpoint}/query",
                json=request_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data)
                else:
                    logger.error(f"Server {server_info.server_id} returned status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request to server {server_info.server_id} failed: {e}")
            return None
    
    async def _make_resource_request(self, server_info: MCPServerInfo, 
                                   uri: str) -> Optional[MCPResource]:
        """Make a resource request to an MCP server."""
        if not self.session:
            await self.start()
        
        try:
            async with self.session.get(
                f"{server_info.endpoint}/resource",
                params={"uri": uri}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_resource(data)
                else:
                    logger.error(f"Resource request failed with status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Resource request failed: {e}")
            return None
    
    async def _health_check_server(self, server_info: MCPServerInfo) -> Dict[str, Any]:
        """Perform health check on a server."""
        if not self.session:
            await self.start()
        
        try:
            async with self.session.get(
                f"{server_info.endpoint}/health"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "error", "http_status": response.status}
                    
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _parse_response(self, data: Dict[str, Any]) -> MCPResponse:
        """Parse server response data into MCPResponse object."""
        resources = []
        for resource_data in data.get("resources", []):
            resource = MCPResource(
                uri=resource_data["uri"],
                name=resource_data["name"],
                description=resource_data["description"],
                mime_type=resource_data["mime_type"],
                metadata=resource_data.get("metadata", {}),
                last_modified=datetime.fromisoformat(resource_data["last_modified"]),
                size=resource_data.get("size"),
                checksum=resource_data.get("checksum")
            )
            resources.append(resource)
        
        return MCPResponse(
            query_id=data["query_id"],
            resources=resources,
            metadata=data.get("metadata", {}),
            processing_time=data.get("processing_time", 0),
            total_results=data.get("total_results", len(resources)),
            has_more=data.get("has_more", False),
            error=data.get("error")
        )
    
    def _parse_resource(self, data: Dict[str, Any]) -> MCPResource:
        """Parse resource data into MCPResource object."""
        return MCPResource(
            uri=data["uri"],
            name=data["name"],
            description=data["description"],
            mime_type=data["mime_type"],
            metadata=data.get("metadata", {}),
            last_modified=datetime.fromisoformat(data["last_modified"]),
            size=data.get("size"),
            checksum=data.get("checksum")
        )
    
    def _filter_servers(self, filters: Dict[str, Any]) -> List[MCPServerInfo]:
        """Filter servers based on criteria."""
        filtered_servers = []
        
        for server in self.servers.values():
            match = True
            
            # Check capability filters
            if "capabilities" in filters:
                required_caps = filters["capabilities"]
                if isinstance(required_caps, list):
                    for cap in required_caps:
                        if not server.capabilities.get(cap, False):
                            match = False
                            break
            
            # Check metadata filters
            if "metadata" in filters and server.metadata:
                for key, value in filters["metadata"].items():
                    if server.metadata.get(key) != value:
                        match = False
                        break
            
            if match:
                filtered_servers.append(server)
        
        return filtered_servers
    
    def _rank_and_deduplicate(self, resources: List[MCPResource], 
                            query_text: str) -> List[MCPResource]:
        """Rank and deduplicate resources."""
        # Simple deduplication by URI
        seen_uris = set()
        unique_resources = []
        
        for resource in resources:
            if resource.uri not in seen_uris:
                seen_uris.add(resource.uri)
                unique_resources.append(resource)
        
        # Simple ranking by relevance score or name match
        query_lower = query_text.lower()
        
        def calculate_score(resource: MCPResource) -> float:
            score = 0
            
            # Check for existing relevance score
            if "relevance_score" in resource.metadata:
                score += resource.metadata["relevance_score"]
            
            # Name match
            if query_lower in resource.name.lower():
                score += 10
            
            # Description match
            if query_lower in resource.description.lower():
                score += 5
            
            return score
        
        # Sort by score
        unique_resources.sort(key=calculate_score, reverse=True)
        
        return unique_resources
    
    def _generate_cache_key(self, server_id: str, query: MCPQuery) -> str:
        """Generate cache key for query."""
        cache_data = {
            "server_id": server_id,
            "query_text": query.query_text,
            "filters": query.filters,
            "max_results": query.max_results
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[MCPResponse]:
        """Get result from cache if available and not expired."""
        if cache_key in self.query_cache:
            cached_data, timestamp = self.query_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.query_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, response: MCPResponse) -> None:
        """Cache query result."""
        self.query_cache[cache_key] = (response, time.time())
        
        # Simple cache cleanup
        if len(self.query_cache) > 500:
            oldest_keys = sorted(self.query_cache.keys(), 
                               key=lambda k: self.query_cache[k][1])[:100]
            for key in oldest_keys:
                del self.query_cache[key]


# Example usage
async def main():
    """Example usage of MCP client."""
    async with MCPClient() as client:
        # Register some servers
        react_server = MCPServerInfo(
            server_id="react-docs",
            name="React Documentation",
            description="Official React documentation",
            endpoint="http://localhost:8001",
            capabilities={"documentation_search": True, "api_reference": True}
        )
        
        client.register_server(react_server)
        
        # Perform health check
        health_results = await client.health_check_all_servers()
        print(f"Health check results: {health_results}")
        
        # Search for knowledge
        results = await client.search_knowledge(
            query_text="getting started with hooks",
            context={"project_type": "web_application"},
            max_results=5
        )
        
        print(f"Found {len(results)} resources:")
        for resource in results:
            print(f"- {resource.name}: {resource.description}")

if __name__ == "__main__":
    asyncio.run(main())
