"""
Enhanced Workflow Learning with User Workspace Rules Integration

This module extends the workflow learning system to integrate user workspace rules,
ensuring all learning recommendations and workflow execution respects user-defined
coding standards, preferences, and constraints.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from .user_workspace_integration import UserWorkspaceRulesIntegration, WorkspaceRulesConfig
from .learning_integration import LearningSystemIntegration, LearningSystemConfig

logger = logging.getLogger(__name__)

@dataclass
class EnhancedWorkflowContext:
    """Enhanced workflow context that includes user workspace rules"""
    workflow_name: str
    project_context: Dict[str, Any]
    user_rules_summary: Dict[str, Any]
    applicable_rules: List[Dict[str, Any]]
    compliance_requirements: Dict[str, Any]
    learning_recommendations: List[Dict[str, Any]]
    created_at: datetime

@dataclass
class RuleAwareRecommendation:
    """Learning recommendation that considers user workspace rules"""
    recommendation_id: str
    title: str
    description: str
    confidence: float
    category: str
    rule_compliance: Dict[str, Any]  # Which rules this recommendation follows/violates
    implementation_guidance: str
    priority_adjustment: float  # Adjustment based on rule compliance
    created_at: datetime

class EnhancedWorkflowLearning:
    """
    Enhanced workflow learning system with user workspace rules integration
    
    This class combines the learning system with user workspace rules to provide
    intelligent, rule-aware recommendations and workflow execution guidance.
    """
    
    def __init__(self, learning_config: LearningSystemConfig, 
                 rules_config: WorkspaceRulesConfig = None,
                 data_dir: str = "learning_data"):
        """Initialize the enhanced workflow learning system"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize core learning system
        self.learning_system = LearningSystemIntegration(learning_config)
        
        # Initialize user workspace rules integration
        if rules_config is None:
            rules_config = WorkspaceRulesConfig()
        self.rules_integration = UserWorkspaceRulesIntegration(rules_config, str(self.data_dir))
        
        # Enhanced workflow contexts storage
        self.workflow_contexts: Dict[str, EnhancedWorkflowContext] = {}
        self.rule_aware_recommendations: Dict[str, List[RuleAwareRecommendation]] = {}
        
        # Integration state
        self.system_context_extracted = False
        self.last_rules_update = None
        
        logger.info("Enhanced workflow learning system initialized")
    
    def extract_system_context_rules(self, system_context: str) -> int:
        """
        Extract user workspace rules from system context
        
        Args:
            system_context: Full system context including user_rules section
            
        Returns:
            Number of rules extracted
        """
        try:
            extracted_count = self.rules_integration.extract_rules_from_context(system_context)
            
            if extracted_count > 0:
                self.system_context_extracted = True
                self.last_rules_update = datetime.now()
                
                logger.info(f"Extracted {extracted_count} user workspace rules from system context")
                
                # Update all existing workflow contexts with new rules
                self._update_existing_contexts_with_rules()
            
            return extracted_count
            
        except Exception as e:
            logger.error(f"Error extracting system context rules: {e}")
            return 0
    
    def _update_existing_contexts_with_rules(self):
        """Update existing workflow contexts with newly extracted rules"""
        for workflow_name, context in self.workflow_contexts.items():
            # Update applicable rules
            context.applicable_rules = self._get_applicable_rules_for_context(
                context.project_context
            )
            
            # Update compliance requirements
            context.compliance_requirements = self._get_compliance_requirements(
                context.project_context
            )
            
            # Update user rules summary
            context.user_rules_summary = self.rules_integration.get_rules_summary()
    
    def start_enhanced_workflow(self, workflow_name: str, 
                              project_context: Dict[str, Any] = None,
                              system_context: str = None) -> EnhancedWorkflowContext:
        """
        Start an enhanced workflow with user workspace rules integration
        
        Args:
            workflow_name: Name of the workflow being started
            project_context: Context about the current project
            system_context: Full system context (for rule extraction)
            
        Returns:
            Enhanced workflow context with rule integration
        """
        try:
            # Extract rules from system context if provided
            if system_context and not self.system_context_extracted:
                self.extract_system_context_rules(system_context)
            
            # Start the core learning workflow
            # Backward-compatibility shim: older LearningSystemIntegration may not define start_workflow
            if hasattr(self.learning_system, "start_workflow"):
                self.learning_system.start_workflow(workflow_name, project_context or {})
            else:
                logger.debug(
                    "LearningSystemIntegration.start_workflow not found; proceeding without base workflow start for backward compatibility"
                )
            
            # Create enhanced workflow context
            enhanced_context = EnhancedWorkflowContext(
                workflow_name=workflow_name,
                project_context=project_context or {},
                user_rules_summary=self.rules_integration.get_rules_summary(),
                applicable_rules=self._get_applicable_rules_for_context(project_context or {}),
                compliance_requirements=self._get_compliance_requirements(project_context or {}),
                learning_recommendations=[],
                created_at=datetime.now()
            )
            
            # Store the enhanced context
            self.workflow_contexts[workflow_name] = enhanced_context
            
            logger.info(f"Started enhanced workflow: {workflow_name} with {len(enhanced_context.applicable_rules)} applicable rules")
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Error starting enhanced workflow: {e}")
            # Fallback to basic workflow
            # Backward-compatibility shim: call only if available
            if hasattr(self.learning_system, "start_workflow"):
                self.learning_system.start_workflow(workflow_name, project_context or {})
            return self._create_fallback_context(workflow_name, project_context or {})
    
    def _create_fallback_context(self, workflow_name: str, 
                                project_context: Dict[str, Any]) -> EnhancedWorkflowContext:
        """Create a fallback context when enhanced features fail"""
        return EnhancedWorkflowContext(
            workflow_name=workflow_name,
            project_context=project_context,
            user_rules_summary={'total_rules': 0, 'rules_by_category': {}},
            applicable_rules=[],
            compliance_requirements={},
            learning_recommendations=[],
            created_at=datetime.now()
        )
    
    def _get_applicable_rules_for_context(self, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get user workspace rules applicable to the current project context"""
        try:
            # Determine context from project information
            context_hints = []
            
            # Extract technology stack
            if 'technologies' in project_context:
                context_hints.extend(project_context['technologies'])
            
            if 'language' in project_context:
                context_hints.append(project_context['language'])
            
            if 'framework' in project_context:
                context_hints.append(project_context['framework'])
            
            # Get applicable rules for each context
            applicable_rules = []
            contexts_to_check = context_hints + ['general']
            
            for context in contexts_to_check:
                rules = self.rules_integration.get_applicable_rules(context=context)
                for rule in rules:
                    rule_dict = asdict(rule)
                    rule_dict['created_at'] = rule_dict['created_at'].isoformat()
                    rule_dict['last_updated'] = rule_dict['last_updated'].isoformat()
                    
                    # Avoid duplicates
                    if not any(r['rule_id'] == rule_dict['rule_id'] for r in applicable_rules):
                        applicable_rules.append(rule_dict)
            
            return applicable_rules
            
        except Exception as e:
            logger.error(f"Error getting applicable rules: {e}")
            return []
    
    def _get_compliance_requirements(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get compliance requirements based on applicable rules"""
        try:
            applicable_rules = self._get_applicable_rules_for_context(project_context)
            
            requirements = {
                'strict_rules': [],
                'warning_rules': [],
                'suggestion_rules': [],
                'categories_covered': set(),
                'high_priority_count': 0,
                'must_comply': [],
                'should_comply': [],
                'nice_to_have': []
            }
            
            for rule in applicable_rules:
                requirements['categories_covered'].add(rule['category'])
                
                if rule['enforcement_level'] == 'strict':
                    requirements['strict_rules'].append(rule['rule_id'])
                    requirements['must_comply'].append({
                        'rule_id': rule['rule_id'],
                        'title': rule['title'],
                        'priority': rule['priority']
                    })
                elif rule['enforcement_level'] == 'warning':
                    requirements['warning_rules'].append(rule['rule_id'])
                    requirements['should_comply'].append({
                        'rule_id': rule['rule_id'],
                        'title': rule['title'],
                        'priority': rule['priority']
                    })
                else:
                    requirements['suggestion_rules'].append(rule['rule_id'])
                    requirements['nice_to_have'].append({
                        'rule_id': rule['rule_id'],
                        'title': rule['title'],
                        'priority': rule['priority']
                    })
                
                if rule['priority'] >= 8:
                    requirements['high_priority_count'] += 1
            
            requirements['categories_covered'] = list(requirements['categories_covered'])
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error getting compliance requirements: {e}")
            return {}
    
    def get_rule_aware_recommendations(self, workflow_name: str, 
                                     current_context: Dict[str, Any] = None) -> List[RuleAwareRecommendation]:
        """
        Get learning recommendations that are aware of user workspace rules
        
        Args:
            workflow_name: Name of the workflow
            current_context: Current execution context
            
        Returns:
            List of rule-aware recommendations
        """
        try:
            # Get base learning recommendations
            # Backward-compatibility shim: map to get_project_recommendations if get_recommendations is unavailable
            if hasattr(self.learning_system, "get_recommendations"):
                base_recommendations = self.learning_system.get_recommendations(workflow_name, current_context)
            else:
                base_recommendations = self.learning_system.get_project_recommendations(current_context or {})
            
            # Get workflow context
            workflow_context = self.workflow_contexts.get(workflow_name)
            if not workflow_context:
                logger.warning(f"No enhanced context found for workflow: {workflow_name}")
                return self._convert_base_recommendations(base_recommendations)
            
            # Enhance recommendations with rule awareness
            rule_aware_recommendations = []
            
            for i, base_rec in enumerate(base_recommendations):
                # Analyze rule compliance for this recommendation
                rule_compliance = self._analyze_recommendation_compliance(
                    base_rec, workflow_context.applicable_rules
                )
                
                # Adjust priority based on rule compliance
                priority_adjustment = self._calculate_priority_adjustment(rule_compliance)
                
                # Create rule-aware recommendation
                enhanced_rec = RuleAwareRecommendation(
                    recommendation_id=f"{workflow_name}_rec_{i+1}",
                    title=base_rec.get('title', 'Learning Recommendation'),
                    description=base_rec.get('description', ''),
                    confidence=base_rec.get('confidence', 0.5),
                    category=base_rec.get('category', 'general'),
                    rule_compliance=rule_compliance,
                    implementation_guidance=self._generate_rule_aware_guidance(
                        base_rec, rule_compliance, workflow_context.applicable_rules
                    ),
                    priority_adjustment=priority_adjustment,
                    created_at=datetime.now()
                )
                
                rule_aware_recommendations.append(enhanced_rec)
            
            # Store recommendations
            self.rule_aware_recommendations[workflow_name] = rule_aware_recommendations
            
            # Sort by adjusted confidence (confidence + priority_adjustment)
            rule_aware_recommendations.sort(
                key=lambda r: r.confidence + r.priority_adjustment, 
                reverse=True
            )
            
            return rule_aware_recommendations
            
        except Exception as e:
            logger.error(f"Error getting rule-aware recommendations: {e}")
            # Fallback to base recommendations
            if hasattr(self.learning_system, "get_recommendations"):
                base_recommendations = self.learning_system.get_recommendations(workflow_name, current_context)
            else:
                base_recommendations = self.learning_system.get_project_recommendations(current_context or {})
            return self._convert_base_recommendations(base_recommendations)
    
    def _convert_base_recommendations(self, base_recommendations: List[Dict[str, Any]]) -> List[RuleAwareRecommendation]:
        """Convert base recommendations to rule-aware format (fallback)"""
        converted = []
        
        for i, base_rec in enumerate(base_recommendations):
            converted.append(RuleAwareRecommendation(
                recommendation_id=f"fallback_rec_{i+1}",
                title=base_rec.get('title', 'Learning Recommendation'),
                description=base_rec.get('description', ''),
                confidence=base_rec.get('confidence', 0.5),
                category=base_rec.get('category', 'general'),
                rule_compliance={'compliant': True, 'violations': [], 'warnings': []},
                implementation_guidance=base_rec.get('description', ''),
                priority_adjustment=0.0,
                created_at=datetime.now()
            ))
        
        return converted
    
    def _analyze_recommendation_compliance(self, recommendation: Dict[str, Any], 
                                         applicable_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well a recommendation complies with user workspace rules"""
        compliance = {
            'compliant': True,
            'violations': [],
            'warnings': [],
            'suggestions': [],
            'supporting_rules': [],
            'conflicting_rules': []
        }
        
        try:
            rec_content = f"{recommendation.get('title', '')} {recommendation.get('description', '')}"
            
            for rule in applicable_rules:
                # Check if recommendation conflicts with rule
                conflict_result = self._check_recommendation_rule_conflict(rec_content, rule)
                
                if conflict_result['conflicts']:
                    if rule['enforcement_level'] == 'strict':
                        compliance['violations'].append({
                            'rule_id': rule['rule_id'],
                            'rule_title': rule['title'],
                            'conflict_reason': conflict_result['reason']
                        })
                        compliance['compliant'] = False
                    elif rule['enforcement_level'] == 'warning':
                        compliance['warnings'].append({
                            'rule_id': rule['rule_id'],
                            'rule_title': rule['title'],
                            'conflict_reason': conflict_result['reason']
                        })
                    else:
                        compliance['suggestions'].append({
                            'rule_id': rule['rule_id'],
                            'rule_title': rule['title'],
                            'conflict_reason': conflict_result['reason']
                        })
                    
                    compliance['conflicting_rules'].append(rule['rule_id'])
                
                # Check if recommendation supports rule
                elif self._check_recommendation_supports_rule(rec_content, rule):
                    compliance['supporting_rules'].append(rule['rule_id'])
            
        except Exception as e:
            logger.error(f"Error analyzing recommendation compliance: {e}")
        
        return compliance
    
    def _check_recommendation_rule_conflict(self, rec_content: str, 
                                          rule: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a recommendation conflicts with a specific rule"""
        # Simplified conflict detection
        # In practice, this would use more sophisticated NLP analysis
        
        rule_content = rule['content'].upper()
        rec_content_upper = rec_content.upper()
        
        # Check for direct conflicts with NEVER/MUST NOT patterns
        if 'NEVER' in rule_content:
            never_items = rule_content.split('NEVER')[1:] 
            for item in never_items:
                prohibited_term = item.split()[0] if item.split() else ''
                if prohibited_term and prohibited_term in rec_content_upper:
                    return {
                        'conflicts': True,
                        'reason': f"Recommendation suggests '{prohibited_term}' which rule prohibits"
                    }
        
        # Check for conflicts with MUST patterns
        if 'MUST' in rule_content and 'NOT' not in rule_content:
            must_items = rule_content.split('MUST')[1:]
            for item in must_items:
                required_term = item.split()[0] if item.split() else ''
                if required_term and required_term not in rec_content_upper:
                    # This is not necessarily a conflict, just lack of support
                    pass
        
        return {'conflicts': False, 'reason': ''}
    
    def _check_recommendation_supports_rule(self, rec_content: str, rule: Dict[str, Any]) -> bool:
        """Check if a recommendation actively supports a rule"""
        rule_content = rule['content'].upper()
        rec_content_upper = rec_content.upper()
        
        # Check if recommendation mentions rule keywords positively
        if 'ALWAYS' in rule_content:
            always_items = rule_content.split('ALWAYS')[1:]
            for item in always_items:
                encouraged_term = item.split()[0] if item.split() else ''
                if encouraged_term and encouraged_term in rec_content_upper:
                    return True
        
        return False
    
    def _calculate_priority_adjustment(self, rule_compliance: Dict[str, Any]) -> float:
        """Calculate priority adjustment based on rule compliance"""
        adjustment = 0.0
        
        # Penalty for violations
        adjustment -= len(rule_compliance['violations']) * 0.3
        
        # Penalty for warnings
        adjustment -= len(rule_compliance['warnings']) * 0.1
        
        # Bonus for supporting rules
        adjustment += len(rule_compliance['supporting_rules']) * 0.1
        
        # Ensure adjustment is within reasonable bounds
        return max(-0.5, min(0.5, adjustment))
    
    def _generate_rule_aware_guidance(self, base_recommendation: Dict[str, Any],
                                    rule_compliance: Dict[str, Any],
                                    applicable_rules: List[Dict[str, Any]]) -> str:
        """Generate implementation guidance that considers user workspace rules"""
        guidance_parts = []
        
        # Base guidance
        base_guidance = base_recommendation.get('description', '')
        if base_guidance:
            guidance_parts.append(f"**Base Recommendation:** {base_guidance}")
        
        # Rule compliance guidance
        if rule_compliance['violations']:
            guidance_parts.append("**⚠️ Rule Violations:**")
            for violation in rule_compliance['violations']:
                guidance_parts.append(f"- {violation['rule_title']}: {violation['conflict_reason']}")
            guidance_parts.append("**Action Required:** Address these violations before implementing.")
        
        if rule_compliance['warnings']:
            guidance_parts.append("**⚠️ Rule Warnings:**")
            for warning in rule_compliance['warnings']:
                guidance_parts.append(f"- {warning['rule_title']}: {warning['conflict_reason']}")
            guidance_parts.append("**Recommendation:** Consider these warnings during implementation.")
        
        if rule_compliance['supporting_rules']:
            guidance_parts.append("**✅ Supporting Rules:**")
            supporting_rule_titles = []
            for rule_id in rule_compliance['supporting_rules']:
                rule = next((r for r in applicable_rules if r['rule_id'] == rule_id), None)
                if rule:
                    supporting_rule_titles.append(rule['title'])
            
            for title in supporting_rule_titles:
                guidance_parts.append(f"- {title}")
            guidance_parts.append("**Benefit:** This recommendation aligns with your workspace rules.")
        
        # Implementation tips
        if not rule_compliance['violations']:
            guidance_parts.append("**Implementation:** This recommendation is compliant with your workspace rules and can be implemented safely.")
        
        return "\n".join(guidance_parts)
    
    def check_code_compliance(self, code_content: str, workflow_name: str = None,
                            context: str = None) -> Dict[str, Any]:
        """
        Check code compliance against user workspace rules
        
        Args:
            code_content: Code to check for compliance
            workflow_name: Associated workflow name (optional)
            context: Code context (language, framework, etc.)
            
        Returns:
            Detailed compliance report
        """
        try:
            # Get basic compliance check
            compliance_result = self.rules_integration.check_compliance(code_content, context)
            
            # Enhance with workflow context if available
            if workflow_name and workflow_name in self.workflow_contexts:
                workflow_context = self.workflow_contexts[workflow_name]
                
                # Add workflow-specific context
                compliance_result['workflow_context'] = {
                    'workflow_name': workflow_name,
                    'applicable_rules_count': len(workflow_context.applicable_rules),
                    'compliance_requirements': workflow_context.compliance_requirements
                }
                
                # Add learning insights
                if workflow_name in self.rule_aware_recommendations:
                    recommendations = self.rule_aware_recommendations[workflow_name]
                    compliance_result['learning_insights'] = {
                        'total_recommendations': len(recommendations),
                        'compliant_recommendations': len([r for r in recommendations if r.rule_compliance['compliant']]),
                        'high_confidence_recommendations': len([r for r in recommendations if r.confidence >= 0.8])
                    }
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error checking code compliance: {e}")
            return {'compliant': True, 'violations': [], 'warnings': [], 'error': str(e)}
    
    def complete_enhanced_workflow(self, workflow_name: str, 
                                 outcome: Dict[str, Any],
                                 final_code: str = None) -> Dict[str, Any]:
        """
        Complete an enhanced workflow with rule compliance analysis
        
        Args:
            workflow_name: Name of the workflow
            outcome: Workflow outcome information
            final_code: Final generated code (optional)
            
        Returns:
            Enhanced completion report with rule compliance
        """
        try:
            # Complete the base learning workflow
            # Backward-compatibility shim: older LearningSystemIntegration may not define complete_workflow
            if hasattr(self.learning_system, "complete_workflow"):
                base_completion = self.learning_system.complete_workflow(workflow_name, outcome)
            else:
                base_completion = {
                    'workflow_name': workflow_name,
                    'outcome': outcome,
                    'status': 'completed'
                }
            
            # Get workflow context
            workflow_context = self.workflow_contexts.get(workflow_name)
            
            # Analyze final code compliance if provided
            final_compliance = None
            if final_code and workflow_context:
                # Determine context from project information
                context_hint = None
                if 'language' in workflow_context.project_context:
                    context_hint = workflow_context.project_context['language']
                
                final_compliance = self.check_code_compliance(
                    final_code, workflow_name, context_hint
                )
            
            # Create enhanced completion report
            enhanced_completion = {
                'workflow_name': workflow_name,
                'base_completion': base_completion,
                'rule_compliance_summary': {
                    'rules_applied': len(workflow_context.applicable_rules) if workflow_context else 0,
                    'compliance_requirements_met': workflow_context.compliance_requirements if workflow_context else {},
                    'final_code_compliance': final_compliance
                },
                'learning_insights': {
                    'recommendations_generated': len(self.rule_aware_recommendations.get(workflow_name, [])),
                    'rule_aware_learning_active': self.system_context_extracted,
                    'user_rules_integrated': self.rules_integration.get_rules_summary()
                },
                'completed_at': datetime.now().isoformat()
            }
            
            # Clean up workflow context
            if workflow_name in self.workflow_contexts:
                del self.workflow_contexts[workflow_name]
            
            if workflow_name in self.rule_aware_recommendations:
                del self.rule_aware_recommendations[workflow_name]
            
            logger.info(f"Completed enhanced workflow: {workflow_name}")
            
            return enhanced_completion
            
        except Exception as e:
            logger.error(f"Error completing enhanced workflow: {e}")
            # Fallback to base completion
            if hasattr(self.learning_system, "complete_workflow"):
                return self.learning_system.complete_workflow(workflow_name, outcome)
            return {
                'workflow_name': workflow_name,
                'outcome': outcome,
                'status': 'completed'
            }
    
    def get_enhanced_system_status(self) -> Dict[str, Any]:
        """Get enhanced system status including rule integration"""
        try:
            # Get base learning system status
            base_status = self.learning_system.get_system_status()
            
            # Get rules integration status
            rules_summary = self.rules_integration.get_rules_summary()
            
            # Create enhanced status
            enhanced_status = {
                'base_learning_system': asdict(base_status),
                'user_workspace_rules': {
                    'rules_extracted': self.system_context_extracted,
                    'last_rules_update': self.last_rules_update.isoformat() if self.last_rules_update else None,
                    'rules_summary': rules_summary,
                    'integration_active': True
                },
                'enhanced_workflows': {
                    'active_workflows': len(self.workflow_contexts),
                    'workflows_with_recommendations': len(self.rule_aware_recommendations),
                    'total_rule_aware_recommendations': sum(
                        len(recs) for recs in self.rule_aware_recommendations.values()
                    )
                },
                'system_health': {
                    'learning_system_active': base_status.system_active,
                    'rules_integration_active': len(self.rules_integration.user_rules) > 0,
                    'enhanced_features_available': self.system_context_extracted
                }
            }
            
            return enhanced_status
            
        except Exception as e:
            logger.error(f"Error getting enhanced system status: {e}")
            return {'error': str(e), 'fallback_status': 'basic_learning_only'}


# Factory function for easy integration
def create_enhanced_workflow_learning(learning_data_dir: str = "learning_data",
                                    learning_config_overrides: Dict[str, Any] = None,
                                    rules_config_overrides: Dict[str, Any] = None) -> EnhancedWorkflowLearning:
    """Create and configure an enhanced workflow learning system"""
    
    # Create learning system config
    learning_config = LearningSystemConfig(learning_data_dir=learning_data_dir)
    if learning_config_overrides:
        for key, value in learning_config_overrides.items():
            if hasattr(learning_config, key):
                setattr(learning_config, key, value)
    
    # Create rules config
    rules_config = WorkspaceRulesConfig()
    if rules_config_overrides:
        for key, value in rules_config_overrides.items():
            if hasattr(rules_config, key):
                setattr(rules_config, key, value)
    
    return EnhancedWorkflowLearning(learning_config, rules_config, learning_data_dir)


if __name__ == "__main__":
    # Example usage
    enhanced_learning = create_enhanced_workflow_learning("test_learning_data")
    
    # Example system context with user rules
    system_context = """
    <user_rules>
    1. NEVER use hardcoded API keys or credentials in code
    2. ALWAYS use type hints for function parameters and return values
    3. Code must be immediately runnable with all necessary imports
    4. Follow debugging best practices: address root cause, not symptoms
    </user_rules>
    
    <MEMORY[security-rule]>
    All external API calls must include proper error handling and timeout configuration.
    Never expose sensitive information in logs or error messages.
    </MEMORY[security-rule]>
    """
    
    # Extract rules from system context
    extracted_count = enhanced_learning.extract_system_context_rules(system_context)
    print(f"Extracted {extracted_count} rules from system context")
    
    # Start enhanced workflow
    project_context = {
        'language': 'python',
        'framework': 'fastapi',
        'technologies': ['python', 'fastapi', 'postgresql']
    }
    
    workflow_context = enhanced_learning.start_enhanced_workflow(
        'test_workflow', 
        project_context,
        system_context
    )
    
    print(f"Started workflow with {len(workflow_context.applicable_rules)} applicable rules")
    
    # Get rule-aware recommendations
    recommendations = enhanced_learning.get_rule_aware_recommendations('test_workflow')
    print(f"Generated {len(recommendations)} rule-aware recommendations")
    
    # Check code compliance
    example_code = '''
def process_user_data(user_data):
    api_key = "sk-1234567890"  # This violates the hardcoded credentials rule
    return user_data.upper()
'''
    
    compliance = enhanced_learning.check_code_compliance(example_code, 'test_workflow', 'python')
    print(f"Code compliance: {compliance['compliant']}")
    print(f"Violations: {len(compliance['violations'])}")
    
    # Get enhanced system status
    status = enhanced_learning.get_enhanced_system_status()
    print(f"Enhanced system status: {status['system_health']}")
