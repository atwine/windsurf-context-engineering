"""
Project Relationship Mapping System

This module implements project similarity analysis, dependency tracking, evolution history,
knowledge graphs, and recommendation systems for cross-project learning.
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
import math
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectNode:
    """Represents a project in the knowledge graph"""
    project_id: str
    name: str
    description: str
    technologies: List[str]
    frameworks: List[str]
    project_type: str
    complexity_score: float
    success_metrics: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

@dataclass
class ProjectRelationship:
    """Represents a relationship between two projects"""
    relationship_id: str
    source_project_id: str
    target_project_id: str
    relationship_type: str  # "similar", "derived", "dependency", "evolution"
    strength: float  # 0.0 to 1.0
    attributes: Dict[str, Any]
    created_at: datetime
    confidence: float

@dataclass
class ProjectEvolution:
    """Represents evolution of a project over time"""
    evolution_id: str
    project_id: str
    version: str
    changes: List[str]
    metrics_delta: Dict[str, float]
    timestamp: datetime
    change_type: str  # "feature", "refactor", "bugfix", "architecture"

@dataclass
class ProjectRecommendation:
    """Represents a project recommendation"""
    recommendation_id: str
    target_project_id: str
    recommended_project_id: str
    recommendation_type: str  # "similar", "pattern", "tool", "architecture"
    confidence: float
    reasoning: str
    benefits: List[str]
    implementation_effort: str  # "low", "medium", "high"

class ProjectRelationshipSystem:
    """
    System for analyzing and mapping relationships between projects
    """
    
    def __init__(self, db_path: str = "memory/project_relationships.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Similarity thresholds
        self.similarity_thresholds = {
            "technology": 0.3,
            "framework": 0.4,
            "architecture": 0.5,
            "domain": 0.3,
            "complexity": 0.2
        }
        
        # Relationship types and their weights
        self.relationship_weights = {
            "similar": 1.0,
            "derived": 0.9,
            "dependency": 0.8,
            "evolution": 0.7,
            "pattern_match": 0.6
        }
        
        self._init_database()
        logger.info("Project Relationship System initialized")
    
    def _init_database(self):
        """Initialize the project relationship database"""
        with sqlite3.connect(self.db_path) as conn:
            # Projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    technologies TEXT,
                    frameworks TEXT,
                    project_type TEXT,
                    complexity_score REAL,
                    success_metrics TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Relationships table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id TEXT PRIMARY KEY,
                    source_project_id TEXT,
                    target_project_id TEXT,
                    relationship_type TEXT,
                    strength REAL,
                    attributes TEXT,
                    created_at TIMESTAMP,
                    confidence REAL,
                    FOREIGN KEY (source_project_id) REFERENCES projects(project_id),
                    FOREIGN KEY (target_project_id) REFERENCES projects(project_id)
                )
            """)
            
            # Evolution history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_evolution (
                    evolution_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    version TEXT,
                    changes TEXT,
                    metrics_delta TEXT,
                    timestamp TIMESTAMP,
                    change_type TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)
            
            # Recommendations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    recommendation_id TEXT PRIMARY KEY,
                    target_project_id TEXT,
                    recommended_project_id TEXT,
                    recommendation_type TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    benefits TEXT,
                    implementation_effort TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (target_project_id) REFERENCES projects(project_id),
                    FOREIGN KEY (recommended_project_id) REFERENCES projects(project_id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_project_type ON projects(project_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationship_type ON relationships(relationship_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationship_strength ON relationships(strength DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evolution_timestamp ON project_evolution(timestamp)")
    
    def add_project(self, project: ProjectNode) -> str:
        """Add a new project to the system"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project.project_id, project.name, project.description,
                json.dumps(project.technologies), json.dumps(project.frameworks),
                project.project_type, project.complexity_score,
                json.dumps(project.success_metrics), project.created_at.isoformat(),
                project.updated_at.isoformat(), json.dumps(project.metadata)
            ))
        
        # Analyze relationships with existing projects
        self._analyze_project_relationships(project.project_id)
        
        logger.info(f"Added project: {project.name} (ID: {project.project_id})")
        return project.project_id
    
    def _analyze_project_relationships(self, project_id: str):
        """Analyze relationships between the given project and all existing projects"""
        target_project = self.get_project(project_id)
        if not target_project:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM projects WHERE project_id != ?
            """, (project_id,))
            
            for row in cursor.fetchall():
                other_project = ProjectNode(
                    project_id=row[0], name=row[1], description=row[2],
                    technologies=json.loads(row[3]), frameworks=json.loads(row[4]),
                    project_type=row[5], complexity_score=row[6],
                    success_metrics=json.loads(row[7]), created_at=datetime.fromisoformat(row[8]),
                    updated_at=datetime.fromisoformat(row[9]), metadata=json.loads(row[10])
                )
                
                # Calculate similarity
                similarity = self._calculate_project_similarity(target_project, other_project)
                
                if similarity > 0.3:  # Minimum similarity threshold
                    relationship = ProjectRelationship(
                        relationship_id=self._generate_relationship_id(project_id, other_project.project_id),
                        source_project_id=project_id,
                        target_project_id=other_project.project_id,
                        relationship_type="similar",
                        strength=similarity,
                        attributes=self._get_similarity_attributes(target_project, other_project),
                        created_at=datetime.now(),
                        confidence=min(similarity * 1.2, 1.0)
                    )
                    
                    self.add_relationship(relationship)
    
    def _calculate_project_similarity(self, project1: ProjectNode, project2: ProjectNode) -> float:
        """Calculate similarity score between two projects"""
        similarity_score = 0.0
        
        # Technology similarity
        tech1 = set(project1.technologies)
        tech2 = set(project2.technologies)
        if tech1 and tech2:
            tech_similarity = len(tech1.intersection(tech2)) / len(tech1.union(tech2))
            similarity_score += tech_similarity * 0.3
        
        # Framework similarity
        frame1 = set(project1.frameworks)
        frame2 = set(project2.frameworks)
        if frame1 and frame2:
            frame_similarity = len(frame1.intersection(frame2)) / len(frame1.union(frame2))
            similarity_score += frame_similarity * 0.25
        
        # Project type similarity
        if project1.project_type == project2.project_type:
            similarity_score += 0.2
        
        # Complexity similarity
        complexity_diff = abs(project1.complexity_score - project2.complexity_score)
        complexity_similarity = max(0, 1.0 - complexity_diff)
        similarity_score += complexity_similarity * 0.15
        
        # Success metrics similarity
        if project1.success_metrics and project2.success_metrics:
            metrics_similarity = self._calculate_metrics_similarity(
                project1.success_metrics, project2.success_metrics
            )
            similarity_score += metrics_similarity * 0.1
        
        return min(similarity_score, 1.0)
    
    def _calculate_metrics_similarity(self, metrics1: Dict[str, float], metrics2: Dict[str, float]) -> float:
        """Calculate similarity between success metrics"""
        common_metrics = set(metrics1.keys()).intersection(set(metrics2.keys()))
        if not common_metrics:
            return 0.0
        
        similarity = 0.0
        for metric in common_metrics:
            diff = abs(metrics1[metric] - metrics2[metric])
            similarity += max(0, 1.0 - diff)
        
        return similarity / len(common_metrics)
    
    def _get_similarity_attributes(self, project1: ProjectNode, project2: ProjectNode) -> Dict[str, Any]:
        """Get attributes that make projects similar"""
        attributes = {}
        
        # Common technologies
        common_tech = set(project1.technologies).intersection(set(project2.technologies))
        if common_tech:
            attributes["common_technologies"] = list(common_tech)
        
        # Common frameworks
        common_frameworks = set(project1.frameworks).intersection(set(project2.frameworks))
        if common_frameworks:
            attributes["common_frameworks"] = list(common_frameworks)
        
        # Project type match
        if project1.project_type == project2.project_type:
            attributes["same_project_type"] = project1.project_type
        
        # Complexity similarity
        complexity_diff = abs(project1.complexity_score - project2.complexity_score)
        if complexity_diff < 0.3:
            attributes["similar_complexity"] = True
        
        return attributes
    
    def _generate_relationship_id(self, source_id: str, target_id: str) -> str:
        """Generate unique relationship ID"""
        return hashlib.md5(f"{source_id}_{target_id}_{time.time()}".encode()).hexdigest()
    
    def add_relationship(self, relationship: ProjectRelationship) -> str:
        """Add a relationship between projects"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO relationships VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                relationship.relationship_id, relationship.source_project_id,
                relationship.target_project_id, relationship.relationship_type,
                relationship.strength, json.dumps(relationship.attributes),
                relationship.created_at.isoformat(), relationship.confidence
            ))
        
        logger.info(f"Added relationship: {relationship.relationship_type} between {relationship.source_project_id} and {relationship.target_project_id}")
        return relationship.relationship_id
    
    def get_project(self, project_id: str) -> Optional[ProjectNode]:
        """Get a project by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM projects WHERE project_id = ?
            """, (project_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ProjectNode(
                project_id=row[0], name=row[1], description=row[2],
                technologies=json.loads(row[3]), frameworks=json.loads(row[4]),
                project_type=row[5], complexity_score=row[6],
                success_metrics=json.loads(row[7]), created_at=datetime.fromisoformat(row[8]),
                updated_at=datetime.fromisoformat(row[9]), metadata=json.loads(row[10])
            )
    
    def get_similar_projects(self, project_id: str, limit: int = 5) -> List[Tuple[ProjectNode, float]]:
        """Get projects similar to the given project"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT p.*, r.strength
                FROM projects p
                JOIN relationships r ON p.project_id = r.target_project_id
                WHERE r.source_project_id = ? AND r.relationship_type = 'similar'
                ORDER BY r.strength DESC
                LIMIT ?
            """, (project_id, limit))
            
            similar_projects = []
            for row in cursor.fetchall():
                project = ProjectNode(
                    project_id=row[0], name=row[1], description=row[2],
                    technologies=json.loads(row[3]), frameworks=json.loads(row[4]),
                    project_type=row[5], complexity_score=row[6],
                    success_metrics=json.loads(row[7]), created_at=datetime.fromisoformat(row[8]),
                    updated_at=datetime.fromisoformat(row[9]), metadata=json.loads(row[10])
                )
                similarity = row[11]
                similar_projects.append((project, similarity))
            
            return similar_projects
    
    def add_evolution_record(self, evolution: ProjectEvolution) -> str:
        """Add an evolution record for a project"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO project_evolution VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                evolution.evolution_id, evolution.project_id, evolution.version,
                json.dumps(evolution.changes), json.dumps(evolution.metrics_delta),
                evolution.timestamp.isoformat(), evolution.change_type
            ))
        
        logger.info(f"Added evolution record: {evolution.evolution_id} for project: {evolution.project_id}")
        return evolution.evolution_id
    
    def get_project_evolution(self, project_id: str, limit: int = 10) -> List[ProjectEvolution]:
        """Get evolution history for a project"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM project_evolution 
                WHERE project_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (project_id, limit))
            
            evolutions = []
            for row in cursor.fetchall():
                evolution = ProjectEvolution(
                    evolution_id=row[0], project_id=row[1], version=row[2],
                    changes=json.loads(row[3]), metrics_delta=json.loads(row[4]),
                    timestamp=datetime.fromisoformat(row[5]), change_type=row[6]
                )
                evolutions.append(evolution)
            
            return evolutions
    
    def generate_recommendations(self, project_id: str) -> List[ProjectRecommendation]:
        """Generate recommendations for a project based on similar projects"""
        recommendations = []
        
        # Get similar projects
        similar_projects = self.get_similar_projects(project_id, limit=10)
        
        target_project = self.get_project(project_id)
        if not target_project:
            return recommendations
        
        for similar_project, similarity in similar_projects:
            # Recommend technologies used in similar projects
            tech_diff = set(similar_project.technologies) - set(target_project.technologies)
            if tech_diff:
                recommendation = ProjectRecommendation(
                    recommendation_id=hashlib.md5(f"tech_{project_id}_{similar_project.project_id}_{time.time()}".encode()).hexdigest(),
                    target_project_id=project_id,
                    recommended_project_id=similar_project.project_id,
                    recommendation_type="technology",
                    confidence=similarity * 0.8,
                    reasoning=f"Similar project '{similar_project.name}' successfully uses these technologies",
                    benefits=[f"Adopt {tech}" for tech in list(tech_diff)[:3]],
                    implementation_effort="medium"
                )
                recommendations.append(recommendation)
            
            # Recommend patterns from successful similar projects
            if similar_project.success_metrics.get("overall", 0) > 0.7:
                recommendation = ProjectRecommendation(
                    recommendation_id=hashlib.md5(f"pattern_{project_id}_{similar_project.project_id}_{time.time()}".encode()).hexdigest(),
                    target_project_id=project_id,
                    recommended_project_id=similar_project.project_id,
                    recommendation_type="pattern",
                    confidence=similarity * similar_project.success_metrics.get("overall", 0.5),
                    reasoning=f"Project '{similar_project.name}' has proven successful patterns",
                    benefits=["Improved architecture", "Better maintainability", "Higher success rate"],
                    implementation_effort="high"
                )
                recommendations.append(recommendation)
        
        # Store recommendations
        for recommendation in recommendations:
            self._store_recommendation(recommendation)
        
        return recommendations
    
    def _store_recommendation(self, recommendation: ProjectRecommendation):
        """Store a recommendation in the database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO recommendations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recommendation.recommendation_id, recommendation.target_project_id,
                recommendation.recommended_project_id, recommendation.recommendation_type,
                recommendation.confidence, recommendation.reasoning,
                json.dumps(recommendation.benefits), recommendation.implementation_effort,
                datetime.now().isoformat()
            ))
    
    def get_project_recommendations(self, project_id: str, limit: int = 5) -> List[ProjectRecommendation]:
        """Get stored recommendations for a project"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM recommendations 
                WHERE target_project_id = ? 
                ORDER BY confidence DESC 
                LIMIT ?
            """, (project_id, limit))
            
            recommendations = []
            for row in cursor.fetchall():
                recommendation = ProjectRecommendation(
                    recommendation_id=row[0], target_project_id=row[1],
                    recommended_project_id=row[2], recommendation_type=row[3],
                    confidence=row[4], reasoning=row[5],
                    benefits=json.loads(row[6]), implementation_effort=row[7]
                )
                recommendations.append(recommendation)
            
            return recommendations
    
    def get_knowledge_graph_data(self) -> Dict[str, Any]:
        """Get data for visualizing the project knowledge graph"""
        with sqlite3.connect(self.db_path) as conn:
            # Get all projects
            cursor = conn.execute("SELECT project_id, name, project_type, complexity_score FROM projects")
            nodes = []
            for row in cursor.fetchall():
                nodes.append({
                    "id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "complexity": row[3]
                })
            
            # Get all relationships
            cursor = conn.execute("""
                SELECT source_project_id, target_project_id, relationship_type, strength 
                FROM relationships
            """)
            edges = []
            for row in cursor.fetchall():
                edges.append({
                    "source": row[0],
                    "target": row[1],
                    "type": row[2],
                    "strength": row[3]
                })
            
            return {"nodes": nodes, "edges": edges}
    
    def get_relationship_stats(self) -> Dict[str, Any]:
        """Get project relationship statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total projects
            cursor = conn.execute("SELECT COUNT(*) FROM projects")
            stats["total_projects"] = cursor.fetchone()[0]
            
            # Total relationships
            cursor = conn.execute("SELECT COUNT(*) FROM relationships")
            stats["total_relationships"] = cursor.fetchone()[0]
            
            # Relationship type distribution
            cursor = conn.execute("""
                SELECT relationship_type, COUNT(*) as count
                FROM relationships
                GROUP BY relationship_type
                ORDER BY count DESC
            """)
            stats["relationship_types"] = dict(cursor.fetchall())
            
            # Project type distribution
            cursor = conn.execute("""
                SELECT project_type, COUNT(*) as count
                FROM projects
                GROUP BY project_type
                ORDER BY count DESC
            """)
            stats["project_types"] = dict(cursor.fetchall())
            
            # Evolution records
            cursor = conn.execute("SELECT COUNT(*) FROM project_evolution")
            stats["evolution_records"] = cursor.fetchone()[0]
            
            # Recommendations
            cursor = conn.execute("SELECT COUNT(*) FROM recommendations")
            stats["total_recommendations"] = cursor.fetchone()[0]
            
            return stats

def main():
    """Test the project relationship system"""
    relationship_system = ProjectRelationshipSystem()
    
    # Add test projects
    project1 = ProjectNode(
        project_id="proj1",
        name="E-commerce API",
        description="REST API for e-commerce platform",
        technologies=["python", "flask", "postgresql"],
        frameworks=["flask", "sqlalchemy"],
        project_type="api_service",
        complexity_score=0.7,
        success_metrics={"overall": 0.8, "performance": 0.9},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"domain": "e-commerce"}
    )
    
    project2 = ProjectNode(
        project_id="proj2",
        name="Blog API",
        description="REST API for blogging platform",
        technologies=["python", "flask", "sqlite"],
        frameworks=["flask", "sqlalchemy"],
        project_type="api_service",
        complexity_score=0.5,
        success_metrics={"overall": 0.7, "performance": 0.8},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"domain": "content"}
    )
    
    # Add projects
    relationship_system.add_project(project1)
    relationship_system.add_project(project2)
    
    # Get similar projects
    similar = relationship_system.get_similar_projects("proj1")
    print(f"Similar projects to proj1: {len(similar)}")
    
    # Generate recommendations
    recommendations = relationship_system.generate_recommendations("proj1")
    print(f"Generated {len(recommendations)} recommendations")
    
    # Get stats
    stats = relationship_system.get_relationship_stats()
    print(f"Relationship stats: {stats}")

if __name__ == "__main__":
    main()
