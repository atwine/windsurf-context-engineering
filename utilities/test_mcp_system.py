#!/usr/bin/env python3
"""
MCP System Integration Test
Tests the complete MCP (Model Context Protocol) system including servers, clients, and knowledge base.
"""

import asyncio
import json
import logging
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any
import uuid
from datetime import datetime

# Add mcp to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server import MCPQuery, MCPResource
from mcp.client import MCPClient, MCPServerInfo
from mcp.registry import MCPRegistry, MCPServerConfig
from mcp.knowledge_base import KnowledgeBase, KnowledgeEntry
from mcp.semantic_search import SemanticSearch
from mcp.servers.react_docs_server import ReactDocumentationServer
from mcp.servers.stackoverflow_server import StackOverflowServer

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise
logger = logging.getLogger(__name__)

class MCPSystemTest:
    """Test suite for the complete MCP system."""
    
    def __init__(self):
        self.test_results = {
            'server_test': {},
            'client_test': {},
            'knowledge_base_test': {},
            'semantic_search_test': {},
            'registry_test': {},
            'integration_test': {}
        }
        self.temp_dir = None
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive MCP system tests."""
        print("🔧 MCP System Integration Test")
        print("=" * 50)
        
        try:
            # Set up temporary directory
            self.temp_dir = tempfile.mkdtemp()
            
            # Run individual tests
            await self.test_mcp_servers()
            await self.test_mcp_client()
            await self.test_knowledge_base()
            await self.test_semantic_search()
            await self.test_mcp_registry()
            await self.test_full_integration()
            
            # Generate final report
            return self._generate_test_report()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return {'error': str(e)}
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
    
    async def test_mcp_servers(self):
        """Test MCP server functionality."""
        print("\n🖥️ Testing MCP Servers...")
        
        try:
            # Test React Documentation Server
            react_server = ReactDocumentationServer()
            
            # Start server
            start_success = await react_server.start()
            if not start_success:
                raise Exception("Failed to start React server")
            
            # Test health check
            health = await react_server.health_check()
            if health.get("status") != "healthy":
                raise Exception(f"Server health check failed: {health}")
            
            # Test query processing
            query = MCPQuery(
                query_id=str(uuid.uuid4()),
                query_text="useState hook examples",
                context={"project_type": "web_application"},
                filters={}
            )
            
            response = await react_server.query(query)
            if response.error:
                raise Exception(f"Query failed: {response.error}")
            
            if len(response.resources) == 0:
                raise Exception("No resources returned from query")
            
            # Test resource retrieval
            if response.resources:
                resource = await react_server.get_resource(response.resources[0].uri)
                if not resource:
                    raise Exception("Failed to retrieve resource")
            
            # Stop server
            await react_server.stop()
            
            print("  ✅ React Documentation Server: PASSED")
            
            # Test Stack Overflow Server (basic functionality)
            so_server = StackOverflowServer()
            
            start_success = await so_server.start()
            if not start_success:
                raise Exception("Failed to start Stack Overflow server")
            
            health = await so_server.health_check()
            if health.get("status") != "healthy":
                raise Exception(f"SO server health check failed: {health}")
            
            await so_server.stop()
            
            print("  ✅ Stack Overflow Server: PASSED")
            
            self.test_results['server_test'] = {
                'status': 'PASSED',
                'react_server': 'PASSED',
                'stackoverflow_server': 'PASSED',
                'summary': 'All MCP servers functioning correctly'
            }
            
        except Exception as e:
            print(f"  ❌ MCP Servers test failed: {e}")
            self.test_results['server_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_mcp_client(self):
        """Test MCP client functionality."""
        print("\n📱 Testing MCP Client...")
        
        try:
            async with MCPClient() as client:
                # Register a test server
                server_info = MCPServerInfo(
                    server_id="test-server",
                    name="Test Server",
                    description="Test server for client testing",
                    endpoint="http://localhost:8001",
                    capabilities={"search": True, "retrieve": True}
                )
                
                client.register_server(server_info)
                
                # Test server registration
                registered_servers = client.list_servers()
                if len(registered_servers) != 1:
                    raise Exception("Server registration failed")
                
                # Test server info retrieval
                info = client.get_server_info("test-server")
                if not info or info.server_id != "test-server":
                    raise Exception("Server info retrieval failed")
                
                # Test unregistration
                success = client.unregister_server("test-server")
                if not success:
                    raise Exception("Server unregistration failed")
                
                if len(client.list_servers()) != 0:
                    raise Exception("Server not properly unregistered")
            
            print("  ✅ MCP Client: PASSED")
            
            self.test_results['client_test'] = {
                'status': 'PASSED',
                'registration': 'PASSED',
                'info_retrieval': 'PASSED',
                'unregistration': 'PASSED',
                'summary': 'MCP client functioning correctly'
            }
            
        except Exception as e:
            print(f"  ❌ MCP Client test failed: {e}")
            self.test_results['client_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_knowledge_base(self):
        """Test knowledge base functionality."""
        print("\n🗄️ Testing Knowledge Base...")
        
        try:
            # Use temporary database
            db_path = os.path.join(self.temp_dir, "test_kb.db")
            
            with KnowledgeBase(db_path) as kb:
                # Test entry creation
                resource = MCPResource(
                    uri="https://example.com/test",
                    name="Test Resource",
                    description="A test resource for knowledge base testing",
                    mime_type="text/plain",
                    metadata={"category": "test", "type": "example"},
                    last_modified=datetime.now()
                )
                
                entry_id = await kb.add_entry(
                    resource=resource,
                    content="This is test content for the knowledge base.",
                    tags=["test", "example", "knowledge"]
                )
                
                if not entry_id:
                    raise Exception("Failed to add entry to knowledge base")
                
                # Test entry retrieval
                retrieved_entry = await kb.get_entry(entry_id)
                if not retrieved_entry:
                    raise Exception("Failed to retrieve entry from knowledge base")
                
                if retrieved_entry.resource.name != "Test Resource":
                    raise Exception("Retrieved entry data mismatch")
                
                # Test search functionality
                search_results = await kb.search_entries("test content")
                if len(search_results) == 0:
                    raise Exception("Search returned no results")
                
                # Test tag-based search
                tag_results = await kb.get_entries_by_tag("test")
                if len(tag_results) == 0:
                    raise Exception("Tag search returned no results")
                
                # Test statistics
                stats = await kb.get_statistics()
                if stats.get("total_entries", 0) == 0:
                    raise Exception("Statistics show no entries")
                
                # Test entry update
                updated_id = await kb.update_entry(
                    entry_id, resource, "Updated test content", ["test", "updated"]
                )
                if updated_id != entry_id:
                    raise Exception("Entry update failed")
                
                # Test entry deletion
                delete_success = await kb.delete_entry(entry_id)
                if not delete_success:
                    raise Exception("Entry deletion failed")
            
            print("  ✅ Knowledge Base: PASSED")
            
            self.test_results['knowledge_base_test'] = {
                'status': 'PASSED',
                'entry_creation': 'PASSED',
                'entry_retrieval': 'PASSED',
                'search': 'PASSED',
                'tag_search': 'PASSED',
                'statistics': 'PASSED',
                'update': 'PASSED',
                'deletion': 'PASSED',
                'summary': 'Knowledge base functioning correctly'
            }
            
        except Exception as e:
            print(f"  ❌ Knowledge Base test failed: {e}")
            self.test_results['knowledge_base_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_semantic_search(self):
        """Test semantic search functionality."""
        print("\n🔍 Testing Semantic Search...")
        
        try:
            # Set up knowledge base with test data
            db_path = os.path.join(self.temp_dir, "test_search_kb.db")
            
            with KnowledgeBase(db_path) as kb:
                # Add test entries
                test_entries = [
                    {
                        "resource": MCPResource(
                            uri="https://example.com/react-hooks",
                            name="React Hooks Guide",
                            description="Complete guide to React hooks",
                            mime_type="text/html",
                            metadata={"framework": "react", "type": "tutorial"},
                            last_modified=datetime.now()
                        ),
                        "content": "React hooks are functions that let you use state and other React features in functional components.",
                        "tags": ["react", "hooks", "tutorial"]
                    },
                    {
                        "resource": MCPResource(
                            uri="https://example.com/python-async",
                            name="Python Async Programming",
                            description="Guide to asynchronous programming in Python",
                            mime_type="text/html",
                            metadata={"language": "python", "type": "tutorial"},
                            last_modified=datetime.now()
                        ),
                        "content": "Asynchronous programming in Python allows you to write concurrent code using async/await syntax.",
                        "tags": ["python", "async", "tutorial"]
                    }
                ]
                
                entry_ids = []
                for entry_data in test_entries:
                    entry_id = await kb.add_entry(
                        resource=entry_data["resource"],
                        content=entry_data["content"],
                        tags=entry_data["tags"]
                    )
                    entry_ids.append(entry_id)
                
                # Initialize semantic search
                search_engine = SemanticSearch(kb)
                await search_engine.initialize()
                
                # Test keyword search
                keyword_results = await search_engine.search("React hooks", "keyword", max_results=5)
                if len(keyword_results) == 0:
                    raise Exception("Keyword search returned no results")
                
                # Test hybrid search
                hybrid_results = await search_engine.search("Python async", "hybrid", max_results=5)
                if len(hybrid_results) == 0:
                    raise Exception("Hybrid search returned no results")
                
                # Test recommendations
                context = {"project_type": "web_application", "technologies": ["react"]}
                recommendations = await search_engine.get_recommendations(context, max_results=3)
                if len(recommendations) == 0:
                    raise Exception("Recommendations returned no results")
                
                # Test similar entries
                if entry_ids:
                    similar = await search_engine.find_similar_entries(entry_ids[0], max_results=2)
                    # Similar entries test is optional since we only have 2 entries
                
                # Test index rebuild
                await search_engine.rebuild_indexes()
            
            print("  ✅ Semantic Search: PASSED")
            
            self.test_results['semantic_search_test'] = {
                'status': 'PASSED',
                'keyword_search': 'PASSED',
                'hybrid_search': 'PASSED',
                'recommendations': 'PASSED',
                'index_rebuild': 'PASSED',
                'summary': 'Semantic search functioning correctly'
            }
            
        except Exception as e:
            print(f"  ❌ Semantic Search test failed: {e}")
            self.test_results['semantic_search_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_mcp_registry(self):
        """Test MCP registry functionality."""
        print("\n📋 Testing MCP Registry...")
        
        try:
            # Create temporary config file
            config_file = os.path.join(self.temp_dir, "test_mcp_config.yaml")
            
            registry = MCPRegistry(config_file)
            
            # Test server configuration registration
            config = MCPServerConfig(
                server_id="test-registry-server",
                name="Test Registry Server",
                description="Test server for registry testing",
                server_type="documentation",
                auto_start=False,
                config={"documentation_url": "https://example.com"}
            )
            
            registry.register_server_config(config)
            
            # Test configuration save/load
            registry.save_configuration()
            if not os.path.exists(config_file):
                raise Exception("Configuration file not created")
            
            # Test server status
            status = registry.get_server_status()
            if status.get("configured_servers", 0) == 0:
                raise Exception("No configured servers found")
            
            # Test unregistration
            success = registry.unregister_server_config("test-registry-server")
            if not success:
                raise Exception("Server configuration unregistration failed")
            
            print("  ✅ MCP Registry: PASSED")
            
            self.test_results['registry_test'] = {
                'status': 'PASSED',
                'configuration': 'PASSED',
                'save_load': 'PASSED',
                'status_check': 'PASSED',
                'unregistration': 'PASSED',
                'summary': 'MCP registry functioning correctly'
            }
            
        except Exception as e:
            print(f"  ❌ MCP Registry test failed: {e}")
            self.test_results['registry_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_full_integration(self):
        """Test full system integration."""
        print("\n🔄 Testing Full Integration...")
        
        try:
            # Set up complete system
            db_path = os.path.join(self.temp_dir, "integration_kb.db")
            
            # Initialize components
            kb = KnowledgeBase(db_path)
            search_engine = SemanticSearch(kb)
            
            with kb:
                # Add sample data
                resource = MCPResource(
                    uri="https://example.com/integration-test",
                    name="Integration Test Resource",
                    description="Resource for testing full system integration",
                    mime_type="text/html",
                    metadata={"type": "integration", "framework": "test"},
                    last_modified=datetime.now()
                )
                
                await kb.add_entry(
                    resource=resource,
                    content="This is content for testing the full MCP system integration.",
                    tags=["integration", "test", "mcp"]
                )
                
                # Initialize search
                await search_engine.initialize()
                
                # Test end-to-end workflow
                # 1. Search for content
                results = await search_engine.search("integration test", "hybrid", max_results=5)
                if len(results) == 0:
                    raise Exception("Integration search returned no results")
                
                # 2. Get recommendations
                context = {"project_type": "test", "technologies": ["mcp"]}
                recommendations = await search_engine.get_recommendations(context, max_results=3)
                
                # 3. Verify data consistency
                stats = await kb.get_statistics()
                if stats.get("total_entries", 0) == 0:
                    raise Exception("No entries found in integration test")
                
                # Test system performance
                import time
                start_time = time.time()
                
                # Perform multiple operations
                for i in range(5):
                    await search_engine.search(f"test query {i}", "keyword", max_results=3)
                
                end_time = time.time()
                performance_time = end_time - start_time
                
                if performance_time > 5.0:  # Should complete within 5 seconds
                    raise Exception(f"System performance too slow: {performance_time:.2f}s")
            
            print("  ✅ Full Integration: PASSED")
            
            self.test_results['integration_test'] = {
                'status': 'PASSED',
                'end_to_end_workflow': 'PASSED',
                'data_consistency': 'PASSED',
                'performance': 'PASSED',
                'performance_time': f"{performance_time:.2f}s",
                'summary': 'Full system integration working correctly'
            }
            
        except Exception as e:
            print(f"  ❌ Full Integration test failed: {e}")
            self.test_results['integration_test'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'PASSED')
        total_tests = len(self.test_results)
        
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': (passed_tests / total_tests) * 100,
                'test_timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results,
            'overall_assessment': self._get_overall_assessment()
        }
        
        return report
    
    def _get_overall_assessment(self) -> str:
        """Get overall assessment of MCP system."""
        passed_count = sum(1 for result in self.test_results.values() if result.get('status') == 'PASSED')
        total_count = len(self.test_results)
        
        if passed_count == total_count:
            return "✅ ALL TESTS PASSED - MCP system is fully functional"
        elif passed_count >= total_count * 0.75:
            return "✅ MOSTLY PASSED - MCP system is largely functional with minor issues"
        elif passed_count >= total_count * 0.5:
            return "⚠️ PARTIALLY PASSED - MCP system has some functionality but needs improvements"
        else:
            return "❌ MOSTLY FAILED - MCP system needs significant work"


def main():
    """Run MCP system integration test."""
    tester = MCPSystemTest()
    
    async def run_tests():
        try:
            report = await tester.run_all_tests()
            
            # Print final results
            print("\n" + "=" * 50)
            print("🔧 MCP SYSTEM TEST RESULTS")
            print("=" * 50)
            
            if 'error' in report:
                print(f"❌ Test execution failed: {report['error']}")
                return
            
            summary = report['test_summary']
            print(f"Total Tests: {summary['total_tests']}")
            print(f"Passed: {summary['passed_tests']}")
            print(f"Failed: {summary['failed_tests']}")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
            
            print(f"\n{report['overall_assessment']}")
            
            # Print detailed results
            for test_name, result in report['test_results'].items():
                status = result.get('status', 'UNKNOWN')
                print(f"\n{test_name.upper().replace('_', ' ')}: {status}")
                
                if status == 'PASSED' and 'summary' in result:
                    print(f"  Summary: {result['summary']}")
                elif status == 'FAILED':
                    print(f"  Error: {result.get('error', 'Unknown error')}")
            
            return report
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return {'error': str(e)}
    
    return asyncio.run(run_tests())


if __name__ == "__main__":
    main()
