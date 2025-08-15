---
description: Initialize ML/AI Context Engineering Framework with TRIPOD+AI Compliance Assessment
---

# ML/AI Context Engineering Initialization

This workflow extends the standard context engineering framework for ML/AI projects with TRIPOD+AI compliance assessment and specialized environment analysis.

// turbo-all

## Phase 1: Foundation Context Loading

1. **Execute Standard Context Initialization**
   ```bash
   # First run the standard init-context to establish foundation
   /init-context
   ```
   - This preserves all existing functionality
   - Establishes environment analysis, Git operations, and user workspace rules
   - Creates project memory and development setup

## Phase 2: ML/AI Project Analysis

2. **ML/AI Project Type Detection**
   ```python
   from tools import IntelligenceEngine, PredictiveAnalytics
   
   intelligence = IntelligenceEngine('.')
   ml_analysis = intelligence.detect_ml_project_type()
   
   print(f"ML Project Type: {ml_analysis['project_type']}")
   print(f"Detected Libraries: {ml_analysis['ml_libraries']}")
   print(f"Data Directories: {ml_analysis['data_paths']}")
   ```

3. **ML Environment Assessment**
   - **GPU/Hardware Detection**: Check for CUDA, GPU availability, memory capacity
   - **ML Library Analysis**: Detect installed ML frameworks (scikit-learn, tensorflow, pytorch, etc.)
   - **Data Infrastructure**: Identify data directories, datasets, model storage
   - **Notebook Environment**: Check for Jupyter, data science tools
   - **Experiment Tracking**: Detect MLflow, Weights & Biases, TensorBoard setups

4. **Clinical/Healthcare ML Detection**
   - **Healthcare Libraries**: Check for lifelines, statsmodels, clinical data tools
   - **Data Compliance**: Assess HIPAA, GDPR considerations
   - **Clinical Workflow Patterns**: Identify prediction model development patterns
   - **Regulatory Requirements**: Check for FDA, CE marking considerations

## Phase 3: TRIPOD+AI Compliance Assessment

5. **TRIPOD+AI Readiness Analysis**
   ```python
   tripod_assessment = intelligence.assess_tripod_compliance()
   
   print(f"TRIPOD+AI Compliance Score: {tripod_assessment['compliance_score']:.1%}")
   print(f"Missing Requirements: {len(tripod_assessment['missing_items'])}")
   print(f"Documentation Status: {tripod_assessment['documentation_status']}")
   ```

6. **Compliance Gap Analysis**
   - **Data Documentation**: Check for data source documentation (Items 5-8)
   - **Model Documentation**: Assess model development documentation (Items 9-17)
   - **Validation Framework**: Check validation and performance documentation (Items 13-16)
   - **Reproducibility**: Assess open science practices (Item 18)
   - **Reporting Structure**: Check results and discussion documentation (Items 20-27)

7. **Create TRIPOD+AI Project Structure**
   ```
   docs/
   ├── tripod_compliance/
   │   ├── checklist.md
   │   ├── data_documentation.md
   │   ├── model_documentation.md
   │   ├── validation_results.md
   │   └── compliance_report.md
   ├── data_management/
   │   ├── data_sources.md
   │   ├── preprocessing.md
   │   └── quality_checks.md
   └── model_development/
       ├── methodology.md
       ├── performance_metrics.md
       └── clinical_interpretation.md
   ```

## Phase 4: ML-Specific Environment Setup

8. **ML Development Environment Optimization**
   - **Virtual Environment Enhancement**: Add ML-specific dependencies to requirements
   - **GPU Configuration**: Set up CUDA environment if available
   - **Data Pipeline Setup**: Configure data loading and preprocessing pipelines
   - **Experiment Tracking**: Initialize MLflow or similar experiment tracking

9. **Model Development Infrastructure**
   - **Model Storage**: Set up model versioning and storage
   - **Performance Monitoring**: Configure model performance tracking
   - **Validation Framework**: Set up cross-validation and testing infrastructure
   - **Documentation Templates**: Create ML-specific documentation templates

## Phase 5: TRIPOD+AI Workflow Preparation

10. **Workflow Recommendation Engine**
    ```python
    workflow_recommendations = intelligence.recommend_ml_workflows(
        project_type=ml_analysis['project_type'],
        compliance_level=tripod_assessment['compliance_score'],
        data_type=ml_analysis['data_characteristics']
    )
    
    for workflow in workflow_recommendations:
        print(f"📋 Recommended: {workflow['name']} - {workflow['description']}")
    ```

11. **Next Steps Guidance**
    - **For Clinical Prediction Models**: Recommend `/tripod-ml-pipeline`
    - **For General ML Projects**: Recommend enhanced `/generate-plan` with ML considerations
    - **For Research Projects**: Recommend `/research-automation` with ML extensions
    - **For Production ML**: Recommend `/execute-plan-enhanced` with MLOps integration

## Phase 6: ML-Enhanced Memory Creation

12. **Store ML-Specific Context**
    ```python
    ml_context = {
        'project_type': ml_analysis['project_type'],
        'ml_libraries': ml_analysis['ml_libraries'],
        'data_characteristics': ml_analysis['data_characteristics'],
        'tripod_compliance': tripod_assessment,
        'hardware_capabilities': ml_analysis['hardware_info'],
        'recommended_workflows': workflow_recommendations
    }
    
    # Store in enhanced project memory
    intelligence.store_ml_context(ml_context)
    ```

## Phase 7: ML Environment Validation

13. **ML-Specific Readiness Check**
    - **Data Access**: Verify data directories and permissions
    - **Compute Resources**: Validate GPU/CPU availability and configuration
    - **Library Compatibility**: Check for version conflicts in ML stack
    - **Storage Capacity**: Assess storage for models, data, and experiments
    - **Compliance Readiness**: Validate TRIPOD+AI documentation structure

14. **Performance Baseline Establishment**
    - **System Benchmarks**: Run basic ML performance tests
    - **Memory Profiling**: Check memory usage patterns
    - **I/O Performance**: Test data loading and saving speeds
    - **Model Training Capacity**: Estimate training capabilities

## Phase 8: Workflow Handoff Preparation

15. **ML-Aware Next Steps**
    - **Environment Summary**: Display comprehensive ML environment analysis
    - **Compliance Status**: Show TRIPOD+AI readiness assessment
    - **Workflow Recommendations**: Present tailored workflow suggestions
    - **Optimization Opportunities**: Highlight performance improvement possibilities

16. **Ready for ML Development**
    - Confirm ML context is loaded and ready for specialized workflows
    - **For TRIPOD+AI Projects**: Ready for `/tripod-ml-pipeline`
    - **For General ML**: Ready for ML-enhanced `/generate-plan`
    - **Integration Status**: All ML-specific enhancements active and ready

## Key Advantages of ML-Specific Initialization

### **Extends Rather Than Replaces**
- Builds on proven `/init-context` foundation
- Preserves all existing functionality
- Adds ML-specific capabilities as enhancements

### **TRIPOD+AI Integration**
- Automated compliance assessment
- Gap analysis and remediation guidance
- Documentation structure creation
- Workflow recommendations based on compliance needs

### **ML Environment Optimization**
- Hardware-aware configuration
- ML library compatibility checking
- Performance optimization recommendations
- Experiment tracking setup

### **Intelligent Workflow Routing**
- Project type-specific workflow recommendations
- Compliance-driven process selection
- Performance-optimized development paths
- Clinical vs. research pathway guidance

This workflow transforms your framework into an ML/AI-aware development environment while maintaining full backward compatibility with existing projects and workflows.
