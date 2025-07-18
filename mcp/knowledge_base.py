#!/usr/bin/env python3
"""
Knowledge Base Management
Handles storage, indexing, and retrieval of knowledge resources.
"""

import asyncio
import json
import logging
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import numpy as np

from .server import MCPResource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KnowledgeEntry:
    """Represents a knowledge entry in the knowledge base."""
    id: str
    resource: MCPResource
    content: str
    embedding: Optional[List[float]] = None
    tags: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    access_count: int = 0
    relevance_score: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []

class KnowledgeBase:
    """
    Knowledge Base for storing and retrieving MCP resources.
    Provides persistent storage, indexing, and search capabilities.
    """
    
    def __init__(self, db_path: str = "knowledge_base.db", 
                 embedding_dim: int = 768):
        self.db_path = db_path
        self.embedding_dim = embedding_dim
        self.connection: Optional[sqlite3.Connection] = None
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        self.max_cache_size = 10000
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"Initialized knowledge base at {db_path}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def connect(self) -> None:
        """Connect to the database."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info("Connected to knowledge base")
    
    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from knowledge base")
    
    def _initialize_database(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            # Create tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id TEXT PRIMARY KEY,
                    resource_uri TEXT NOT NULL,
                    resource_name TEXT NOT NULL,
                    resource_description TEXT,
                    resource_metadata TEXT,
                    content TEXT NOT NULL,
                    embedding BLOB,
                    tags TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    relevance_score REAL DEFAULT 0.0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_tags (
                    entry_id TEXT,
                    tag TEXT,
                    FOREIGN KEY (entry_id) REFERENCES knowledge_entries (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_relationships (
                    source_id TEXT,
                    target_id TEXT,
                    relationship_type TEXT,
                    strength REAL DEFAULT 1.0,
                    FOREIGN KEY (source_id) REFERENCES knowledge_entries (id),
                    FOREIGN KEY (target_id) REFERENCES knowledge_entries (id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_resource_uri ON knowledge_entries(resource_uri)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags ON knowledge_tags(tag)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON knowledge_entries(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_count ON knowledge_entries(access_count)")
            
            conn.commit()
            logger.info("Database schema initialized")
    
    async def add_entry(self, resource: MCPResource, content: str, 
                       tags: Optional[List[str]] = None,
                       embedding: Optional[List[float]] = None) -> str:
        """Add a knowledge entry to the database."""
        if not self.connection:
            self.connect()
        
        # Generate entry ID
        entry_id = self._generate_entry_id(resource.uri, content)
        
        # Check if entry already exists
        existing = await self.get_entry(entry_id)
        if existing:
            logger.info(f"Entry {entry_id} already exists, updating...")
            return await self.update_entry(entry_id, resource, content, tags, embedding)
        
        # Create knowledge entry
        entry = KnowledgeEntry(
            id=entry_id,
            resource=resource,
            content=content,
            embedding=embedding,
            tags=tags or []
        )
        
        try:
            # Insert into database
            self.connection.execute("""
                INSERT INTO knowledge_entries 
                (id, resource_uri, resource_name, resource_description, resource_metadata,
                 content, embedding, tags, created_at, updated_at, access_count, relevance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                resource.uri,
                resource.name,
                resource.description,
                json.dumps(resource.metadata),
                content,
                pickle.dumps(embedding) if embedding else None,
                json.dumps(tags or []),
                entry.created_at,
                entry.updated_at,
                entry.access_count,
                entry.relevance_score
            ))
            
            # Insert tags
            if tags:
                for tag in tags:
                    self.connection.execute("""
                        INSERT INTO knowledge_tags (entry_id, tag) VALUES (?, ?)
                    """, (entry_id, tag))
            
            self.connection.commit()
            
            # Cache embedding
            if embedding:
                self.embeddings_cache[entry_id] = np.array(embedding)
            
            logger.info(f"Added knowledge entry: {entry_id}")
            return entry_id
            
        except Exception as e:
            logger.error(f"Failed to add knowledge entry: {e}")
            self.connection.rollback()
            raise
    
    async def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.execute("""
                SELECT * FROM knowledge_entries WHERE id = ?
            """, (entry_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Reconstruct resource
            resource = MCPResource(
                uri=row["resource_uri"],
                name=row["resource_name"],
                description=row["resource_description"],
                mime_type="text/plain",  # Default
                metadata=json.loads(row["resource_metadata"]) if row["resource_metadata"] else {},
                last_modified=datetime.fromisoformat(row["updated_at"])
            )
            
            # Reconstruct entry
            entry = KnowledgeEntry(
                id=row["id"],
                resource=resource,
                content=row["content"],
                embedding=pickle.loads(row["embedding"]) if row["embedding"] else None,
                tags=json.loads(row["tags"]) if row["tags"] else [],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                access_count=row["access_count"],
                relevance_score=row["relevance_score"]
            )
            
            # Update access count
            await self._update_access_count(entry_id)
            
            return entry
            
        except Exception as e:
            logger.error(f"Failed to get knowledge entry {entry_id}: {e}")
            return None
    
    async def update_entry(self, entry_id: str, resource: MCPResource, 
                          content: str, tags: Optional[List[str]] = None,
                          embedding: Optional[List[float]] = None) -> str:
        """Update an existing knowledge entry."""
        if not self.connection:
            self.connect()
        
        try:
            # Update main entry
            self.connection.execute("""
                UPDATE knowledge_entries 
                SET resource_name = ?, resource_description = ?, resource_metadata = ?,
                    content = ?, embedding = ?, tags = ?, updated_at = ?
                WHERE id = ?
            """, (
                resource.name,
                resource.description,
                json.dumps(resource.metadata),
                content,
                pickle.dumps(embedding) if embedding else None,
                json.dumps(tags or []),
                datetime.now(),
                entry_id
            ))
            
            # Update tags
            self.connection.execute("DELETE FROM knowledge_tags WHERE entry_id = ?", (entry_id,))
            if tags:
                for tag in tags:
                    self.connection.execute("""
                        INSERT INTO knowledge_tags (entry_id, tag) VALUES (?, ?)
                    """, (entry_id, tag))
            
            self.connection.commit()
            
            # Update embedding cache
            if embedding:
                self.embeddings_cache[entry_id] = np.array(embedding)
            elif entry_id in self.embeddings_cache:
                del self.embeddings_cache[entry_id]
            
            logger.info(f"Updated knowledge entry: {entry_id}")
            return entry_id
            
        except Exception as e:
            logger.error(f"Failed to update knowledge entry {entry_id}: {e}")
            self.connection.rollback()
            raise
    
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a knowledge entry."""
        if not self.connection:
            self.connect()
        
        try:
            # Delete from all tables
            self.connection.execute("DELETE FROM knowledge_relationships WHERE source_id = ? OR target_id = ?", 
                                  (entry_id, entry_id))
            self.connection.execute("DELETE FROM knowledge_tags WHERE entry_id = ?", (entry_id,))
            self.connection.execute("DELETE FROM knowledge_entries WHERE id = ?", (entry_id,))
            
            self.connection.commit()
            
            # Remove from cache
            if entry_id in self.embeddings_cache:
                del self.embeddings_cache[entry_id]
            
            logger.info(f"Deleted knowledge entry: {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete knowledge entry {entry_id}: {e}")
            self.connection.rollback()
            return False
    
    async def search_entries(self, query: str, tags: Optional[List[str]] = None,
                           limit: int = 10, offset: int = 0) -> List[KnowledgeEntry]:
        """Search knowledge entries by text and tags."""
        if not self.connection:
            self.connect()
        
        try:
            # Build query
            sql = """
                SELECT DISTINCT ke.* FROM knowledge_entries ke
            """
            params = []
            conditions = []
            
            # Add tag filtering
            if tags:
                sql += " JOIN knowledge_tags kt ON ke.id = kt.entry_id"
                tag_conditions = " OR ".join(["kt.tag = ?"] * len(tags))
                conditions.append(f"({tag_conditions})")
                params.extend(tags)
            
            # Add text search
            if query:
                conditions.append("(ke.content LIKE ? OR ke.resource_name LIKE ? OR ke.resource_description LIKE ?)")
                query_param = f"%{query}%"
                params.extend([query_param, query_param, query_param])
            
            # Add WHERE clause
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            # Add ordering and pagination
            sql += " ORDER BY ke.relevance_score DESC, ke.access_count DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = self.connection.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert to KnowledgeEntry objects
            entries = []
            for row in rows:
                resource = MCPResource(
                    uri=row["resource_uri"],
                    name=row["resource_name"],
                    description=row["resource_description"],
                    mime_type="text/plain",
                    metadata=json.loads(row["resource_metadata"]) if row["resource_metadata"] else {},
                    last_modified=datetime.fromisoformat(row["updated_at"])
                )
                
                entry = KnowledgeEntry(
                    id=row["id"],
                    resource=resource,
                    content=row["content"],
                    embedding=pickle.loads(row["embedding"]) if row["embedding"] else None,
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    access_count=row["access_count"],
                    relevance_score=row["relevance_score"]
                )
                
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to search knowledge entries: {e}")
            return []
    
    async def get_entries_by_tag(self, tag: str, limit: int = 10) -> List[KnowledgeEntry]:
        """Get entries by tag."""
        return await self.search_entries(query="", tags=[tag], limit=limit)
    
    async def get_recent_entries(self, limit: int = 10) -> List[KnowledgeEntry]:
        """Get recently added entries."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.execute("""
                SELECT * FROM knowledge_entries 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            entries = []
            
            for row in rows:
                resource = MCPResource(
                    uri=row["resource_uri"],
                    name=row["resource_name"],
                    description=row["resource_description"],
                    mime_type="text/plain",
                    metadata=json.loads(row["resource_metadata"]) if row["resource_metadata"] else {},
                    last_modified=datetime.fromisoformat(row["updated_at"])
                )
                
                entry = KnowledgeEntry(
                    id=row["id"],
                    resource=resource,
                    content=row["content"],
                    embedding=pickle.loads(row["embedding"]) if row["embedding"] else None,
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    access_count=row["access_count"],
                    relevance_score=row["relevance_score"]
                )
                
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get recent entries: {e}")
            return []
    
    async def get_popular_entries(self, limit: int = 10) -> List[KnowledgeEntry]:
        """Get most accessed entries."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.execute("""
                SELECT * FROM knowledge_entries 
                ORDER BY access_count DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            entries = []
            
            for row in rows:
                resource = MCPResource(
                    uri=row["resource_uri"],
                    name=row["resource_name"],
                    description=row["resource_description"],
                    mime_type="text/plain",
                    metadata=json.loads(row["resource_metadata"]) if row["resource_metadata"] else {},
                    last_modified=datetime.fromisoformat(row["updated_at"])
                )
                
                entry = KnowledgeEntry(
                    id=row["id"],
                    resource=resource,
                    content=row["content"],
                    embedding=pickle.loads(row["embedding"]) if row["embedding"] else None,
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    access_count=row["access_count"],
                    relevance_score=row["relevance_score"]
                )
                
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get popular entries: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        if not self.connection:
            self.connect()
        
        try:
            # Get basic counts
            cursor = self.connection.execute("SELECT COUNT(*) as total FROM knowledge_entries")
            total_entries = cursor.fetchone()["total"]
            
            cursor = self.connection.execute("SELECT COUNT(DISTINCT tag) as total FROM knowledge_tags")
            total_tags = cursor.fetchone()["total"]
            
            # Get recent activity
            week_ago = datetime.now() - timedelta(days=7)
            cursor = self.connection.execute("""
                SELECT COUNT(*) as recent FROM knowledge_entries 
                WHERE created_at > ?
            """, (week_ago,))
            recent_entries = cursor.fetchone()["recent"]
            
            # Get top tags
            cursor = self.connection.execute("""
                SELECT tag, COUNT(*) as count FROM knowledge_tags 
                GROUP BY tag ORDER BY count DESC LIMIT 10
            """)
            top_tags = [{"tag": row["tag"], "count": row["count"]} for row in cursor.fetchall()]
            
            return {
                "total_entries": total_entries,
                "total_tags": total_tags,
                "recent_entries": recent_entries,
                "top_tags": top_tags,
                "cache_size": len(self.embeddings_cache)
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    # Private helper methods
    
    def _generate_entry_id(self, uri: str, content: str) -> str:
        """Generate a unique entry ID."""
        content_hash = hashlib.md5(f"{uri}:{content}".encode()).hexdigest()
        return f"kb_{content_hash}"
    
    async def _update_access_count(self, entry_id: str) -> None:
        """Update access count for an entry."""
        if not self.connection:
            return
        
        try:
            self.connection.execute("""
                UPDATE knowledge_entries 
                SET access_count = access_count + 1 
                WHERE id = ?
            """, (entry_id,))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to update access count for {entry_id}: {e}")
    
    def cleanup_old_entries(self, days: int = 30) -> int:
        """Clean up old entries that haven't been accessed recently."""
        if not self.connection:
            self.connect()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get entries to delete
            cursor = self.connection.execute("""
                SELECT id FROM knowledge_entries 
                WHERE updated_at < ? AND access_count = 0
            """, (cutoff_date,))
            
            entry_ids = [row["id"] for row in cursor.fetchall()]
            
            # Delete entries
            for entry_id in entry_ids:
                self.connection.execute("DELETE FROM knowledge_relationships WHERE source_id = ? OR target_id = ?", 
                                      (entry_id, entry_id))
                self.connection.execute("DELETE FROM knowledge_tags WHERE entry_id = ?", (entry_id,))
                self.connection.execute("DELETE FROM knowledge_entries WHERE id = ?", (entry_id,))
                
                # Remove from cache
                if entry_id in self.embeddings_cache:
                    del self.embeddings_cache[entry_id]
            
            self.connection.commit()
            
            logger.info(f"Cleaned up {len(entry_ids)} old entries")
            return len(entry_ids)
            
        except Exception as e:
            logger.error(f"Failed to cleanup old entries: {e}")
            self.connection.rollback()
            return 0


# Example usage
async def main():
    """Example usage of knowledge base."""
    kb = KnowledgeBase()
    
    with kb:
        # Create a sample resource
        resource = MCPResource(
            uri="https://example.com/doc1",
            name="Sample Documentation",
            description="A sample documentation resource",
            mime_type="text/html",
            metadata={"category": "tutorial", "difficulty": "beginner"},
            last_modified=datetime.now()
        )
        
        # Add entry
        entry_id = await kb.add_entry(
            resource=resource,
            content="This is sample documentation content about getting started.",
            tags=["tutorial", "getting-started", "beginner"]
        )
        
        print(f"Added entry: {entry_id}")
        
        # Search entries
        results = await kb.search_entries("getting started")
        print(f"Search results: {len(results)} entries found")
        
        # Get statistics
        stats = await kb.get_statistics()
        print(f"Knowledge base statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
