"""
Test Suite for Enhanced Memory and Context Persistence System

This module provides comprehensive testing for all components of Step 2.3:
- Enhanced Memory System
- Pattern Recognition
- Context Inheritance
- Project Relationships
- Context Persistence Optimization
"""

import unittest
import tempfile
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.enhanced_memory_system import EnhancedMemorySystem, MemoryEntry
from memory.pattern_recognition import PatternRecognitionSystem, ProjectPattern
from memory.context_inheritance import ContextInheritanceSystem, ContextType, ConflictResolution
from memory.project_relationships import ProjectRelationshipSystem, ProjectNode

class TestEnhancedMemorySystem(unittest.TestCase):
    """Test the enhanced memory system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")
        self.memory_system = EnhancedMemorySystem(self.db_path)
    
    def tearDown(self):
        """Clean up test environment"""
        # Close database connections
        if hasattr(self, 'memory_system'):
            del self.memory_system
        # Small delay to ensure file handles are released
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            # Retry after a short delay
            time.sleep(0.5)
            shutil.rmtree(self.temp_dir)
    
    def test_add_memory(self):
        """Test adding memories with semantic indexing"""
        memory_id = self.memory_system.add_memory(
            title="React Hook Best Practices",
            content="Use useCallback for expensive computations and useMemo for object dependencies",
            category="code_solutions",
            subcategory="react_patterns",
            tags=["react", "hooks", "performance"],
            metadata={"difficulty": "intermediate", "language": "javascript"}
        )
        
        self.assertIsNotNone(memory_id)
        self.assertEqual(len(memory_id), 32)  # MD5 hash length
    
    def test_search_memories(self):
        """Test memory search functionality"""
        # Add test memories
        self.memory_system.add_memory(
            title="React Performance Optimization",
            content="Use React.memo and useMemo to prevent unnecessary re-renders",
            category="code_solutions",
            tags=["react", "performance", "optimization"]
        )
        
        self.memory_system.add_memory(
            title="Docker Multi-stage Build",
            content="Use multi-stage builds to reduce image size",
            category="deployment_strategies",
            tags=["docker", "optimization"]
        )
        
        # Search for React-related memories
        results = self.memory_system.search_memories("react performance")
        self.assertGreater(len(results), 0)
        
        # Check that React memory is returned
        react_memory = next((m for m in results if "react" in m.title.lower()), None)
        self.assertIsNotNone(react_memory)
    
    def test_memory_categorization(self):
        """Test memory categorization"""
        # Add memories in different categories
        categories = ["code_solutions", "deployment_strategies", "debugging_solutions"]
        
        for category in categories:
            self.memory_system.add_memory(
                title=f"Test {category}",
                content=f"Content for {category}",
                category=category
            )
        
        # Get category distribution
        category_dist = self.memory_system.get_memory_categories()
        
        for category in categories:
            self.assertIn(category, category_dist)
            self.assertEqual(category_dist[category], 1)
    
    def test_similar_memories(self):
        """Test finding similar memories"""
        # Add a memory
        memory_id = self.memory_system.add_memory(
            title="Python Flask API",
            content="Building REST APIs with Flask",
            category="code_solutions",
            tags=["python", "flask", "api"]
        )
        
        # Add a similar memory
        self.memory_system.add_memory(
            title="Python FastAPI Tutorial",
            content="Creating APIs with FastAPI framework",
            category="code_solutions",
            tags=["python", "fastapi", "api"]
        )
        
        # Find similar memories
        similar = self.memory_system.get_similar_memories(memory_id)
        self.assertGreater(len(similar), 0)
    
    def test_memory_cleanup(self):
        """Test expired memory cleanup"""
        # Add memory that expires in 1 day
        self.memory_system.add_memory(
            title="Temporary Memory",
            content="This memory will expire",
            category="debugging_solutions",
            expires_in_days=1
        )
        
        # Add memory that expires immediately (for testing)
        expired_memory_id = self.memory_system.add_memory(
            title="Expired Memory",
            content="This memory should be cleaned up",
            category="debugging_solutions",
            expires_in_days=-1  # Already expired
        )
        
        # Clean up expired memories
        cleaned_count = self.memory_system.cleanup_expired_memories()
        self.assertEqual(cleaned_count, 1)

class TestPatternRecognitionSystem(unittest.TestCase):
    """Test the pattern recognition system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_patterns.db")
        self.pattern_system = PatternRecognitionSystem(self.db_path)
    
    def tearDown(self):
        """Clean up test environment"""
        # Close database connections
        if hasattr(self, 'memory_system'):
            del self.memory_system
        # Small delay to ensure file handles are released
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            # Retry after a short delay
            time.sleep(0.5)
            shutil.rmtree(self.temp_dir)
    
    def test_extract_architecture_patterns(self):
        """Test architecture pattern extraction"""
        project_data = {
            "project_id": "test_mvc",
            "technologies": ["python", "flask"],
            "directory_structure": {
                "models": {"user.py": None, "product.py": None},
                "views": {"user_view.py": None},
                "controllers": {"user_controller.py": None}
            },
            "files": ["app.py", "requirements.txt"]
        }
        
        patterns = self.pattern_system.extract_patterns_from_project(project_data)
        
        # Should detect MVC pattern
        mvc_pattern = next((p for p in patterns if "mvc" in p.name.lower()), None)
        self.assertIsNotNone(mvc_pattern)
        self.assertEqual(mvc_pattern.pattern_type, "architecture")
    
    def test_extract_configuration_patterns(self):
        """Test configuration pattern extraction"""
        project_data = {
            "project_id": "test_docker",
            "technologies": ["python", "docker"],
            "files": ["Dockerfile", "docker-compose.yml", "requirements.txt"]
        }
        
        patterns = self.pattern_system.extract_patterns_from_project(project_data)
        
        # Should detect Docker pattern
        docker_pattern = next((p for p in patterns if "docker" in p.name.lower()), None)
        self.assertIsNotNone(docker_pattern)
        self.assertEqual(docker_pattern.pattern_type, "configuration")
    
    def test_pattern_similarity(self):
        """Test pattern similarity detection"""
        # Create and store a pattern
        pattern = ProjectPattern(
            id="test_pattern",
            name="Test Pattern",
            description="A test pattern",
            pattern_type="architecture",
            technology_stack=["python", "flask"],
            success_metrics={"maintainability": 0.8},
            usage_frequency=1,
            projects_used=["test_project"],
            pattern_data={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            confidence_score=0.8
        )
        
        self.pattern_system.store_pattern(pattern)
        
        # Search for similar patterns
        query = {
            "technologies": ["python", "flask"],
            "pattern_type": "architecture"
        }
        
        matches = self.pattern_system.find_similar_patterns(query)
        self.assertGreater(len(matches), 0)
        
        # Check that our pattern is found
        found_pattern = next((m for m in matches if m.pattern.id == "test_pattern"), None)
        self.assertIsNotNone(found_pattern)

class TestContextInheritanceSystem(unittest.TestCase):
    """Test the context inheritance system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_context.db")
        self.context_system = ContextInheritanceSystem(self.db_path)
    
    def tearDown(self):
        """Clean up test environment"""
        # Close database connections
        if hasattr(self, 'memory_system'):
            del self.memory_system
        # Small delay to ensure file handles are released
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            # Retry after a short delay
            time.sleep(0.5)
            shutil.rmtree(self.temp_dir)
    
    def test_create_context_version(self):
        """Test creating context versions"""
        context_data = {
            "theme": "dark",
            "font_size": 14,
            "auto_save": True
        }
        
        version_id = self.context_system.create_context_version(
            context_id="user_prefs",
            data=context_data,
            created_by="test_user",
            change_summary="Initial preferences"
        )
        
        self.assertIsNotNone(version_id)
        
        # Retrieve the version
        version = self.context_system.get_context_version(version_id)
        self.assertIsNotNone(version)
        self.assertEqual(version.context_id, "user_prefs")
        self.assertEqual(version.data["theme"], "dark")
    
    def test_context_inheritance(self):
        """Test context inheritance between projects"""
        # Create user preferences
        user_prefs = {
            "theme": "dark",
            "font_size": 14,
            "auto_save": True,
            "inherit_to_projects": True,
            "user_preferences": {"inherit_to_projects": True}
        }
        
        self.context_system.create_context_version(
            context_id="user_global",
            data=user_prefs,
            created_by="test_user",
            change_summary="User preferences"
        )
        
        # Create project settings
        project_settings = {
            "name": "test_project",
            "technologies": ["python", "flask"]
        }
        
        self.context_system.create_context_version(
            context_id="project_test",
            data=project_settings,
            created_by="test_user",
            change_summary="Project settings"
        )
        
        # Test inheritance
        inherited_data = self.context_system.inherit_context("user_global", "project_test")
        
        # Should contain both user preferences and project settings
        self.assertIn("name", inherited_data)
        self.assertIn("theme", inherited_data)
    
    def test_context_versioning(self):
        """Test context versioning and history"""
        context_id = "test_context"
        
        # Create initial version
        version1 = self.context_system.create_context_version(
            context_id=context_id,
            data={"version": 1, "feature": "initial"},
            created_by="test_user",
            change_summary="Initial version"
        )
        
        # Create second version
        version2 = self.context_system.create_context_version(
            context_id=context_id,
            data={"version": 2, "feature": "updated"},
            created_by="test_user",
            change_summary="Updated version",
            parent_version=version1
        )
        
        # Get history
        history = self.context_system.get_context_history(context_id)
        self.assertEqual(len(history), 2)
        
        # Check version order (newest first)
        self.assertEqual(history[0].data["version"], 2)
        self.assertEqual(history[1].data["version"], 1)
    
    def test_context_rollback(self):
        """Test context rollback functionality"""
        context_id = "rollback_test"
        
        # Create versions
        version1 = self.context_system.create_context_version(
            context_id=context_id,
            data={"state": "good"},
            created_by="test_user",
            change_summary="Good state"
        )
        
        version2 = self.context_system.create_context_version(
            context_id=context_id,
            data={"state": "bad"},
            created_by="test_user",
            change_summary="Bad state"
        )
        
        # Rollback to version 1
        rollback_version = self.context_system.rollback_to_version(
            context_id=context_id,
            version_id=version1,
            created_by="test_user"
        )
        
        self.assertIsNotNone(rollback_version)
        
        # Check that latest version has rolled back data
        latest = self.context_system.get_latest_context_version(context_id)
        self.assertEqual(latest.data["state"], "good")

class TestProjectRelationshipSystem(unittest.TestCase):
    """Test the project relationship system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_relationships.db")
        self.relationship_system = ProjectRelationshipSystem(self.db_path)
    
    def tearDown(self):
        """Clean up test environment"""
        # Close database connections
        if hasattr(self, 'memory_system'):
            del self.memory_system
        # Small delay to ensure file handles are released
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            # Retry after a short delay
            time.sleep(0.5)
            shutil.rmtree(self.temp_dir)
    
    def test_add_project(self):
        """Test adding projects"""
        project = ProjectNode(
            project_id="test_project",
            name="Test Project",
            description="A test project",
            technologies=["python", "flask"],
            frameworks=["flask"],
            project_type="web_application",
            complexity_score=0.5,
            success_metrics={"overall": 0.8},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"domain": "test"}
        )
        
        project_id = self.relationship_system.add_project(project)
        self.assertEqual(project_id, "test_project")
        
        # Retrieve the project
        retrieved = self.relationship_system.get_project("test_project")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Project")
    
    def test_project_similarity(self):
        """Test project similarity calculation"""
        # Add two similar projects
        project1 = ProjectNode(
            project_id="proj1",
            name="E-commerce API",
            description="REST API for e-commerce",
            technologies=["python", "flask", "postgresql"],
            frameworks=["flask"],
            project_type="api_service",
            complexity_score=0.7,
            success_metrics={"overall": 0.8},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        project2 = ProjectNode(
            project_id="proj2",
            name="Blog API",
            description="REST API for blogging",
            technologies=["python", "flask", "sqlite"],
            frameworks=["flask"],
            project_type="api_service",
            complexity_score=0.6,
            success_metrics={"overall": 0.7},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.relationship_system.add_project(project1)
        self.relationship_system.add_project(project2)
        
        # Get similar projects
        similar = self.relationship_system.get_similar_projects("proj1")
        self.assertGreater(len(similar), 0)
        
        # Check that proj2 is similar to proj1
        similar_project = next((p for p, s in similar if p.project_id == "proj2"), None)
        self.assertIsNotNone(similar_project)
    
    def test_project_recommendations(self):
        """Test project recommendation generation"""
        # Add a successful project
        successful_project = ProjectNode(
            project_id="successful_proj",
            name="Successful Project",
            description="A very successful project",
            technologies=["python", "flask", "redis"],
            frameworks=["flask"],
            project_type="api_service",
            complexity_score=0.8,
            success_metrics={"overall": 0.9, "performance": 0.95},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        # Add a target project
        target_project = ProjectNode(
            project_id="target_proj",
            name="Target Project",
            description="Project needing recommendations",
            technologies=["python", "flask"],
            frameworks=["flask"],
            project_type="api_service",
            complexity_score=0.7,
            success_metrics={"overall": 0.6},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.relationship_system.add_project(successful_project)
        self.relationship_system.add_project(target_project)
        
        # Generate recommendations
        recommendations = self.relationship_system.generate_recommendations("target_proj")
        self.assertGreater(len(recommendations), 0)
        
        # Check that Redis is recommended (from successful project)
        tech_recommendation = next((r for r in recommendations if r.recommendation_type == "technology"), None)
        self.assertIsNotNone(tech_recommendation)

class TestIntegrationWorkflow(unittest.TestCase):
    """Test integration between all memory system components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize all systems
        self.memory_system = EnhancedMemorySystem(os.path.join(self.temp_dir, "memory.db"))
        self.pattern_system = PatternRecognitionSystem(os.path.join(self.temp_dir, "patterns.db"))
        self.context_system = ContextInheritanceSystem(os.path.join(self.temp_dir, "context.db"))
        self.relationship_system = ProjectRelationshipSystem(os.path.join(self.temp_dir, "relationships.db"))
    
    def tearDown(self):
        """Clean up test environment"""
        # Close database connections
        if hasattr(self, 'memory_system'):
            del self.memory_system
        # Small delay to ensure file handles are released
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            # Retry after a short delay
            time.sleep(0.5)
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from project creation to recommendations"""
        # 1. Add project memories
        memory_id = self.memory_system.add_memory(
            title="Flask API Best Practices",
            content="Use blueprints for modular design and proper error handling",
            category="code_solutions",
            tags=["flask", "api", "best-practices"],
            project_id="flask_project"
        )
        
        # 2. Extract patterns from project
        project_data = {
            "project_id": "flask_project",
            "technologies": ["python", "flask"],
            "directory_structure": {
                "api": {"routes.py": None, "models.py": None},
                "tests": {"test_api.py": None}
            },
            "files": ["app.py", "requirements.txt"]
        }
        
        patterns = self.pattern_system.extract_patterns_from_project(project_data)
        for pattern in patterns:
            self.pattern_system.store_pattern(pattern)
        
        # 3. Create context versions
        project_context = {
            "name": "Flask API Project",
            "technologies": ["python", "flask"],
            "patterns": [p.name for p in patterns],
            "memories": [memory_id]
        }
        
        context_version = self.context_system.create_context_version(
            context_id="flask_project",
            data=project_context,
            created_by="developer",
            change_summary="Initial project setup"
        )
        
        # 4. Add project to relationship system
        project_node = ProjectNode(
            project_id="flask_project",
            name="Flask API Project",
            description="REST API built with Flask",
            technologies=["python", "flask"],
            frameworks=["flask"],
            project_type="api_service",
            complexity_score=0.6,
            success_metrics={"overall": 0.8},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"context_version": context_version}
        )
        
        self.relationship_system.add_project(project_node)
        
        # 5. Verify all systems are working together
        # Check memory search
        memories = self.memory_system.search_memories("flask api")
        self.assertGreater(len(memories), 0)
        
        # Check pattern storage
        pattern_stats = self.pattern_system.get_pattern_stats()
        self.assertGreater(pattern_stats["total_patterns"], 0)
        
        # Check context inheritance
        latest_context = self.context_system.get_latest_context_version("flask_project")
        self.assertIsNotNone(latest_context)
        
        # Check project relationships
        relationship_stats = self.relationship_system.get_relationship_stats()
        self.assertEqual(relationship_stats["total_projects"], 1)

def run_all_tests():
    """Run all test suites"""
    print("🧪 Running Enhanced Memory and Context Persistence Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEnhancedMemorySystem,
        TestPatternRecognitionSystem,
        TestContextInheritanceSystem,
        TestProjectRelationshipSystem,
        TestIntegrationWorkflow
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Error:')[-1].strip()}")
    
    if not result.failures and not result.errors:
        print("\n✅ All tests passed! Enhanced Memory and Context Persistence system is working correctly.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
