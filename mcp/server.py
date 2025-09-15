#!/usr/bin/env python3
"""
MCP Server Base Class
Provides the foundation for all MCP server implementations.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import uuid

# Library logging: do not configure handlers/levels at import time.
# Leave configuration to applications. Configure only in __main__ example usage.
logger = logging.getLogger(__name__)

@dataclass
class MCPResource:
    """Represents a resource available through MCP."""
    uri: str
    name: str
    description: str
    mime_type: str
    metadata: Dict[str, Any]
    last_modified: datetime
    size: Optional[int] = None
    checksum: Optional[str] = None

@dataclass
class MCPQuery:
    """Represents a query to an MCP server."""
    query_id: str
    query_text: str
    context: Dict[str, Any]
    filters: Dict[str, Any]
    max_results: int = 10
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class MCPResponse:
    """Represents a response from an MCP server."""
    query_id: str
    resources: List[MCPResource]
    metadata: Dict[str, Any]
    processing_time: float
    total_results: int
    has_more: bool = False
    error: Optional[str] = None

class MCPServer(ABC):
    """
    Abstract base class for MCP servers.
    Provides common functionality for all MCP server implementations.
    """
    
    def __init__(self, server_id: str, name: str, description: str):
        self.server_id = server_id
        self.name = name
        self.description = description
        self.resources: Dict[str, MCPResource] = {}
        self.is_running = False
        self.health_status = "healthy"
        self.last_health_check = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour default TTL
        
        # Server capabilities
        self.capabilities = {
            "search": True,
            "retrieve": True,
            "index": True,
            "cache": True,
            "health_check": True
        }
        
        logger.info(f"Initialized MCP server: {self.name} ({self.server_id})")
    
    async def start(self) -> bool:
        """Start the MCP server."""
        try:
            logger.info(f"Starting MCP server: {self.name}")
            
            # Initialize server-specific resources
            await self._initialize_resources()
            
            # Start health monitoring
            asyncio.create_task(self._health_monitor())
            
            self.is_running = True
            logger.info(f"MCP server {self.name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server {self.name}: {e}")
            self.health_status = "error"
            return False
    
    async def stop(self) -> bool:
        """Stop the MCP server."""
        try:
            logger.info(f"Stopping MCP server: {self.name}")
            
            # Cleanup resources
            await self._cleanup_resources()
            
            self.is_running = False
            logger.info(f"MCP server {self.name} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop MCP server {self.name}: {e}")
            return False
    
    async def query(self, query: MCPQuery) -> MCPResponse:
        """
        Process a query and return results.
        This is the main entry point for MCP queries.
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            logger.info(f"Processing query: {query.query_text[:100]}...")
            
            # Check cache first
            cache_key = self._generate_cache_key(query)
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result:
                logger.info("Returning cached result")
                cached_result.metadata["from_cache"] = True
                return cached_result
            
            # Process query
            resources = await self._process_query(query)
            
            # Create response
            processing_time = time.time() - start_time
            response = MCPResponse(
                query_id=query.query_id,
                resources=resources,
                metadata={
                    "server_id": self.server_id,
                    "server_name": self.name,
                    "from_cache": False,
                    "query_filters": query.filters
                },
                processing_time=processing_time,
                total_results=len(resources),
                has_more=len(resources) >= query.max_results
            )
            
            # Cache result
            self._cache_result(cache_key, response)
            
            logger.info(f"Query processed successfully: {len(resources)} results in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Query processing failed: {e}")
            
            processing_time = time.time() - start_time
            return MCPResponse(
                query_id=query.query_id,
                resources=[],
                metadata={"server_id": self.server_id, "server_name": self.name},
                processing_time=processing_time,
                total_results=0,
                error=str(e)
            )
    
    async def get_resource(self, uri: str) -> Optional[MCPResource]:
        """Retrieve a specific resource by URI."""
        try:
            return await self._get_resource_content(uri)
        except Exception as e:
            logger.error(f"Failed to retrieve resource {uri}: {e}")
            return None
    
    async def list_resources(self) -> List[MCPResource]:
        """List all available resources."""
        try:
            return await self._list_all_resources()
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        try:
            # Update health status
            await self._perform_health_check()
            
            return {
                "server_id": self.server_id,
                "name": self.name,
                "status": self.health_status,
                "is_running": self.is_running,
                "last_health_check": self.last_health_check.isoformat(),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate": self.error_count / max(self.request_count, 1),
                "capabilities": self.capabilities,
                "resource_count": len(self.resources)
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.health_status = "error"
            return {
                "server_id": self.server_id,
                "name": self.name,
                "status": "error",
                "error": str(e)
            }
    
    # Abstract methods that must be implemented by subclasses
    
    @abstractmethod
    async def _initialize_resources(self) -> None:
        """Initialize server-specific resources."""
        pass
    
    @abstractmethod
    async def _process_query(self, query: MCPQuery) -> List[MCPResource]:
        """Process a query and return matching resources."""
        pass
    
    @abstractmethod
    async def _get_resource_content(self, uri: str) -> Optional[MCPResource]:
        """Retrieve the content of a specific resource."""
        pass
    
    @abstractmethod
    async def _list_all_resources(self) -> List[MCPResource]:
        """List all available resources."""
        pass
    
    # Helper methods
    
    async def _cleanup_resources(self) -> None:
        """Cleanup server resources."""
        self.resources.clear()
        self.cache.clear()
    
    async def _perform_health_check(self) -> None:
        """Perform server-specific health checks."""
        self.last_health_check = datetime.now()
        
        # Basic health checks
        if not self.is_running:
            self.health_status = "stopped"
        elif self.error_count / max(self.request_count, 1) > 0.1:  # >10% error rate
            self.health_status = "degraded"
        else:
            self.health_status = "healthy"
    
    async def _health_monitor(self) -> None:
        """Background health monitoring task."""
        while self.is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    def _generate_cache_key(self, query: MCPQuery) -> str:
        """Generate a cache key for a query."""
        query_data = {
            "query_text": query.query_text,
            "filters": query.filters,
            "max_results": query.max_results
        }
        query_str = json.dumps(query_data, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[MCPResponse]:
        """Retrieve result from cache if available and not expired."""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, response: MCPResponse) -> None:
        """Cache a query result."""
        self.cache[cache_key] = (response, time.time())
        
        # Simple cache cleanup - remove oldest entries if cache is too large
        if len(self.cache) > 1000:
            # Remove oldest 100 entries
            oldest_keys = sorted(self.cache.keys(), key=lambda k: self.cache[k][1])[:100]
            for key in oldest_keys:
                del self.cache[key]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert server info to dictionary."""
        return {
            "server_id": self.server_id,
            "name": self.name,
            "description": self.description,
            "is_running": self.is_running,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "resource_count": len(self.resources),
            "request_count": self.request_count,
            "error_count": self.error_count
        }


class DocumentationMCPServer(MCPServer):
    """
    Specialized MCP server for documentation sources.
    Handles documentation indexing, search, and retrieval.
    """
    
    def __init__(self, server_id: str, name: str, documentation_url: str, 
                 api_key: Optional[str] = None):
        super().__init__(server_id, name, f"Documentation server for {name}")
        self.documentation_url = documentation_url
        self.api_key = api_key
        self.indexed_pages: Dict[str, Dict[str, Any]] = {}
        
        # Documentation-specific capabilities
        self.capabilities.update({
            "documentation_search": True,
            "api_reference": True,
            "code_examples": True,
            "version_tracking": True
        })
    
    async def _initialize_resources(self) -> None:
        """Initialize documentation resources."""
        logger.info(f"Initializing documentation resources for {self.name}")
        
        # This would typically crawl and index documentation
        # For now, we'll create placeholder resources
        await self._index_documentation()
    
    async def _index_documentation(self) -> None:
        """Index documentation pages."""
        # Placeholder implementation
        # In a real implementation, this would crawl the documentation site
        logger.info(f"Indexing documentation from {self.documentation_url}")
        
        # Create sample resources
        sample_resources = [
            {
                "uri": f"{self.documentation_url}/getting-started",
                "name": "Getting Started Guide",
                "description": "Introduction and setup guide",
                "content_type": "guide",
                "sections": ["installation", "configuration", "first-steps"]
            },
            {
                "uri": f"{self.documentation_url}/api-reference",
                "name": "API Reference",
                "description": "Complete API documentation",
                "content_type": "api",
                "sections": ["authentication", "endpoints", "examples"]
            }
        ]
        
        for resource_data in sample_resources:
            resource = MCPResource(
                uri=resource_data["uri"],
                name=resource_data["name"],
                description=resource_data["description"],
                mime_type="text/html",
                metadata={
                    "content_type": resource_data["content_type"],
                    "sections": resource_data["sections"],
                    "source": self.name
                },
                last_modified=datetime.now()
            )
            self.resources[resource.uri] = resource
    
    async def _process_query(self, query: MCPQuery) -> List[MCPResource]:
        """Process documentation search query."""
        results = []
        query_lower = query.query_text.lower()
        
        for resource in self.resources.values():
            # Simple relevance scoring based on name and description
            score = 0
            if query_lower in resource.name.lower():
                score += 10
            if query_lower in resource.description.lower():
                score += 5
            
            # Check metadata sections
            if "sections" in resource.metadata:
                for section in resource.metadata["sections"]:
                    if query_lower in section.lower():
                        score += 3
            
            if score > 0:
                resource.metadata["relevance_score"] = score
                results.append(resource)
        
        # Sort by relevance score
        results.sort(key=lambda r: r.metadata.get("relevance_score", 0), reverse=True)
        
        return results[:query.max_results]
    
    async def _get_resource_content(self, uri: str) -> Optional[MCPResource]:
        """Retrieve documentation resource content."""
        return self.resources.get(uri)
    
    async def _list_all_resources(self) -> List[MCPResource]:
        """List all documentation resources."""
        return list(self.resources.values())


# Example usage and testing
async def main():
    """Example usage of MCP server."""
    # Create a documentation server
    server = DocumentationMCPServer(
        server_id="react-docs",
        name="React Documentation",
        documentation_url="https://react.dev"
    )
    
    # Start the server
    await server.start()
    
    # Perform a health check
    health = await server.health_check()
    print(f"Server health: {health}")
    
    # Create a query
    query = MCPQuery(
        query_id=str(uuid.uuid4()),
        query_text="getting started",
        context={"project_type": "web_application"},
        filters={"content_type": "guide"}
    )
    
    # Process the query
    response = await server.query(query)
    print(f"Query results: {len(response.resources)} resources found")
    
    for resource in response.resources:
        print(f"- {resource.name}: {resource.description}")
    
    # Stop the server
    await server.stop()

if __name__ == "__main__":
    # Example script entrypoint: configure basic logging for demo run only
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
