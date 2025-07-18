#!/usr/bin/env python3
"""
React Documentation MCP Server
Specialized server for React documentation and resources.
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup

from ..server import DocumentationMCPServer, MCPResource, MCPQuery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReactDocumentationServer(DocumentationMCPServer):
    """
    Specialized MCP server for React documentation.
    Provides access to React docs, API references, and examples.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            server_id="react-docs",
            name="React Documentation",
            documentation_url="https://react.dev",
            api_key=api_key
        )
        
        # React-specific capabilities
        self.capabilities.update({
            "react_hooks": True,
            "component_examples": True,
            "api_reference": True,
            "migration_guides": True,
            "best_practices": True
        })
        
        # React documentation structure
        self.doc_sections = {
            "learn": {
                "url": "https://react.dev/learn",
                "description": "Learn React fundamentals",
                "subsections": [
                    "installation", "your-first-component", "importing-and-exporting-components",
                    "writing-markup-with-jsx", "javascript-in-jsx-with-curly-braces",
                    "passing-props-to-a-component", "conditional-rendering", "rendering-lists",
                    "keeping-components-pure", "your-ui-as-a-tree"
                ]
            },
            "reference": {
                "url": "https://react.dev/reference",
                "description": "React API reference",
                "subsections": [
                    "react", "react-dom", "react-dom-client", "react-dom-server",
                    "legacy-react-apis", "built-in-react-components", "built-in-react-hooks"
                ]
            },
            "community": {
                "url": "https://react.dev/community",
                "description": "React community resources",
                "subsections": [
                    "meetups", "conferences", "react-developers", "acknowledgements"
                ]
            }
        }
        
        # Common React patterns and solutions
        self.react_patterns = {
            "hooks": {
                "useState": "Managing component state",
                "useEffect": "Side effects and lifecycle",
                "useContext": "Consuming context",
                "useReducer": "Complex state management",
                "useMemo": "Performance optimization",
                "useCallback": "Callback optimization",
                "useRef": "DOM references and mutable values",
                "useImperativeHandle": "Customizing exposed refs",
                "useLayoutEffect": "Synchronous effects",
                "useDebugValue": "Custom hook debugging"
            },
            "patterns": {
                "component-composition": "Building reusable components",
                "render-props": "Sharing code between components",
                "higher-order-components": "Component enhancement",
                "context-api": "Global state management",
                "error-boundaries": "Error handling",
                "code-splitting": "Performance optimization",
                "lazy-loading": "Dynamic imports",
                "memoization": "Preventing unnecessary re-renders"
            }
        }
    
    async def _initialize_resources(self) -> None:
        """Initialize React documentation resources."""
        logger.info("Initializing React documentation resources...")
        
        # Create resources for main documentation sections
        for section_key, section_data in self.doc_sections.items():
            await self._create_section_resources(section_key, section_data)
        
        # Create resources for React patterns and hooks
        await self._create_pattern_resources()
        
        # Create resources for common React problems and solutions
        await self._create_solution_resources()
        
        logger.info(f"Initialized {len(self.resources)} React documentation resources")
    
    async def _create_section_resources(self, section_key: str, section_data: Dict[str, Any]) -> None:
        """Create resources for a documentation section."""
        # Main section resource
        main_resource = MCPResource(
            uri=section_data["url"],
            name=f"React {section_key.title()}",
            description=section_data["description"],
            mime_type="text/html",
            metadata={
                "section": section_key,
                "type": "documentation",
                "framework": "react",
                "official": True,
                "subsections": section_data.get("subsections", [])
            },
            last_modified=datetime.now()
        )
        self.resources[main_resource.uri] = main_resource
        
        # Subsection resources
        for subsection in section_data.get("subsections", []):
            subsection_uri = f"{section_data['url']}/{subsection}"
            subsection_resource = MCPResource(
                uri=subsection_uri,
                name=f"React {subsection.replace('-', ' ').title()}",
                description=f"React documentation: {subsection.replace('-', ' ')}",
                mime_type="text/html",
                metadata={
                    "section": section_key,
                    "subsection": subsection,
                    "type": "documentation",
                    "framework": "react",
                    "official": True,
                    "parent": section_data["url"]
                },
                last_modified=datetime.now()
            )
            self.resources[subsection_resource.uri] = subsection_resource
    
    async def _create_pattern_resources(self) -> None:
        """Create resources for React patterns and hooks."""
        # Hook resources
        for hook_name, hook_description in self.react_patterns["hooks"].items():
            hook_uri = f"https://react.dev/reference/react/{hook_name}"
            hook_resource = MCPResource(
                uri=hook_uri,
                name=f"React {hook_name}",
                description=hook_description,
                mime_type="text/html",
                metadata={
                    "type": "hook",
                    "hook_name": hook_name,
                    "framework": "react",
                    "category": "hooks",
                    "official": True,
                    "examples": True
                },
                last_modified=datetime.now()
            )
            self.resources[hook_resource.uri] = hook_resource
        
        # Pattern resources
        for pattern_name, pattern_description in self.react_patterns["patterns"].items():
            pattern_uri = f"https://react.dev/learn/{pattern_name}"
            pattern_resource = MCPResource(
                uri=pattern_uri,
                name=f"React {pattern_name.replace('-', ' ').title()}",
                description=pattern_description,
                mime_type="text/html",
                metadata={
                    "type": "pattern",
                    "pattern_name": pattern_name,
                    "framework": "react",
                    "category": "patterns",
                    "official": True,
                    "examples": True
                },
                last_modified=datetime.now()
            )
            self.resources[pattern_resource.uri] = pattern_resource
    
    async def _create_solution_resources(self) -> None:
        """Create resources for common React problems and solutions."""
        common_solutions = [
            {
                "problem": "state-management",
                "title": "State Management in React",
                "description": "Solutions for managing state in React applications",
                "solutions": ["useState", "useReducer", "Context API", "Redux", "Zustand"]
            },
            {
                "problem": "performance-optimization",
                "title": "React Performance Optimization",
                "description": "Techniques for optimizing React application performance",
                "solutions": ["React.memo", "useMemo", "useCallback", "Code splitting", "Lazy loading"]
            },
            {
                "problem": "form-handling",
                "title": "Form Handling in React",
                "description": "Best practices for handling forms in React",
                "solutions": ["Controlled components", "Uncontrolled components", "Form libraries", "Validation"]
            },
            {
                "problem": "data-fetching",
                "title": "Data Fetching in React",
                "description": "Patterns for fetching and managing data in React",
                "solutions": ["useEffect", "Custom hooks", "SWR", "React Query", "Suspense"]
            },
            {
                "problem": "testing",
                "title": "Testing React Components",
                "description": "Strategies for testing React applications",
                "solutions": ["Jest", "React Testing Library", "Enzyme", "Cypress", "Storybook"]
            }
        ]
        
        for solution in common_solutions:
            solution_uri = f"https://react.dev/learn/{solution['problem']}"
            solution_resource = MCPResource(
                uri=solution_uri,
                name=solution["title"],
                description=solution["description"],
                mime_type="text/html",
                metadata={
                    "type": "solution",
                    "problem": solution["problem"],
                    "framework": "react",
                    "category": "solutions",
                    "solutions": solution["solutions"],
                    "official": True
                },
                last_modified=datetime.now()
            )
            self.resources[solution_resource.uri] = solution_resource
    
    async def _process_query(self, query: MCPQuery) -> List[MCPResource]:
        """Process React-specific queries."""
        results = []
        query_lower = query.query_text.lower()
        
        # React-specific query processing
        react_keywords = {
            "hook": ["hooks", "useState", "useEffect", "useContext", "useReducer"],
            "component": ["component", "jsx", "props", "state"],
            "performance": ["performance", "optimization", "memo", "callback"],
            "state": ["state", "useState", "useReducer", "context"],
            "effect": ["effect", "useEffect", "lifecycle", "side effect"],
            "routing": ["routing", "router", "navigation", "route"],
            "form": ["form", "input", "validation", "controlled"],
            "testing": ["test", "testing", "jest", "enzyme", "cypress"],
            "styling": ["css", "styled", "emotion", "styling", "theme"]
        }
        
        # Identify query category
        query_categories = []
        for category, keywords in react_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                query_categories.append(category)
        
        # Score resources based on relevance
        for resource in self.resources.values():
            score = 0
            
            # Basic text matching
            if query_lower in resource.name.lower():
                score += 10
            if query_lower in resource.description.lower():
                score += 5
            
            # Category-specific scoring
            for category in query_categories:
                if category in resource.metadata.get("category", ""):
                    score += 8
                if category in resource.metadata.get("type", ""):
                    score += 6
            
            # React-specific metadata scoring
            if "hook" in query_lower and resource.metadata.get("type") == "hook":
                score += 15
            if "component" in query_lower and resource.metadata.get("type") == "pattern":
                score += 10
            if "performance" in query_lower and "performance" in resource.description.lower():
                score += 12
            
            # Hook-specific matching
            if resource.metadata.get("type") == "hook":
                hook_name = resource.metadata.get("hook_name", "")
                if hook_name.lower() in query_lower:
                    score += 20
            
            # Pattern-specific matching
            if resource.metadata.get("type") == "pattern":
                pattern_name = resource.metadata.get("pattern_name", "")
                if pattern_name.replace("-", " ") in query_lower:
                    score += 15
            
            # Solution-specific matching
            if resource.metadata.get("type") == "solution":
                problem = resource.metadata.get("problem", "")
                if problem.replace("-", " ") in query_lower:
                    score += 18
                
                # Check if query matches any solution
                solutions = resource.metadata.get("solutions", [])
                for solution in solutions:
                    if solution.lower() in query_lower:
                        score += 12
            
            # Context-based scoring
            if query.context:
                project_type = query.context.get("project_type", "")
                if project_type == "web_application" and "web" in resource.description.lower():
                    score += 5
                
                complexity = query.context.get("complexity", "")
                if complexity == "simple" and "beginner" in resource.description.lower():
                    score += 3
                elif complexity == "complex" and "advanced" in resource.description.lower():
                    score += 3
            
            if score > 0:
                resource.metadata["relevance_score"] = score
                results.append(resource)
        
        # Sort by relevance score
        results.sort(key=lambda r: r.metadata.get("relevance_score", 0), reverse=True)
        
        return results[:query.max_results]
    
    async def _get_resource_content(self, uri: str) -> Optional[MCPResource]:
        """Retrieve React documentation content."""
        resource = self.resources.get(uri)
        if not resource:
            return None
        
        # For demonstration, we'll return the resource with enhanced content
        # In a real implementation, this would fetch actual content from the URL
        try:
            enhanced_content = await self._fetch_enhanced_content(resource)
            if enhanced_content:
                resource.metadata["content"] = enhanced_content
            
            return resource
            
        except Exception as e:
            logger.error(f"Failed to get enhanced content for {uri}: {e}")
            return resource
    
    async def _fetch_enhanced_content(self, resource: MCPResource) -> Optional[str]:
        """Fetch enhanced content for a resource."""
        # This would typically fetch real content from the React documentation
        # For now, we'll return simulated content based on the resource type
        
        resource_type = resource.metadata.get("type", "")
        
        if resource_type == "hook":
            hook_name = resource.metadata.get("hook_name", "")
            return self._generate_hook_content(hook_name)
        elif resource_type == "pattern":
            pattern_name = resource.metadata.get("pattern_name", "")
            return self._generate_pattern_content(pattern_name)
        elif resource_type == "solution":
            problem = resource.metadata.get("problem", "")
            return self._generate_solution_content(problem)
        else:
            return self._generate_general_content(resource)
    
    def _generate_hook_content(self, hook_name: str) -> str:
        """Generate content for React hooks."""
        hook_examples = {
            "useState": """
# useState Hook

The useState hook lets you add state to functional components.

## Basic Usage
```javascript
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

## Best Practices
- Use multiple state variables for unrelated state
- Use functional updates when new state depends on previous state
- Consider useReducer for complex state logic
            """,
            "useEffect": """
# useEffect Hook

The useEffect hook lets you perform side effects in functional components.

## Basic Usage
```javascript
import React, { useState, useEffect } from 'react';

function Example() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    document.title = `You clicked ${count} times`;
  });
  
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

## Cleanup
```javascript
useEffect(() => {
  const subscription = subscribeToSomething();
  return () => {
    subscription.unsubscribe();
  };
}, []);
```
            """
        }
        
        return hook_examples.get(hook_name, f"Documentation for {hook_name} hook")
    
    def _generate_pattern_content(self, pattern_name: str) -> str:
        """Generate content for React patterns."""
        return f"""
# {pattern_name.replace('-', ' ').title()}

This is a comprehensive guide to the {pattern_name} pattern in React.

## Overview
The {pattern_name} pattern is commonly used in React applications to solve specific architectural challenges.

## Implementation
[Implementation details would be provided here]

## Examples
[Code examples would be provided here]

## Best Practices
[Best practices would be listed here]
        """
    
    def _generate_solution_content(self, problem: str) -> str:
        """Generate content for React solutions."""
        return f"""
# {problem.replace('-', ' ').title()} Solutions

This guide covers various approaches to handling {problem.replace('-', ' ')} in React applications.

## Common Approaches
[Different approaches would be listed here]

## Recommended Solutions
[Recommended solutions would be provided here]

## Examples
[Code examples would be provided here]
        """
    
    def _generate_general_content(self, resource: MCPResource) -> str:
        """Generate general content for resources."""
        return f"""
# {resource.name}

{resource.description}

## Overview
This section covers important concepts related to {resource.name.lower()}.

## Key Points
[Key points would be listed here]

## Examples
[Examples would be provided here]
        """


# Example usage
async def main():
    """Example usage of React documentation server."""
    server = ReactDocumentationServer()
    
    try:
        # Start the server
        await server.start()
        
        # Perform health check
        health = await server.health_check()
        print(f"Server health: {health}")
        
        # Test queries
        queries = [
            "useState hook examples",
            "React component performance optimization",
            "form handling in React",
            "useEffect cleanup",
            "React testing best practices"
        ]
        
        for query_text in queries:
            query = MCPQuery(
                query_id=f"test_{hash(query_text)}",
                query_text=query_text,
                context={"project_type": "web_application"},
                filters={}
            )
            
            response = await server.query(query)
            print(f"\nQuery: {query_text}")
            print(f"Results: {len(response.resources)} resources found")
            
            for resource in response.resources[:3]:  # Show top 3
                score = resource.metadata.get("relevance_score", 0)
                print(f"  - {resource.name} (score: {score})")
    
    finally:
        # Stop the server
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
