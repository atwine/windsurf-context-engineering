# How Research Automation Works: Step-by-Step

## 🔄 **Automated Research Workflow for Scikit-learn + sksurv**

### **Phase 1: Documentation Discovery & Validation**
```python
# The system automatically:
1. Extracts URLs from your project prompt
2. Validates each documentation URL:
   - https://scikit-survival.readthedocs.io/
   - https://scikit-learn.org/stable/modules/survival_analysis.html
3. Checks accessibility, response time, and freshness
4. Scans for documentation quality indicators
```

### **Phase 2: Package Version Research**
```python
# For each package mentioned (scikit-learn, sksurv):
1. Queries PyPI API for latest versions
2. Checks compatibility between packages
3. Identifies version-specific requirements
4. Scans changelogs for breaking changes
```

### **Phase 3: API Endpoint Validation**
```python
# Tests critical API endpoints:
- PyPI package information: https://pypi.org/pypi/scikit-survival/json
- Documentation API: https://scikit-survival.readthedocs.io/en/stable/api/
- GitHub releases: https://api.github.com/repos/sebp/scikit-survival/releases
```

### **Phase 4: Best Practice Research**
```python
# Web searches for current best practices:
- "scikit-survival cox regression best practices 2024"
- "sksurv preprocessing censored data"
- "survival analysis scikit-learn validation metrics"
- "time to event analysis python performance"
```

### **Phase 5: Common Issues Detection**
```python
# Searches Stack Overflow and GitHub issues:
- Recent issues with scikit-survival installation
- Common errors with Cox proportional hazards
- Performance optimization techniques
- Data preprocessing gotchas
```

### **Phase 6: Context Assembly**
```python
# Combines all research into structured context:
{
    "packages": {
        "scikit-survival": {
            "version": "0.22.2",
            "breaking_changes": ["CoxPHSurvivalAnalysis API change"],
            "best_practices": ["Use CoxnetSurvivalAnalysis for regularization"]
        }
    },
    "documentation_quality": 0.95,
    "common_issues": [...],
    "recommended_patterns": [...]
}
```

## 🎯 **What This Means for Your Project**

### **1. Accurate Implementation**
Instead of generating code with outdated APIs, the system knows:
```python
# ❌ OLD WAY (might be generated without research):
from sksurv.linear_model import CoxPHSurvivalAnalysis
model = CoxPHSurvivalAnalysis(fit_baseline_model=True)  # This parameter was removed!

# ✅ NEW WAY (with research automation):
from sksurv.linear_model import CoxPHSurvivalAnalysis
model = CoxPHSurvivalAnalysis()  # Correct current API
```

### **2. Proactive Problem Prevention**
The system includes solutions for known issues:
```python
# Automatically includes proper preprocessing:
from sksurv.preprocessing import encode_categorical
from sklearn.preprocessing import StandardScaler

# Handles censored data correctly:
X_encoded = encode_categorical(X_categorical)
X_scaled = StandardScaler().fit_transform(X_numeric)
```

### **3. Current Best Practices**
Incorporates latest recommendations:
```python
# Uses current validation metrics:
from sksurv.metrics import concordance_index_censored  # Current
# Instead of: concordance_index_ipcw  # Deprecated

# Includes proper model selection:
from sksurv.linear_model import CoxnetSurvivalAnalysis  # Regularized version
from sksurv.ensemble import RandomSurvivalForest        # For non-linear relationships
```

### **4. Complete Project Structure**
Generates a project with:
```
survival-analysis-project/
├── data/
│   ├── preprocessing.py      # Handles censored data correctly
│   └── validation.py         # Current validation metrics
├── models/
│   ├── cox_regression.py     # Updated API usage
│   ├── random_forest.py      # Best practice implementation
│   └── ensemble.py           # Advanced techniques
├── visualization/
│   ├── survival_curves.py    # Kaplan-Meier plots
│   └── risk_assessment.py    # Risk prediction visualization
├── tests/
│   ├── test_preprocessing.py # Comprehensive test coverage
│   └── test_models.py        # Model validation tests
├── requirements.txt          # Exact compatible versions
└── README.md                 # Current setup instructions
```

## 🚀 **The Power of Dynamic Research**

### **Without Research Automation:**
- Might use outdated APIs that cause runtime errors
- Miss important preprocessing steps for survival data
- Use deprecated validation metrics
- Struggle with version compatibility issues
- Spend hours debugging known issues

### **With Research Automation:**
- ✅ Always uses current, working APIs
- ✅ Includes proper preprocessing for censored data
- ✅ Uses latest validation metrics and best practices
- ✅ Ensures package compatibility from the start
- ✅ Includes solutions for common pitfalls
- ✅ Generates production-ready code structure

## 🔧 **How to Use It**

1. **Create your project prompt** with scikit-learn and sksurv requirements
2. **Run `/generate-plan ./your-prompt.md`** - research happens automatically
3. **Review the generated plan** - includes all current best practices
4. **Run `/execute-plan ./plans/your-plan.md`** - implements with validated APIs
5. **Get working code** that uses current APIs and best practices

The research automation ensures your survival analysis project starts with the most current, validated information available!
