#!/usr/bin/env python3
"""
Stack Overflow MCP Server
Integrates with Stack Overflow API to provide community-driven solutions.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from urllib.parse import quote_plus
import html

from ..server import MCPServer, MCPResource, MCPQuery, MCPResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StackOverflowServer(MCPServer):
    """
    MCP server for Stack Overflow integration.
    Provides access to questions, answers, and community solutions.
    """
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 100):
        super().__init__(
            server_id="stackoverflow",
            name="Stack Overflow",
            description="Community-driven programming solutions from Stack Overflow"
        )
        
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.api_base_url = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"
        
        # Rate limiting
        self.request_count = 0
        self.rate_limit_reset = time.time() + 86400  # 24 hours
        
        # Stack Overflow specific capabilities
        self.capabilities.update({
            "question_search": True,
            "answer_retrieval": True,
            "tag_filtering": True,
            "user_reputation": True,
            "vote_scoring": True,
            "accepted_answers": True,
            "community_solutions": True
        })
        
        # Common programming tags for better filtering
        self.programming_tags = {
            "javascript", "python", "java", "c#", "php", "android", "html", "jquery",
            "css", "ios", "sql", "r", "node.js", "arrays", "c++", "json", "mysql",
            "react", "angular", "vue.js", "typescript", "django", "flask", "spring",
            "mongodb", "postgresql", "git", "docker", "kubernetes", "aws", "azure"
        }
        
        logger.info("Initialized Stack Overflow MCP server")
    
    async def _initialize_resources(self) -> None:
        """Initialize Stack Overflow resources."""
        logger.info("Initializing Stack Overflow resources...")
        
        # Create resources for popular tags and topics
        await self._create_tag_resources()
        
        # Create resources for common programming problems
        await self._create_problem_resources()
        
        logger.info(f"Initialized {len(self.resources)} Stack Overflow resources")
    
    async def _create_tag_resources(self) -> None:
        """Create resources for popular programming tags."""
        for tag in list(self.programming_tags)[:20]:  # Limit to top 20 tags
            tag_uri = f"https://stackoverflow.com/questions/tagged/{tag}"
            tag_resource = MCPResource(
                uri=tag_uri,
                name=f"Stack Overflow: {tag}",
                description=f"Questions and answers about {tag}",
                mime_type="application/json",
                metadata={
                    "type": "tag",
                    "tag": tag,
                    "source": "stackoverflow",
                    "community": True
                },
                last_modified=datetime.now()
            )
            self.resources[tag_resource.uri] = tag_resource
    
    async def _create_problem_resources(self) -> None:
        """Create resources for common programming problems."""
        common_problems = [
            {
                "problem": "authentication",
                "description": "User authentication and authorization solutions",
                "tags": ["authentication", "oauth", "jwt", "security"]
            },
            {
                "problem": "database-queries",
                "description": "Database query optimization and solutions",
                "tags": ["sql", "database", "mysql", "postgresql", "mongodb"]
            },
            {
                "problem": "api-integration",
                "description": "REST API integration and best practices",
                "tags": ["api", "rest", "http", "json", "web-services"]
            },
            {
                "problem": "error-handling",
                "description": "Error handling and debugging techniques",
                "tags": ["error-handling", "debugging", "exceptions", "logging"]
            },
            {
                "problem": "performance-optimization",
                "description": "Performance optimization strategies",
                "tags": ["performance", "optimization", "caching", "memory"]
            }
        ]
        
        for problem in common_problems:
            problem_uri = f"https://stackoverflow.com/search?q={quote_plus(problem['problem'])}"
            problem_resource = MCPResource(
                uri=problem_uri,
                name=f"Stack Overflow: {problem['problem'].replace('-', ' ').title()}",
                description=problem["description"],
                mime_type="application/json",
                metadata={
                    "type": "problem",
                    "problem": problem["problem"],
                    "tags": problem["tags"],
                    "source": "stackoverflow",
                    "community": True
                },
                last_modified=datetime.now()
            )
            self.resources[problem_resource.uri] = problem_resource
    
    async def _process_query(self, query: MCPQuery) -> List[MCPResource]:
        """Process Stack Overflow search queries."""
        try:
            # Check rate limit
            if not self._check_rate_limit():
                logger.warning("Rate limit exceeded for Stack Overflow API")
                return []
            
            # Search Stack Overflow
            search_results = await self._search_stackoverflow(query)
            
            # Convert to MCPResource objects
            resources = []
            for result in search_results:
                resource = self._create_resource_from_question(result)
                if resource:
                    resources.append(resource)
            
            return resources[:query.max_results]
            
        except Exception as e:
            logger.error(f"Failed to process Stack Overflow query: {e}")
            return []
    
    async def _search_stackoverflow(self, query: MCPQuery) -> List[Dict[str, Any]]:
        """Search Stack Overflow using the API."""
        try:
            # Prepare search parameters
            params = {
                "order": "desc",
                "sort": "relevance",
                "site": self.site,
                "q": query.query_text,
                "pagesize": min(query.max_results, 50),  # API limit
                "filter": "withbody"  # Include question body
            }
            
            # Add API key if available
            if self.api_key:
                params["key"] = self.api_key
            
            # Add tag filtering from context
            if query.context:
                technologies = query.context.get("technologies", [])
                if technologies:
                    # Filter to known programming tags
                    valid_tags = [tech.lower() for tech in technologies if tech.lower() in self.programming_tags]
                    if valid_tags:
                        params["tagged"] = ";".join(valid_tags)
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/search"
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.request_count += 1
                        
                        # Check for API quota
                        if "quota_remaining" in data:
                            logger.info(f"Stack Overflow API quota remaining: {data['quota_remaining']}")
                        
                        return data.get("items", [])
                    else:
                        logger.error(f"Stack Overflow API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Stack Overflow search failed: {e}")
            return []
    
    async def _get_question_answers(self, question_id: int) -> List[Dict[str, Any]]:
        """Get answers for a specific question."""
        try:
            params = {
                "order": "desc",
                "sort": "votes",
                "site": self.site,
                "filter": "withbody"
            }
            
            if self.api_key:
                params["key"] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/questions/{question_id}/answers"
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.request_count += 1
                        return data.get("items", [])
                    else:
                        logger.error(f"Failed to get answers: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Failed to get question answers: {e}")
            return []
    
    def _create_resource_from_question(self, question: Dict[str, Any]) -> Optional[MCPResource]:
        """Create an MCPResource from a Stack Overflow question."""
        try:
            question_id = question.get("question_id")
            title = html.unescape(question.get("title", ""))
            body = html.unescape(question.get("body", ""))
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(question)
            
            # Extract relevant metadata
            metadata = {
                "type": "question",
                "question_id": question_id,
                "source": "stackoverflow",
                "community": True,
                "score": question.get("score", 0),
                "view_count": question.get("view_count", 0),
                "answer_count": question.get("answer_count", 0),
                "is_answered": question.get("is_answered", False),
                "has_accepted_answer": question.get("accepted_answer_id") is not None,
                "tags": question.get("tags", []),
                "creation_date": question.get("creation_date"),
                "last_activity_date": question.get("last_activity_date"),
                "quality_score": quality_score,
                "relevance_score": quality_score  # Use quality as initial relevance
            }
            
            # Add owner information
            if "owner" in question:
                owner = question["owner"]
                metadata["owner"] = {
                    "user_id": owner.get("user_id"),
                    "display_name": owner.get("display_name"),
                    "reputation": owner.get("reputation", 0)
                }
            
            # Create resource
            resource = MCPResource(
                uri=f"https://stackoverflow.com/questions/{question_id}",
                name=title,
                description=self._extract_description(body),
                mime_type="text/html",
                metadata=metadata,
                last_modified=datetime.fromtimestamp(question.get("last_activity_date", time.time()))
            )
            
            return resource
            
        except Exception as e:
            logger.error(f"Failed to create resource from question: {e}")
            return None
    
    def _calculate_quality_score(self, question: Dict[str, Any]) -> float:
        """Calculate a quality score for a Stack Overflow question."""
        score = 0.0
        
        # Vote score (normalized)
        vote_score = question.get("score", 0)
        score += min(vote_score / 10.0, 5.0)  # Cap at 5 points
        
        # Answer count
        answer_count = question.get("answer_count", 0)
        score += min(answer_count / 5.0, 3.0)  # Cap at 3 points
        
        # Has accepted answer
        if question.get("accepted_answer_id"):
            score += 2.0
        
        # View count (logarithmic scale)
        view_count = question.get("view_count", 0)
        if view_count > 0:
            import math
            score += min(math.log10(view_count), 2.0)
        
        # Owner reputation
        if "owner" in question:
            reputation = question["owner"].get("reputation", 0)
            score += min(reputation / 10000.0, 1.0)  # Cap at 1 point
        
        # Recency bonus (questions from last year get bonus)
        creation_date = question.get("creation_date", 0)
        if creation_date > time.time() - 365 * 24 * 3600:  # Last year
            score += 0.5
        
        return min(score, 10.0)  # Cap total score at 10
    
    def _extract_description(self, body: str) -> str:
        """Extract a description from question body."""
        if not body:
            return "Stack Overflow question"
        
        # Remove HTML tags
        import re
        clean_body = re.sub(r'<[^>]+>', '', body)
        
        # Get first sentence or first 200 characters
        sentences = clean_body.split('.')
        if sentences and len(sentences[0]) > 10:
            return sentences[0].strip()[:200] + "..."
        else:
            return clean_body[:200].strip() + "..."
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        
        # Reset counter if 24 hours have passed
        if current_time > self.rate_limit_reset:
            self.request_count = 0
            self.rate_limit_reset = current_time + 86400
        
        return self.request_count < self.rate_limit
    
    async def _get_resource_content(self, uri: str) -> Optional[MCPResource]:
        """Get detailed content for a Stack Overflow resource."""
        # Extract question ID from URI
        import re
        match = re.search(r'/questions/(\d+)', uri)
        if not match:
            return self.resources.get(uri)
        
        question_id = int(match.group(1))
        
        try:
            # Get question details and answers
            answers = await self._get_question_answers(question_id)
            
            # Find the resource and enhance it with answers
            resource = self.resources.get(uri)
            if resource and answers:
                # Add answer information to metadata
                resource.metadata["answers"] = []
                
                for answer in answers[:5]:  # Top 5 answers
                    answer_info = {
                        "answer_id": answer.get("answer_id"),
                        "score": answer.get("score", 0),
                        "is_accepted": answer.get("is_accepted", False),
                        "body": html.unescape(answer.get("body", "")),
                        "creation_date": answer.get("creation_date")
                    }
                    
                    if "owner" in answer:
                        answer_info["owner"] = {
                            "display_name": answer["owner"].get("display_name"),
                            "reputation": answer["owner"].get("reputation", 0)
                        }
                    
                    resource.metadata["answers"].append(answer_info)
            
            return resource
            
        except Exception as e:
            logger.error(f"Failed to get enhanced content for {uri}: {e}")
            return self.resources.get(uri)
    
    async def _list_all_resources(self) -> List[MCPResource]:
        """List all Stack Overflow resources."""
        return list(self.resources.values())
    
    async def get_trending_questions(self, tags: Optional[List[str]] = None) -> List[MCPResource]:
        """Get trending questions from Stack Overflow."""
        try:
            params = {
                "order": "desc",
                "sort": "hot",
                "site": self.site,
                "pagesize": 20,
                "filter": "withbody"
            }
            
            if tags:
                valid_tags = [tag.lower() for tag in tags if tag.lower() in self.programming_tags]
                if valid_tags:
                    params["tagged"] = ";".join(valid_tags)
            
            if self.api_key:
                params["key"] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/questions"
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.request_count += 1
                        
                        resources = []
                        for question in data.get("items", []):
                            resource = self._create_resource_from_question(question)
                            if resource:
                                resources.append(resource)
                        
                        return resources
                    else:
                        logger.error(f"Failed to get trending questions: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Failed to get trending questions: {e}")
            return []


# Example usage
async def main():
    """Example usage of Stack Overflow server."""
    server = StackOverflowServer()
    
    try:
        # Start the server
        await server.start()
        
        # Test queries
        queries = [
            "React hooks useState",
            "Python async await",
            "JavaScript promises",
            "SQL join optimization",
            "Docker container networking"
        ]
        
        for query_text in queries:
            query = MCPQuery(
                query_id=f"test_{hash(query_text)}",
                query_text=query_text,
                context={"technologies": ["react", "python", "javascript"]},
                filters={},
                max_results=5
            )
            
            response = await server.query(query)
            print(f"\nQuery: {query_text}")
            print(f"Results: {len(response.resources)} resources found")
            
            for resource in response.resources:
                score = resource.metadata.get("quality_score", 0)
                votes = resource.metadata.get("score", 0)
                answers = resource.metadata.get("answer_count", 0)
                print(f"  - {resource.name[:60]}... (quality: {score:.1f}, votes: {votes}, answers: {answers})")
        
        # Test trending questions
        trending = await server.get_trending_questions(["python", "javascript"])
        print(f"\nTrending questions: {len(trending)} found")
        
    finally:
        # Stop the server
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
