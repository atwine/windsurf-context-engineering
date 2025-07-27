"""
User Workspace Rules Integration

This module provides integration with Windsurf user workspace rules,
ensuring that all learning system recommendations and workflow execution
respects user-defined coding standards, preferences, and constraints.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class UserRule:
    """Represents a single user workspace rule"""
    rule_id: str
    title: str
    content: str
    category: str  # e.g., 'coding_style', 'security', 'workflow', 'debugging'
    priority: int  # 1-10, higher = more important
    applies_to: List[str]  # file types, languages, or contexts
    enforcement_level: str  # 'strict', 'warning', 'suggestion'
    created_at: datetime
    last_updated: datetime

@dataclass
class WorkspaceRulesConfig:
    """Configuration for workspace rules integration"""
    rules_extraction_enabled: bool = True
    auto_compliance_checking: bool = True
    rule_violation_warnings: bool = True
    learning_from_violations: bool = True
    custom_rules_path: Optional[str] = None
    rule_categories: List[str] = None

    def __post_init__(self):
        if self.rule_categories is None:
            self.rule_categories = [
                'coding_style', 'security', 'workflow', 'debugging', 
                'testing', 'documentation', 'performance', 'architecture'
            ]

class UserWorkspaceRulesIntegration:
    """
    Integration system for user workspace rules with the learning framework
    
    This class extracts, parses, and integrates user-defined workspace rules
    into the learning system, ensuring all recommendations and workflow
    execution respects user preferences and constraints.
    """
    
    def __init__(self, config: WorkspaceRulesConfig, data_dir: str = "learning_data"):
        """Initialize the user workspace rules integration"""
        self.config = config
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage for extracted rules
        self.user_rules: Dict[str, UserRule] = {}
        self.rules_by_category: Dict[str, List[UserRule]] = {}
        self.rules_by_context: Dict[str, List[UserRule]] = {}
        
        # Rule extraction patterns
        self.rule_patterns = {
            'memory_rule': r'<MEMORY\[([^\]]+)\]>(.*?)</MEMORY\[([^\]]+)\]>',
            'user_rule_section': r'<user_rules>(.*?)</user_rules>',
            'rule_enforcement': r'(MUST|NEVER|ALWAYS|SHOULD|AVOID|REQUIRE)',
            'code_constraint': r'(DO NOT|NEVER|ALWAYS|MUST)',
            'workflow_rule': r'(Step-by-Step|Workflow|Process|Protocol)',
        }
        
        # Initialize rules database
        self._init_rules_database()
        
        # Extract rules from system context if available
        self._extract_workspace_rules()
        
        logger.info(f"User workspace rules integration initialized with {len(self.user_rules)} rules")
    
    def _init_rules_database(self):
        """Initialize the rules database for persistence"""
        self.rules_db_path = self.data_dir / "user_workspace_rules.json"
        
        if self.rules_db_path.exists():
            self._load_rules_from_database()
        else:
            self._create_empty_database()
    
    def _create_empty_database(self):
        """Create an empty rules database"""
        empty_db = {
            'rules': {},
            'categories': {cat: [] for cat in self.config.rule_categories},
            'contexts': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_rules': 0
            }
        }
        
        with open(self.rules_db_path, 'w', encoding='utf-8') as f:
            json.dump(empty_db, f, indent=2, ensure_ascii=False)
    
    def _load_rules_from_database(self):
        """Load existing rules from database"""
        try:
            with open(self.rules_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct UserRule objects
            for rule_id, rule_data in data.get('rules', {}).items():
                rule_data['created_at'] = datetime.fromisoformat(rule_data['created_at'])
                rule_data['last_updated'] = datetime.fromisoformat(rule_data['last_updated'])
                self.user_rules[rule_id] = UserRule(**rule_data)
            
            # Rebuild category and context indexes
            self._rebuild_indexes()
            
            logger.info(f"Loaded {len(self.user_rules)} user rules from database")
            
        except Exception as e:
            logger.error(f"Error loading rules database: {e}")
            self._create_empty_database()
    
    def _save_rules_to_database(self):
        """Save current rules to database"""
        try:
            db_data = {
                'rules': {rule_id: asdict(rule) for rule_id, rule in self.user_rules.items()},
                'categories': {cat: [rule.rule_id for rule in rules] 
                             for cat, rules in self.rules_by_category.items()},
                'contexts': {ctx: [rule.rule_id for rule in rules] 
                           for ctx, rules in self.rules_by_context.items()},
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'total_rules': len(self.user_rules)
                }
            }
            
            # Convert datetime objects to ISO strings
            for rule_data in db_data['rules'].values():
                rule_data['created_at'] = rule_data['created_at'].isoformat()
                rule_data['last_updated'] = rule_data['last_updated'].isoformat()
            
            with open(self.rules_db_path, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving rules database: {e}")
    
    def _rebuild_indexes(self):
        """Rebuild category and context indexes"""
        self.rules_by_category = {cat: [] for cat in self.config.rule_categories}
        self.rules_by_context = {}
        
        for rule in self.user_rules.values():
            # Category index
            if rule.category in self.rules_by_category:
                self.rules_by_category[rule.category].append(rule)
            
            # Context index
            for context in rule.applies_to:
                if context not in self.rules_by_context:
                    self.rules_by_context[context] = []
                self.rules_by_context[context].append(rule)
    
    def _extract_workspace_rules(self):
        """Extract user workspace rules from system context"""
        if not self.config.rules_extraction_enabled:
            return
        
        # This would be called with actual system context
        # For now, we'll create a method that can be called with context
        logger.info("Workspace rules extraction ready - call extract_rules_from_context() with system context")
    
    def extract_rules_from_context(self, system_context: str) -> int:
        """
        Extract user rules from system context (like user_rules section)
        
        Args:
            system_context: The full system context containing user rules
            
        Returns:
            Number of rules extracted
        """
        rules_extracted = 0
        
        try:
            # Extract user_rules section
            user_rules_match = re.search(self.rule_patterns['user_rule_section'], 
                                       system_context, re.DOTALL | re.IGNORECASE)
            
            if user_rules_match:
                user_rules_content = user_rules_match.group(1)
                rules_extracted += self._parse_user_rules_section(user_rules_content)
            
            # Extract memory rules
            memory_matches = re.findall(self.rule_patterns['memory_rule'], 
                                      system_context, re.DOTALL | re.IGNORECASE)
            
            for match in memory_matches:
                rule_id, content, _ = match
                rules_extracted += self._parse_memory_rule(rule_id, content)
            
            # Save extracted rules
            if rules_extracted > 0:
                self._rebuild_indexes()
                self._save_rules_to_database()
                logger.info(f"Extracted {rules_extracted} user workspace rules")
            
        except Exception as e:
            logger.error(f"Error extracting rules from context: {e}")
        
        return rules_extracted
    
    def _parse_user_rules_section(self, content: str) -> int:
        """Parse the user_rules section and extract individual rules"""
        rules_found = 0
        
        # Split by common rule delimiters
        rule_sections = re.split(r'\n\s*(?=\d+\.|\*|\-|##|###)', content)
        
        for i, section in enumerate(rule_sections):
            if not section.strip():
                continue
                
            rule = self._create_rule_from_text(
                rule_id=f"user_rule_{i+1}",
                content=section.strip(),
                category=self._categorize_rule_content(section)
            )
            
            if rule:
                self.user_rules[rule.rule_id] = rule
                rules_found += 1
        
        return rules_found
    
    def _parse_memory_rule(self, rule_id: str, content: str) -> int:
        """Parse a memory rule and extract it"""
        rule = self._create_rule_from_text(
            rule_id=f"memory_{rule_id}",
            content=content.strip(),
            category=self._categorize_rule_content(content),
            title=rule_id.replace('_', ' ').title()
        )
        
        if rule:
            self.user_rules[rule.rule_id] = rule
            return 1
        
        return 0
    
    def _create_rule_from_text(self, rule_id: str, content: str, 
                              category: str, title: str = None) -> Optional[UserRule]:
        """Create a UserRule object from text content"""
        try:
            # Extract title if not provided
            if not title:
                title_match = re.match(r'^(?:\d+\.\s*)?([^\n]+)', content)
                title = title_match.group(1).strip() if title_match else rule_id
            
            # Determine enforcement level
            enforcement_level = 'suggestion'
            if any(word in content.upper() for word in ['MUST', 'NEVER', 'ALWAYS', 'REQUIRED']):
                enforcement_level = 'strict'
            elif any(word in content.upper() for word in ['SHOULD', 'AVOID', 'PREFER']):
                enforcement_level = 'warning'
            
            # Determine priority based on enforcement words
            priority = 5  # default
            if 'CRITICAL' in content.upper() or 'MANDATORY' in content.upper():
                priority = 10
            elif enforcement_level == 'strict':
                priority = 8
            elif enforcement_level == 'warning':
                priority = 6
            
            # Determine what it applies to
            applies_to = self._extract_applies_to(content)
            
            return UserRule(
                rule_id=rule_id,
                title=title[:100],  # Limit title length
                content=content,
                category=category,
                priority=priority,
                applies_to=applies_to,
                enforcement_level=enforcement_level,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error creating rule from text: {e}")
            return None
    
    def _categorize_rule_content(self, content: str) -> str:
        """Categorize rule based on its content"""
        content_upper = content.upper()
        
        # Category keywords mapping
        category_keywords = {
            'coding_style': ['STYLE', 'FORMAT', 'NAMING', 'CONVENTION', 'INDENT'],
            'security': ['SECURITY', 'CREDENTIAL', 'API KEY', 'PASSWORD', 'AUTH'],
            'workflow': ['WORKFLOW', 'STEP', 'PROCESS', 'SEQUENCE', 'ORDER'],
            'debugging': ['DEBUG', 'ERROR', 'EXCEPTION', 'LOG', 'TRACE'],
            'testing': ['TEST', 'UNIT', 'INTEGRATION', 'COVERAGE', 'ASSERT'],
            'documentation': ['DOCUMENT', 'COMMENT', 'README', 'DOC', 'EXPLAIN'],
            'performance': ['PERFORMANCE', 'OPTIMIZE', 'SPEED', 'MEMORY', 'EFFICIENT'],
            'architecture': ['ARCHITECTURE', 'DESIGN', 'PATTERN', 'STRUCTURE', 'MODULE']
        }
        
        # Find best matching category
        best_category = 'workflow'  # default
        best_score = 0
        
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_upper)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def _extract_applies_to(self, content: str) -> List[str]:
        """Extract what contexts/languages this rule applies to"""
        applies_to = ['general']  # default
        
        # Common programming languages and contexts
        contexts = [
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust',
            'html', 'css', 'sql', 'bash', 'powershell', 'yaml', 'json', 'xml',
            'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express',
            'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'testing', 'deployment', 'ci/cd', 'database', 'api', 'frontend', 'backend'
        ]
        
        content_lower = content.lower()
        found_contexts = [ctx for ctx in contexts if ctx in content_lower]
        
        if found_contexts:
            applies_to = found_contexts
        
        return applies_to
    
    def get_applicable_rules(self, context: str = None, 
                           category: str = None, 
                           enforcement_level: str = None) -> List[UserRule]:
        """Get rules applicable to a specific context or category"""
        applicable_rules = []
        
        # Start with all rules
        candidate_rules = list(self.user_rules.values())
        
        # Filter by context
        if context:
            candidate_rules = [rule for rule in candidate_rules 
                             if context in rule.applies_to or 'general' in rule.applies_to]
        
        # Filter by category
        if category:
            candidate_rules = [rule for rule in candidate_rules if rule.category == category]
        
        # Filter by enforcement level
        if enforcement_level:
            candidate_rules = [rule for rule in candidate_rules 
                             if rule.enforcement_level == enforcement_level]
        
        # Sort by priority (highest first)
        applicable_rules = sorted(candidate_rules, key=lambda r: r.priority, reverse=True)
        
        return applicable_rules
    
    def check_compliance(self, code_content: str, context: str = None) -> Dict[str, Any]:
        """Check code compliance against user workspace rules"""
        if not self.config.auto_compliance_checking:
            return {'compliant': True, 'violations': [], 'warnings': []}
        
        applicable_rules = self.get_applicable_rules(context=context)
        violations = []
        warnings = []
        suggestions = []
        
        for rule in applicable_rules:
            violation_result = self._check_rule_violation(code_content, rule)
            
            if violation_result['violated']:
                violation_info = {
                    'rule_id': rule.rule_id,
                    'rule_title': rule.title,
                    'enforcement_level': rule.enforcement_level,
                    'priority': rule.priority,
                    'violation_details': violation_result['details'],
                    'suggested_fix': violation_result.get('suggested_fix', '')
                }
                
                if rule.enforcement_level == 'strict':
                    violations.append(violation_info)
                elif rule.enforcement_level == 'warning':
                    warnings.append(violation_info)
                else:
                    suggestions.append(violation_info)
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'suggestions': suggestions,
            'total_rules_checked': len(applicable_rules)
        }
    
    def _check_rule_violation(self, code_content: str, rule: UserRule) -> Dict[str, Any]:
        """Check if code violates a specific rule"""
        # This is a simplified implementation
        # In practice, this would use more sophisticated analysis
        
        violation_patterns = {
            'NEVER': r'(?i)' + rule.content.split('NEVER')[1].split()[0] if 'NEVER' in rule.content else None,
            'MUST': r'(?i)' + rule.content.split('MUST')[1].split()[0] if 'MUST' in rule.content else None,
            'ALWAYS': r'(?i)' + rule.content.split('ALWAYS')[1].split()[0] if 'ALWAYS' in rule.content else None,
        }
        
        for pattern_type, pattern in violation_patterns.items():
            if pattern and re.search(pattern, code_content):
                return {
                    'violated': True,
                    'details': f"Code violates rule: {rule.title}",
                    'pattern_matched': pattern_type,
                    'suggested_fix': f"Please review and fix according to rule: {rule.title}"
                }
        
        return {'violated': False}
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Get a summary of all user workspace rules"""
        return {
            'total_rules': len(self.user_rules),
            'rules_by_category': {cat: len(rules) for cat, rules in self.rules_by_category.items()},
            'rules_by_enforcement': {
                'strict': len([r for r in self.user_rules.values() if r.enforcement_level == 'strict']),
                'warning': len([r for r in self.user_rules.values() if r.enforcement_level == 'warning']),
                'suggestion': len([r for r in self.user_rules.values() if r.enforcement_level == 'suggestion'])
            },
            'high_priority_rules': len([r for r in self.user_rules.values() if r.priority >= 8]),
            'contexts_covered': list(self.rules_by_context.keys())
        }
    
    def add_custom_rule(self, title: str, content: str, category: str, 
                       applies_to: List[str] = None, priority: int = 5,
                       enforcement_level: str = 'suggestion') -> str:
        """Add a custom user rule"""
        rule_id = f"custom_{len(self.user_rules) + 1}"
        
        rule = UserRule(
            rule_id=rule_id,
            title=title,
            content=content,
            category=category,
            priority=priority,
            applies_to=applies_to or ['general'],
            enforcement_level=enforcement_level,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.user_rules[rule_id] = rule
        self._rebuild_indexes()
        self._save_rules_to_database()
        
        logger.info(f"Added custom rule: {title}")
        return rule_id
    
    def update_rule(self, rule_id: str, **updates) -> bool:
        """Update an existing rule"""
        if rule_id not in self.user_rules:
            return False
        
        rule = self.user_rules[rule_id]
        
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        rule.last_updated = datetime.now()
        
        self._rebuild_indexes()
        self._save_rules_to_database()
        
        logger.info(f"Updated rule: {rule_id}")
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule"""
        if rule_id not in self.user_rules:
            return False
        
        del self.user_rules[rule_id]
        self._rebuild_indexes()
        self._save_rules_to_database()
        
        logger.info(f"Removed rule: {rule_id}")
        return True


# Factory function for easy integration
def create_workspace_rules_integration(data_dir: str = "learning_data", 
                                     config_overrides: Dict[str, Any] = None) -> UserWorkspaceRulesIntegration:
    """Create and configure a workspace rules integration instance"""
    config = WorkspaceRulesConfig()
    
    if config_overrides:
        for key, value in config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    return UserWorkspaceRulesIntegration(config, data_dir)


if __name__ == "__main__":
    # Example usage
    rules_integration = create_workspace_rules_integration("test_learning_data")
    
    # Example system context with user rules
    example_context = """
    <user_rules>
    1. NEVER use hardcoded API keys or credentials in code
    2. ALWAYS use type hints for function parameters and return values
    3. Code must be immediately runnable with all necessary imports
    4. Follow PEP 8 style guidelines for Python code
    5. Use meaningful commit messages and maintain clean git history
    </user_rules>
    
    <MEMORY[debugging-rule]>
    When debugging, only make code changes if you are certain that you can solve the problem.
    Otherwise, follow debugging best practices:
    1. Address the root cause instead of the symptoms.
    2. Add descriptive logging statements and error messages.
    </MEMORY[debugging-rule]>
    """
    
    # Extract rules from context
    extracted_count = rules_integration.extract_rules_from_context(example_context)
    print(f"Extracted {extracted_count} rules")
    
    # Get rules summary
    summary = rules_integration.get_rules_summary()
    print(f"Rules summary: {summary}")
    
    # Check compliance example
    example_code = """
    def process_data(data):
        api_key = "sk-1234567890abcdef"  # This violates the hardcoded credentials rule
        return data.upper()
    """
    
    compliance = rules_integration.check_compliance(example_code, context="python")
    print(f"Compliance check: {compliance}")
