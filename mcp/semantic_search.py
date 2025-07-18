#!/usr/bin/env python3
"""
Semantic Search Engine
Provides semantic search capabilities using embeddings and similarity matching.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import json
import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re

from .knowledge_base import KnowledgeBase, KnowledgeEntry
from .server import MCPResource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a search result with relevance scoring."""
    entry: KnowledgeEntry
    relevance_score: float
    match_type: str  # 'semantic', 'keyword', 'hybrid'
    match_details: Dict[str, Any]

class SemanticSearch:
    """
    Semantic Search Engine for knowledge base queries.
    Combines embedding-based semantic search with keyword matching.
    """
    
    def __init__(self, knowledge_base: KnowledgeBase, 
                 embedding_model: Optional[str] = None):
        self.knowledge_base = knowledge_base
        self.embedding_model = embedding_model or "sentence-transformers/all-MiniLM-L6-v2"
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.entry_ids = []
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        self.last_index_update = None
        
        # Search configuration
        self.semantic_weight = 0.7
        self.keyword_weight = 0.3
        self.min_relevance_threshold = 0.1
        
        logger.info(f"Initialized semantic search with model: {self.embedding_model}")
    
    async def initialize(self) -> None:
        """Initialize the search engine."""
        logger.info("Initializing semantic search engine...")
        
        # Build initial indexes
        await self.rebuild_indexes()
        
        logger.info("Semantic search engine initialized")
    
    async def search(self, query: str, 
                    search_type: str = "hybrid",
                    max_results: int = 10,
                    tags: Optional[List[str]] = None,
                    filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Perform semantic search on the knowledge base.
        
        Args:
            query: Search query text
            search_type: 'semantic', 'keyword', or 'hybrid'
            max_results: Maximum number of results to return
            tags: Filter by tags
            filters: Additional filters
        """
        start_time = time.time()
        
        try:
            # Get candidate entries
            candidates = await self._get_candidate_entries(tags, filters)
            
            if not candidates:
                logger.info("No candidate entries found")
                return []
            
            # Perform search based on type
            if search_type == "semantic":
                results = await self._semantic_search(query, candidates, max_results)
            elif search_type == "keyword":
                results = await self._keyword_search(query, candidates, max_results)
            else:  # hybrid
                results = await self._hybrid_search(query, candidates, max_results)
            
            # Filter by relevance threshold
            filtered_results = [r for r in results if r.relevance_score >= self.min_relevance_threshold]
            
            search_time = time.time() - start_time
            logger.info(f"Search completed in {search_time:.2f}s: {len(filtered_results)} results")
            
            return filtered_results[:max_results]
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def find_similar_entries(self, entry_id: str, 
                                 max_results: int = 5) -> List[SearchResult]:
        """Find entries similar to a given entry."""
        try:
            # Get the reference entry
            reference_entry = await self.knowledge_base.get_entry(entry_id)
            if not reference_entry:
                logger.error(f"Reference entry {entry_id} not found")
                return []
            
            # Use the entry's content as query
            query = reference_entry.content
            
            # Get all entries except the reference
            all_entries = await self.knowledge_base.search_entries("", limit=1000)
            candidates = [e for e in all_entries if e.id != entry_id]
            
            # Perform semantic search
            results = await self._semantic_search(query, candidates, max_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar entries: {e}")
            return []
    
    async def get_recommendations(self, context: Dict[str, Any], 
                                max_results: int = 5) -> List[SearchResult]:
        """Get recommendations based on context."""
        try:
            # Extract query from context
            query_parts = []
            
            if "project_type" in context:
                query_parts.append(context["project_type"])
            
            if "technologies" in context:
                query_parts.extend(context["technologies"])
            
            if "domain" in context:
                query_parts.append(context["domain"])
            
            if "keywords" in context:
                query_parts.extend(context["keywords"])
            
            query = " ".join(query_parts)
            
            if not query:
                # Return popular entries if no context
                popular_entries = await self.knowledge_base.get_popular_entries(max_results)
                return [
                    SearchResult(
                        entry=entry,
                        relevance_score=0.5,
                        match_type="popular",
                        match_details={"reason": "popular_content"}
                    )
                    for entry in popular_entries
                ]
            
            # Perform hybrid search
            return await self.search(query, "hybrid", max_results)
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
    
    async def rebuild_indexes(self) -> None:
        """Rebuild search indexes."""
        logger.info("Rebuilding search indexes...")
        
        try:
            # Get all entries
            all_entries = await self.knowledge_base.search_entries("", limit=10000)
            
            if not all_entries:
                logger.info("No entries found, skipping index rebuild")
                return
            
            # Build TF-IDF index
            documents = [entry.content for entry in all_entries]
            self.entry_ids = [entry.id for entry in all_entries]
            
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            
            # Cache embeddings if available
            for entry in all_entries:
                if entry.embedding:
                    self.embeddings_cache[entry.id] = np.array(entry.embedding)
            
            self.last_index_update = time.time()
            
            logger.info(f"Rebuilt indexes for {len(all_entries)} entries")
            
        except Exception as e:
            logger.error(f"Failed to rebuild indexes: {e}")
    
    async def update_entry_embedding(self, entry_id: str, 
                                   embedding: List[float]) -> None:
        """Update embedding for a specific entry."""
        self.embeddings_cache[entry_id] = np.array(embedding)
        logger.info(f"Updated embedding for entry {entry_id}")
    
    # Private methods
    
    async def _get_candidate_entries(self, tags: Optional[List[str]] = None,
                                   filters: Optional[Dict[str, Any]] = None) -> List[KnowledgeEntry]:
        """Get candidate entries for search."""
        # Apply basic filtering
        if tags:
            candidates = []
            for tag in tags:
                tag_entries = await self.knowledge_base.get_entries_by_tag(tag, limit=1000)
                candidates.extend(tag_entries)
            
            # Remove duplicates
            seen_ids = set()
            unique_candidates = []
            for entry in candidates:
                if entry.id not in seen_ids:
                    seen_ids.add(entry.id)
                    unique_candidates.append(entry)
            
            return unique_candidates
        else:
            # Get all entries
            return await self.knowledge_base.search_entries("", limit=1000)
    
    async def _semantic_search(self, query: str, 
                             candidates: List[KnowledgeEntry],
                             max_results: int) -> List[SearchResult]:
        """Perform semantic search using embeddings."""
        results = []
        
        try:
            # Get query embedding (placeholder - would use actual embedding model)
            query_embedding = self._get_query_embedding(query)
            
            if query_embedding is None:
                logger.warning("Could not generate query embedding, falling back to keyword search")
                return await self._keyword_search(query, candidates, max_results)
            
            # Calculate similarities
            for entry in candidates:
                if entry.id in self.embeddings_cache:
                    entry_embedding = self.embeddings_cache[entry.id]
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        entry_embedding.reshape(1, -1)
                    )[0][0]
                    
                    if similarity > 0:
                        result = SearchResult(
                            entry=entry,
                            relevance_score=float(similarity),
                            match_type="semantic",
                            match_details={
                                "similarity": float(similarity),
                                "embedding_dim": len(entry_embedding)
                            }
                        )
                        results.append(result)
            
            # Sort by relevance
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def _keyword_search(self, query: str, 
                            candidates: List[KnowledgeEntry],
                            max_results: int) -> List[SearchResult]:
        """Perform keyword-based search using TF-IDF."""
        results = []
        
        try:
            if self.tfidf_matrix is None:
                await self.rebuild_indexes()
            
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Create results for candidates
            candidate_ids = {entry.id: entry for entry in candidates}
            
            for i, entry_id in enumerate(self.entry_ids):
                if entry_id in candidate_ids and similarities[i] > 0:
                    # Calculate additional keyword matches
                    entry = candidate_ids[entry_id]
                    keyword_matches = self._calculate_keyword_matches(query, entry.content)
                    
                    # Combine TF-IDF score with keyword matches
                    combined_score = similarities[i] * 0.7 + keyword_matches * 0.3
                    
                    result = SearchResult(
                        entry=entry,
                        relevance_score=float(combined_score),
                        match_type="keyword",
                        match_details={
                            "tfidf_score": float(similarities[i]),
                            "keyword_matches": keyword_matches,
                            "combined_score": float(combined_score)
                        }
                    )
                    results.append(result)
            
            # Sort by relevance
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    async def _hybrid_search(self, query: str, 
                           candidates: List[KnowledgeEntry],
                           max_results: int) -> List[SearchResult]:
        """Perform hybrid search combining semantic and keyword approaches."""
        try:
            # Get results from both approaches
            semantic_results = await self._semantic_search(query, candidates, max_results * 2)
            keyword_results = await self._keyword_search(query, candidates, max_results * 2)
            
            # Combine results
            combined_results = {}
            
            # Add semantic results
            for result in semantic_results:
                entry_id = result.entry.id
                combined_results[entry_id] = {
                    "entry": result.entry,
                    "semantic_score": result.relevance_score,
                    "keyword_score": 0.0,
                    "semantic_details": result.match_details
                }
            
            # Add keyword results
            for result in keyword_results:
                entry_id = result.entry.id
                if entry_id in combined_results:
                    combined_results[entry_id]["keyword_score"] = result.relevance_score
                    combined_results[entry_id]["keyword_details"] = result.match_details
                else:
                    combined_results[entry_id] = {
                        "entry": result.entry,
                        "semantic_score": 0.0,
                        "keyword_score": result.relevance_score,
                        "keyword_details": result.match_details
                    }
            
            # Calculate hybrid scores
            hybrid_results = []
            for entry_id, data in combined_results.items():
                hybrid_score = (
                    data["semantic_score"] * self.semantic_weight +
                    data["keyword_score"] * self.keyword_weight
                )
                
                match_details = {
                    "semantic_score": data["semantic_score"],
                    "keyword_score": data["keyword_score"],
                    "hybrid_score": hybrid_score,
                    "semantic_weight": self.semantic_weight,
                    "keyword_weight": self.keyword_weight
                }
                
                # Add details from individual searches
                if "semantic_details" in data:
                    match_details["semantic_details"] = data["semantic_details"]
                if "keyword_details" in data:
                    match_details["keyword_details"] = data["keyword_details"]
                
                result = SearchResult(
                    entry=data["entry"],
                    relevance_score=hybrid_score,
                    match_type="hybrid",
                    match_details=match_details
                )
                hybrid_results.append(result)
            
            # Sort by hybrid score
            hybrid_results.sort(key=lambda r: r.relevance_score, reverse=True)
            
            return hybrid_results[:max_results]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    def _get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Get embedding for query (placeholder implementation)."""
        # This would use an actual embedding model like sentence-transformers
        # For now, return a random embedding for demonstration
        try:
            # Placeholder: generate a simple embedding based on query
            # In practice, this would use a pre-trained model
            words = query.lower().split()
            if not words:
                return None
            
            # Simple word-based embedding (for demonstration)
            embedding = np.random.rand(384)  # Typical embedding dimension
            
            # Add some deterministic component based on query
            query_hash = hash(query) % 1000
            embedding[0] = query_hash / 1000.0
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return None
    
    def _calculate_keyword_matches(self, query: str, content: str) -> float:
        """Calculate keyword match score."""
        try:
            query_words = set(re.findall(r'\b\w+\b', query.lower()))
            content_words = set(re.findall(r'\b\w+\b', content.lower()))
            
            if not query_words:
                return 0.0
            
            # Calculate intersection
            matches = query_words.intersection(content_words)
            match_ratio = len(matches) / len(query_words)
            
            # Bonus for exact phrase matches
            if query.lower() in content.lower():
                match_ratio += 0.2
            
            return min(match_ratio, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate keyword matches: {e}")
            return 0.0


# Example usage
async def main():
    """Example usage of semantic search."""
    # Initialize knowledge base and search engine
    kb = KnowledgeBase()
    search_engine = SemanticSearch(kb)
    
    await search_engine.initialize()
    
    with kb:
        # Add some sample entries
        resources = [
            MCPResource(
                uri="https://example.com/react-hooks",
                name="React Hooks Guide",
                description="Complete guide to React hooks",
                mime_type="text/html",
                metadata={"category": "tutorial", "framework": "react"},
                last_modified=datetime.now()
            ),
            MCPResource(
                uri="https://example.com/python-async",
                name="Python Async Programming",
                description="Guide to asynchronous programming in Python",
                mime_type="text/html",
                metadata={"category": "tutorial", "language": "python"},
                last_modified=datetime.now()
            )
        ]
        
        contents = [
            "React hooks are functions that let you use state and other React features in functional components. The most common hooks are useState and useEffect.",
            "Asynchronous programming in Python allows you to write concurrent code using async/await syntax. This is useful for I/O-bound operations."
        ]
        
        for resource, content in zip(resources, contents):
            await kb.add_entry(
                resource=resource,
                content=content,
                tags=["tutorial", "programming"]
            )
        
        # Perform searches
        print("=== Semantic Search ===")
        results = await search_engine.search("React state management", "semantic")
        for result in results:
            print(f"- {result.entry.resource.name}: {result.relevance_score:.3f}")
        
        print("\n=== Keyword Search ===")
        results = await search_engine.search("async programming", "keyword")
        for result in results:
            print(f"- {result.entry.resource.name}: {result.relevance_score:.3f}")
        
        print("\n=== Hybrid Search ===")
        results = await search_engine.search("Python functions", "hybrid")
        for result in results:
            print(f"- {result.entry.resource.name}: {result.relevance_score:.3f}")

if __name__ == "__main__":
    import datetime
    asyncio.run(main())
