"""
Enhanced Memory System for Windsurf Context Engineering Framework

This module implements semantic indexing, categorization, and intelligent retrieval
for project memories and context persistence.
"""

import json
import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import re
from collections import defaultdict, Counter
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Enhanced memory entry with semantic indexing and metadata"""
    id: str
    title: str
    content: str
    category: str
    subcategory: str
    tags: List[str]
    project_id: Optional[str]
    relevance_score: float
    success_score: float
    usage_count: int
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]
    semantic_keywords: List[str]
    context_hash: str

class EnhancedMemorySystem:
    """
    Enhanced memory system with semantic indexing, categorization, and intelligent retrieval
    """
    
    def __init__(self, db_path: str = "memory/enhanced_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Memory categories and their weights
        self.categories = {
            "project_patterns": 1.0,
            "code_solutions": 0.9,
            "architecture_decisions": 0.8,
            "tool_configurations": 0.7,
            "debugging_solutions": 0.9,
            "performance_optimizations": 0.8,
            "security_patterns": 0.9,
            "deployment_strategies": 0.7,
            "user_preferences": 0.6,
            "learning_notes": 0.5
        }
        
        # Semantic keyword extraction patterns
        self.keyword_patterns = {
            "technologies": r'\b(?:react|vue|angular|python|javascript|typescript|docker|kubernetes|aws|azure|gcp)\b',
            "frameworks": r'\b(?:django|flask|express|fastapi|spring|laravel|rails)\b',
            "databases": r'\b(?:postgresql|mysql|mongodb|redis|elasticsearch|sqlite)\b',
            "tools": r'\b(?:git|github|gitlab|jenkins|docker|terraform|ansible)\b',
            "concepts": r'\b(?:api|rest|graphql|microservices|serverless|devops|ci/cd)\b'
        }
        
        self._init_database()
        logger.info("Enhanced Memory System initialized")
    
    def _init_database(self):
        """Initialize the enhanced memory database with semantic indexing"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    tags TEXT,
                    project_id TEXT,
                    relevance_score REAL DEFAULT 0.0,
                    success_score REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    metadata TEXT,
                    semantic_keywords TEXT,
                    context_hash TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON memories(category)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relevance ON memories(relevance_score DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_project ON memories(project_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_hash ON memories(context_hash)
            """)
            
            # Create semantic search table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_index (
                    memory_id TEXT,
                    keyword TEXT,
                    keyword_type TEXT,
                    weight REAL,
                    FOREIGN KEY (memory_id) REFERENCES memories(id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_semantic_keyword ON semantic_index(keyword)
            """)
    
    def _extract_semantic_keywords(self, text: str) -> List[str]:
        """Extract semantic keywords from text using pattern matching"""
        keywords = []
        text_lower = text.lower()
        
        for keyword_type, pattern in self.keyword_patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.extend(matches)
        
        # Extract additional keywords using simple NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)
        word_freq = Counter(words)
        
        # Add high-frequency words as keywords
        for word, freq in word_freq.most_common(10):
            if freq > 1 and word not in keywords:
                keywords.append(word)
        
        return list(set(keywords))
    
    def _calculate_context_hash(self, content: str, tags: List[str], metadata: Dict[str, Any]) -> str:
        """Calculate a hash for the context to detect similar memories"""
        context_data = {
            "content_hash": hashlib.md5(content.encode()).hexdigest()[:16],
            "tags": sorted(tags),
            "metadata_keys": sorted(metadata.keys()) if metadata else []
        }
        context_str = json.dumps(context_data, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def add_memory(self, 
                   title: str, 
                   content: str, 
                   category: str,
                   subcategory: str = None,
                   tags: List[str] = None,
                   project_id: str = None,
                   metadata: Dict[str, Any] = None,
                   expires_in_days: int = None) -> str:
        """Add a new memory with semantic indexing"""
        
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}
        
        # Generate unique ID
        memory_id = hashlib.md5(f"{title}_{content}_{time.time()}".encode()).hexdigest()
        
        # Extract semantic keywords
        semantic_keywords = self._extract_semantic_keywords(f"{title} {content}")
        
        # Calculate context hash
        context_hash = self._calculate_context_hash(content, tags, metadata)
        
        # Calculate expiration date
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        # Create memory entry
        memory = MemoryEntry(
            id=memory_id,
            title=title,
            content=content,
            category=category,
            subcategory=subcategory or "",
            tags=tags,
            project_id=project_id,
            relevance_score=self.categories.get(category, 0.5),
            success_score=0.5,  # Default, will be updated based on usage
            usage_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expires_at=expires_at,
            metadata=metadata,
            semantic_keywords=semantic_keywords,
            context_hash=context_hash
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id, memory.title, memory.content, memory.category,
                memory.subcategory, json.dumps(memory.tags), memory.project_id,
                memory.relevance_score, memory.success_score, memory.usage_count,
                memory.created_at.isoformat(), memory.updated_at.isoformat(),
                memory.expires_at.isoformat() if memory.expires_at else None,
                json.dumps(memory.metadata), json.dumps(memory.semantic_keywords),
                memory.context_hash
            ))
            
            # Add semantic index entries
            for keyword in semantic_keywords:
                keyword_type = self._get_keyword_type(keyword)
                weight = self._calculate_keyword_weight(keyword, keyword_type)
                
                conn.execute("""
                    INSERT INTO semantic_index VALUES (?, ?, ?, ?)
                """, (memory_id, keyword, keyword_type, weight))
        
        logger.info(f"Added memory: {title} (ID: {memory_id})")
        return memory_id
    
    def _get_keyword_type(self, keyword: str) -> str:
        """Determine the type of a keyword"""
        for keyword_type, pattern in self.keyword_patterns.items():
            if re.search(pattern, keyword, re.IGNORECASE):
                return keyword_type
        return "general"
    
    def _calculate_keyword_weight(self, keyword: str, keyword_type: str) -> float:
        """Calculate the weight of a keyword based on its type and characteristics"""
        base_weights = {
            "technologies": 1.0,
            "frameworks": 0.9,
            "databases": 0.8,
            "tools": 0.7,
            "concepts": 0.6,
            "general": 0.5
        }
        
        base_weight = base_weights.get(keyword_type, 0.5)
        
        # Adjust weight based on keyword length and specificity
        if len(keyword) > 8:
            base_weight *= 1.1  # Longer keywords are often more specific
        
        return min(base_weight, 1.0)
    
    def search_memories(self, 
                       query: str, 
                       category: str = None,
                       project_id: str = None,
                       tags: List[str] = None,
                       limit: int = 10,
                       min_relevance: float = 0.1) -> List[MemoryEntry]:
        """Search memories using semantic and keyword matching"""
        
        # Extract keywords from query
        query_keywords = self._extract_semantic_keywords(query)
        
        with sqlite3.connect(self.db_path) as conn:
            # Build base query
            base_query = """
                SELECT DISTINCT m.*, 
                       COALESCE(AVG(si.weight), 0) as semantic_score
                FROM memories m
                LEFT JOIN semantic_index si ON m.id = si.memory_id
            """
            
            conditions = []
            params = []
            
            # Add semantic keyword matching
            if query_keywords:
                keyword_placeholders = ",".join(["?" for _ in query_keywords])
                conditions.append(f"si.keyword IN ({keyword_placeholders})")
                params.extend(query_keywords)
            
            # Add filters
            if category:
                conditions.append("m.category = ?")
                params.append(category)
            
            if project_id:
                conditions.append("m.project_id = ?")
                params.append(project_id)
            
            if tags:
                for tag in tags:
                    conditions.append("m.tags LIKE ?")
                    params.append(f"%{tag}%")
            
            # Add relevance filter
            conditions.append("m.relevance_score >= ?")
            params.append(min_relevance)
            
            # Add expiration filter
            conditions.append("(m.expires_at IS NULL OR m.expires_at > ?)")
            params.append(datetime.now().isoformat())
            
            # Combine query
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += """
                GROUP BY m.id
                ORDER BY semantic_score DESC, m.relevance_score DESC, m.usage_count DESC
                LIMIT ?
            """
            params.append(limit)
            
            cursor = conn.execute(base_query, params)
            rows = cursor.fetchall()
            
            # Convert to MemoryEntry objects
            memories = []
            for row in rows:
                memory = MemoryEntry(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    category=row[3],
                    subcategory=row[4],
                    tags=json.loads(row[5]) if row[5] else [],
                    project_id=row[6],
                    relevance_score=row[7],
                    success_score=row[8],
                    usage_count=row[9],
                    created_at=datetime.fromisoformat(row[10]),
                    updated_at=datetime.fromisoformat(row[11]),
                    expires_at=datetime.fromisoformat(row[12]) if row[12] else None,
                    metadata=json.loads(row[13]) if row[13] else {},
                    semantic_keywords=json.loads(row[14]) if row[14] else [],
                    context_hash=row[15]
                )
                memories.append(memory)
            
            # Update usage counts
            for memory in memories:
                self._update_usage_count(memory.id)
            
            return memories
    
    def _update_usage_count(self, memory_id: str):
        """Update the usage count for a memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE memories 
                SET usage_count = usage_count + 1,
                    updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), memory_id))
    
    def get_memory_categories(self) -> Dict[str, int]:
        """Get all memory categories with counts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM memories
                WHERE expires_at IS NULL OR expires_at > ?
                GROUP BY category
                ORDER BY count DESC
            """, (datetime.now().isoformat(),))
            
            return dict(cursor.fetchall())
    
    def get_similar_memories(self, memory_id: str, limit: int = 5) -> List[MemoryEntry]:
        """Find memories similar to the given memory"""
        with sqlite3.connect(self.db_path) as conn:
            # Get the context hash of the target memory
            cursor = conn.execute("""
                SELECT context_hash, category, semantic_keywords
                FROM memories WHERE id = ?
            """, (memory_id,))
            
            row = cursor.fetchone()
            if not row:
                return []
            
            context_hash, category, semantic_keywords_json = row
            semantic_keywords = json.loads(semantic_keywords_json) if semantic_keywords_json else []
            
            # Find similar memories
            if semantic_keywords:
                keyword_placeholders = ",".join(["?" for _ in semantic_keywords])
                similar_query = f"""
                    SELECT DISTINCT m.*, COUNT(si.keyword) as keyword_matches
                    FROM memories m
                    JOIN semantic_index si ON m.id = si.memory_id
                    WHERE m.id != ? 
                    AND (m.context_hash = ? OR si.keyword IN ({keyword_placeholders}))
                    AND (m.expires_at IS NULL OR m.expires_at > ?)
                    GROUP BY m.id
                    ORDER BY keyword_matches DESC, m.relevance_score DESC
                    LIMIT ?
                """
                params = [memory_id, context_hash] + semantic_keywords + [datetime.now().isoformat(), limit]
            else:
                similar_query = """
                    SELECT m.*, 0 as keyword_matches
                    FROM memories m
                    WHERE m.id != ? 
                    AND m.context_hash = ?
                    AND (m.expires_at IS NULL OR m.expires_at > ?)
                    ORDER BY m.relevance_score DESC
                    LIMIT ?
                """
                params = [memory_id, context_hash, datetime.now().isoformat(), limit]
            
            cursor = conn.execute(similar_query, params)
            rows = cursor.fetchall()
            
            # Convert to MemoryEntry objects
            memories = []
            for row in rows:
                memory = MemoryEntry(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    category=row[3],
                    subcategory=row[4],
                    tags=json.loads(row[5]) if row[5] else [],
                    project_id=row[6],
                    relevance_score=row[7],
                    success_score=row[8],
                    usage_count=row[9],
                    created_at=datetime.fromisoformat(row[10]),
                    updated_at=datetime.fromisoformat(row[11]),
                    expires_at=datetime.fromisoformat(row[12]) if row[12] else None,
                    metadata=json.loads(row[13]) if row[13] else {},
                    semantic_keywords=json.loads(row[14]) if row[14] else [],
                    context_hash=row[15]
                )
                memories.append(memory)
            
            return memories
    
    def cleanup_expired_memories(self) -> int:
        """Remove expired memories and return count of removed entries"""
        with sqlite3.connect(self.db_path) as conn:
            # Get expired memory IDs
            cursor = conn.execute("""
                SELECT id FROM memories 
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            """, (datetime.now().isoformat(),))
            
            expired_ids = [row[0] for row in cursor.fetchall()]
            
            if expired_ids:
                # Delete from semantic index
                id_placeholders = ",".join(["?" for _ in expired_ids])
                conn.execute(f"""
                    DELETE FROM semantic_index 
                    WHERE memory_id IN ({id_placeholders})
                """, expired_ids)
                
                # Delete from memories
                conn.execute(f"""
                    DELETE FROM memories 
                    WHERE id IN ({id_placeholders})
                """, expired_ids)
                
                logger.info(f"Cleaned up {len(expired_ids)} expired memories")
            
            return len(expired_ids)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total memories
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            stats["total_memories"] = cursor.fetchone()[0]
            
            # Active memories (not expired)
            cursor = conn.execute("""
                SELECT COUNT(*) FROM memories 
                WHERE expires_at IS NULL OR expires_at > ?
            """, (datetime.now().isoformat(),))
            stats["active_memories"] = cursor.fetchone()[0]
            
            # Category distribution
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM memories
                WHERE expires_at IS NULL OR expires_at > ?
                GROUP BY category
                ORDER BY count DESC
            """, (datetime.now().isoformat(),))
            stats["category_distribution"] = dict(cursor.fetchall())
            
            # Top keywords
            cursor = conn.execute("""
                SELECT si.keyword, COUNT(*) as frequency
                FROM semantic_index si
                JOIN memories m ON si.memory_id = m.id
                WHERE m.expires_at IS NULL OR m.expires_at > ?
                GROUP BY si.keyword
                ORDER BY frequency DESC
                LIMIT 10
            """, (datetime.now().isoformat(),))
            stats["top_keywords"] = dict(cursor.fetchall())
            
            # Average relevance score
            cursor = conn.execute("""
                SELECT AVG(relevance_score) FROM memories
                WHERE expires_at IS NULL OR expires_at > ?
            """, (datetime.now().isoformat(),))
            stats["avg_relevance_score"] = cursor.fetchone()[0] or 0.0
            
            return stats

def main():
    """Test the enhanced memory system"""
    memory_system = EnhancedMemorySystem()
    
    # Add some test memories
    memory_system.add_memory(
        title="React Hook Best Practices",
        content="Use useCallback for expensive computations and useMemo for object dependencies",
        category="code_solutions",
        subcategory="react_patterns",
        tags=["react", "hooks", "performance"],
        metadata={"difficulty": "intermediate", "language": "javascript"}
    )
    
    memory_system.add_memory(
        title="Docker Multi-stage Build",
        content="Use multi-stage builds to reduce image size and improve security",
        category="deployment_strategies",
        tags=["docker", "optimization", "security"],
        metadata={"tool": "docker", "impact": "high"}
    )
    
    # Search memories
    results = memory_system.search_memories("react performance optimization")
    print(f"Found {len(results)} memories")
    
    for memory in results:
        print(f"- {memory.title} (Score: {memory.relevance_score:.2f})")
    
    # Get stats
    stats = memory_system.get_memory_stats()
    print(f"\nMemory Stats: {stats}")

if __name__ == "__main__":
    main()
