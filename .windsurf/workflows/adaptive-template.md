---
description: Generate adaptive project templates based on project analysis
---

# Adaptive Template Generation Workflow

This workflow analyzes your project requirements and generates customized project templates, structure, and implementation plans.

## Step 1: Project Analysis
Analyze the project prompt to determine type, complexity, and technology stack.

```bash
python utilities/project-type-detector.py --prompt "Your project description here" --output analysis.json
```

## Step 2: Template Selection
Select the most appropriate template based on the analysis.

```bash
python utilities/adaptive-template-engine.py --analysis analysis.json --select-template
```

## Step 3: Generate Project Templates
Generate customized project files based on the selected template.

```bash
python utilities/adaptive-template-engine.py --analysis analysis.json --generate-templates --output-dir generated_project
```

## Step 4: Review Generated Templates
Review the generated project structure and templates:

- Check `generated_project/README.md` for project overview
- Review `generated_project/project_structure.md` for file organization
- Examine `generated_project/implementation_plan.md` for development roadmap
- Validate `generated_project/requirements.txt` for dependencies

## Step 5: Customize Templates (Optional)
Modify templates based on specific requirements:

```bash
# Edit template variables
python utilities/adaptive-template-engine.py --analysis analysis.json --customize --variables project_name=my_project,author=your_name

# Add specific features
python utilities/adaptive-template-engine.py --analysis analysis.json --add-features authentication,logging,testing
```

## Step 6: Initialize Project
Create the actual project structure:

```bash
# Create project directory
mkdir my_project
cd my_project

# Copy generated templates
cp -r ../generated_project/* .

# Initialize version control
git init
git add .
git commit -m "Initial project structure from adaptive template"
```

## Step 7: Validate Project Setup
Run quality checks on the generated project:

```bash
# Run project validation
python ../utilities/test_simple_templates.py

# Check dependencies
pip install -r requirements.txt

# Run any generated tests
python -m pytest tests/ -v
```

## Available Templates

### Web Applications
- `web_application_simple`: Basic web app with Flask/FastAPI
- `web_application_complex`: Full-featured web app with authentication, database, API

### API Services
- `rest_api_simple`: Basic REST API with CRUD operations
- `rest_api_complex`: Enterprise API with authentication, rate limiting, documentation

### Machine Learning
- `ml_project_simple`: Basic ML project with data processing and model training
- `ml_project_complex`: MLOps pipeline with experiment tracking and deployment

### CLI Tools
- `cli_tool_simple`: Basic command-line tool with argument parsing
- `cli_tool_complex`: Advanced CLI with subcommands, configuration, plugins

### Data Processing
- `data_pipeline_simple`: Basic ETL pipeline
- `data_pipeline_complex`: Scalable data processing with monitoring

## Template Customization Options

### Variables
- `project_name`: Name of the project
- `description`: Project description
- `author`: Project author
- `version`: Initial version
- `license`: License type

### Features
- `authentication`: User authentication system
- `database`: Database integration
- `api`: REST API endpoints
- `testing`: Test suite setup
- `logging`: Logging configuration
- `monitoring`: Application monitoring
- `documentation`: API documentation

### Technology Stack
- `python`: Python-based project
- `javascript`: JavaScript/Node.js project
- `java`: Java-based project
- `docker`: Docker containerization
- `kubernetes`: Kubernetes deployment

## Quality Assurance

The adaptive template system includes:

1. **Template Validation**: Ensures generated templates are syntactically correct
2. **Dependency Checking**: Validates all required dependencies are included
3. **Structure Validation**: Confirms project structure follows best practices
4. **Security Scanning**: Checks for common security issues in templates
5. **Code Quality**: Ensures generated code meets quality standards

## Integration with Existing Workflows

This workflow integrates with:

- `/generate-plan`: Uses adaptive templates for implementation planning
- `/validate-result`: Validates generated project quality
- `/research-automation`: Incorporates latest best practices into templates
- `/init-context`: Initializes projects with appropriate templates

## Troubleshooting

### Common Issues

1. **Template Not Found**: Ensure template files exist in `templates/` directory
2. **Analysis Failed**: Check project prompt is descriptive enough
3. **Generation Failed**: Verify template syntax and variables
4. **Dependencies Missing**: Run `pip install -r requirements.txt`

### Debug Mode
Enable debug mode for detailed logging:

```bash
python utilities/adaptive-template-engine.py --debug --analysis analysis.json
```

### Manual Template Selection
Override automatic selection:

```bash
python utilities/adaptive-template-engine.py --template rest_api_simple --generate-templates
```

## Next Steps

After generating templates:

1. Review and customize generated files
2. Install dependencies and set up environment
3. Run initial tests to validate setup
4. Begin development following the implementation plan
5. Use quality guardrails to maintain code quality

The adaptive template system ensures your project starts with the right structure, dependencies, and best practices for your specific use case.
