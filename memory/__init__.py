"""
Enhanced Memory and Context Persistence System

This package provides comprehensive memory management, pattern recognition,
context inheritance, and project relationship mapping capabilities.
"""

from .enhanced_memory_system import EnhancedMemorySystem, MemoryEntry
from .pattern_recognition import PatternRecognitionSystem, ProjectPattern, PatternMatch
from .context_inheritance import ContextInheritanceSystem, ContextType, ConflictResolution
from .project_relationships import ProjectRelationshipSystem, ProjectNode, ProjectRelationship

__version__ = "2.3.0"
__author__ = "Windsurf Context Engineering Team"

__all__ = [
    # Enhanced Memory System
    "EnhancedMemorySystem",
    "MemoryEntry",
    
    # Pattern Recognition
    "PatternRecognitionSystem", 
    "ProjectPattern",
    "PatternMatch",
    
    # Context Inheritance
    "ContextInheritanceSystem",
    "ContextType",
    "ConflictResolution",
    
    # Project Relationships
    "ProjectRelationshipSystem",
    "ProjectNode", 
    "ProjectRelationship"
]
