"""
Simple Test for Enhanced Memory System Components

This provides a quick validation of the core functionality without complex database operations.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import tempfile
import json

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_memory_system():
    """Test enhanced memory system basic functionality"""
    print("🧠 Testing Enhanced Memory System...")
    
    try:
        from memory.enhanced_memory_system import EnhancedMemorySystem
        
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        memory_system = EnhancedMemorySystem(temp_db.name)
        
        # Test adding memory
        memory_id = memory_system.add_memory(
            title="Test Memory",
            content="This is a test memory for validation",
            category="code_solutions",
            tags=["test", "validation"]
        )
        
        print(f"   ✅ Memory added successfully: {memory_id[:8]}...")
        
        # Test searching memories
        results = memory_system.search_memories("test validation")
        print(f"   ✅ Memory search returned {len(results)} results")
        
        # Test memory stats
        stats = memory_system.get_memory_stats()
        print(f"   ✅ Memory stats: {stats['total_memories']} total memories")
        
        # Cleanup
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_pattern_recognition():
    """Test pattern recognition system"""
    print("🔍 Testing Pattern Recognition System...")
    
    try:
        from memory.pattern_recognition import PatternRecognitionSystem
        
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        pattern_system = PatternRecognitionSystem(temp_db.name)
        
        # Test pattern extraction
        project_data = {
            "project_id": "test_project",
            "technologies": ["python", "flask"],
            "directory_structure": {
                "models": {"user.py": None},
                "views": {"user_view.py": None}
            },
            "files": ["app.py", "requirements.txt"]
        }
        
        patterns = pattern_system.extract_patterns_from_project(project_data)
        print(f"   ✅ Extracted {len(patterns)} patterns from project")
        
        # Test pattern storage
        for pattern in patterns:
            pattern_system.store_pattern(pattern)
        
        # Test pattern stats
        stats = pattern_system.get_pattern_stats()
        print(f"   ✅ Pattern stats: {stats['total_patterns']} total patterns")
        
        # Cleanup
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_context_inheritance():
    """Test context inheritance system"""
    print("🔄 Testing Context Inheritance System...")
    
    try:
        from memory.context_inheritance import ContextInheritanceSystem
        
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        context_system = ContextInheritanceSystem(temp_db.name)
        
        # Test context version creation
        context_data = {"theme": "dark", "font_size": 14}
        version_id = context_system.create_context_version(
            context_id="test_context",
            data=context_data,
            created_by="test_user",
            change_summary="Test context"
        )
        
        print(f"   ✅ Context version created: {version_id[:8]}...")
        
        # Test context retrieval
        version = context_system.get_context_version(version_id)
        if version and version.data["theme"] == "dark":
            print("   ✅ Context retrieval successful")
        else:
            print("   ❌ Context retrieval failed")
            return False
        
        # Test inheritance stats
        stats = context_system.get_inheritance_stats()
        print(f"   ✅ Inheritance stats: {stats['total_versions']} versions")
        
        # Cleanup
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_project_relationships():
    """Test project relationship system"""
    print("🔗 Testing Project Relationship System...")
    
    try:
        from memory.project_relationships import ProjectRelationshipSystem, ProjectNode
        
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        relationship_system = ProjectRelationshipSystem(temp_db.name)
        
        # Test project creation
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
            metadata={}
        )
        
        project_id = relationship_system.add_project(project)
        print(f"   ✅ Project added: {project_id}")
        
        # Test project retrieval
        retrieved = relationship_system.get_project(project_id)
        if retrieved and retrieved.name == "Test Project":
            print("   ✅ Project retrieval successful")
        else:
            print("   ❌ Project retrieval failed")
            return False
        
        # Test relationship stats
        stats = relationship_system.get_relationship_stats()
        print(f"   ✅ Relationship stats: {stats['total_projects']} projects")
        
        # Cleanup
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Run all simple tests"""
    print("🧪 Running Simple Enhanced Memory System Tests...")
    print("=" * 60)
    
    tests = [
        test_memory_system,
        test_pattern_recognition,
        test_context_inheritance,
        test_project_relationships
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("✅ All core components are working correctly!")
        print("🎉 Step 2.3: Enhanced Memory and Context Persistence is ready!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
