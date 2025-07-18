"""
Cross-Project Pattern Recognition System

This module implements pattern extraction, similarity detection, and recommendation
algorithms for identifying successful patterns across projects.
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
class ProjectPattern:
    """Represents a recognized pattern from project analysis"""
    id: str
    name: str
    description: str
    pattern_type: str  # architecture, code, workflow, configuration
    technology_stack: List[str]
    success_metrics: Dict[str, float]
    usage_frequency: int
    projects_used: List[str]
    pattern_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    confidence_score: float

@dataclass
class PatternMatch:
    """Represents a pattern match with similarity score"""
    pattern: ProjectPattern
    similarity_score: float
    matching_elements: List[str]
    recommendation_reason: str

class PatternRecognitionSystem:
    """
    System for extracting, analyzing, and recommending patterns across projects
    """
    
    def __init__(self, db_path: str = "memory/patterns.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Pattern types and their characteristics
        self.pattern_types = {
            "architecture": {
                "weight": 1.0,
                "indicators": ["mvc", "microservices", "layered", "clean", "hexagonal"]
            },
            "code": {
                "weight": 0.9,
                "indicators": ["factory", "singleton", "observer", "strategy", "decorator"]
            },
            "workflow": {
                "weight": 0.8,
                "indicators": ["ci/cd", "gitflow", "agile", "testing", "deployment"]
            },
            "configuration": {
                "weight": 0.7,
                "indicators": ["docker", "kubernetes", "terraform", "ansible", "config"]
            }
        }
        
        self._init_database()
        logger.info("Pattern Recognition System initialized")
    
    def _init_database(self):
        """Initialize the pattern database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    pattern_type TEXT NOT NULL,
                    technology_stack TEXT,
                    success_metrics TEXT,
                    usage_frequency INTEGER DEFAULT 0,
                    projects_used TEXT,
                    pattern_data TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    confidence_score REAL DEFAULT 0.0
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pattern_type ON patterns(pattern_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_confidence ON patterns(confidence_score DESC)
            """)
    
    def extract_patterns_from_project(self, project_data: Dict[str, Any]) -> List[ProjectPattern]:
        """Extract patterns from project data"""
        patterns = []
        
        # Extract architecture patterns
        arch_patterns = self._extract_architecture_patterns(project_data)
        patterns.extend(arch_patterns)
        
        # Extract code patterns
        code_patterns = self._extract_code_patterns(project_data)
        patterns.extend(code_patterns)
        
        # Extract workflow patterns
        workflow_patterns = self._extract_workflow_patterns(project_data)
        patterns.extend(workflow_patterns)
        
        # Extract configuration patterns
        config_patterns = self._extract_configuration_patterns(project_data)
        patterns.extend(config_patterns)
        
        return patterns
    
    def _extract_architecture_patterns(self, project_data: Dict[str, Any]) -> List[ProjectPattern]:
        """Extract architecture patterns from project"""
        patterns = []
        
        # Analyze directory structure
        structure = project_data.get("directory_structure", {})
        files = project_data.get("files", [])
        
        # Detect MVC pattern
        if self._has_mvc_structure(structure, files):
            pattern = ProjectPattern(
                id=self._generate_pattern_id("mvc", project_data.get("project_id", "")),
                name="Model-View-Controller (MVC)",
                description="Separation of concerns using MVC architecture",
                pattern_type="architecture",
                technology_stack=project_data.get("technologies", []),
                success_metrics={"maintainability": 0.8, "scalability": 0.7},
                usage_frequency=1,
                projects_used=[project_data.get("project_id", "")],
                pattern_data={
                    "structure": structure,
                    "key_files": ["models/", "views/", "controllers/"]
                },
                created_at=datetime.now(),
                updated_at=datetime.now(),
                confidence_score=0.8
            )
            patterns.append(pattern)
        
        # Detect microservices pattern
        if self._has_microservices_structure(structure, files):
            pattern = ProjectPattern(
                id=self._generate_pattern_id("microservices", project_data.get("project_id", "")),
                name="Microservices Architecture",
                description="Distributed system with independent services",
                pattern_type="architecture",
                technology_stack=project_data.get("technologies", []),
                success_metrics={"scalability": 0.9, "maintainability": 0.6},
                usage_frequency=1,
                projects_used=[project_data.get("project_id", "")],
                pattern_data={
                    "services": self._identify_services(structure),
                    "communication": "REST/gRPC"
                },
                created_at=datetime.now(),
                updated_at=datetime.now(),
                confidence_score=0.7
            )
            patterns.append(pattern)
        
        return patterns
    
    def _extract_code_patterns(self, project_data: Dict[str, Any]) -> List[ProjectPattern]:
        """Extract code patterns from project"""
        patterns = []
        
        code_files = project_data.get("code_analysis", {})
        
        # Detect design patterns in code
        for file_path, analysis in code_files.items():
            if "factory" in analysis.get("patterns", []):
                pattern = ProjectPattern(
                    id=self._generate_pattern_id("factory", file_path),
                    name="Factory Pattern",
                    description="Object creation pattern for flexible instantiation",
                    pattern_type="code",
                    technology_stack=project_data.get("technologies", []),
                    success_metrics={"flexibility": 0.8, "testability": 0.7},
                    usage_frequency=1,
                    projects_used=[project_data.get("project_id", "")],
                    pattern_data={
                        "implementation": analysis.get("implementation", ""),
                        "file_path": file_path
                    },
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    confidence_score=0.6
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_workflow_patterns(self, project_data: Dict[str, Any]) -> List[ProjectPattern]:
        """Extract workflow patterns from project"""
        patterns = []
        
        # Detect CI/CD patterns
        ci_files = project_data.get("ci_files", [])
        if ci_files:
            pattern = ProjectPattern(
                id=self._generate_pattern_id("cicd", project_data.get("project_id", "")),
                name="CI/CD Pipeline",
                description="Automated continuous integration and deployment",
                pattern_type="workflow",
                technology_stack=project_data.get("technologies", []),
                success_metrics={"automation": 0.9, "reliability": 0.8},
                usage_frequency=1,
                projects_used=[project_data.get("project_id", "")],
                pattern_data={
                    "pipeline_files": ci_files,
                    "stages": ["build", "test", "deploy"]
                },
                created_at=datetime.now(),
                updated_at=datetime.now(),
                confidence_score=0.9
            )
            patterns.append(pattern)
        
        return patterns
    
    def _extract_configuration_patterns(self, project_data: Dict[str, Any]) -> List[ProjectPattern]:
        """Extract configuration patterns from project"""
        patterns = []
        
        # Detect Docker patterns
        if "Dockerfile" in project_data.get("files", []):
            pattern = ProjectPattern(
                id=self._generate_pattern_id("docker", project_data.get("project_id", "")),
                name="Docker Containerization",
                description="Application containerization using Docker",
                pattern_type="configuration",
                technology_stack=project_data.get("technologies", []),
                success_metrics={"portability": 0.9, "consistency": 0.8},
                usage_frequency=1,
                projects_used=[project_data.get("project_id", "")],
                pattern_data={
                    "dockerfile_content": project_data.get("dockerfile_analysis", {}),
                    "base_image": "detected_from_dockerfile"
                },
                created_at=datetime.now(),
                updated_at=datetime.now(),
                confidence_score=0.8
            )
            patterns.append(pattern)
        
        return patterns
    
    def _has_mvc_structure(self, structure: Dict, files: List[str]) -> bool:
        """Check if project has MVC structure"""
        mvc_indicators = ["models", "views", "controllers", "model", "view", "controller"]
        structure_str = json.dumps(structure).lower()
        files_str = " ".join(files).lower()
        
        return sum(1 for indicator in mvc_indicators if indicator in structure_str or indicator in files_str) >= 2
    
    def _has_microservices_structure(self, structure: Dict, files: List[str]) -> bool:
        """Check if project has microservices structure"""
        microservice_indicators = ["services", "service", "api", "gateway", "docker-compose"]
        structure_str = json.dumps(structure).lower()
        files_str = " ".join(files).lower()
        
        return sum(1 for indicator in microservice_indicators if indicator in structure_str or indicator in files_str) >= 2
    
    def _identify_services(self, structure: Dict) -> List[str]:
        """Identify individual services in microservices architecture"""
        services = []
        
        def find_services(node, path=""):
            if isinstance(node, dict):
                for key, value in node.items():
                    if "service" in key.lower() or "api" in key.lower():
                        services.append(f"{path}/{key}" if path else key)
                    find_services(value, f"{path}/{key}" if path else key)
        
        find_services(structure)
        return services
    
    def _generate_pattern_id(self, pattern_name: str, context: str) -> str:
        """Generate unique pattern ID"""
        return hashlib.md5(f"{pattern_name}_{context}_{time.time()}".encode()).hexdigest()
    
    def store_pattern(self, pattern: ProjectPattern) -> str:
        """Store a pattern in the database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO patterns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.id, pattern.name, pattern.description, pattern.pattern_type,
                json.dumps(pattern.technology_stack), json.dumps(pattern.success_metrics),
                pattern.usage_frequency, json.dumps(pattern.projects_used),
                json.dumps(pattern.pattern_data), pattern.created_at.isoformat(),
                pattern.updated_at.isoformat(), pattern.confidence_score
            ))
        
        logger.info(f"Stored pattern: {pattern.name} (ID: {pattern.id})")
        return pattern.id
    
    def find_similar_patterns(self, query_pattern: Dict[str, Any], limit: int = 5) -> List[PatternMatch]:
        """Find patterns similar to the query pattern"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM patterns 
                ORDER BY confidence_score DESC, usage_frequency DESC
            """)
            
            patterns = []
            for row in cursor.fetchall():
                pattern = ProjectPattern(
                    id=row[0], name=row[1], description=row[2], pattern_type=row[3],
                    technology_stack=json.loads(row[4]), success_metrics=json.loads(row[5]),
                    usage_frequency=row[6], projects_used=json.loads(row[7]),
                    pattern_data=json.loads(row[8]), created_at=datetime.fromisoformat(row[9]),
                    updated_at=datetime.fromisoformat(row[10]), confidence_score=row[11]
                )
                patterns.append(pattern)
            
            # Calculate similarity scores
            matches = []
            for pattern in patterns:
                similarity = self._calculate_pattern_similarity(query_pattern, pattern)
                if similarity > 0.3:  # Minimum similarity threshold
                    match = PatternMatch(
                        pattern=pattern,
                        similarity_score=similarity,
                        matching_elements=self._get_matching_elements(query_pattern, pattern),
                        recommendation_reason=self._generate_recommendation_reason(pattern, similarity)
                    )
                    matches.append(match)
            
            # Sort by similarity score
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            return matches[:limit]
    
    def _calculate_pattern_similarity(self, query: Dict[str, Any], pattern: ProjectPattern) -> float:
        """Calculate similarity between query and stored pattern"""
        similarity_score = 0.0
        
        # Technology stack similarity
        query_tech = set(query.get("technologies", []))
        pattern_tech = set(pattern.technology_stack)
        
        if query_tech and pattern_tech:
            tech_similarity = len(query_tech.intersection(pattern_tech)) / len(query_tech.union(pattern_tech))
            similarity_score += tech_similarity * 0.4
        
        # Pattern type similarity
        if query.get("pattern_type") == pattern.pattern_type:
            similarity_score += 0.3
        
        # Success metrics similarity
        query_metrics = query.get("success_metrics", {})
        if query_metrics and pattern.success_metrics:
            metric_similarity = self._calculate_metric_similarity(query_metrics, pattern.success_metrics)
            similarity_score += metric_similarity * 0.3
        
        return min(similarity_score, 1.0)
    
    def _calculate_metric_similarity(self, metrics1: Dict[str, float], metrics2: Dict[str, float]) -> float:
        """Calculate similarity between success metrics"""
        common_metrics = set(metrics1.keys()).intersection(set(metrics2.keys()))
        if not common_metrics:
            return 0.0
        
        similarity = 0.0
        for metric in common_metrics:
            similarity += 1.0 - abs(metrics1[metric] - metrics2[metric])
        
        return similarity / len(common_metrics)
    
    def _get_matching_elements(self, query: Dict[str, Any], pattern: ProjectPattern) -> List[str]:
        """Get list of matching elements between query and pattern"""
        matches = []
        
        # Technology matches
        query_tech = set(query.get("technologies", []))
        pattern_tech = set(pattern.technology_stack)
        common_tech = query_tech.intersection(pattern_tech)
        matches.extend([f"Technology: {tech}" for tech in common_tech])
        
        # Pattern type match
        if query.get("pattern_type") == pattern.pattern_type:
            matches.append(f"Pattern Type: {pattern.pattern_type}")
        
        return matches
    
    def _generate_recommendation_reason(self, pattern: ProjectPattern, similarity: float) -> str:
        """Generate human-readable recommendation reason"""
        if similarity > 0.8:
            return f"Highly similar pattern with {pattern.usage_frequency} successful implementations"
        elif similarity > 0.6:
            return f"Similar pattern used in {len(pattern.projects_used)} projects"
        else:
            return f"Related pattern with {pattern.confidence_score:.1f} confidence score"
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get pattern recognition statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total patterns
            cursor = conn.execute("SELECT COUNT(*) FROM patterns")
            stats["total_patterns"] = cursor.fetchone()[0]
            
            # Pattern type distribution
            cursor = conn.execute("""
                SELECT pattern_type, COUNT(*) as count
                FROM patterns
                GROUP BY pattern_type
                ORDER BY count DESC
            """)
            stats["pattern_type_distribution"] = dict(cursor.fetchall())
            
            # Top patterns by usage
            cursor = conn.execute("""
                SELECT name, usage_frequency
                FROM patterns
                ORDER BY usage_frequency DESC
                LIMIT 5
            """)
            stats["top_patterns"] = dict(cursor.fetchall())
            
            return stats

def main():
    """Test the pattern recognition system"""
    pattern_system = PatternRecognitionSystem()
    
    # Test pattern extraction
    project_data = {
        "project_id": "test_project",
        "technologies": ["python", "flask", "docker"],
        "directory_structure": {
            "models": {"user.py": None, "product.py": None},
            "views": {"user_view.py": None},
            "controllers": {"user_controller.py": None}
        },
        "files": ["Dockerfile", "requirements.txt", "app.py"]
    }
    
    patterns = pattern_system.extract_patterns_from_project(project_data)
    print(f"Extracted {len(patterns)} patterns")
    
    for pattern in patterns:
        pattern_system.store_pattern(pattern)
        print(f"- {pattern.name} ({pattern.pattern_type})")
    
    # Test pattern matching
    query = {
        "technologies": ["python", "flask"],
        "pattern_type": "architecture"
    }
    
    matches = pattern_system.find_similar_patterns(query)
    print(f"\nFound {len(matches)} similar patterns")
    
    for match in matches:
        print(f"- {match.pattern.name} (Similarity: {match.similarity_score:.2f})")

if __name__ == "__main__":
    main()
