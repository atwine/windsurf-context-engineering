"""
Context Inheritance and Persistence System

This module implements context inheritance rules, merging algorithms, conflict resolution,
versioning, and rollback capabilities for maintaining context across projects and sessions.
"""

import json
import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import copy
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of context that can be inherited"""
    PROJECT_SETTINGS = "project_settings"
    USER_PREFERENCES = "user_preferences"
    TOOL_CONFIGURATIONS = "tool_configurations"
    ARCHITECTURAL_DECISIONS = "architectural_decisions"
    CODING_PATTERNS = "coding_patterns"
    DEPLOYMENT_CONFIGS = "deployment_configs"

class ConflictResolution(Enum):
    """Strategies for resolving context conflicts"""
    MERGE = "merge"
    OVERRIDE = "override"
    PRESERVE = "preserve"
    PROMPT_USER = "prompt_user"

@dataclass
class ContextVersion:
    """Represents a version of context data"""
    version_id: str
    context_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    created_by: str
    change_summary: str
    parent_version: Optional[str] = None

@dataclass
class ContextInheritanceRule:
    """Rules for how context should be inherited"""
    rule_id: str
    name: str
    source_context_type: ContextType
    target_context_type: ContextType
    inheritance_strategy: str  # "full", "partial", "selective"
    merge_strategy: ConflictResolution
    conditions: Dict[str, Any]
    priority: int
    active: bool = True

@dataclass
class ContextSnapshot:
    """Snapshot of context at a specific point in time"""
    snapshot_id: str
    context_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    description: str

class ContextInheritanceSystem:
    """
    System for managing context inheritance, versioning, and persistence
    """
    
    def __init__(self, db_path: str = "memory/context_inheritance.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Default inheritance rules
        self.default_rules = [
            ContextInheritanceRule(
                rule_id="user_prefs_inherit",
                name="User Preferences Inheritance",
                source_context_type=ContextType.USER_PREFERENCES,
                target_context_type=ContextType.PROJECT_SETTINGS,
                inheritance_strategy="selective",
                merge_strategy=ConflictResolution.MERGE,
                conditions={"inherit_user_prefs": True},
                priority=1
            ),
            ContextInheritanceRule(
                rule_id="tool_config_inherit",
                name="Tool Configuration Inheritance",
                source_context_type=ContextType.TOOL_CONFIGURATIONS,
                target_context_type=ContextType.PROJECT_SETTINGS,
                inheritance_strategy="partial",
                merge_strategy=ConflictResolution.OVERRIDE,
                conditions={"same_technology_stack": True},
                priority=2
            )
        ]
        
        self._init_database()
        self._load_default_rules()
        logger.info("Context Inheritance System initialized")
    
    def _init_database(self):
        """Initialize the context inheritance database"""
        with sqlite3.connect(self.db_path) as conn:
            # Context versions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_versions (
                    version_id TEXT PRIMARY KEY,
                    context_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP,
                    created_by TEXT,
                    change_summary TEXT,
                    parent_version TEXT,
                    FOREIGN KEY (parent_version) REFERENCES context_versions(version_id)
                )
            """)
            
            # Inheritance rules table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS inheritance_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_context_type TEXT,
                    target_context_type TEXT,
                    inheritance_strategy TEXT,
                    merge_strategy TEXT,
                    conditions TEXT,
                    priority INTEGER,
                    active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Context snapshots table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    context_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP,
                    description TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_context_id ON context_versions(context_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON context_versions(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rule_priority ON inheritance_rules(priority)")
    
    def _load_default_rules(self):
        """Load default inheritance rules"""
        with sqlite3.connect(self.db_path) as conn:
            for rule in self.default_rules:
                conn.execute("""
                    INSERT OR IGNORE INTO inheritance_rules VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule.rule_id, rule.name, rule.source_context_type.value,
                    rule.target_context_type.value, rule.inheritance_strategy,
                    rule.merge_strategy.value, json.dumps(rule.conditions),
                    rule.priority, rule.active
                ))
    
    def create_context_version(self, 
                             context_id: str,
                             data: Dict[str, Any],
                             created_by: str,
                             change_summary: str,
                             metadata: Dict[str, Any] = None,
                             parent_version: str = None) -> str:
        """Create a new version of context data"""
        
        if metadata is None:
            metadata = {}
        
        version_id = hashlib.md5(f"{context_id}_{time.time()}".encode()).hexdigest()
        
        version = ContextVersion(
            version_id=version_id,
            context_id=context_id,
            data=data,
            metadata=metadata,
            created_at=datetime.now(),
            created_by=created_by,
            change_summary=change_summary,
            parent_version=parent_version
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO context_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version.version_id, version.context_id, json.dumps(version.data),
                json.dumps(version.metadata), version.created_at.isoformat(),
                version.created_by, version.change_summary, version.parent_version
            ))
        
        logger.info(f"Created context version: {version_id} for context: {context_id}")
        return version_id
    
    def get_context_version(self, version_id: str) -> Optional[ContextVersion]:
        """Retrieve a specific context version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM context_versions WHERE version_id = ?
            """, (version_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ContextVersion(
                version_id=row[0],
                context_id=row[1],
                data=json.loads(row[2]),
                metadata=json.loads(row[3]) if row[3] else {},
                created_at=datetime.fromisoformat(row[4]),
                created_by=row[5],
                change_summary=row[6],
                parent_version=row[7]
            )
    
    def get_latest_context_version(self, context_id: str) -> Optional[ContextVersion]:
        """Get the latest version of a context"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM context_versions 
                WHERE context_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (context_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ContextVersion(
                version_id=row[0],
                context_id=row[1],
                data=json.loads(row[2]),
                metadata=json.loads(row[3]) if row[3] else {},
                created_at=datetime.fromisoformat(row[4]),
                created_by=row[5],
                change_summary=row[6],
                parent_version=row[7]
            )
    
    def inherit_context(self, 
                       source_context_id: str,
                       target_context_id: str,
                       inheritance_rules: List[str] = None) -> Dict[str, Any]:
        """Inherit context from source to target using specified rules"""
        
        # Get source context
        source_version = self.get_latest_context_version(source_context_id)
        if not source_version:
            logger.warning(f"Source context not found: {source_context_id}")
            return {}
        
        # Get target context (if exists)
        target_version = self.get_latest_context_version(target_context_id)
        target_data = target_version.data if target_version else {}
        
        # Get applicable inheritance rules
        if inheritance_rules is None:
            rules = self._get_applicable_rules(source_version.data, target_data)
        else:
            rules = [self._get_rule_by_id(rule_id) for rule_id in inheritance_rules]
            rules = [rule for rule in rules if rule is not None]
        
        # Apply inheritance rules
        inherited_data = copy.deepcopy(target_data)
        
        for rule in sorted(rules, key=lambda r: r.priority):
            if not rule.active:
                continue
            
            # Check if rule conditions are met
            if not self._check_rule_conditions(rule, source_version.data, target_data):
                continue
            
            # Apply inheritance based on strategy
            if rule.inheritance_strategy == "full":
                inherited_data = self._merge_contexts(
                    inherited_data, source_version.data, rule.merge_strategy
                )
            elif rule.inheritance_strategy == "partial":
                partial_data = self._extract_partial_context(source_version.data, rule)
                inherited_data = self._merge_contexts(
                    inherited_data, partial_data, rule.merge_strategy
                )
            elif rule.inheritance_strategy == "selective":
                selective_data = self._extract_selective_context(source_version.data, rule)
                inherited_data = self._merge_contexts(
                    inherited_data, selective_data, rule.merge_strategy
                )
        
        return inherited_data
    
    def _get_applicable_rules(self, source_data: Dict[str, Any], target_data: Dict[str, Any]) -> List[ContextInheritanceRule]:
        """Get inheritance rules applicable to the given context data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM inheritance_rules 
                WHERE active = TRUE 
                ORDER BY priority
            """)
            
            rules = []
            for row in cursor.fetchall():
                rule = ContextInheritanceRule(
                    rule_id=row[0],
                    name=row[1],
                    source_context_type=ContextType(row[2]),
                    target_context_type=ContextType(row[3]),
                    inheritance_strategy=row[4],
                    merge_strategy=ConflictResolution(row[5]),
                    conditions=json.loads(row[6]),
                    priority=row[7],
                    active=row[8]
                )
                rules.append(rule)
            
            return rules
    
    def _get_rule_by_id(self, rule_id: str) -> Optional[ContextInheritanceRule]:
        """Get a specific inheritance rule by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM inheritance_rules WHERE rule_id = ?
            """, (rule_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ContextInheritanceRule(
                rule_id=row[0],
                name=row[1],
                source_context_type=ContextType(row[2]),
                target_context_type=ContextType(row[3]),
                inheritance_strategy=row[4],
                merge_strategy=ConflictResolution(row[5]),
                conditions=json.loads(row[6]),
                priority=row[7],
                active=row[8]
            )
    
    def _check_rule_conditions(self, rule: ContextInheritanceRule, source_data: Dict[str, Any], target_data: Dict[str, Any]) -> bool:
        """Check if rule conditions are satisfied"""
        for condition, expected_value in rule.conditions.items():
            if condition == "inherit_user_prefs":
                if not source_data.get("user_preferences", {}).get("inherit_to_projects", False):
                    return False
            elif condition == "same_technology_stack":
                source_tech = set(source_data.get("technologies", []))
                target_tech = set(target_data.get("technologies", []))
                if not source_tech.intersection(target_tech):
                    return False
        
        return True
    
    def _merge_contexts(self, target: Dict[str, Any], source: Dict[str, Any], strategy: ConflictResolution) -> Dict[str, Any]:
        """Merge source context into target context using specified strategy"""
        if strategy == ConflictResolution.OVERRIDE:
            # Source completely overrides target
            return copy.deepcopy(source)
        
        elif strategy == ConflictResolution.PRESERVE:
            # Target is preserved, only add new keys from source
            result = copy.deepcopy(target)
            for key, value in source.items():
                if key not in result:
                    result[key] = copy.deepcopy(value)
            return result
        
        elif strategy == ConflictResolution.MERGE:
            # Intelligent merge of both contexts
            result = copy.deepcopy(target)
            for key, value in source.items():
                if key not in result:
                    result[key] = copy.deepcopy(value)
                elif isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_contexts(result[key], value, strategy)
                elif isinstance(value, list) and isinstance(result[key], list):
                    # Merge lists, avoiding duplicates
                    result[key] = list(set(result[key] + value))
            return result
        
        else:  # PROMPT_USER - for now, default to MERGE
            return self._merge_contexts(target, source, ConflictResolution.MERGE)
    
    def _extract_partial_context(self, source_data: Dict[str, Any], rule: ContextInheritanceRule) -> Dict[str, Any]:
        """Extract partial context based on rule configuration"""
        # Define what constitutes "partial" for each context type
        partial_keys = {
            ContextType.USER_PREFERENCES: ["editor_settings", "code_style", "shortcuts"],
            ContextType.TOOL_CONFIGURATIONS: ["linting_rules", "formatting_config"],
            ContextType.PROJECT_SETTINGS: ["build_settings", "test_config"]
        }
        
        keys_to_extract = partial_keys.get(rule.source_context_type, [])
        return {key: source_data[key] for key in keys_to_extract if key in source_data}
    
    def _extract_selective_context(self, source_data: Dict[str, Any], rule: ContextInheritanceRule) -> Dict[str, Any]:
        """Extract selective context based on rule configuration"""
        # Define selective extraction rules
        selective_rules = {
            ContextType.USER_PREFERENCES: lambda data: {
                key: value for key, value in data.items() 
                if key in ["theme", "font_size", "auto_save"] and data.get("inherit_to_projects", False)
            }
        }
        
        extractor = selective_rules.get(rule.source_context_type)
        if extractor:
            return extractor(source_data)
        
        return {}
    
    def create_snapshot(self, context_id: str, description: str) -> str:
        """Create a snapshot of current context state"""
        latest_version = self.get_latest_context_version(context_id)
        if not latest_version:
            logger.warning(f"No context found for snapshot: {context_id}")
            return ""
        
        snapshot_id = hashlib.md5(f"snapshot_{context_id}_{time.time()}".encode()).hexdigest()
        
        snapshot = ContextSnapshot(
            snapshot_id=snapshot_id,
            context_id=context_id,
            data=latest_version.data,
            metadata=latest_version.metadata,
            created_at=datetime.now(),
            description=description
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO context_snapshots VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snapshot.snapshot_id, snapshot.context_id, json.dumps(snapshot.data),
                json.dumps(snapshot.metadata), snapshot.created_at.isoformat(),
                snapshot.description
            ))
        
        logger.info(f"Created snapshot: {snapshot_id} for context: {context_id}")
        return snapshot_id
    
    def rollback_to_version(self, context_id: str, version_id: str, created_by: str) -> str:
        """Rollback context to a specific version"""
        target_version = self.get_context_version(version_id)
        if not target_version or target_version.context_id != context_id:
            logger.error(f"Invalid version for rollback: {version_id}")
            return ""
        
        # Create new version with rollback data
        new_version_id = self.create_context_version(
            context_id=context_id,
            data=target_version.data,
            created_by=created_by,
            change_summary=f"Rollback to version {version_id}",
            metadata={"rollback_from": version_id},
            parent_version=self.get_latest_context_version(context_id).version_id
        )
        
        logger.info(f"Rolled back context {context_id} to version {version_id}")
        return new_version_id
    
    def get_context_history(self, context_id: str, limit: int = 10) -> List[ContextVersion]:
        """Get version history for a context"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM context_versions 
                WHERE context_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (context_id, limit))
            
            versions = []
            for row in cursor.fetchall():
                version = ContextVersion(
                    version_id=row[0],
                    context_id=row[1],
                    data=json.loads(row[2]),
                    metadata=json.loads(row[3]) if row[3] else {},
                    created_at=datetime.fromisoformat(row[4]),
                    created_by=row[5],
                    change_summary=row[6],
                    parent_version=row[7]
                )
                versions.append(version)
            
            return versions
    
    def get_inheritance_stats(self) -> Dict[str, Any]:
        """Get context inheritance system statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total versions
            cursor = conn.execute("SELECT COUNT(*) FROM context_versions")
            stats["total_versions"] = cursor.fetchone()[0]
            
            # Unique contexts
            cursor = conn.execute("SELECT COUNT(DISTINCT context_id) FROM context_versions")
            stats["unique_contexts"] = cursor.fetchone()[0]
            
            # Active rules
            cursor = conn.execute("SELECT COUNT(*) FROM inheritance_rules WHERE active = TRUE")
            stats["active_rules"] = cursor.fetchone()[0]
            
            # Snapshots
            cursor = conn.execute("SELECT COUNT(*) FROM context_snapshots")
            stats["total_snapshots"] = cursor.fetchone()[0]
            
            return stats

def main():
    """Test the context inheritance system"""
    inheritance_system = ContextInheritanceSystem()
    
    # Create test contexts
    user_prefs = {
        "theme": "dark",
        "font_size": 14,
        "auto_save": True,
        "inherit_to_projects": True,
        "user_preferences": {"inherit_to_projects": True}
    }
    
    project_settings = {
        "name": "test_project",
        "technologies": ["python", "flask"],
        "build_tool": "pip"
    }
    
    # Create context versions
    user_version = inheritance_system.create_context_version(
        context_id="user_global",
        data=user_prefs,
        created_by="user",
        change_summary="Initial user preferences"
    )
    
    project_version = inheritance_system.create_context_version(
        context_id="project_test",
        data=project_settings,
        created_by="user",
        change_summary="Initial project settings"
    )
    
    # Test inheritance
    inherited_data = inheritance_system.inherit_context("user_global", "project_test")
    print(f"Inherited data: {inherited_data}")
    
    # Create snapshot
    snapshot_id = inheritance_system.create_snapshot("project_test", "Before major changes")
    print(f"Created snapshot: {snapshot_id}")
    
    # Get stats
    stats = inheritance_system.get_inheritance_stats()
    print(f"Inheritance stats: {stats}")

if __name__ == "__main__":
    main()
